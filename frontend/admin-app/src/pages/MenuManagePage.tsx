import { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { useToastStore } from '../stores/toastStore';
import { getMenus, getCategories, deleteMenu, reorderMenus } from '../api/menus';
import ConfirmDialog from '../components/ConfirmDialog';
import type { Menu, Category } from '../types';
import { DndContext, closestCenter, PointerSensor, useSensor, useSensors, type DragEndEvent } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy, useSortable, arrayMove } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

function SortableMenuItem({ menu, categoryName, onEdit, onDelete }: { menu: Menu; categoryName: string; onEdit: (id: string) => void; onDelete: (id: string, name: string) => void }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: menu.id });
  const style = { transform: CSS.Transform.toString(transform), transition, opacity: isDragging ? 0.5 : 1 };

  return (
    <div ref={setNodeRef} style={style} className="flex items-center gap-3 rounded-xl border border-gray-200 bg-white px-4 py-3 dark:border-gray-700 dark:bg-gray-800">
      <button {...attributes} {...listeners} className="cursor-grab text-gray-400 hover:text-gray-600" aria-label="드래그">≡</button>
      <div className="h-12 w-12 flex-shrink-0 overflow-hidden rounded-lg bg-gray-100 dark:bg-gray-700">
        {menu.image_url ? <img src={menu.image_url} alt={menu.name} className="h-full w-full object-cover" /> : <div className="flex h-full w-full items-center justify-center text-xs text-gray-400">🍽️</div>}
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-gray-900 dark:text-white truncate">{menu.name}</p>
        <p className="text-sm text-blue-600 dark:text-blue-400">₩{menu.price.toLocaleString()}</p>
      </div>
      <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600 dark:bg-gray-700 dark:text-gray-400">{categoryName}</span>
      <div className="flex gap-1">
        <button onClick={() => onEdit(menu.id)} className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700" aria-label="수정">✏️</button>
        <button onClick={() => onDelete(menu.id, menu.name)} className="rounded-lg p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20" aria-label="삭제">🗑️</button>
      </div>
    </div>
  );
}

export default function MenuManagePage() {
  const navigate = useNavigate();
  const storeId = useAuthStore((s) => s.storeId);
  const addToast = useToastStore((s) => s.addToast);

  const [menus, setMenus] = useState<Menu[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [deleteTarget, setDeleteTarget] = useState<{ id: string; name: string } | null>(null);

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }));

  const categoryMap = useMemo(() => new Map(categories.map((c) => [c.id, c.name])), [categories]);

  useEffect(() => {
    if (!storeId) return;
    setIsLoading(true);
    Promise.all([getMenus(storeId), getCategories(storeId)])
      .then(([m, c]) => { setMenus(m); setCategories(c); })
      .finally(() => setIsLoading(false));
  }, [storeId]);

  const filteredMenus = selectedCategory ? menus.filter((m) => m.category_id === selectedCategory) : menus;

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id || !storeId) return;
    const oldIndex = filteredMenus.findIndex((m) => m.id === active.id);
    const newIndex = filteredMenus.findIndex((m) => m.id === over.id);
    const reordered = arrayMove(filteredMenus, oldIndex, newIndex);
    const prevMenus = menus;
    const updatedMenus = menus.map((m) => { const idx = reordered.findIndex((r) => r.id === m.id); return idx >= 0 ? { ...m, sort_order: idx } : m; });
    setMenus(updatedMenus);
    try {
      await reorderMenus(storeId, reordered.map((m, i) => ({ menu_id: m.id, sort_order: i })));
      addToast({ type: 'success', message: '메뉴 순서가 변경되었습니다.' });
    } catch { setMenus(prevMenus); addToast({ type: 'error', message: '순서 변경에 실패했습니다.' }); }
  };

  const handleDelete = async () => {
    if (!storeId || !deleteTarget) return;
    try { await deleteMenu(storeId, deleteTarget.id); setMenus((prev) => prev.filter((m) => m.id !== deleteTarget.id)); addToast({ type: 'success', message: '메뉴가 삭제되었습니다.' }); }
    catch { addToast({ type: 'error', message: '메뉴 삭제에 실패했습니다.' }); }
    setDeleteTarget(null);
  };

  if (isLoading) return <div className="flex h-64 items-center justify-center"><div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" /></div>;

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">메뉴 관리</h2>
        <button onClick={() => navigate('/menus/new')} className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">+ 메뉴 추가</button>
      </div>
      <div className="mb-4 flex gap-2 overflow-x-auto">
        <button onClick={() => setSelectedCategory(null)} className={`whitespace-nowrap rounded-full px-3 py-1.5 text-sm ${!selectedCategory ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'}`}>전체</button>
        {categories.map((cat) => (
          <button key={cat.id} onClick={() => setSelectedCategory(cat.id)} className={`whitespace-nowrap rounded-full px-3 py-1.5 text-sm ${selectedCategory === cat.id ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'}`}>{cat.name}</button>
        ))}
      </div>
      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <SortableContext items={filteredMenus.map((m) => m.id)} strategy={verticalListSortingStrategy}>
          <div className="space-y-2">
            {filteredMenus.map((menu) => (
              <SortableMenuItem key={menu.id} menu={menu} categoryName={categoryMap.get(menu.category_id) ?? ''} onEdit={(id) => navigate(`/menus/${id}/edit`)} onDelete={(id, name) => setDeleteTarget({ id, name })} />
            ))}
          </div>
        </SortableContext>
      </DndContext>
      {filteredMenus.length === 0 && <p className="py-8 text-center text-gray-500">메뉴가 없습니다.</p>}
      <ConfirmDialog isOpen={deleteTarget != null} title="메뉴 삭제" message={`'${deleteTarget?.name}'을(를) 삭제하시겠습니까?\n기존 주문에는 영향이 없으며, 신규 주문에서만 제외됩니다.`} confirmText="삭제" confirmVariant="danger" onConfirm={handleDelete} onCancel={() => setDeleteTarget(null)} />
    </div>
  );
}
