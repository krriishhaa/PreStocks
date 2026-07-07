import React from "react";
import type { CompositeRiskScore } from "@/types/flags";
import { cn } from "@/components/ui/utils";

interface RiskCompositeScoreProps {
  score: CompositeRiskScore;
}

const severityColor = {
  low: "#10B981",
  medium: "#F59E0B",
  high: "#EF4444",
  critical: "#EF4444",
};

export function RiskCompositeScore({ score }: RiskCompositeScoreProps) {
  const color = severityColor[score.severity];

  return (
    <div className="p-6 rounded-[8px] border border-[#E5E7EB] bg-white shadow-[0px_1px_3px_rgba(0,0,0,0.1)]">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-[18px] font-semibold text-[#1F2937]">
          Risk Score — {score.symbol}
        </h3>
        <div
          className="flex items-center justify-center w-14 h-14 rounded-full border-[3px]"
          style={{ borderColor: color }}
        >
          <span className="text-[18px] font-bold" style={{ color }}>
            {score.overallScore}
          </span>
        </div>
      </div>

      <div className="flex flex-col gap-3">
        {score.factors.map((factor) => (
          <div key={factor.category}>
            <div className="flex justify-between text-[12px] mb-1">
              <span className="text-[#9CA3AF] font-medium">{factor.category}</span>
              <span className="text-[#1F2937] font-semibold">{factor.score}</span>
            </div>
            <div className="h-1.5 bg-[#F1F5F9] rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${factor.score}%`,
                  backgroundColor: factor.score > 60 ? "#EF4444" : factor.score > 30 ? "#F59E0B" : "#10B981",
                }}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-[#E5E7EB]">
        <span className="text-[12px] text-[#9CA3AF]">
          {score.flags.length} active flag{score.flags.length !== 1 ? "s" : ""}
        </span>
      </div>
    </div>
  );
}
