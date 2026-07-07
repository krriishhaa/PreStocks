import React from "react";
import { useAppSelector } from "@/store/store";
import { formatCurrency, formatDateTime } from "@/utils/formatting";
import { cn } from "@/components/ui/utils";

export function OrderHistory() {
  const transactions = useAppSelector(
    (state) => state.portfolio.portfolio.transactions
  );

  if (transactions.length === 0) {
    return (
      <div className="text-center py-8 text-[13px] text-[#9CA3AF]">
        No trades yet. Place your first order to get started.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2">
      {transactions.slice(0, 20).map((tx) => (
        <div
          key={tx.id}
          className="flex items-center justify-between p-3 rounded-[6px] border border-[#E5E7EB] bg-[#F8FAFC]"
        >
          <div className="flex flex-col gap-0.5">
            <div className="flex items-center gap-2">
              <span
                className={cn(
                  "text-[10px] font-bold uppercase px-1.5 py-0.5 rounded",
                  tx.action === "buy"
                    ? "bg-[rgba(16,185,129,0.1)] text-[#10B981]"
                    : "bg-[rgba(239,68,68,0.1)] text-[#EF4444]"
                )}
              >
                {tx.action}
              </span>
              <span className="text-[13px] font-semibold text-[#1F2937]">
                {tx.symbol}
              </span>
            </div>
            <span className="text-[11px] text-[#9CA3AF]">
              {tx.shares} shares @ {formatCurrency(tx.price)}
            </span>
          </div>
          <div className="flex flex-col items-end gap-0.5">
            <span className="text-[13px] font-semibold text-[#1F2937]">
              {formatCurrency(tx.total)}
            </span>
            <span className="text-[10px] text-[#9CA3AF]">
              {formatDateTime(tx.timestamp)}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
