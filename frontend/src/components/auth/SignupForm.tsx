import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/common/Button";
import { ProgressBar } from "@/components/learning/ProgressBar";
import { useAuth } from "@/hooks/useAuth";

const step1Schema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Enter a valid email address"),
  password: z.string().min(8, "Password must be 8+ characters"),
  ageConfirm: z.literal(true, { errorMap: () => ({ message: "You must be 18+ to use PreStocks" }) }),
  termsAccept: z.literal(true, { errorMap: () => ({ message: "You must accept Terms & Privacy" }) }),
});
type Step1Data = z.infer<typeof step1Schema>;

const riskQuestions = [
  {
    question: "You invest $1,000. The next day, it drops to $800. What do you do?",
    options: [
      { label: "Sell immediately to stop losses", value: "a" },
      { label: "Hold and ignore it", value: "b" },
      { label: "Buy more at the lower price", value: "c" },
      { label: "It depends on why it dropped", value: "d" },
    ],
  },
  {
    question: "A stock you own doubles in 3 months. What's your move?",
    options: [
      { label: "Sell everything — lock in the gains", value: "a" },
      { label: "Sell half, keep half", value: "b" },
      { label: "Hold — it might keep going", value: "c" },
      { label: "Research whether the fundamentals justify the price", value: "d" },
    ],
  },
  {
    question: "How would you describe a P/E ratio?",
    options: [
      { label: "I don't know what that is", value: "a" },
      { label: "Something about price and earnings", value: "b" },
      { label: "Price divided by earnings per share — a valuation metric", value: "c" },
      { label: "One of many metrics I use alongside PEG, EV/EBITDA, etc.", value: "d" },
    ],
  },
  {
    question: "You hear a 'hot stock tip' from a friend. What do you do?",
    options: [
      { label: "Buy immediately before it goes up", value: "a" },
      { label: "Look at the chart to see if it's trending up", value: "b" },
      { label: "Research the company's financials first", value: "c" },
      { label: "Ignore it — tips are unreliable and possibly illegal", value: "d" },
    ],
  },
  {
    question: "What percentage of your savings would you invest in a single stock?",
    options: [
      { label: "50%+ if I believe in it", value: "a" },
      { label: "25-50%", value: "b" },
      { label: "5-10% max per position", value: "c" },
      { label: "Depends on my total portfolio size and diversification", value: "d" },
    ],
  },
];

const sectors = ["Technology", "Healthcare", "Energy", "Finance", "Consumer", "Real Estate", "Industrials", "Crypto"];
const goals = ["Retirement", "Wealth-building", "Side income", "Learning only", "Day trading"];

