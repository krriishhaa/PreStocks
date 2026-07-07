import React, { useState } from "react";
import Head from "next/head";
import { useRouter } from "next/router";
import Link from "next/link";
import { Navbar } from "@/components/common/Navbar";
import { Card, CardBody } from "@/components/common/Card";
import { Button } from "@/components/common/Button";
import { cn } from "@/components/ui/utils";

interface QuizQuestion {
  id: number;
  question: string;
  options: string[];
  correctIndex: number;
}

interface ScenarioChoice {
  label: string;
  outcome: string;
  isOptimal: boolean;
}

const moduleData: Record<string, {
  title: string;
  duration: string;
  tier: string;
  takeaways: string[];
  quiz: QuizQuestion[];
  scenario?: { prompt: string; choices: ScenarioChoice[] };
  nextModuleId?: string;
}> = {
  "stocks-101": {
    title: "Stocks 101",
    duration: "8 min",
    tier: "Beginner",
    takeaways: [
      "A stock represents partial ownership in a company",
      "Stock prices are driven by supply and demand",
      "Markets reflect expectations about future earnings",
      "Diversification reduces risk from any single stock",
    ],
    quiz: [
      { id: 1, question: "What does owning a stock represent?", options: ["A loan to the company", "Partial ownership of the company", "A fixed-income bond", "A futures contract"], correctIndex: 1 },
      { id: 2, question: "What primarily drives stock prices?", options: ["Government policy", "Company logo design", "Supply and demand", "Time of day"], correctIndex: 2 },
      { id: 3, question: "Why do investors diversify?", options: ["To increase fees", "To reduce risk from any single stock", "To make accounting harder", "It's required by law"], correctIndex: 1 },
    ],
    scenario: {
      prompt: "You have $1,000 to invest. Company ABC just announced record earnings. Its stock rose 15% today. What do you do?",
      choices: [
        { label: "Buy as much as possible immediately", outcome: "The stock had already priced in the earnings. It dropped 5% the next day. You lost $50.", isOptimal: false },
        { label: "Buy a smaller position and set a stop-loss", outcome: "Smart approach. The stock dipped 3% then recovered. Your stop-loss wasn't hit and you're up 2% a week later.", isOptimal: true },
        { label: "Wait for a pullback before buying", outcome: "The stock pulled back 8% over the week. You bought lower and saved $80 vs. buying immediately.", isOptimal: true },
        { label: "Skip it — too risky after a big move", outcome: "You avoided a volatile trade. Sometimes the best trade is no trade. You preserved capital.", isOptimal: false },
      ],
    },
    nextModuleId: "pe-ratios",
  },
  "pe-ratios": {
    title: "Understanding P/E Ratios",
    duration: "6 min",
    tier: "Beginner",
    takeaways: [
      "P/E ratio = Price per share ÷ Earnings per share",
      "A high P/E may signal growth expectations or overvaluation",
      "Compare P/E within the same industry for meaningful insights",
      "Negative P/E means the company is not profitable",
    ],
    quiz: [
      { id: 1, question: "What does P/E ratio stand for?", options: ["Price to Equity", "Price to Earnings", "Profit to Expense", "Portfolio to Equity"], correctIndex: 1 },
      { id: 2, question: "A stock with P/E of 50 vs. industry average of 20 suggests:", options: ["It's definitely overvalued", "Market expects higher growth", "The company is unprofitable", "Nothing meaningful"], correctIndex: 1 },
      { id: 3, question: "When is P/E most useful?", options: ["Comparing across all industries", "Comparing within the same industry", "For crypto assets", "For real estate"], correctIndex: 1 },
    ],
    nextModuleId: "risk-reward",
  },
};

