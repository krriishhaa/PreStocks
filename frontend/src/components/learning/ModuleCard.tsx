import React from "react";
import { Button } from "@/components/common/Button";
import { cn } from "@/components/ui/utils";

interface ModuleCardProps {
  title: string;
  description: string;
  icon: string;
  totalLessons: number;
  completedLessons: number;
  onStart: () => void;
}

export function ModuleCard({
  title,
  description,
  icon,
  totalLessons,
  completedLessons,
  onStart,
}: ModuleCardProps) {
  const progress = totalLessons > 0 ? (completedLessons / totalLessons) * 100 : 0;
  const isComplete = completedLessons === totalLessons;

  return (
    <div className="flex flex-col justify-between h-[220px] p-5 rounded-[8px] border border-[#E5E7EB] bg-white shadow-[0px_1px_3px_rgba(0,0,0,0.1)] transition-all hover:shadow-[0px_4px_12px_rgba(0,0,0,0.1)]">
      <div>
        <div className="flex items-center gap-3 mb-3">
          <span className="text-[28px]">{icon}</span>
          <div>
            <h4 className="text-[16px] font-semibold text-[#1F2937]">{title}</h4>
            <span className="text-[11px] text-[#9CA3AF] bg-[#F1F5F9] px-1.5 py-0.5 rounded">
              {totalLessons} lessons
            </span>
          </div>
        </div>
        <p className="text-[12px] text-[#9CA3AF] leading-relaxed line-clamp-2">
          {description}
        </p>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-20 h-1.5 bg-[#F1F5F9] rounded-full overflow-hidden">
            <div
              className="h-full rounded-full bg-[#1E40AF] transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
          <span className="text-[11px] text-[#9CA3AF]">
            {completedLessons}/{totalLessons}
          </span>
        </div>
        {isComplete ? (
          <span className="text-[11px] font-semibold text-[#10B981]">✓ Complete</span>
        ) : (
          <Button variant="secondary" size="sm" onClick={onStart}>
            {completedLessons > 0 ? "Continue" : "Start"}
          </Button>
        )}
      </div>
    </div>
  );
}
