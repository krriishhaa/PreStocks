import React, { useState } from "react";
import Head from "next/head";
import { useRouter } from "next/router";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { Navbar } from "@/components/common/Navbar";
import { Card, CardBody } from "@/components/common/Card";
import { Button } from "@/components/common/Button";
import { useStockData } from "@/hooks/useStockData";
import { useFlagData } from "@/hooks/useFlagData";
import { formatCurrency, formatPercent, formatLargeNumber, formatRelativeTime } from "@/utils/formatting";
import { cn } from "@/components/ui/utils";
import type { RiskFlag } from "@/types/flags";

const severityColor: Record<string, string> = {
  low: "#10B981",
  medium: "#F59E0B",
  high: "#EF4444",
  critical: "#EF4444",
};
const severityLabel: Record<string, string> = {
  low: "Low Risk",
  medium: "Moderate Risk",
  high: "High Risk",
  critical: "Critical Risk",
};

const TIMEFRAMES = ["1D", "1W", "1M", "6M", "1Y"] as const;

const mockChartData = Array.from({ length: 30 }, (_, i) => ({
  date: `Day ${i + 1}`,
  price: 140 + Math.random() * 20 - 10 + i * 0.3,
}));

const mockNews = [
  { id: "1", title: "Strong Q2 earnings beat expectations", source: "Reuters", publishedAt: new Date(Date.now() - 3600000).toISOString(), sentiment: "bullish" as const },
  { id: "2", title: "New product line announced at developer conference", source: "TechCrunch", publishedAt: new Date(Date.now() - 7200000).toISOString(), sentiment: "bullish" as const },
  { id: "3", title: "Analyst downgrades on valuation concerns", source: "Bloomberg", publishedAt: new Date(Date.now() - 14400000).toISOString(), sentiment: "bearish" as const },
];

const mockComments = [
  { id: "1", user: "Alex M.", avatar: "A", reasoning: "Great fundamentals + AI tailwinds. Holding long.", score: 24 },
  { id: "2", user: "Priya S.", avatar: "P", reasoning: "Overvalued at these levels. Waiting for a pullback to add.", score: 18 },
  { id: "3", user: "Carlos R.", avatar: "C", reasoning: "Earnings momentum strong. Added this week.", score: 12 },
];

