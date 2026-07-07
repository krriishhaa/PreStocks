import React from "react";
import type { RiskFlag } from "@/types/flags";
import { cn } from "@/components/ui/utils";

interface FlagExplanationProps {
  flag: RiskFlag;
}

export function FlagExplanation({ flag }: FlagExplanationProps) {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-3">
        <span className="text-[14px] font-bold text-[#1F2937]">{flag.symbol}</span>
        <span className="text-[12px] text-[#9CA3AF]">{flag.type}</span>
      </div>

      <h3 className="text-[18px] font-semibold text-[#1F2937]">{flag.title}</h3>

      <div className="p-4 rounded-[8px] bg-[#F8FAFC] border border-[#E5E7EB]">
        <p className="text-[14px] text-[#1F2937] leading-relaxed">
          {flag.explanation}
        </p>
      </div>

      <div className="flex items-center gap-4 text-[12px] text-[#9CA3AF]">
        <span>Score: <strong className="text-[#1F2937]">{flag.score}/100</strong></span>
        <span>Triggered: {new Date(flag.triggeredAt).toLocaleDateString()}</span>
        {flag.resolved && (
          <span className="text-[#10B981] font-medium">✓ Resolved</span>
        )}
      </div>
    </div>
  );
}
