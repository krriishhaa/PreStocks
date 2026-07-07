import React from "react";
import Head from "next/head";
import Link from "next/link";
import { Navbar } from "@/components/common/Navbar";
import { Sidebar } from "@/components/common/Sidebar";
import { Card, CardBody } from "@/components/common/Card";
import { Button } from "@/components/common/Button";
import { ProgressBar } from "@/components/learning/ProgressBar";
import { useAppSelector } from "@/store/store";
import { formatCurrency, formatPercent } from "@/utils/formatting";
import { cn } from "@/components/ui/utils";

export default function DashboardPage() {
  const portfolio = useAppSelector((state) => state.portfolio.portfolio);
  const flags = useAppSelector((state) => state.flags.flags);
  const isPositiveDay = portfolio.dayChange >= 0;

  const unresolvedFlags = flags.filter((f) => !f.resolved && f.severity !== "low");
  const concentrationFlag = unresolvedFlags.find((f) => f.type === "concentration");

  return (
    <>
      <Head>
        <title>Dashboard - PreStocks</title>
      </Head>
      <div className="flex h-screen flex-col">
        <Navbar />
        <div className="flex flex-1 overflow-hidden">
          <main className="flex-1 overflow-y-auto bg-[#F8FAFC] p-6">
            {/* Top: Portfolio Card */}
            <Card>
              <CardBody>
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-[13px] font-medium text-[#9CA3AF] uppercase tracking-wide mb-1">
                      Portfolio Value
                    </p>
                    <h2 className="text-[32px] font-bold text-[#1F2937] tracking-tight leading-tight">
                      {formatCurrency(portfolio.totalValue)}
                    </h2>
                    <p className={cn(
                      "text-[15px] font-semibold mt-1",
                      isPositiveDay ? "text-[#10B981]" : "text-[#EF4444]"
                    )}>
                      Today: {isPositiveDay ? "+" : ""}{formatCurrency(portfolio.dayChange)} ({formatPercent(portfolio.dayChangePercent)})
                    </p>
                    <p className="text-[13px] text-[#9CA3AF] mt-1">
                      Buying Power: {formatCurrency(portfolio.cashBalance)}
                    </p>
                  </div>
                  <Link href="/app/portfolio">
                    <Button variant="secondary" size="sm">View Full Portfolio</Button>
                  </Link>
                </div>
              </CardBody>
            </Card>

            {/* Middle: Alerts & Recommendations */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
              {/* Risk Alerts */}
              <Card>
                <CardBody>
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-[18px]">⚠️</span>
                    <h3 className="text-[16px] font-semibold text-[#1F2937]">Risk Alerts</h3>
                  </div>
                  {unresolvedFlags.length === 0 ? (
                    <p className="text-[13px] text-[#9CA3AF]">
                      No active risk alerts. Your portfolio looks healthy.
                    </p>
                  ) : (
                    <div className="flex flex-col gap-3">
                      {unresolvedFlags.slice(0, 2).map((flag) => (
                        <div
                          key={flag.id}
                          className="p-3 rounded-[6px] border border-[#E5E7EB] border-l-[3px] border-l-[#F59E0B] bg-[rgba(245,158,11,0.04)]"
                        >
                          <p className="text-[13px] text-[#1F2937] font-medium">
                            {flag.title}
                          </p>
                          <p className="text-[12px] text-[#9CA3AF] mt-1">{flag.description}</p>
                        </div>
                      ))}
                      <Link href="/app/portfolio">
                        <Button variant="secondary" size="sm" className="w-full">
                          View recommendation
                        </Button>
                      </Link>
                    </div>
                  )}
                </CardBody>
              </Card>

              {/* Learning Progress */}
              <Card>
                <CardBody>
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-[18px]">🎓</span>
                    <h3 className="text-[16px] font-semibold text-[#1F2937]">Learning Progress</h3>
                  </div>
                  <div className="mb-3">
                    <ProgressBar value={40} className="h-2.5" />
                    <p className="text-[13px] text-[#9CA3AF] mt-2">
                      Beginner Level — 2 of 5 modules complete
                    </p>
                  </div>
                  <div className="p-3 rounded-[6px] bg-[#F8FAFC] border border-[#E5E7EB]">
                    <p className="text-[12px] text-[#9CA3AF]">Next module:</p>
                    <p className="text-[14px] font-medium text-[#1F2937]">Understanding P/E Ratios</p>
                  </div>
                  <Link href="/app/learning">
                    <Button variant="primary" size="sm" className="w-full mt-3">
                      Continue learning
                    </Button>
                  </Link>
                </CardBody>
              </Card>
            </div>

            {/* Market Update */}
            <Card className="mt-6">
              <CardBody>
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-[18px]">📰</span>
                  <h3 className="text-[16px] font-semibold text-[#1F2937]">Market Update</h3>
                </div>
                <div className="flex flex-wrap gap-4">
                  <div className="flex items-center gap-2 px-3 py-2 rounded-[6px] bg-[#F8FAFC] border border-[#E5E7EB]">
                    <span className="text-[13px] font-medium text-[#1F2937]">S&P 500</span>
                    <span className="text-[13px] font-semibold text-[#10B981]">+0.5%</span>
                  </div>
                  <div className="flex items-center gap-2 px-3 py-2 rounded-[6px] bg-[#F8FAFC] border border-[#E5E7EB]">
                    <span className="text-[13px] font-medium text-[#1F2937]">VIX</span>
                    <span className="text-[13px] font-semibold text-[#9CA3AF]">15.2</span>
                  </div>
                  <div className="flex items-center gap-2 px-3 py-2 rounded-[6px] bg-[#F8FAFC] border border-[#E5E7EB]">
                    <span className="text-[13px] font-medium text-[#1F2937]">NASDAQ</span>
                    <span className="text-[13px] font-semibold text-[#10B981]">+0.8%</span>
                  </div>
                  <div className="flex items-center gap-2 px-3 py-2 rounded-[6px] bg-[rgba(245,158,11,0.08)] border border-[#F59E0B]/20">
                    <span className="text-[13px] font-medium text-[#F59E0B]">📌 Fed announcement today at 2pm ET</span>
                  </div>
                </div>
              </CardBody>
            </Card>

            {/* Watchlist / Recent Activity */}
            <Card className="mt-6">
              <CardBody>
                <h3 className="text-[16px] font-semibold text-[#1F2937] mb-3">
                  Watchlist
                </h3>
                {portfolio.holdings.length === 0 ? (
                  <p className="text-[13px] text-[#9CA3AF] py-4 text-center">
                    Add stocks to your watchlist to track them here.
                  </p>
                ) : (
                  <div className="flex flex-col divide-y divide-[#E5E7EB]">
                    {portfolio.holdings.slice(0, 5).map((h) => (
                      <Link key={h.symbol} href={`/app/stock/${h.symbol.toLowerCase()}`}>
                        <div className="flex items-center justify-between py-3 hover:bg-[#F8FAFC] rounded-[6px] px-2 -mx-2 transition-colors cursor-pointer">
                          <div className="flex items-center gap-3">
                            <span className="text-[14px] font-bold text-[#1F2937]">{h.symbol}</span>
                            <span className="text-[12px] text-[#9CA3AF]">{h.name}</span>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="text-[14px] font-semibold text-[#1F2937]">
                              {formatCurrency(h.currentPrice)}
                            </span>
                            <span className={cn(
                              "text-[12px] font-semibold px-1.5 py-0.5 rounded",
                              h.dayChangePercent >= 0
                                ? "text-[#10B981] bg-[rgba(16,185,129,0.1)]"
                                : "text-[#EF4444] bg-[rgba(239,68,68,0.1)]"
                            )}>
                              {formatPercent(h.dayChangePercent)}
                            </span>
                            <Link href={`/app/stock/${h.symbol.toLowerCase()}`}>
                              <span className="text-[11px] text-[#1E40AF] hover:underline">Details</span>
                            </Link>
                          </div>
                        </div>
                      </Link>
                    ))}
                  </div>
                )}
              </CardBody>
            </Card>
          </main>
          <Sidebar />
        </div>
      </div>
    </>
  );
}
