import React, { useEffect } from "react";
import Head from "next/head";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Navbar } from "@/components/common/Navbar";
import { Sidebar } from "@/components/common/Sidebar";
import { Card, CardBody } from "@/components/common/Card";
import { Button } from "@/components/common/Button";
import { ProgressBar } from "@/components/learning/ProgressBar";
import { Skeleton } from "@/components/common/States";
import { useAppSelector, useAppDispatch } from "@/store/store";
import { fetchPortfolio, fetchTrades } from "@/store/slices/portfolioSlice";
import { formatCurrency, formatPercent } from "@/utils/formatting";
import { api } from "@/utils/api";
import { cn } from "@/components/ui/utils";

interface LearningProgress {
  total_modules: number;
  completed: number;
  in_progress: number;
  not_started: number;
  completion_pct: number;
}

export default function DashboardPage() {
  const dispatch = useAppDispatch();
  const { data: portfolio, loading, error } = useAppSelector((state) => state.portfolio);
  const trades = useAppSelector((state) => state.portfolio.trades);

  // Fetch portfolio from API on mount
  useEffect(() => {
    dispatch(fetchPortfolio());
    dispatch(fetchTrades());
  }, [dispatch]);

  // Fetch learning progress from API
  const { data: learningProgress } = useQuery<LearningProgress>({
    queryKey: ["learning", "progress"],
    queryFn: async () => {
      const res = await api.get("/learning/progress");
      return res.data;
    },
  });

  // Derived values (all computed from API data, no hardcoding)
  const totalValue = portfolio?.total_value ?? 0;
  const cash = portfolio?.cash ?? 0;
  const invested = portfolio?.total_invested ?? 0;
  const pnl = totalValue - (portfolio?.initial_capital ?? 0);
  const pnlPct = portfolio?.initial_capital ? (pnl / portfolio.initial_capital) * 100 : 0;
  const holdings = portfolio?.holdings ?? [];
  const recentTrades = trades.slice(0, 5);

  return (
    <>
      <Head>
        <title>Dashboard - PreStocks</title>
      </Head>
      <div className="flex h-screen flex-col">
        <Navbar />
        <div className="flex flex-1 overflow-hidden">
          <main className="flex-1 overflow-y-auto bg-neutral-50 p-6">

            {/* Portfolio Value Card */}
            <Card>
              <CardBody>
                {loading ? (
                  <div className="space-y-3">
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-8 w-40" />
                    <Skeleton className="h-4 w-32" />
                  </div>
                ) : (
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-xs font-medium text-neutral-400 uppercase tracking-wide mb-1">
                        Net Worth
                      </p>
                      <h2 className="text-3xl font-bold text-neutral-900 tracking-tight">
                        {formatCurrency(totalValue)}
                      </h2>
                      <div className="flex items-center gap-3 mt-1">
                        <span className={cn(
                          "text-sm font-semibold",
                          pnl >= 0 ? "text-success-500" : "text-alert-500"
                        )}>
                          {pnl >= 0 ? "+" : ""}{formatCurrency(pnl)} ({formatPercent(pnlPct)})
                        </span>
                        <span className="text-xs text-neutral-400">all time</span>
                      </div>
                      <div className="flex gap-4 mt-3 text-xs text-neutral-500">
                        <span>Cash: <strong className="text-neutral-700">{formatCurrency(cash)}</strong></span>
                        <span>Invested: <strong className="text-neutral-700">{formatCurrency(invested)}</strong></span>
                      </div>
                    </div>
                    <Link href="/app/portfolio">
                      <Button variant="secondary" size="sm">View Portfolio</Button>
                    </Link>
                  </div>
                )}
              </CardBody>
            </Card>

            {/* Middle Row: Learning + Risk */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
              {/* Learning Progress — from API */}
              <Card>
                <CardBody>
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-lg">🎓</span>
                    <h3 className="text-base font-semibold text-neutral-900">Learning Progress</h3>
                  </div>
                  {learningProgress ? (
                    <>
                      <ProgressBar value={learningProgress.completion_pct} className="h-2.5" />
                      <p className="text-xs text-neutral-500 mt-2">
                        {learningProgress.completed} of {learningProgress.total_modules} modules complete
                        {learningProgress.in_progress > 0 && ` · ${learningProgress.in_progress} in progress`}
                      </p>
                    </>
                  ) : (
                    <>
                      <Skeleton className="h-2.5 w-full" />
                      <Skeleton className="h-3 w-40 mt-2" />
                    </>
                  )}
                  <Link href="/app/learning">
                    <Button variant="primary" size="sm" className="w-full mt-4">
                      {learningProgress && learningProgress.in_progress > 0 ? "Continue learning" : "Start learning"}
                    </Button>
                  </Link>
                </CardBody>
              </Card>

              {/* Portfolio Risk — from API-driven holdings */}
              <Card>
                <CardBody>
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-lg">📊</span>
                    <h3 className="text-base font-semibold text-neutral-900">Portfolio Snapshot</h3>
                  </div>
                  {portfolio ? (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-neutral-500">Positions</span>
                        <span className="font-medium text-neutral-900">{portfolio.positions}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-neutral-500">Unrealized P&L</span>
                        <span className={cn("font-medium", portfolio.unrealized_pnl >= 0 ? "text-success-500" : "text-alert-500")}>
                          {portfolio.unrealized_pnl >= 0 ? "+" : ""}{formatCurrency(portfolio.unrealized_pnl)}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-neutral-500">Cash available</span>
                        <span className="font-medium text-neutral-900">{formatCurrency(cash)}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-neutral-500">Buying power used</span>
                        <span className="font-medium text-neutral-900">
                          {portfolio.initial_capital > 0
                            ? `${((invested / portfolio.initial_capital) * 100).toFixed(0)}%`
                            : "0%"
                          }
                        </span>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-5 w-full" />)}
                    </div>
                  )}
                </CardBody>
              </Card>
            </div>

            {/* Holdings — from API */}
            <Card className="mt-6">
              <CardBody>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-base font-semibold text-neutral-900">Holdings</h3>
                  {holdings.length > 0 && (
                    <Link href="/app/portfolio" className="text-xs text-primary-800 hover:underline font-medium">
                      View all →
                    </Link>
                  )}
                </div>
                {loading ? (
                  <div className="space-y-3">
                    {[1, 2, 3].map((i) => <Skeleton key={i} className="h-12 w-full" />)}
                  </div>
                ) : holdings.length === 0 ? (
                  <div className="text-center py-6">
                    <p className="text-sm text-neutral-400 mb-3">No holdings yet. Place your first trade to get started.</p>
                    <Link href="/app/trade">
                      <Button variant="primary" size="sm">Trade Now</Button>
                    </Link>
                  </div>
                ) : (
                  <div className="flex flex-col divide-y divide-neutral-100">
                    {holdings.map((h) => (
                      <Link key={h.id} href={`/app/stock/${h.symbol.toLowerCase()}`}>
                        <div className="flex items-center justify-between py-3 px-2 -mx-2 rounded hover:bg-neutral-50 transition-colors cursor-pointer">
                          <div className="flex items-center gap-3">
                            <div>
                              <span className="text-sm font-bold text-neutral-900">{h.symbol}</span>
                              {h.company_name && (
                                <span className="text-xs text-neutral-400 ml-2">{h.company_name}</span>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center gap-4 text-right">
                            <div>
                              <p className="text-sm font-semibold text-neutral-900">
                                {formatCurrency(h.market_value)}
                              </p>
                              <p className="text-xs text-neutral-400">
                                {h.shares} shares @ {formatCurrency(h.current_price || h.avg_buy_price)}
                              </p>
                            </div>
                            <span className={cn(
                              "text-xs font-semibold px-1.5 py-0.5 rounded min-w-[52px] text-center",
                              h.unrealized_pnl_pct >= 0
                                ? "text-success-500 bg-success-500/10"
                                : "text-alert-500 bg-alert-500/10"
                            )}>
                              {formatPercent(h.unrealized_pnl_pct)}
                            </span>
                          </div>
                        </div>
                      </Link>
                    ))}
                  </div>
                )}
              </CardBody>
            </Card>

            {/* Recent Activity — from API trades */}
            <Card className="mt-6">
              <CardBody>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-base font-semibold text-neutral-900">Recent Activity</h3>
                  {recentTrades.length > 0 && (
                    <Link href="/app/portfolio" className="text-xs text-primary-800 hover:underline font-medium">
                      Full history →
                    </Link>
                  )}
                </div>
                {recentTrades.length === 0 ? (
                  <p className="text-sm text-neutral-400 text-center py-4">
                    No trades yet. Your transaction history will appear here.
                  </p>
                ) : (
                  <div className="flex flex-col divide-y divide-neutral-100">
                    {recentTrades.map((t) => (
                      <div key={t.id} className="flex items-center justify-between py-2.5">
                        <div className="flex items-center gap-2">
                          <span className={cn(
                            "text-xs font-bold uppercase px-1.5 py-0.5 rounded",
                            t.side === "buy" ? "text-success-500 bg-success-500/10" : "text-alert-500 bg-alert-500/10"
                          )}>
                            {t.side}
                          </span>
                          <span className="text-sm font-medium text-neutral-900">{t.symbol}</span>
                          <span className="text-xs text-neutral-400">
                            {t.shares} @ {formatCurrency(t.price)}
                          </span>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-medium text-neutral-900">{formatCurrency(t.total_amount)}</p>
                          <p className="text-xs text-neutral-400">
                            {new Date(t.executed_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
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
