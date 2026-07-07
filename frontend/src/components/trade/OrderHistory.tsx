import React from "react";
import { useAppSelector } from "@/store/store";
import { formatCurrency, formatDateTime } from "@/utils/formatting";
import { cn } from "@/components/ui/utils";

export function OrderHistory() {
  const trades = useAppSelector((state) => state.portfolio.trades);

  if (trades.length === 0) {
    return (
      <div className="text-center py-8 text-sm text-neutral-400">
        No trades yet. Place your first order to get started.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2">
      {trades.slice(0, 20).map((t) => (
        <div
          key={t.id}
          className="flex items-center justify-between p-3 rounded-md border border-neutral-200 bg-neutral-50"
        >
          <div className="flex flex-col gap-0.5">
            <div className="flex items-center gap-2">
              <span
                className={cn(
                  "text-[10px] font-bold uppercase px-1.5 py-0.5 rounded",
                  t.side === "buy" ? "bg-success-500/10 text-success-500" : "bg-alert-500/10 text-alert-500"
                )}
              >
                {t.side}
              </span>
              <span className="text-sm font-semibold text-neutral-900">{t.symbol}</span>
            </div>
            <span className="text-[11px] text-neutral-400">
              {t.shares} shares @ {formatCurrency(t.price)}
            </span>
          </div>
          <div className="flex flex-col items-end gap-0.5">
            <span className="text-sm font-semibold text-neutral-900">
              {formatCurrency(t.total_amount)}
            </span>
            <span className="text-[10px] text-neutral-400">
              {formatDateTime(t.executed_at)}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
