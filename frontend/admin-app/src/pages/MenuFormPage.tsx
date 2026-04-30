import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuthStore } from '../stores/authStore';
import { useToastStore } from '../stores/toastStore';
import { getMenu, getCategories, createMenu, updateMenu } from '../api/menus';
import type { Category } from '../types';

interface MenuFormData { name: string; price: string; category_id: string; description: string; }

export default function MenuFormPage() {
  const { menuId } = useParams<{ menuId: string }>();
  const navigate = useNavigate();
  const storeId = useAuthStore((s) => s.storeId);
  const addToast = useToastStore((s) => s.addToast);
  const isEdit = !!menuId;

  const { register, handleSubmit, setValue, formState: { errors } } = useForm<MenuFormData>();
  const [categories, setCategories] = useState<Category[]>([]);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoading, setIsLoading] = useState(isEdit);

  useEffect(() => {
    if (!storeId) return;
    getCategories(storeId).then(setCategories);
    if (isEdit && menuId) {
      setIsLoading(true);
      getMenu(storeId, menuId).then((menu) => {
        setValue('name', menu.name);
        setValue('price', String(menu.price));
        setValue('category_id', menu.category_id);
        setValue('description', menu.description ?? '');
        if (menu.image_url) setImagePreview(menu.image_url);
      }).finally(() => setIsLoading(false));
    }
  }, [storeId, isEdit, menuId, setValue]);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) { addToast({ type: 'error', message: '지원하지 않는 파일 형식입니다.' }); return; }
    if (file.size > 5 * 1024 * 1024) { addToast({ type: 'error', message: '파일 크기는 5MB 이하여야 합니다.' }); return; }
    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
  };

  const onSubmit = async (data: MenuFormData) => {
    if (!storeId) return;
    setIsSubmitting(true);
    const formData = new FormData();
    formData.append('name', data.name);
    formData.append('price', data.price);
    formData.append('category_id', data.category_id);
    if (data.description) formData.append('description', data.description);
    if (imageFile) formData.append('image', imageFile);
    try {
      if (isEdit && menuId) { await updateMenu(storeId, menuId, formData); addToast({ type: 'success', message: '메뉴가 수정되었습니다.' }); }
      else { await createMenu(storeId, formData); addToast({ type: 'success', message: '메뉴가 등록되었습니다.' }); }
      navigate('/menus');
    } catch { addToast({ type: 'error', message: isEdit ? '메뉴 수정에 실패했습니다.' : '메뉴 등록에 실패했습니다.' }); }
    finally { setIsSubmitting(false); }
  };

  if (isLoading) return <div className="flex h-64 items-center justify-center"><div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" /></div>;

  return (
    <div className="mx-auto max-w-lg">
      <h2 className="mb-4 text-xl font-bold text-gray-900 dark:text-white">{isEdit ? '메뉴 수정' : '메뉴 등록'}</h2>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">메뉴명 *</label>
          <input {...register('name', { required: '메뉴명을 입력해주세요.' })} className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white" />
          {errors.name && <p className="mt-1 text-xs text-red-500">{errors.name.message}</p>}
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">가격 *</label>
          <input type="number" {...register('price', { required: '가격을 입력해주세요.', validate: (v) => Number(v) > 0 || '가격은 0보다 커야 합니다.' })} className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white" />
          {errors.price && <p className="mt-1 text-xs text-red-500">{errors.price.message}</p>}
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">카테고리 *</label>
          <select {...register('category_id', { required: '카테고리를 선택해주세요.' })} className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white">
            <option value="">선택</option>
            {categories.map((cat) => <option key={cat.id} value={cat.id}>{cat.name}</option>)}
          </select>
          {errors.category_id && <p className="mt-1 text-xs text-red-500">{errors.category_id.message}</p>}
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">설명</label>
          <textarea {...register('description')} rows={3} className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white" />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">이미지</label>
          <div className="flex items-center gap-4">
            <div className="h-24 w-24 flex-shrink-0 overflow-hidden rounded-lg border border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-800">
              {imagePreview ? <img src={imagePreview} alt="미리보기" className="h-full w-full object-cover" /> : <div className="flex h-full w-full items-center justify-center text-2xl text-gray-300">🍽️</div>}
            </div>
            <div className="flex flex-col gap-2">
              <label className="cursor-pointer rounded-lg border border-gray-300 px-3 py-1.5 text-sm hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300">이미지 선택<input type="file" accept=".jpg,.jpeg,.png,.webp" onChange={handleImageChange} className="hidden" /></label>
              {imagePreview && <button type="button" onClick={() => { setImageFile(null); setImagePreview(null); }} className="text-xs text-red-500 hover:underline">이미지 제거</button>}
            </div>
          </div>
        </div>
        <div className="flex gap-2 pt-2">
          <button type="submit" disabled={isSubmitting} className="flex-1 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">{isSubmitting ? '처리 중...' : isEdit ? '수정' : '등록'}</button>
          <button type="button" onClick={() => navigate('/menus')} className="rounded-lg border border-gray-300 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300">취소</button>
        </div>
      </form>
    </div>
  );
}
