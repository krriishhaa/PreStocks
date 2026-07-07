import React from "react";
import { useAppSelector } from "@/store/store";
import { cn } from "@/components/ui/utils";
import { formatCurrency, formatPercent } from "@/utils/formatting";

export function Sidebar() {
  const holdings = useAppSelector((state) => state.portfolio.portfolio.holdings);

  return (
    <aside className="w-80 bg-white border-l border-[#E5E7EB] flex flex-col overflow-y-auto shrink-0">
      <div className="py-5">
        <h4 className="text-[13px] uppercase text-[#9CA3AF] tracking-wider px-5 pb-3 font-semibold">
          Your Holdings
        </h4>
        <div className="flex flex-col">
          {holdings.length === 0 ? (
            <p className="text-[#9CA3AF] text-[13px] px-5 py-8 text-center">
              No holdings yet. Start trading to build your portfolio.
            </p>
          ) : (
            holdings.map((holding) => {
              const isPositive = holding.dayChangePercent >= 0;
              return (
                <div
                  key={holding.symbol}
                  className="flex items-center justify-between px-5 py-3 cursor-pointer transition-all hover:bg-[#F8FAFC] border-l-[3px] border-transparent hover:border-l-[#1E40AF]"
                >
                  <div className="flex flex-col gap-0.5">
                    <span className="text-[14px] font-bold text-[#1F2937]">
                      {holding.symbol}
                    </span>
                    <span className="text-[11px] text-[#9CA3AF] truncate max-w-[120px]">
                      {holding.name}
                    </span>
                    <span className="text-[10px] bg-[#F8FAFC] text-[#1E40AF] px-1.5 py-px rounded font-medium inline-block w-fit">
                      {holding.shares} shares
                    </span>
                  </div>
                  <div className="flex flex-col items-end gap-0.5">
                    <span className="text-[14px] font-semibold text-[#1F2937]">
                      {formatCurrency(holding.currentPrice)}
                    </span>
                    <span
                      className={cn(
                        "text-[11px] font-semibold px-1.5 py-0.5 rounded min-w-[60px] text-center",
                        isPositive
                          ? "bg-[rgba(16,185,129,0.1)] text-[#10B981]"
                          : "bg-[rgba(239,68,68,0.1)] text-[#EF4444]"
                      )}
                    >
                      {formatPercent(holding.dayChangePercent)}
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </aside>
  );
}
