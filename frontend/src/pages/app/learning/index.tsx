import React, { useState } from "react";
import Head from "next/head";
import Link from "next/link";
import { Navbar } from "@/components/common/Navbar";
import { Card, CardBody } from "@/components/common/Card";
import { cn } from "@/components/ui/utils";

type Tier = "beginner" | "intermediate" | "advanced";
type ModuleStatus = "completed" | "in_progress" | "available" | "locked";

interface LearningModule {
  id: string;
  title: string;
  description: string;
  duration: string;
  tier: Tier;
  progress: number;
  status: ModuleStatus;
}

const modules: LearningModule[] = [
  // Beginner
  { id: "stocks-101", title: "Stocks 101", description: "What is a stock, why do prices move", duration: "8 min", tier: "beginner", progress: 100, status: "completed" },
  { id: "pe-ratios", title: "Understanding P/E Ratios", description: "Valuation basics", duration: "6 min", tier: "beginner", progress: 50, status: "in_progress" },
  { id: "risk-reward", title: "Risk vs. Reward", description: "How to think about risk", duration: "7 min", tier: "beginner", progress: 0, status: "available" },
  { id: "financial-statements", title: "Reading Financial Statements", description: "Balance sheet, income statement basics", duration: "10 min", tier: "beginner", progress: 0, status: "available" },
  { id: "diversification", title: "Diversification", description: "Why and how to diversify", duration: "6 min", tier: "beginner", progress: 0, status: "available" },
  // Intermediate
  { id: "technical-analysis", title: "Technical Analysis Intro", description: "Charts, trends, and indicators", duration: "12 min", tier: "intermediate", progress: 0, status: "locked" },
  { id: "earnings-volatility", title: "Earnings & Volatility", description: "What happens around earnings reports", duration: "9 min", tier: "intermediate", progress: 0, status: "locked" },
  { id: "insider-signals", title: "Insider Trading Signals", description: "Reading insider buy/sell data", duration: "8 min", tier: "intermediate", progress: 0, status: "locked" },
  { id: "sector-rotation", title: "Sector Rotation", description: "How money flows between sectors", duration: "10 min", tier: "intermediate", progress: 0, status: "locked" },
  { id: "options-explained", title: "Options Explained", description: "Theory only; basics of options", duration: "11 min", tier: "intermediate", progress: 0, status: "locked" },
  // Advanced
  { id: "options-deep-dive", title: "Options Trading Deep Dive", description: "Strategies, Greeks, and execution", duration: "15 min", tier: "advanced", progress: 0, status: "locked" },
  { id: "short-selling", title: "Short Selling & Shorting", description: "How to profit from declining stocks", duration: "12 min", tier: "advanced", progress: 0, status: "locked" },
  { id: "leverage-margin", title: "Leverage & Margin", description: "Theory + simulation", duration: "14 min", tier: "advanced", progress: 0, status: "locked" },
];

const tierLabels: Record<Tier, string> = { beginner: "Beginner", intermediate: "Intermediate", advanced: "Advanced" };
const tierColors: Record<Tier, string> = { beginner: "#10B981", intermediate: "#F59E0B", advanced: "#EF4444" };

