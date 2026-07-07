import React from "react";
import { cn } from "@/components/ui/utils";
import { formatCurrency, formatPercent } from "@/utils/formatting";
import type { Holding } from "@/types/portfolio";

interface HoldingRowProps {
  holding: Holding;
  onClick?: (symbol: string) => void;
}

export function HoldingRow({ holding, onClick }: HoldingRowProps) {
  const isPositive = holding.unrealized_pnl_pct >= 0;

  return (
    <div
      onClick={() => onClick?.(holding.symbol)}
      className="flex items-center justify-between py-3 px-4 cursor-pointer transition-all hover:bg-neutral-50 rounded-md group"
    >
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-full bg-neutral-100 flex items-center justify-center text-xs font-bold text-primary-800">
          {holding.symbol.slice(0, 2)}
        </div>
        <div>
          <p className="text-sm font-semibold text-neutral-900">{holding.symbol}</p>
          <p className="text-[11px] text-neutral-400">
            {holding.shares} shares @ {formatCurrency(holding.avg_buy_price)}
          </p>
        </div>
      </div>

      <div className="text-right">
        <p className="text-sm font-semibold text-neutral-900">
          {formatCurrency(holding.market_value)}
        </p>
        <p className={cn("text-xs font-medium", isPositive ? "text-success-500" : "text-alert-500")}>
          {formatPercent(holding.unrealized_pnl_pct)}
        </p>
      </div>
    </div>
  );
}
