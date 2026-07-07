import React from "react";
import Link from "next/link";
import { useAppSelector } from "@/store/store";
import { cn } from "@/components/ui/utils";
import { formatCurrency, formatPercent } from "@/utils/formatting";
import { Skeleton } from "@/components/common/States";

export function Sidebar() {
  const portfolio = useAppSelector((state) => state.portfolio.data);
  const loading = useAppSelector((state) => state.portfolio.loading);
  const holdings = portfolio?.holdings ?? [];

  return (
    <aside className="w-80 bg-white border-l border-neutral-200 flex flex-col overflow-y-auto shrink-0 hidden lg:flex">
      <div className="py-5">
        <h4 className="text-xs uppercase text-neutral-400 tracking-wider px-5 pb-3 font-semibold">
          Your Holdings
        </h4>
        <div className="flex flex-col">
          {loading ? (
            <div className="px-5 space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex justify-between">
                  <Skeleton className="h-10 w-24" />
                  <Skeleton className="h-10 w-16" />
                </div>
              ))}
            </div>
          ) : holdings.length === 0 ? (
            <p className="text-neutral-400 text-xs px-5 py-8 text-center">
              No holdings yet. Start trading to build your portfolio.
            </p>
          ) : (
            holdings.map((holding) => (
              <Link key={holding.id} href={`/app/stock/${holding.symbol.toLowerCase()}`}>
                <div className="flex items-center justify-between px-5 py-3 cursor-pointer transition-all hover:bg-neutral-50 border-l-[3px] border-transparent hover:border-l-primary-800">
                  <div className="flex flex-col gap-0.5">
                    <span className="text-sm font-bold text-neutral-900">
                      {holding.symbol}
                    </span>
                    {holding.company_name && (
                      <span className="text-[11px] text-neutral-400 truncate max-w-[120px]">
                        {holding.company_name}
                      </span>
                    )}
                    <span className="text-[10px] bg-neutral-50 text-primary-800 px-1.5 py-px rounded font-medium inline-block w-fit">
                      {holding.shares} shares
                    </span>
                  </div>
                  <div className="flex flex-col items-end gap-0.5">
                    <span className="text-sm font-semibold text-neutral-900">
                      {formatCurrency(holding.market_value)}
                    </span>
                    <span
                      className={cn(
                        "text-[11px] font-semibold px-1.5 py-0.5 rounded min-w-[52px] text-center",
                        holding.unrealized_pnl_pct >= 0
                          ? "bg-success-500/10 text-success-500"
                          : "bg-alert-500/10 text-alert-500"
                      )}
                    >
                      {formatPercent(holding.unrealized_pnl_pct)}
                    </span>
                  </div>
                </div>
              </Link>
            ))
          )}
        </div>
      </div>
    </aside>
  );
}
