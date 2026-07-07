import React, { useState } from "react";
import { Button } from "@/components/common/Button";
import { ProgressBar } from "./ProgressBar";

interface Slide {
  title: string;
  content: string;
  bullets?: string[];
}

interface ModuleViewerProps {
  moduleTitle: string;
  slides: Slide[];
  onComplete: () => void;
  onClose: () => void;
}

export function ModuleViewer({
  moduleTitle,
  slides,
  onComplete,
  onClose,
}: ModuleViewerProps) {
  const [current, setCurrent] = useState(0);
  const slide = slides[current];
  const isLast = current === slides.length - 1;

  const handleNext = () => {
    if (isLast) {
      onComplete();
    } else {
      setCurrent((c) => c + 1);
    }
  };

  return (
    <div className="rounded-[8px] border border-[#E5E7EB] border-l-4 border-l-[#1E40AF] bg-white shadow-[0px_1px_3px_rgba(0,0,0,0.1)] p-6">
      <div className="flex items-center justify-between border-b border-[#E5E7EB] pb-4 mb-5">
        <div className="flex items-center gap-3">
          <span className="text-[10px] font-bold uppercase bg-[rgba(30,64,175,0.08)] text-[#1E40AF] px-2 py-1 rounded">
            {moduleTitle}
          </span>
          <h3 className="text-[20px] font-semibold text-[#1F2937]">{slide.title}</h3>
        </div>
        <button
          onClick={onClose}
          className="text-[12px] text-[#9CA3AF] hover:text-[#1F2937] transition-colors px-2 py-1"
        >
          Close
        </button>
      </div>

      <div className="text-[11px] text-[#9CA3AF] mb-3">
        Slide {current + 1} of {slides.length}
      </div>

      <ProgressBar value={((current + 1) / slides.length) * 100} className="mb-5" />

      <div className="min-h-[200px]">
        <p className="text-[15px] leading-relaxed text-[#1F2937]">{slide.content}</p>
        {slide.bullets && (
          <ul className="mt-4 flex flex-col gap-2 ml-5 list-disc text-[14px] text-[#9CA3AF]">
            {slide.bullets.map((b, i) => (
              <li key={i}>{b}</li>
            ))}
          </ul>
        )}
      </div>

      <div className="flex justify-end gap-3 border-t border-[#E5E7EB] pt-4 mt-6">
        {current > 0 && (
          <Button variant="secondary" onClick={() => setCurrent((c) => c - 1)}>
            Previous
          </Button>
        )}
        <Button variant="primary" onClick={handleNext}>
          {isLast ? "Complete Module" : "Next"}
        </Button>
      </div>
    </div>
  );
}