export default function StockDetailPage() {
  const router = useRouter();
  const { ticker } = router.query;
  const symbol = typeof ticker === "string" ? ticker.toUpperCase() : "";
  const { stock, isLoading } = useStockData(symbol);
  const { compositeScore, flags } = useFlagData(symbol);
  const [expandedFlag, setExpandedFlag] = useState<string | null>(null);
  const [showAllFlags, setShowAllFlags] = useState(false);
  const [selectedTimeframe, setSelectedTimeframe] = useState<string>("1M");
  const [orderShares, setOrderShares] = useState("");
  const [showCoolingOff, setShowCoolingOff] = useState(false);
  const [showExplain, setShowExplain] = useState<string | null>(null);
  const [explanation, setExplanation] = useState<string>("");
  const [explanationLoading, setExplanationLoading] = useState(false);
  const [showShareReasoning, setShowShareReasoning] = useState(false);
  const [reasoning, setReasoning] = useState("");

  if (!symbol) return null;

  const score = compositeScore?.overallScore ?? 42;
  const severity = compositeScore?.severity ?? "medium";
  const color = severityColor[severity];
  const circumference = 2 * Math.PI * 45;
  const offset = circumference - (score / 100) * circumference;

  const mockPrice = stock?.price ?? 152.30;
  const mockChange = stock?.changePercent ?? 1.24;

  return (
    <>
      <Head>
        <title>{symbol} — PreStocks</title>
      </Head>
      <div className="flex h-screen flex-col">
        <Navbar />
        <main className="flex-1 overflow-y-auto bg-[#F8FAFC] p-6">
          {isLoading && !stock ? (
            <div className="text-center py-16 text-[#9CA3AF]">Loading...</div>
          ) : (
            <div className="grid grid-cols-[1fr_380px] gap-6 items-start max-w-7xl mx-auto">
              {/* LEFT COLUMN (60%) */}
              <div className="flex flex-col gap-6">
                {/* Section A: Stock Header */}
                <Card>
                  <CardBody>
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="flex items-center gap-3 mb-1">
                          <h1 className="text-[28px] font-bold text-[#1F2937]">
                            {stock?.name ?? symbol}
                          </h1>
                          <span className="text-[12px] font-bold text-[#9CA3AF] bg-[#F1F5F9] px-2 py-1 rounded-[4px]">
                            {symbol}
                          </span>
                          <span className="text-[11px] text-[#06B6D4] bg-[rgba(6,182,212,0.08)] px-2 py-0.5 rounded-[4px] font-medium">
                            {stock?.sector ?? "Technology"}
                          </span>
                        </div>
                        <div className="flex gap-4 text-[13px] text-[#9CA3AF]">
                          <span>Market Cap: {formatLargeNumber(stock?.marketCap ?? 2400000000000)}</span>
                          <span>52W: {formatCurrency(stock?.low52w ?? 102.5)} – {formatCurrency(stock?.high52w ?? 178.3)}</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-[36px] font-extrabold text-[#1F2937] tracking-tight">
                          {formatCurrency(mockPrice)}
                        </p>
                        <p className={cn("text-[16px] font-semibold", mockChange >= 0 ? "text-[#10B981]" : "text-[#EF4444]")}>
                          {formatPercent(mockChange)} today
                        </p>
                      </div>
                    </div>
                  </CardBody>
                </Card>

                {/* Section B: Risk Flag Engine */}
                <Card>
                  <CardBody>
                    <h3 className="text-[18px] font-semibold text-[#1F2937] mb-4">Risk Flag Engine</h3>
                    <div className="flex items-center gap-8 mb-6">
                      <div className="relative w-28 h-28">
                        <svg className="w-28 h-28 -rotate-90" viewBox="0 0 100 100">
                          <circle cx="50" cy="50" r="45" fill="none" stroke="#F1F5F9" strokeWidth="8" />
                          <circle cx="50" cy="50" r="45" fill="none" stroke={color} strokeWidth="8"
                            strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round"
                            className="transition-all duration-700" />
                        </svg>
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                          <span className="text-[24px] font-bold" style={{ color }}>{score}</span>
                          <span className="text-[10px] text-[#9CA3AF]">/100</span>
                        </div>
                      </div>
                      <div>
                        <p className="text-[16px] font-semibold" style={{ color }}>{severityLabel[severity]}</p>
                        <p className="text-[13px] text-[#9CA3AF] mt-1 max-w-xs">
                          Based on {compositeScore?.factors.length ?? 8} factors. Click below for details.
                        </p>
                      </div>
                    </div>

                    {compositeScore && (
                      <div className="grid grid-cols-2 gap-3 mb-4">
                        {compositeScore.factors.map((f) => (
                          <div key={f.category} className="p-3 rounded-[6px] bg-[#F8FAFC] border border-[#E5E7EB]">
                            <div className="flex justify-between text-[12px] mb-1.5">
                              <span className="text-[#9CA3AF] font-medium">{f.category}</span>
                              <span className="font-semibold" style={{ color: f.score > 60 ? "#EF4444" : f.score > 30 ? "#F59E0B" : "#10B981" }}>{f.score}%</span>
                            </div>
                            <div className="h-1.5 bg-[#E5E7EB] rounded-full overflow-hidden">
                              <div className="h-full rounded-full transition-all duration-500"
                                style={{ width: `${f.score}%`, backgroundColor: f.score > 60 ? "#EF4444" : f.score > 30 ? "#F59E0B" : "#10B981" }} />
                            </div>
                            <button
                              onClick={() => { setShowExplain(f.category); setExplanationLoading(true); setTimeout(() => { setExplanation(`The ${f.category} flag for ${symbol} is at ${f.score}/100. This indicates elevated risk in this area based on recent data. Historically, when this flag was triggered at similar levels, the stock experienced mixed returns over the following 30 days.`); setExplanationLoading(false); }, 1200); }}
                              className="mt-2 text-[10px] font-medium text-[#06B6D4] hover:underline">
                              Explain this →
                            </button>
                          </div>
                        ))}
                      </div>
                    )}

                    <div className="border-t border-[#E5E7EB] pt-3">
                      <button onClick={() => setShowAllFlags(!showAllFlags)}
                        className="flex items-center gap-2 text-[13px] font-medium text-[#1E40AF] hover:underline">
                        <svg className={`w-3 h-3 transition-transform ${showAllFlags ? "rotate-180" : ""}`}
                          fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                        {showAllFlags ? "Hide" : "Show"} all risk flags
                      </button>
                      {showAllFlags && (
                        <div className="mt-3 flex flex-col gap-2">
                          {flags.length > 0 ? flags.map((flag) => (
                            <FlagItem key={flag.id} flag={flag} isExpanded={expandedFlag === flag.id}
                              onToggle={() => setExpandedFlag(expandedFlag === flag.id ? null : flag.id)} />
                          )) : (
                            <p className="text-[13px] text-[#9CA3AF] py-2">No flags currently active.</p>
                          )}
                        </div>
                      )}
                    </div>
                  </CardBody>
                </Card>

                {/* Section C: Quick Stats Table */}
                <Card>
                  <CardBody>
                    <h3 className="text-[16px] font-semibold text-[#1F2937] mb-4">Quick Stats</h3>
                    <div className="overflow-x-auto">
                      <table className="w-full text-[13px]">
                        <thead>
                          <tr className="border-b border-[#E5E7EB]">
                            <th className="text-left py-2 pr-4 font-medium text-[#9CA3AF]">Metric</th>
                            <th className="text-right py-2 px-3 font-medium text-[#1F2937]">Value</th>
                            <th className="text-right py-2 px-3 font-medium text-[#9CA3AF]">1Y Avg</th>
                            <th className="text-right py-2 px-3 font-medium text-[#9CA3AF]">Industry Avg</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr className="border-b border-[#E5E7EB]">
                            <td className="py-2.5 pr-4 text-[#1F2937]">P/E Ratio</td>
                            <td className="py-2.5 px-3 text-right font-semibold text-[#1F2937]">45.2</td>
                            <td className="py-2.5 px-3 text-right text-[#9CA3AF]">38.5</td>
                            <td className="py-2.5 px-3 text-right text-[#9CA3AF]">22.1</td>
                          </tr>
                          <tr className="border-b border-[#E5E7EB]">
                            <td className="py-2.5 pr-4 text-[#1F2937]">Debt/Equity</td>
                            <td className="py-2.5 px-3 text-right font-semibold text-[#1F2937]">0.8</td>
                            <td className="py-2.5 px-3 text-right text-[#9CA3AF]">0.9</td>
                            <td className="py-2.5 px-3 text-right text-[#9CA3AF]">0.5</td>
                          </tr>
                          <tr className="border-b border-[#E5E7EB]">
                            <td className="py-2.5 pr-4 text-[#1F2937]">EPS</td>
                            <td className="py-2.5 px-3 text-right font-semibold text-[#10B981]">$3.42</td>
                            <td className="py-2.5 px-3 text-right text-[#9CA3AF]">$2.80</td>
                            <td className="py-2.5 px-3 text-right text-[#9CA3AF]">$1.95</td>
                          </tr>
                          <tr className="border-b border-[#E5E7EB]">
                            <td className="py-2.5 pr-4 text-[#1F2937]">Revenue Growth</td>
                            <td className="py-2.5 px-3 text-right font-semibold text-[#10B981]">+122%</td>
                            <td className="py-2.5 px-3 text-right text-[#9CA3AF]">+84%</td>
                            <td className="py-2.5 px-3 text-right text-[#9CA3AF]">+12%</td>
                          </tr>
                          <tr>
                            <td className="py-2.5 pr-4 text-[#1F2937]">Insider Activity</td>
                            <td className="py-2.5 px-3 text-right font-semibold text-[#EF4444]">Net Sell</td>
                            <td className="py-2.5 px-3 text-right text-[#10B981]">Net Buy</td>
                            <td className="py-2.5 px-3 text-right text-[#9CA3AF]">—</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </CardBody>
                </Card>

                {/* Section D: Price Chart */}
                <Card>
                  <CardBody>
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-[16px] font-semibold text-[#1F2937]">Price Chart</h3>
                      <div className="flex gap-1">
                        {TIMEFRAMES.map((tf) => (
                          <button
                            key={tf}
                            onClick={() => setSelectedTimeframe(tf)}
                            className={cn(
                              "px-3 py-1 rounded-[6px] text-[12px] font-bold transition-all",
                              selectedTimeframe === tf
                                ? "bg-[rgba(30,64,175,0.08)] text-[#1E40AF]"
                                : "text-[#9CA3AF] hover:text-[#1F2937]"
                            )}
                          >
                            {tf}
                          </button>
                        ))}
                      </div>
                    </div>
                    <div className="h-[280px] w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={mockChartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                          <defs>
                            <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#1E40AF" stopOpacity={0.12} />
                              <stop offset="95%" stopColor="#1E40AF" stopOpacity={0} />
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                          <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#9CA3AF" }} axisLine={{ stroke: "#E5E7EB" }} tickLine={false} />
                          <YAxis tick={{ fontSize: 11, fill: "#9CA3AF" }} axisLine={false} tickLine={false}
                            tickFormatter={(v) => `$${v.toFixed(0)}`} domain={["auto", "auto"]} />
                          <Tooltip
                            contentStyle={{ backgroundColor: "#FFF", border: "1px solid #E5E7EB", borderRadius: "8px", fontSize: "13px", boxShadow: "0 4px 12px rgba(0,0,0,0.1)" }}
                            formatter={(value: number) => [`$${value.toFixed(2)}`, "Price"]}
                          />
                          <Area type="monotone" dataKey="price" stroke="#1E40AF" strokeWidth={2} fill="url(#priceGradient)" />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </CardBody>
                </Card>

                {/* Section F: News & Social */}
                <Card>
                  <CardBody>
                    <h3 className="text-[16px] font-semibold text-[#1F2937] mb-4">News & Social</h3>
                    <div className="flex flex-col gap-3 mb-6">
                      {mockNews.map((n) => (
                        <div key={n.id} className="flex items-start justify-between p-3 rounded-[6px] border border-[#E5E7EB] bg-[#F8FAFC]">
                          <div className="flex-1">
                            <p className="text-[14px] font-medium text-[#1F2937] leading-snug">{n.title}</p>
                            <div className="flex items-center gap-2 mt-1">
                              <span className="text-[11px] text-[#9CA3AF]">{n.source}</span>
                              <span className="text-[11px] text-[#9CA3AF]">• {formatRelativeTime(n.publishedAt)}</span>
                            </div>
                          </div>
                          <span className={cn(
                            "text-[10px] font-bold uppercase px-1.5 py-0.5 rounded-[4px]",
                            n.sentiment === "bullish" ? "text-[#10B981] bg-[rgba(16,185,129,0.1)]" :
                            n.sentiment === "bearish" ? "text-[#EF4444] bg-[rgba(239,68,68,0.1)]" :
                            "text-[#06B6D4] bg-[rgba(6,182,212,0.1)]"
                          )}>
                            {n.sentiment}
                          </span>
                        </div>
                      ))}
                    </div>

                    <h4 className="text-[14px] font-medium text-[#9CA3AF] mb-3">Community Insights</h4>
                    <div className="flex flex-col gap-3">
                      {mockComments.map((c) => (
                        <div key={c.id} className="flex gap-3 p-3 rounded-[6px] border border-[#E5E7EB]">
                          <div className="w-8 h-8 rounded-full bg-[#F1F5F9] flex items-center justify-center text-[12px] font-bold text-[#1E40AF] shrink-0">
                            {c.avatar}
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center justify-between">
                              <span className="text-[13px] font-semibold text-[#1F2937]">{c.user}</span>
                              <span className="text-[11px] text-[#9CA3AF]">👍 {c.score}</span>
                            </div>
                            <p className="text-[13px] text-[#9CA3AF] mt-0.5">{c.reasoning}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardBody>
                </Card>
              </div>

              {/* RIGHT COLUMN (40%): Section E: CTA Card (Sticky) */}
              <div className="sticky top-6 flex flex-col gap-4">
                <Card className="bg-[#E0F2FE] border-[#BAE6FD]">
                  <CardBody>
                    <h3 className="text-[16px] font-semibold text-[#1F2937] mb-4">Trade {symbol}</h3>
                    <div className="flex flex-col gap-3">
                      <div className="flex flex-col gap-1.5">
                        <label className="text-[12px] font-medium text-[#9CA3AF]">Shares or $ amount</label>
                        <input
                          type="text"
                          value={orderShares}
                          onChange={(e) => setOrderShares(e.target.value)}
                          className="h-10 px-3 rounded-[6px] border border-[#E5E7EB] bg-white text-[14px] text-[#1F2937] placeholder:text-[#9CA3AF] focus:outline-none focus:border-[#1E40AF]"
                          placeholder="10 shares or $1,500"
                        />
                      </div>
                      {/* Cooling-off prompt */}
                      {Number(orderShares) > 0 && score > 50 && (
                        <div className="p-2.5 rounded-[6px] bg-[#FEF3C7] border border-[#F59E0B]/30">
                          <p className="text-[11px] text-[#D97706] font-medium">
                            ⚠ This stock has a risk score of {score}/100. Consider starting with a smaller position.
                          </p>
                        </div>
                      )}
                      <Button variant="primary" size="lg" className="w-full" onClick={() => {
                        if (Number(orderShares) > 0 && score > 60) {
                          setShowCoolingOff(true);
                        } else {
                          window.location.href = `/app/trade?ticker=${symbol}&shares=${orderShares}`;
                        }
                      }}>
                        Buy {symbol}
                      </Button>
                      <Button variant="secondary" size="md" className="w-full">
                        + Add to Watchlist
                      </Button>
                    </div>
                    <p className="text-[11px] text-[#9CA3AF] mt-3 leading-relaxed">
                      You'll be buying with paper money (simulated).
                      Learn about real trading in the Advanced module.
                    </p>
                  </CardBody>
                </Card>

                {/* Risk summary mini-card */}
                <Card>
                  <CardBody>
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-6 h-6 rounded-full flex items-center justify-center text-[11px] font-bold text-white" style={{ backgroundColor: color }}>
                        {score}
                      </div>
                      <span className="text-[13px] font-semibold" style={{ color }}>{severityLabel[severity]}</span>
                    </div>
                    <p className="text-[12px] text-[#9CA3AF]">
                      {score > 60 ? "Consider a smaller position size due to elevated risk." :
                       score > 30 ? "Moderate risk — suitable for diversified portfolios." :
                       "Low risk profile. Suitable for most investors."}
                    </p>
                  </CardBody>
                </Card>

                {/* Share your reasoning */}
                <Card>
                  <CardBody>
                    <h4 className="text-[13px] font-semibold text-[#1F2937] mb-2">Share your reasoning</h4>
                    <textarea
                      value={reasoning}
                      onChange={(e) => setReasoning(e.target.value.slice(0, 300))}
                      placeholder={`Why are you buying/selling ${symbol}?`}
                      className="w-full h-20 p-2.5 rounded-[6px] border border-[#E5E7EB] text-[13px] text-[#1F2937] placeholder:text-[#9CA3AF] resize-none focus:outline-none focus:border-[#1E40AF]"
                    />
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-[10px] text-[#9CA3AF]">{reasoning.length}/300</span>
                      <button
                        disabled={reasoning.length < 10}
                        className="text-[12px] font-medium text-[#1E40AF] hover:underline disabled:text-[#9CA3AF] disabled:no-underline"
                      >
                        Post to Social Feed →
                      </button>
                    </div>
                  </CardBody>
                </Card>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Cooling-off Modal */}
      {showCoolingOff && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/40" onClick={() => setShowCoolingOff(false)} />
          <div className="relative z-10 w-full max-w-md rounded-[12px] bg-white p-6 shadow-xl">
            <div className="flex items-start gap-3 mb-4">
              <span className="text-[24px]">⚠️</span>
              <div>
                <h3 className="text-[16px] font-semibold text-[#1F2937]">Cooling-Off Prompt</h3>
                <p className="text-[13px] text-[#9CA3AF] mt-1">
                  This stock has a risk score of {score}/100. {Number(orderShares) > 0 && `Buying ${orderShares} shares may represent a significant position.`}
                </p>
              </div>
            </div>
            <div className="p-3 rounded-[6px] bg-[#FEF3C7] border border-[#F59E0B]/30 mb-4">
              <p className="text-[12px] text-[#D97706]">
                This is a high-risk trade. Consider: Is this position size appropriate for your experience level? Have you reviewed all the risk flags?
              </p>
            </div>
            <label className="flex items-start gap-2 mb-4 cursor-pointer">
              <input type="checkbox" id="cooling-confirm" className="mt-0.5 w-4 h-4 rounded accent-[#1E40AF]" />
              <span className="text-[12px] text-[#1F2937]">
                I understand this is simulated and educational. I have reviewed the risk flags.
              </span>
            </label>
            <div className="flex gap-3">
              <button onClick={() => setShowCoolingOff(false)} className="flex-1 h-10 rounded-[6px] border border-[#E5E7EB] text-[13px] font-medium text-[#1F2937]">
                Go Back
              </button>
              <button onClick={() => { setShowCoolingOff(false); window.location.href = `/app/trade?ticker=${symbol}&shares=${orderShares}`; }}
                className="flex-1 h-10 rounded-[6px] bg-[#1E40AF] text-white text-[13px] font-medium hover:bg-[#1e3a8a]">
                Proceed to Trade
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Explain This Modal */}
      {showExplain && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/40" onClick={() => setShowExplain(null)} />
          <div className="relative z-10 w-full max-w-lg rounded-[12px] bg-white p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-[16px] font-semibold text-[#1F2937]">Explain: {showExplain}</h3>
              <button onClick={() => setShowExplain(null)} className="text-[#9CA3AF] hover:text-[#1F2937]">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            {explanationLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="w-6 h-6 border-2 border-[#1E40AF] border-t-transparent rounded-full animate-spin" />
                <span className="ml-3 text-[13px] text-[#9CA3AF]">Generating explanation...</span>
              </div>
            ) : (
              <div>
                <p className="text-[14px] text-[#1F2937] leading-relaxed mb-4">{explanation}</p>
                <div className="p-3 rounded-[6px] bg-[#F8FAFC] border border-[#E5E7EB]">
                  <p className="text-[11px] text-[#06B6D4] font-medium mb-1">💡 Guidance</p>
                  <p className="text-[12px] text-[#1F2937]">
                    Consider reviewing this flag in the context of your overall portfolio diversification.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}

function FlagItem({ flag, isExpanded, onToggle }: { flag: RiskFlag; isExpanded: boolean; onToggle: () => void }) {
  const color = severityColor[flag.severity];
  return (
    <div className="border border-[#E5E7EB] rounded-[6px] overflow-hidden">
      <button onClick={onToggle} className="w-full flex items-center justify-between p-3 text-left hover:bg-[#F8FAFC] transition-colors">
        <div className="flex items-center gap-2">
          <svg className={`w-3 h-3 transition-transform ${isExpanded ? "rotate-90" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
          <span className="text-[13px] font-medium text-[#1F2937]">{flag.type}</span>
          <span className="text-[11px] font-semibold px-1.5 py-0.5 rounded-[4px]" style={{ backgroundColor: `${color}15`, color }}>↑ {flag.score}%</span>
        </div>
        <span className="text-[12px] text-[#9CA3AF] max-w-[180px] truncate">{flag.title}</span>
      </button>
      {isExpanded && (
        <div className="px-3 pb-3 border-t border-[#E5E7EB] pt-3 bg-[#F8FAFC]">
          <p className="text-[13px] text-[#1F2937] leading-relaxed mb-2">{flag.explanation}</p>
          <div className="flex gap-3">
            <button className="text-[12px] text-[#1E40AF] hover:underline font-medium">Learn more</button>
            <button className="text-[12px] text-[#1E40AF] hover:underline font-medium">Historical chart</button>
            <button className="text-[12px] text-[#1E40AF] hover:underline font-medium">Peer comparison</button>
          </div>
        </div>
      )}
    </div>
  );
}