export default function ModuleViewerPage() {
  const router = useRouter();
  const { moduleId } = router.query;
  const id = typeof moduleId === "string" ? moduleId : "";
  const mod = moduleData[id];

  const [currentSection, setCurrentSection] = useState<"content" | "quiz" | "scenario">("content");
  const [quizAnswers, setQuizAnswers] = useState<Record<number, number>>({});
  const [quizSubmitted, setQuizSubmitted] = useState(false);
  const [scenarioChoice, setScenarioChoice] = useState<number | null>(null);
  const [completed, setCompleted] = useState(false);

  if (!mod) {
    return (
      <>
        <Head><title>Module Not Found - PreStocks</title></Head>
        <div className="flex h-screen flex-col">
          <Navbar />
          <main className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <p className="text-[16px] text-[#9CA3AF]">Module not found</p>
              <Link href="/app/learning">
                <span className="text-[14px] text-[#1E40AF] hover:underline mt-2 inline-block cursor-pointer">← Back to Learning Hub</span>
              </Link>
            </div>
          </main>
        </div>
      </>
    );
  }

  const quizScore = mod.quiz.reduce((s, q) => s + (quizAnswers[q.id] === q.correctIndex ? 1 : 0), 0);
  const quizPassed = quizScore >= Math.ceil(mod.quiz.length * 0.8);

  return (
    <>
      <Head>
        <title>{mod.title} - Learning - PreStocks</title>
      </Head>
      <div className="flex h-screen flex-col">
        <Navbar />
        <main className="flex-1 overflow-y-auto bg-[#F8FAFC] p-6">
          <div className="max-w-3xl mx-auto flex flex-col gap-6">
            {/* Breadcrumb */}
            <div className="flex items-center gap-2 text-[12px]">
              <Link href="/app/learning">
                <span className="text-[#1E40AF] hover:underline cursor-pointer">Learning Hub</span>
              </Link>
              <span className="text-[#9CA3AF]">/</span>
              <span className="text-[#1F2937] font-medium">{mod.title}</span>
            </div>

            {/* Module Header */}
            <Card>
              <CardBody>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h1 className="text-[22px] font-bold text-[#1F2937]">{mod.title}</h1>
                      <span className="text-[11px] font-bold text-[#10B981] bg-[rgba(16,185,129,0.1)] px-2 py-0.5 rounded-[4px]">{mod.tier}</span>
                    </div>
                    <p className="text-[13px] text-[#9CA3AF]">{mod.duration} • Score 80%+ on quiz to complete</p>
                  </div>
                  {completed && (
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-[6px] bg-[rgba(16,185,129,0.1)]">
                      <svg className="w-4 h-4 text-[#10B981]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-[13px] font-semibold text-[#10B981]">Completed</span>
                    </div>
                  )}
                </div>
              </CardBody>
            </Card>

            {/* Section Tabs */}
            <div className="flex gap-1 bg-[#F1F5F9] rounded-[8px] p-1">
              {(["content", "quiz", ...(mod.scenario ? ["scenario"] : [])] as const).map((s) => (
                <button key={s} onClick={() => setCurrentSection(s as any)}
                  className={cn("flex-1 px-4 py-2 rounded-[6px] text-[13px] font-medium capitalize transition-all",
                    currentSection === s ? "bg-white text-[#1F2937] shadow-sm" : "text-[#9CA3AF]"
                  )}>
                  {s === "content" ? "📖 Content" : s === "quiz" ? "📝 Quiz" : "🎯 Scenario"}
                </button>
              ))}
            </div>

            {/* Content Section */}
            {currentSection === "content" && (
              <div className="flex flex-col gap-4">
                {/* Video placeholder */}
                <Card>
                  <CardBody>
                    <div className="w-full aspect-video bg-[#1F2937] rounded-[8px] flex items-center justify-center">
                      <div className="text-center">
                        <div className="w-16 h-16 rounded-full bg-white/10 flex items-center justify-center mx-auto mb-3">
                          <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M8 5v14l11-7z" />
                          </svg>
                        </div>
                        <p className="text-[14px] text-white/80 font-medium">{mod.title}</p>
                        <p className="text-[12px] text-white/50 mt-1">{mod.duration} video</p>
                      </div>
                    </div>
                  </CardBody>
                </Card>

                {/* Key Takeaways */}
                <Card>
                  <CardBody>
                    <h3 className="text-[16px] font-semibold text-[#1F2937] mb-3">Key Takeaways</h3>
                    <ul className="flex flex-col gap-2">
                      {mod.takeaways.map((t, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="w-5 h-5 rounded-full bg-[rgba(30,64,175,0.08)] text-[#1E40AF] flex items-center justify-center text-[11px] font-bold shrink-0 mt-0.5">{i + 1}</span>
                          <span className="text-[14px] text-[#1F2937] leading-relaxed">{t}</span>
                        </li>
                      ))}
                    </ul>
                  </CardBody>
                </Card>
              </div>
            )}

            {/* Quiz Section */}
            {currentSection === "quiz" && (
              <div className="flex flex-col gap-4">
                {mod.quiz.map((q, qi) => (
                  <Card key={q.id}>
                    <CardBody>
                      <p className="text-[14px] font-medium text-[#1F2937] mb-3">
                        {qi + 1}. {q.question}
                      </p>
                      <div className="flex flex-col gap-2">
                        {q.options.map((opt, oi) => {
                          const isSelected = quizAnswers[q.id] === oi;
                          const isCorrect = oi === q.correctIndex;
                          const showResult = quizSubmitted;
                          return (
                            <label key={oi}
                              className={cn(
                                "flex items-center gap-3 p-3 rounded-[6px] border cursor-pointer transition-all",
                                showResult && isCorrect ? "border-[#10B981] bg-[rgba(16,185,129,0.04)]" :
                                showResult && isSelected && !isCorrect ? "border-[#EF4444] bg-[rgba(239,68,68,0.04)]" :
                                isSelected ? "border-[#1E40AF] bg-[rgba(30,64,175,0.04)]" :
                                "border-[#E5E7EB] hover:border-[#D1D5DB]"
                              )}>
                              <input type="radio" name={`q-${q.id}`} checked={isSelected}
                                onChange={() => !quizSubmitted && setQuizAnswers({ ...quizAnswers, [q.id]: oi })}
                                className="w-4 h-4 accent-[#1E40AF]" disabled={quizSubmitted} />
                              <span className="text-[13px] text-[#1F2937]">{opt}</span>
                              {showResult && isCorrect && <span className="ml-auto text-[11px] text-[#10B981] font-medium">✓</span>}
                              {showResult && isSelected && !isCorrect && <span className="ml-auto text-[11px] text-[#EF4444] font-medium">✗</span>}
                            </label>
                          );
                        })}
                      </div>
                    </CardBody>
                  </Card>
                ))}

                {!quizSubmitted ? (
                  <Button variant="primary" size="lg"
                    disabled={Object.keys(quizAnswers).length < mod.quiz.length}
                    onClick={() => setQuizSubmitted(true)}>
                    Submit Quiz
                  </Button>
                ) : (
                  <Card className={quizPassed ? "border-[#10B981]" : "border-[#EF4444]"}>
                    <CardBody>
                      <div className="text-center">
                        <p className="text-[18px] font-bold text-[#1F2937]">
                          {quizScore}/{mod.quiz.length} correct
                        </p>
                        <p className={cn("text-[14px] font-medium mt-1", quizPassed ? "text-[#10B981]" : "text-[#EF4444]")}>
                          {quizPassed ? "Passed! You scored 80%+." : "Not quite. You need 80% to pass. Try again!"}
                        </p>
                        {!quizPassed && (
                          <Button variant="secondary" className="mt-3" onClick={() => { setQuizSubmitted(false); setQuizAnswers({}); }}>
                            Retry Quiz
                          </Button>
                        )}
                      </div>
                    </CardBody>
                  </Card>
                )}
              </div>
            )}

            {/* Scenario Section */}
            {currentSection === "scenario" && mod.scenario && (
              <div className="flex flex-col gap-4">
                <Card className="bg-[#E0F2FE] border-[#BAE6FD]">
                  <CardBody>
                    <h3 className="text-[16px] font-semibold text-[#1F2937] mb-2">Scenario</h3>
                    <p className="text-[14px] text-[#1F2937] leading-relaxed">{mod.scenario.prompt}</p>
                  </CardBody>
                </Card>

                <div className="flex flex-col gap-3">
                  {mod.scenario.choices.map((c, i) => (
                    <button key={i} onClick={() => setScenarioChoice(i)}
                      className={cn(
                        "text-left p-4 rounded-[8px] border transition-all",
                        scenarioChoice === i
                          ? c.isOptimal ? "border-[#10B981] bg-[rgba(16,185,129,0.04)]" : "border-[#F59E0B] bg-[rgba(245,158,11,0.04)]"
                          : "border-[#E5E7EB] hover:border-[#D1D5DB]"
                      )}>
                      <p className="text-[14px] font-medium text-[#1F2937]">
                        ({String.fromCharCode(97 + i)}) {c.label}
                      </p>
                      {scenarioChoice === i && (
                        <div className="mt-2 pt-2 border-t border-[#E5E7EB]">
                          <p className="text-[13px] text-[#1F2937] leading-relaxed">{c.outcome}</p>
                          <span className={cn("inline-block mt-2 text-[11px] font-bold px-2 py-0.5 rounded-[4px]",
                            c.isOptimal ? "text-[#10B981] bg-[rgba(16,185,129,0.1)]" : "text-[#F59E0B] bg-[rgba(245,158,11,0.1)]"
                          )}>
                            {c.isOptimal ? "Good choice" : "Risky choice"}
                          </span>
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Mark Complete & Navigation */}
            <div className="flex items-center justify-between pt-4 border-t border-[#E5E7EB]">
              <Link href="/app/learning">
                <span className="text-[13px] text-[#1E40AF] hover:underline cursor-pointer font-medium">← Back to Learning Hub</span>
              </Link>
              <div className="flex gap-3">
                {!completed && quizPassed && (
                  <Button variant="primary" onClick={() => setCompleted(true)}>
                    Mark as Complete
                  </Button>
                )}
                {mod.nextModuleId && (
                  <Link href={`/app/learning/${mod.nextModuleId}`}>
                    <Button variant="secondary">
                      Next Module →
                    </Button>
                  </Link>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>
    </>
  );
}