export default function LearningPage() {
  const [selectedTier, setSelectedTier] = useState<Tier | "all">("all");

  const userTier: Tier = "beginner";
  const completedCount = modules.filter((m) => m.status === "completed").length;
  const totalBeginner = modules.filter((m) => m.tier === "beginner").length;
  const overallProgress = Math.round((completedCount / totalBeginner) * 100);
  const userLevel = completedCount + 1;

  const filtered = selectedTier === "all" ? modules : modules.filter((m) => m.tier === selectedTier);

  const grouped: Record<Tier, LearningModule[]> = {
    beginner: filtered.filter((m) => m.tier === "beginner"),
    intermediate: filtered.filter((m) => m.tier === "intermediate"),
    advanced: filtered.filter((m) => m.tier === "advanced"),
  };

  return (
    <>
      <Head>
        <title>Learning Hub - PreStocks</title>
      </Head>
      <div className="flex h-screen flex-col">
        <Navbar />
        <main className="flex-1 overflow-y-auto bg-[#F8FAFC] p-6">
          <div className="max-w-6xl mx-auto flex flex-col gap-6">
            {/* Header */}
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-3">
                  <h1 className="text-[24px] font-bold text-[#1F2937]">Learning Hub</h1>
                  <span className="text-[12px] font-bold text-white px-2.5 py-1 rounded-[6px]"
                    style={{ backgroundColor: tierColors[userTier] }}>
                    {tierLabels[userTier]}
                  </span>
                </div>
                <p className="text-[14px] text-[#9CA3AF] mt-1">
                  You are: {tierLabels[userTier]} | Level {userLevel} of 5
                </p>
              </div>
              <div className="flex gap-1 bg-[#F1F5F9] rounded-[6px] p-1">
                {(["all", "beginner", "intermediate", "advanced"] as const).map((t) => (
                  <button key={t} onClick={() => setSelectedTier(t)}
                    className={cn("px-3 py-1.5 rounded-[4px] text-[12px] font-medium transition-all capitalize",
                      selectedTier === t ? "bg-white text-[#1F2937] shadow-sm" : "text-[#9CA3AF]"
                    )}>
                    {t === "all" ? "All" : tierLabels[t]}
                  </button>
                ))}
              </div>
            </div>

            {/* Progress Bar */}
            <Card>
              <CardBody>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-[13px] font-medium text-[#1F2937]">
                    {completedCount}/{totalBeginner} Beginner modules completed
                  </p>
                  <span className="text-[13px] font-semibold text-[#1E40AF]">{overallProgress}%</span>
                </div>
                <div className="h-3 bg-[#E5E7EB] rounded-full overflow-hidden">
                  <div className="h-full bg-[#1E40AF] rounded-full transition-all duration-500" style={{ width: `${overallProgress}%` }} />
                </div>
                <p className="text-[11px] text-[#9CA3AF] mt-2">
                  Complete all Beginner modules to unlock Intermediate tier
                </p>
              </CardBody>
            </Card>

            {/* Module Groups */}
            {(["beginner", "intermediate", "advanced"] as Tier[]).map((tier) => {
              const tierModules = grouped[tier];
              if (tierModules.length === 0) return null;
              return (
                <div key={tier}>
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: tierColors[tier] }} />
                    <h2 className="text-[16px] font-semibold text-[#1F2937]">{tierLabels[tier]}</h2>
                    <span className="text-[12px] text-[#9CA3AF]">
                      {tier === "beginner" ? "Unlocked" :
                       tier === "intermediate" ? "Unlock after Beginner" :
                       "Unlock after Intermediate"}
                    </span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {tierModules.map((m) => (
                      <ModuleCard key={m.id} module={m} />
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </main>
      </div>
    </>
  );
}

function ModuleCard({ module }: { module: LearningModule }) {
  const isLocked = module.status === "locked";
  const isCompleted = module.status === "completed";
  const isInProgress = module.status === "in_progress";
  const color = tierColors[module.tier];

  return (
    <Card className={cn("relative overflow-hidden transition-all", isLocked && "opacity-60")}>
      {isLocked && (
        <div className="absolute inset-0 bg-[rgba(31,41,55,0.04)] z-10 flex items-center justify-center">
          <div className="w-10 h-10 rounded-full bg-[rgba(31,41,55,0.8)] flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
        </div>
      )}
      <CardBody>
        <div className="flex items-center gap-2 mb-2">
          <div className="w-8 h-8 rounded-[6px] flex items-center justify-center" style={{ backgroundColor: `${color}15` }}>
            {isCompleted ? (
              <svg className="w-4 h-4" style={{ color }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <svg className="w-4 h-4" style={{ color }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            )}
          </div>
          <span className="text-[11px] font-medium text-[#9CA3AF]">{module.duration}</span>
        </div>
        <h4 className="text-[14px] font-semibold text-[#1F2937] mb-1">{module.title}</h4>
        <p className="text-[12px] text-[#9CA3AF] mb-3">{module.description}</p>

        {/* Progress */}
        {(isCompleted || isInProgress) && (
          <div className="mb-3">
            <div className="h-1.5 bg-[#E5E7EB] rounded-full overflow-hidden">
              <div className="h-full rounded-full transition-all" style={{ width: `${module.progress}%`, backgroundColor: color }} />
            </div>
            <p className="text-[10px] text-[#9CA3AF] mt-1">{module.progress}% complete</p>
          </div>
        )}

        {/* CTA */}
        {isLocked ? (
          <p className="text-[11px] text-[#9CA3AF] font-medium">
            🔒 Unlock at {module.tier === "intermediate" ? "Intermediate" : "Advanced"} tier
          </p>
        ) : (
          <Link href={`/app/learning/${module.id}`}>
            <span className={cn(
              "inline-block px-3 py-1.5 rounded-[6px] text-[12px] font-semibold cursor-pointer transition-all",
              isCompleted ? "bg-[rgba(16,185,129,0.1)] text-[#10B981]" :
              isInProgress ? "bg-[rgba(30,64,175,0.08)] text-[#1E40AF]" :
              "bg-[#1E40AF] text-white hover:bg-[#1E3A8A]"
            )}>
              {isCompleted ? "✓ Completed" : isInProgress ? "Resume" : "Start"}
            </span>
          </Link>
        )}
      </CardBody>
    </Card>
  );
}
