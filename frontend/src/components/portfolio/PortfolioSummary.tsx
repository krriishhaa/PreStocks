import React from "react";
import { usePortfolio } from "@/hooks/usePortfolio";
import { Card, CardBody } from "@/components/common/Card";
import { Skeleton } from "@/components/common/States";
import { formatCurrency, formatPercent } from "@/utils/formatting";
import { cn } from "@/components/ui/utils";

export function PortfolioSummary() {
  const { portfolio, loading } = usePortfolio();

  if (loading || !portfolio) {
    return (
      <Card>
        <CardBody>
          <Skeleton className="h-8 w-40 mb-2" />
          <Skeleton className="h-5 w-24" />
        </CardBody>
      </Card>
    );
  }

  const pnl = portfolio.total_value - portfolio.initial_capital;
  const pnlPct = portfolio.initial_capital ? (pnl / portfolio.initial_capital) * 100 : 0;
  const isPositive = pnl >= 0;

  return (
    <Card>
      <CardBody>
        <div className="flex justify-between items-end">
          <div>
            <p className="text-xs font-medium text-neutral-400 uppercase tracking-wide mb-1">
              Total Portfolio Value
            </p>
            <h2 className="text-3xl font-bold text-neutral-900 tracking-tight">
              {formatCurrency(portfolio.total_value)}
            </h2>
            <span className={cn("text-sm font-semibold", isPositive ? "text-success-500" : "text-alert-500")}>
              {formatPercent(pnlPct)} all time
            </span>
          </div>
          <div className="grid grid-cols-2 gap-4 text-right">
            <div>
              <p className="text-[11px] text-neutral-400 uppercase">Cash</p>
              <p className="text-sm font-semibold text-neutral-900">
                {formatCurrency(portfolio.cash)}
              </p>
            </div>
            <div>
              <p className="text-[11px] text-neutral-400 uppercase">Holdings</p>
              <p className="text-sm font-semibold text-neutral-900">
                {portfolio.positions}
              </p>
            </div>
          </div>
        </div>
      </CardBody>
    </Card>
  );
}
