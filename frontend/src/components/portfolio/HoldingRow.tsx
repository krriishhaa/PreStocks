import React from "react";
import { cn } from "@/components/ui/utils";
import { formatCurrency, formatPercent } from "@/utils/formatting";
import type { Holding } from "@/types/portfolio";

interface HoldingRowProps {
  holding: Holding;
  onClick?: (symbol: string) => void;
}

export function HoldingRow({ holding, onClick }: HoldingRowProps) {
  const isPositive = holding.totalReturnPercent >= 0;

  return (
    <div
      onClick={() => onClick?.(holding.symbol)}
      className="flex items-center justify-between py-3 px-4 cursor-pointer transition-all hover:bg-[#F8FAFC] rounded-[6px] group"
    >
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-full bg-[#F1F5F9] flex items-center justify-center text-[12px] font-bold text-[#1E40AF]">
          {holding.symbol.slice(0, 2)}
        </div>
        <div>
          <p className="text-[14px] font-semibold text-[#1F2937]">{holding.symbol}</p>
          <p className="text-[11px] text-[#9CA3AF]">
            {holding.shares} shares @ {formatCurrency(holding.avgCost)}
          </p>
        </div>
      </div>

      <div className="text-right">
        <p className="text-[14px] font-semibold text-[#1F2937]">
          {formatCurrency(holding.totalValue)}
        </p>
        <p
          className={cn(
            "text-[12px] font-medium",
            isPositive ? "text-[#10B981]" : "text-[#EF4444]"
          )}
        >
          {formatPercent(holding.totalReturnPercent)}
        </p>
      </div>
    </div>
  );
}
