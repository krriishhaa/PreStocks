import React, { useState } from "react";
import Head from "next/head";
import Link from "next/link";
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
} from "recharts";
import { Navbar } from "@/components/common/Navbar";
import { Card, CardBody } from "@/components/common/Card";
import { Button } from "@/components/common/Button";
import { usePortfolio } from "@/hooks/usePortfolio";
import { formatCurrency, formatPercent } from "@/utils/formatting";
import { cn } from "@/components/ui/utils";

const SECTOR_COLORS = ["#1E40AF", "#06B6D4", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"];

const mockHoldings = [
  { symbol: "NVDA", company: "NVIDIA", shares: 10, avgPrice: 87.50, currentPrice: 92.30, value: 923.00, gainLoss: 5.5, portfolioPercent: 28.3, risk: "high" as const, sector: "Technology" },
  { symbol: "MSFT", company: "Microsoft", shares: 5, avgPrice: 320.00, currentPrice: 315.50, value: 1577.50, gainLoss: -1.4, portfolioPercent: 48.3, risk: "medium" as const, sector: "Technology" },
  { symbol: "JNJ", company: "Johnson & Johnson", shares: 8, avgPrice: 155.00, currentPrice: 162.40, value: 1299.20, gainLoss: 4.8, portfolioPercent: 5.0, risk: "low" as const, sector: "Healthcare" },
];

const mockSectorData = [
  { name: "Technology", value: 60 },
  { name: "Finance", value: 20 },
  { name: "Consumer", value: 12 },
  { name: "Healthcare", value: 8 },
];

const suggestions = [
  { title: "Healthcare ETF", description: "Diversify into healthcare with a single trade", ticker: "XLV" },
  { title: "Energy Stocks", description: "Add energy exposure for balance", ticker: "XLE" },
  { title: "S&P 500 ETF", description: "Broad market index for stability", ticker: "SPY" },
];

const riskColors: Record<string, string> = {
  high: "#EF4444",
  medium: "#F59E0B",
  low: "#10B981",
};
const riskEmoji: Record<string, string> = {
  high: "🔴",
  medium: "🟡",
  low: "🟢",
};

export default function PortfolioPage() {
  const { portfolio } = usePortfolio();
  const [sortCol, setSortCol] = useState<string>("value");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const cashBalance = portfolio.cashBalance || 600.50;
  const totalValue = mockHoldings.reduce((s, h) => s + h.value, 0) + cashBalance;
  const dayPL = 42.18;
  const holdingsCount = mockHoldings.length;
  const sectorCount = new Set(mockHoldings.map((h) => h.sector)).size;
  const cashPercent = (cashBalance / totalValue) * 100;

  const aggregateRisk = 62;
  const concentrated = mockSectorData.find((s) => s.value > 50);

  return (
    <>
      <Head>
        <title>Portfolio - PreStocks</title>
      </Head>
      <div className="flex h-screen flex-col">
        <Navbar />
        <main className="flex-1 overflow-y-auto bg-[#F8FAFC] p-6">
          <div className="max-w-7xl mx-auto flex flex-col gap-6">
            {/* Portfolio Summary */}
            <Card>
              <CardBody>
                <div className="flex items-center justify-between flex-wrap gap-4">
                  <div>
                    <p className="text-[13px] text-[#9CA3AF] mb-1">Total Portfolio Value</p>
                    <p className="text-[32px] font-bold text-[#1F2937] tracking-tight">{formatCurrency(totalValue)}</p>
                    <p className={cn("text-[14px] font-semibold mt-1", dayPL >= 0 ? "text-[#10B981]" : "text-[#EF4444]")}>
                      {dayPL >= 0 ? "+" : ""}{formatCurrency(dayPL)} ({formatPercent(dayPL / totalValue * 100)}) today
                    </p>
                  </div>
                  <div className="flex gap-6">
                    <div>
                      <p className="text-[12px] text-[#9CA3AF]">Buying Power</p>
                      <p className="text-[18px] font-semibold text-[#1F2937]">{formatCurrency(cashBalance)}</p>
                    </div>
                    <div>
                      <p className="text-[12px] text-[#9CA3AF]">Holdings</p>
                      <p className="text-[18px] font-semibold text-[#1F2937]">{holdingsCount}</p>
                    </div>
                    <div>
                      <p className="text-[12px] text-[#9CA3AF]">Sectors</p>
                      <p className="text-[18px] font-semibold text-[#1F2937]">{sectorCount}</p>
                    </div>
                    <div>
                      <p className="text-[12px] text-[#9CA3AF]">Cash %</p>
                      <p className="text-[18px] font-semibold text-[#1F2937]">{cashPercent.toFixed(1)}%</p>
                    </div>
                  </div>
                </div>
              </CardBody>
            </Card>

            {/* Holdings Table */}
            <Card>
              <CardBody>
                <h3 className="text-[18px] font-semibold text-[#1F2937] mb-4">Holdings</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-[13px]">
                    <thead>
                      <tr className="border-b border-[#E5E7EB]">
                        <th className="text-left py-2.5 pr-3 font-medium text-[#9CA3AF]">Ticker</th>
                        <th className="text-left py-2.5 pr-3 font-medium text-[#9CA3AF]">Company</th>
                        <th className="text-right py-2.5 px-2 font-medium text-[#9CA3AF]">Shares</th>
                        <th className="text-right py-2.5 px-2 font-medium text-[#9CA3AF]">Avg Price</th>
                        <th className="text-right py-2.5 px-2 font-medium text-[#9CA3AF]">Current</th>
                        <th className="text-right py-2.5 px-2 font-medium text-[#9CA3AF]">Value</th>
                        <th className="text-right py-2.5 px-2 font-medium text-[#9CA3AF]">Gain/Loss</th>
                        <th className="text-right py-2.5 px-2 font-medium text-[#9CA3AF]">% Portfolio</th>
                        <th className="text-center py-2.5 px-2 font-medium text-[#9CA3AF]">Risk</th>
                        <th className="text-right py-2.5 pl-3 font-medium text-[#9CA3AF]">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {mockHoldings.map((h, i) => (
                        <tr key={h.symbol} className={cn("border-b border-[#E5E7EB]", i % 2 === 1 && "bg-[#F8FAFC]")}>
                          <td className="py-3 pr-3 font-semibold text-[#1E40AF]">{h.symbol}</td>
                          <td className="py-3 pr-3 text-[#1F2937]">{h.company}</td>
                          <td className="py-3 px-2 text-right text-[#1F2937]">{h.shares.toFixed(2)}</td>
                          <td className="py-3 px-2 text-right text-[#1F2937]">{formatCurrency(h.avgPrice)}</td>
                          <td className="py-3 px-2 text-right text-[#1F2937]">{formatCurrency(h.currentPrice)}</td>
                          <td className="py-3 px-2 text-right font-semibold text-[#1F2937]">{formatCurrency(h.value)}</td>
                          <td className={cn("py-3 px-2 text-right font-semibold", h.gainLoss >= 0 ? "text-[#10B981]" : "text-[#EF4444]")}>
                            {h.gainLoss >= 0 ? "+" : ""}{h.gainLoss.toFixed(1)}%
                          </td>
                          <td className="py-3 px-2 text-right text-[#1F2937]">{h.portfolioPercent.toFixed(1)}%</td>
                          <td className="py-3 px-2 text-center">
                            <span title={h.risk}>{riskEmoji[h.risk]}</span>
                          </td>
                          <td className="py-3 pl-3 text-right">
                            <div className="flex gap-2 justify-end">
                              <Link href={`/app/stock/${h.symbol}`}>
                                <span className="text-[12px] text-[#1E40AF] hover:underline font-medium cursor-pointer">View</span>
                              </Link>
                              <Link href={`/app/trade?ticker=${h.symbol}`}>
                                <span className="text-[12px] text-[#EF4444] hover:underline font-medium cursor-pointer">Sell</span>
                              </Link>
                            </div>
                          </td>
                        </tr>
                      ))}
                      {/* Cash row */}
                      <tr className="bg-[#F8FAFC]">
                        <td className="py-3 pr-3 font-semibold text-[#1F2937]">—</td>
                        <td className="py-3 pr-3 text-[#1F2937]">Cash</td>
                        <td className="py-3 px-2 text-right text-[#9CA3AF]">—</td>
                        <td className="py-3 px-2 text-right text-[#9CA3AF]">—</td>
                        <td className="py-3 px-2 text-right text-[#9CA3AF]">—</td>
                        <td className="py-3 px-2 text-right font-semibold text-[#1F2937]">{formatCurrency(cashBalance)}</td>
                        <td className="py-3 px-2 text-right text-[#9CA3AF]">—</td>
                        <td className="py-3 px-2 text-right text-[#1F2937]">{cashPercent.toFixed(1)}%</td>
                        <td className="py-3 px-2 text-center text-[#9CA3AF]">—</td>
                        <td className="py-3 pl-3 text-right text-[#9CA3AF]">—</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </CardBody>
            </Card>

            {/* Diversification & Risk Row */}
            <div className="grid grid-cols-[1fr_1fr] gap-6">
              {/* Diversification Analysis */}
              <Card>
                <CardBody>
                  <h3 className="text-[16px] font-semibold text-[#1F2937] mb-4">Diversification Analysis</h3>
                  <div className="flex items-center gap-6">
                    <div className="w-40 h-40">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie data={mockSectorData} dataKey="value" cx="50%" cy="50%" innerRadius={40} outerRadius={70} paddingAngle={2}>
                            {mockSectorData.map((_, idx) => (
                              <Cell key={idx} fill={SECTOR_COLORS[idx % SECTOR_COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip
                            formatter={(value: number, name: string) => [`${value}%`, name]}
                            contentStyle={{ fontSize: "12px", borderRadius: "6px", border: "1px solid #E5E7EB" }}
                          />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="flex flex-col gap-2 flex-1">
                      {mockSectorData.map((s, i) => (
                        <div key={s.name} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: SECTOR_COLORS[i] }} />
                            <span className="text-[13px] text-[#1F2937]">{s.name}</span>
                          </div>
                          <span className="text-[13px] font-medium text-[#1F2937]">{s.value}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  {concentrated && (
                    <div className="mt-4 p-3 rounded-[6px] bg-[#FEF3C7] border border-[#F59E0B]/20">
                      <p className="text-[12px] text-[#D97706] font-medium">
                        ⚠ Concentrated in {concentrated.name} — consider adding other sectors
                      </p>
                    </div>
                  )}
                </CardBody>
              </Card>

              {/* Risk Summary */}
              <Card>
                <CardBody>
                  <h3 className="text-[16px] font-semibold text-[#1F2937] mb-4">Risk Summary</h3>
                  <div className="flex items-center gap-4 mb-4">
                    <div className={cn(
                      "w-16 h-16 rounded-full flex items-center justify-center text-[20px] font-bold text-white",
                      aggregateRisk > 60 ? "bg-[#EF4444]" : aggregateRisk > 30 ? "bg-[#F59E0B]" : "bg-[#10B981]"
                    )}>
                      {aggregateRisk}
                    </div>
                    <div>
                      <p className={cn("text-[16px] font-semibold",
                        aggregateRisk > 60 ? "text-[#EF4444]" : aggregateRisk > 30 ? "text-[#F59E0B]" : "text-[#10B981]"
                      )}>
                        {aggregateRisk > 60 ? "High Risk" : aggregateRisk > 30 ? "Moderate Risk" : "Low Risk"}
                      </p>
                      <p className="text-[13px] text-[#9CA3AF]">{aggregateRisk}/100 aggregate score</p>
                    </div>
                  </div>
                  <p className="text-[13px] text-[#1F2937] leading-relaxed">
                    Your portfolio&apos;s overall risk score is {aggregateRisk}/100 (Moderate Risk). This is driven primarily by Tech sector exposure and NVDA volatility.
                  </p>
                  <div className="mt-4 h-2 bg-[#E5E7EB] rounded-full overflow-hidden">
                    <div className="h-full rounded-full transition-all"
                      style={{ width: `${aggregateRisk}%`, backgroundColor: aggregateRisk > 60 ? "#EF4444" : aggregateRisk > 30 ? "#F59E0B" : "#10B981" }} />
                  </div>
                </CardBody>
              </Card>
            </div>

            {/* Suggested Diversification */}
            <div>
              <h3 className="text-[16px] font-semibold text-[#1F2937] mb-3">Suggested Diversification</h3>
              <div className="grid grid-cols-3 gap-4">
                {suggestions.map((s) => (
                  <Card key={s.ticker}>
                    <CardBody>
                      <h4 className="text-[14px] font-semibold text-[#1F2937]">{s.title}</h4>
                      <p className="text-[12px] text-[#9CA3AF] mt-1">{s.description}</p>
                      <div className="flex items-center justify-between mt-3">
                        <span className="text-[11px] font-bold text-[#1E40AF] bg-[rgba(30,64,175,0.06)] px-2 py-0.5 rounded-[4px]">{s.ticker}</span>
                        <Link href={`/app/stock/${s.ticker}`}>
                          <span className="text-[12px] text-[#1E40AF] hover:underline cursor-pointer font-medium">View →</span>
                        </Link>
                      </div>
                    </CardBody>
                  </Card>
                ))}
              </div>
              <div className="mt-3">
                <Link href="/app/learning">
                  <span className="text-[13px] text-[#06B6D4] hover:underline font-medium cursor-pointer">
                    📚 Understanding diversification — Learn more
                  </span>
                </Link>
              </div>
            </div>
          </div>
        </main>
      </div>
    </>
  );
}