export function SignupForm() {
  const { signup, isLoading, error } = useAuth();
  const [step, setStep] = useState(1);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [selectedSectors, setSelectedSectors] = useState<string[]>([]);
  const [selectedGoals, setSelectedGoals] = useState<string[]>([]);

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
  } = useForm<Step1Data>({
    resolver: zodResolver(step1Schema),
    mode: "onChange",
  });

  const totalSteps = 3;
  const progress = (step / totalSteps) * 100;

  const handleStep1 = (data: Step1Data) => {
    setStep(2);
  };

  const handleRiskAnswer = (qIndex: number, value: string) => {
    setAnswers((prev) => ({ ...prev, [qIndex]: value }));
  };

  const allRiskAnswered = Object.keys(answers).length === riskQuestions.length;

  const handleStep2 = () => {
    setStep(3);
  };

  const handleStep3 = () => {
    signup("User", "user@example.com", "password123");
  };

  const toggleSector = (s: string) => {
    setSelectedSectors((prev) =>
      prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s]
    );
  };

  const toggleGoal = (g: string) => {
    setSelectedGoals((prev) =>
      prev.includes(g) ? prev.filter((x) => x !== g) : [...prev, g]
    );
  };

  return (
    <div className="flex flex-col gap-6">
      <ProgressBar value={progress} className="mb-2" />
      <p className="text-[12px] text-[#9CA3AF] text-center">
        Step {step} of {totalSteps}
      </p>

      {/* Step 1: Basic Info */}
      {step === 1 && (
        <form onSubmit={handleSubmit(handleStep1)} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-[13px] font-medium text-[#9CA3AF]">Full Name</label>
            <input
              {...register("name")}
              className="h-10 px-3 rounded-[6px] border border-[#E5E7EB] bg-white text-[14px] text-[#1F2937] placeholder:text-[#9CA3AF] focus:outline-none focus:border-[#1E40AF] focus:shadow-[0px_1px_2px_rgba(0,0,0,0.05)]"
              placeholder="Jane Doe"
            />
            {errors.name && <span className="text-[12px] text-[#EF4444]">{errors.name.message}</span>}
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-[13px] font-medium text-[#9CA3AF]">Email</label>
            <input
              type="email"
              {...register("email")}
              className="h-10 px-3 rounded-[6px] border border-[#E5E7EB] bg-white text-[14px] text-[#1F2937] placeholder:text-[#9CA3AF] focus:outline-none focus:border-[#1E40AF] focus:shadow-[0px_1px_2px_rgba(0,0,0,0.05)]"
              placeholder="you@example.com"
            />
            {errors.email && <span className="text-[12px] text-[#EF4444]">{errors.email.message}</span>}
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-[13px] font-medium text-[#9CA3AF]">Password</label>
            <input
              type="password"
              {...register("password")}
              className="h-10 px-3 rounded-[6px] border border-[#E5E7EB] bg-white text-[14px] text-[#1F2937] placeholder:text-[#9CA3AF] focus:outline-none focus:border-[#1E40AF] focus:shadow-[0px_1px_2px_rgba(0,0,0,0.05)]"
              placeholder="••••••••"
            />
            {errors.password && <span className="text-[12px] text-[#EF4444]">{errors.password.message}</span>}
          </div>

          <label className="flex items-start gap-2 cursor-pointer mt-2">
            <input type="checkbox" {...register("ageConfirm")} className="mt-0.5 w-4 h-4 rounded border-[#E5E7EB] accent-[#1E40AF]" />
            <span className="text-[13px] text-[#1F2937]">I confirm I am 18 years or older</span>
          </label>
          {errors.ageConfirm && <span className="text-[12px] text-[#EF4444]">{errors.ageConfirm.message}</span>}

          <label className="flex items-start gap-2 cursor-pointer">
            <input type="checkbox" {...register("termsAccept")} className="mt-0.5 w-4 h-4 rounded border-[#E5E7EB] accent-[#1E40AF]" />
            <span className="text-[13px] text-[#1F2937]">
              I agree to the <a href="#" className="text-[#1E40AF] underline">Terms of Service</a> and{" "}
              <a href="#" className="text-[#1E40AF] underline">Privacy Policy</a>
            </span>
          </label>
          {errors.termsAccept && <span className="text-[12px] text-[#EF4444]">{errors.termsAccept.message}</span>}

          <Button type="submit" variant="primary" size="lg" className="w-full mt-3" disabled={!isValid}>
            Next
          </Button>
        </form>
      )}

      {/* Step 2: Risk Assessment */}
      {step === 2 && (
        <div className="flex flex-col gap-6">
          <div className="text-center mb-2">
            <h3 className="text-[18px] font-semibold text-[#1F2937]">Risk Assessment</h3>
            <p className="text-[13px] text-[#9CA3AF]">
              This helps us match you to the right content. Not a test — no wrong answers.
            </p>
          </div>

          {riskQuestions.map((q, qi) => (
            <div key={qi} className="flex flex-col gap-2">
              <p className="text-[14px] font-medium text-[#1F2937]">
                {qi + 1}. {q.question}
              </p>
              <div className="flex flex-col gap-1.5">
                {q.options.map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => handleRiskAnswer(qi, opt.value)}
                    className={`p-3 rounded-[6px] border text-left text-[13px] transition-all ${
                      answers[qi] === opt.value
                        ? "border-[#1E40AF] bg-[rgba(30,64,175,0.04)] text-[#1E40AF] font-medium"
                        : "border-[#E5E7EB] text-[#1F2937] hover:border-[#D1D5DB]"
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>
          ))}

          <Button
            variant="primary"
            size="lg"
            className="w-full mt-2"
            disabled={!allRiskAnswered}
            onClick={handleStep2}
          >
            Next
          </Button>
        </div>
      )}

      {/* Step 3: Interests */}
      {step === 3 && (
        <div className="flex flex-col gap-6">
          <div className="text-center mb-2">
            <h3 className="text-[18px] font-semibold text-[#1F2937]">Your Interests</h3>
            <p className="text-[13px] text-[#9CA3AF]">
              Select sectors and goals so we can personalize your experience.
            </p>
          </div>

          <div>
            <p className="text-[13px] font-medium text-[#9CA3AF] mb-2">Sectors I'm interested in</p>
            <div className="flex flex-wrap gap-2">
              {sectors.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => toggleSector(s)}
                  className={`px-3 py-1.5 rounded-[6px] border text-[13px] transition-all ${
                    selectedSectors.includes(s)
                      ? "border-[#1E40AF] bg-[rgba(30,64,175,0.08)] text-[#1E40AF] font-medium"
                      : "border-[#E5E7EB] text-[#1F2937] hover:border-[#D1D5DB]"
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          <div>
            <p className="text-[13px] font-medium text-[#9CA3AF] mb-2">Investment goals</p>
            <div className="flex flex-wrap gap-2">
              {goals.map((g) => (
                <button
                  key={g}
                  type="button"
                  onClick={() => toggleGoal(g)}
                  className={`px-3 py-1.5 rounded-[6px] border text-[13px] transition-all ${
                    selectedGoals.includes(g)
                      ? "border-[#10B981] bg-[rgba(16,185,129,0.08)] text-[#10B981] font-medium"
                      : "border-[#E5E7EB] text-[#1F2937] hover:border-[#D1D5DB]"
                  }`}
                >
                  {g}
                </button>
              ))}
            </div>
          </div>

          {error && (
            <div className="p-3 rounded-[6px] bg-[rgba(239,68,68,0.1)] border border-[#EF4444]/30 text-[13px] text-[#EF4444]">
              {error}
            </div>
          )}

          <Button
            variant="primary"
            size="lg"
            className="w-full mt-2"
            loading={isLoading}
            onClick={handleStep3}
          >
            Create Account
          </Button>
        </div>
      )}
    </div>
  );
}
