import React, { useState } from "react";
import { Button } from "@/components/common/Button";

const steps = [
  {
    title: "Welcome to PreStocks",
    description: "Learn investing, build portfolios, and predict markets with AI.",
  },
  {
    title: "What's your experience?",
    options: ["Beginner", "Intermediate", "Advanced"],
  },
  {
    title: "Risk Tolerance",
    options: ["Conservative", "Moderate", "Aggressive"],
  },
];

interface OnboardingFlowProps {
  onComplete: (data: { experience: string; riskTolerance: string }) => void;
}

export function OnboardingFlow({ onComplete }: OnboardingFlowProps) {
  const [step, setStep] = useState(0);
  const [experience, setExperience] = useState("");
  const [riskTolerance, setRiskTolerance] = useState("");

  const current = steps[step];

  const handleNext = () => {
    if (step === steps.length - 1) {
      onComplete({ experience, riskTolerance });
    } else {
      setStep((s) => s + 1);
    }
  };

  const canProceed =
    step === 0 || (step === 1 && experience) || (step === 2 && riskTolerance);

  return (
    <div className="max-w-md mx-auto text-center">
      <div className="flex gap-1 mb-8 justify-center">
        {steps.map((_, i) => (
          <div
            key={i}
            className={`h-1 w-8 rounded-full transition-colors ${
              i <= step ? "bg-[#1E40AF]" : "bg-[#E5E7EB]"
            }`}
          />
        ))}
      </div>

      <h2 className="text-[24px] font-semibold text-[#1F2937] mb-2">
        {current.title}
      </h2>

      {"description" in current && (
        <p className="text-[14px] text-[#9CA3AF] mb-8">{current.description}</p>
      )}

      {"options" in current && (
        <div className="flex flex-col gap-3 mb-8">
          {current.options!.map((opt) => {
            const selected =
              step === 1 ? experience === opt : riskTolerance === opt;
            return (
              <button
                key={opt}
                onClick={() =>
                  step === 1 ? setExperience(opt) : setRiskTolerance(opt)
                }
                className={`p-4 rounded-[8px] border text-[14px] font-medium transition-all ${
                  selected
                    ? "border-[#1E40AF] bg-[rgba(30,64,175,0.04)] text-[#1E40AF]"
                    : "border-[#E5E7EB] bg-white text-[#1F2937] hover:border-[#D1D5DB]"
                }`}
              >
                {opt}
              </button>
            );
          })}
        </div>
      )}

      <Button
        variant="primary"
        size="lg"
        className="w-full"
        onClick={handleNext}
        disabled={!canProceed}
      >
        {step === steps.length - 1 ? "Get Started" : "Continue"}
      </Button>
    </div>
  );
}
