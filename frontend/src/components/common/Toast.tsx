import React, { useState, useEffect, useCallback, createContext, useContext } from "react";
import { cn } from "@/components/ui/utils";

/**
 * Toast Notification System — per §6.8:
 * - Appears bottom-right
 * - Auto-dismisses after 4 seconds
 * - 300px width, 60px height
 * - Rounded 8px, padding 12px
 * - Icon + text
 */

type ToastType = "success" | "error" | "info";

interface Toast {
  id: string;
  type: ToastType;
  message: string;
}

interface ToastContextType {
  showToast: (type: ToastType, message: string) => void;
}

const ToastContext = createContext<ToastContextType>({ showToast: () => {} });

export function useToast() {
  return useContext(ToastContext);
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback((type: ToastType, message: string) => {
    const id = Math.random().toString(36).slice(2);
    setToasts((prev) => [...prev, { id, type, message }]);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div className="fixed bottom-6 right-6 z-[100] flex flex-col gap-2">
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} onDismiss={removeToast} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

function ToastItem({ toast, onDismiss }: { toast: Toast; onDismiss: (id: string) => void }) {
  useEffect(() => {
    const timer = setTimeout(() => onDismiss(toast.id), 4000);
    return () => clearTimeout(timer);
  }, [toast.id, onDismiss]);

  const styles: Record<ToastType, { bg: string; icon: string; iconColor: string }> = {
    success: { bg: "bg-[#DCFCE7]", icon: "✓", iconColor: "text-[#10B981]" },
    error: { bg: "bg-[#FEE2E2]", icon: "✕", iconColor: "text-[#EF4444]" },
    info: { bg: "bg-[#DBEAFE]", icon: "ℹ", iconColor: "text-[#1E40AF]" },
  };

  const style = styles[toast.type];

  return (
    <div className={cn(
      "w-[300px] h-[60px] rounded-[8px] p-3 flex items-center gap-3 shadow-lg animate-in slide-in-from-right-5 fade-in duration-200",
      style.bg
    )}>
      <span className={cn("text-[18px] font-bold", style.iconColor)}>{style.icon}</span>
      <p className="text-[13px] font-medium text-[#1F2937] flex-1 leading-tight">{toast.message}</p>
      <button onClick={() => onDismiss(toast.id)} className="text-[#9CA3AF] hover:text-[#1F2937] text-[14px]">×</button>
    </div>
  );
}
