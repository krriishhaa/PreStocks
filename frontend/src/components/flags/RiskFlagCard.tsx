import React from "react";
import { cn } from "@/components/ui/utils";
import type { RiskFlag } from "@/types/flags";
import { RISK_LEVELS } from "@/config/constants";

interface RiskFlagCardProps {
  flag: RiskFlag;
  onClick?: (flag: RiskFlag) => void;
}

const severityStyles = {
  low: "border-l-[#10B981] bg-[rgba(16,185,129,0.04)]",
  medium: "border-l-[#F59E0B] bg-[rgba(245,158,11,0.04)]",
  high: "border-l-[#EF4444] bg-[rgba(239,68,68,0.04)]",
  critical: "border-l-[#EF4444] bg-[rgba(239,68,68,0.08)]",
};

const severityBadge = {
  low: "bg-[rgba(16,185,129,0.1)] text-[#10B981]",
  medium: "bg-[rgba(245,158,11,0.1)] text-[#F59E0B]",
  high: "bg-[rgba(239,68,68,0.1)] text-[#EF4444]",
  critical: "bg-[#EF4444] text-white",
};

export function RiskFlagCard({ flag, onClick }: RiskFlagCardProps) {
  return (
    <div
      onClick={() => onClick?.(flag)}
      className={cn(
        "p-4 rounded-[8px] border border-[#E5E7EB] border-l-[3px] cursor-pointer transition-all hover:shadow-[0px_4px_12px_rgba(0,0,0,0.1)]",
        severityStyles[flag.severity]
      )}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-[14px] font-bold text-[#1F2937]">{flag.symbol}</span>
          <span
            className={cn(
              "text-[11px] font-semibold px-2 py-0.5 rounded-[6px]",
              severityBadge[flag.severity]
            )}
          >
            {flag.severity.toUpperCase()}
          </span>
        </div>
        <span className="text-[11px] text-[#9CA3AF]">{flag.type}</span>
      </div>
      <h4 className="text-[14px] font-semibold text-[#1F2937] mb-1">{flag.title}</h4>
      <p className="text-[12px] text-[#9CA3AF] line-clamp-2">{flag.description}</p>
    </div>
  );
}
