import React from "react";
import { usePortfolio } from "@/hooks/usePortfolio";
import { Card, CardBody } from "@/components/common/Card";
import { formatCurrency, formatPercent } from "@/utils/formatting";
import { cn } from "@/components/ui/utils";

export function PortfolioSummary() {
  const { portfolio } = usePortfolio();
  const isPositive = portfolio.totalReturn >= 0;

  return (
    <Card>
      <CardBody>
        <div className="flex justify-between items-end">
          <div>
            <p className="text-[13px] font-medium text-[#9CA3AF] uppercase tracking-wide mb-1">
              Total Portfolio Value
            </p>
            <h2 className="text-[32px] font-bold text-[#1F2937] tracking-tight">
              {formatCurrency(portfolio.totalValue)}
            </h2>
            <span
              className={cn(
                "text-[15px] font-semibold",
                isPositive ? "text-[#10B981]" : "text-[#EF4444]"
              )}
            >
              {formatPercent(portfolio.totalReturnPercent)} all time
            </span>
          </div>
          <div className="grid grid-cols-2 gap-4 text-right">
            <div>
              <p className="text-[11px] text-[#9CA3AF] uppercase">Cash</p>
              <p className="text-[15px] font-semibold text-[#1F2937]">
                {formatCurrency(portfolio.cashBalance)}
              </p>
            </div>
            <div>
              <p className="text-[11px] text-[#9CA3AF] uppercase">Holdings</p>
              <p className="text-[15px] font-semibold text-[#1F2937]">
                {portfolio.holdings.length}
              </p>
            </div>
          </div>
        </div>
      </CardBody>
    </Card>
  );
}
