import { useToastStore } from '../stores/toastStore';

const typeStyles = {
  success: 'bg-green-500',
  error: 'bg-red-500',
  warning: 'bg-yellow-500',
  info: 'bg-blue-500',
};

const typeIcons = {
  success: '✓',
  error: '✕',
  warning: '⚠',
  info: 'ℹ',
};

export default function Toast() {
  const { messages, removeToast } = useToastStore();

  if (messages.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`${typeStyles[msg.type]} flex min-w-[280px] items-center gap-2 rounded-lg px-4 py-3 text-white shadow-lg animate-in slide-in-from-right`}
        >
          <span className="text-lg">{typeIcons[msg.type]}</span>
          <span className="flex-1 text-sm">{msg.message}</span>
          <button onClick={() => removeToast(msg.id)} className="ml-2 opacity-70 hover:opacity-100" aria-label="닫기">
            ✕
          </button>
        </div>
      ))}
    </div>
  );
}
