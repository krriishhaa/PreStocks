import React, { useState } from "react";
import Head from "next/head";
import { useRouter } from "next/router";
import { Navbar } from "@/components/common/Navbar";
import { Card, CardBody } from "@/components/common/Card";
import { Modal } from "@/components/common/Modal";
import { Button } from "@/components/common/Button";
import { usePortfolio } from "@/hooks/usePortfolio";
import { useFlagData } from "@/hooks/useFlagData";
import { formatCurrency, formatPercent } from "@/utils/formatting";
import { cn } from "@/components/ui/utils";

export default function TradePage() {
  const router = useRouter();
  const { ticker: queryTicker } = router.query;
  const { portfolio, buyStock, sellStock } = usePortfolio();
  const [symbol, setSymbol] = useState(typeof queryTicker === "string" ? queryTicker.toUpperCase() : "");
  const [action, setAction] = useState<"buy" | "sell">("buy");
  const [inputMode, setInputMode] = useState<"shares" | "dollars">("shares");
  const [quantity, setQuantity] = useState("");
  const [orderType, setOrderType] = useState<"market" | "limit">("market");
  const [limitPrice, setLimitPrice] = useState("");
  const [riskAcknowledged, setRiskAcknowledged] = useState(false);
  const [showReview, setShowReview] = useState(false);
  const [reviewConfirmed, setReviewConfirmed] = useState(false);
  const [orderPlaced, setOrderPlaced] = useState(false);
  const [error, setError] = useState("");

  const { flags } = useFlagData(symbol);
  const highRiskFlags = flags.filter((f) => f.severity === "high" || f.severity === "critical");
  const hasHighRisk = highRiskFlags.length > 0;

  const price = 152.30; // mock price
  const shares = inputMode === "shares" ? Number(quantity) || 0 : Math.floor((Number(quantity) || 0) / price);
  const total = shares * price;

  const holdingsValue = portfolio.holdings.reduce((s, h) => s + h.totalValue, 0);
  const newPortfolioValue = portfolio.totalValue + (action === "buy" ? 0 : total) - (action === "buy" ? total : 0);
  const positionPercent = newPortfolioValue > 0 ? (total / newPortfolioValue) * 100 : 0;
  const isLargePosition = positionPercent > 25;

  const existingHolding = portfolio.holdings.find((h) => h.symbol === symbol);
  const existingSectorPercent = 45; // mock

  const handleReview = () => {
    setError("");
    if (!symbol) { setError("Enter a ticker symbol"); return; }
    if (shares <= 0) { setError("Enter a valid quantity"); return; }
    if (action === "buy" && total > portfolio.cashBalance) { setError("Insufficient buying power"); return; }
    if (action === "sell" && (!existingHolding || existingHolding.shares < shares)) { setError("Insufficient shares to sell"); return; }
    if (hasHighRisk && !riskAcknowledged) { setError("Please acknowledge the risk warning"); return; }
    setShowReview(true);
  };

  const handleConfirm = () => {
    try {
      if (action === "buy") {
        buyStock(symbol, symbol, shares, price);
      } else {
        sellStock(symbol, shares, price);
      }
      setShowReview(false);
      setOrderPlaced(true);
      setTimeout(() => setOrderPlaced(false), 4000);
    } catch (err: any) {
      setError(err.message);
      setShowReview(false);
    }
  };

  return (
    <>
      <Head>
        <title>Trade - PreStocks</title>
      </Head>
      <div className="flex h-screen flex-col">
        <Navbar />
        <main className="flex-1 overflow-y-auto bg-[#F8FAFC] p-6">
          <div className="max-w-2xl mx-auto">
            {/* Toast */}
            {orderPlaced && (
              <div className="mb-4 p-3 rounded-[8px] bg-[rgba(16,185,129,0.1)] border border-[#10B981]/30 text-[14px] text-[#10B981] font-medium text-center">
                ✓ Order placed! Your portfolio has been updated.
              </div>
            )}

            {/* High-Risk Warning Banner */}
            {hasHighRisk && (
              <div className="mb-4 p-4 rounded-[8px] bg-[#FEF3C7] border border-[#F59E0B]/30">
                <div className="flex items-start gap-3">
                  <span className="text-[20px]">⚠️</span>
                  <div className="flex-1">
                    <p className="text-[14px] font-semibold text-[#D97706]">High Risk Warning</p>
                    <p className="text-[13px] text-[#D97706] mt-1 leading-relaxed">
                      This stock has extreme volatility. Historically, moves of 8%+ happen weekly. Consider starting smaller.
                    </p>
                    <label className="flex items-center gap-2 mt-3 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={riskAcknowledged}
                        onChange={(e) => setRiskAcknowledged(e.target.checked)}
                        className="w-4 h-4 rounded accent-[#D97706]"
                      />
                      <span className="text-[12px] text-[#D97706] font-medium">
                        I understand, proceed anyway
                      </span>
                    </label>
                  </div>
                </div>
              </div>
            )}

            {/* Main Order Form */}
            <Card>
              <CardBody>
                <h2 className="text-[20px] font-semibold text-[#1F2937] mb-5">Place Order</h2>

                <div className="flex flex-col gap-4">
                  {/* Ticker */}
                  <div className="flex flex-col gap-1.5">
                    <label className="text-[13px] font-medium text-[#9CA3AF]">Ticker</label>
                    <input
                      type="text"
                      value={symbol}
                      onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                      className="h-10 px-3 rounded-[6px] border border-[#E5E7EB] bg-white text-[14px] font-semibold text-[#1F2937] uppercase focus:outline-none focus:border-[#1E40AF]"
                      placeholder="AAPL"
                    />
                  </div>

                  {/* Buy / Sell */}
                  <div className="flex flex-col gap-1.5">
                    <label className="text-[13px] font-medium text-[#9CA3AF]">Order Type</label>
                    <div className="flex gap-2">
                      {(["buy", "sell"] as const).map((a) => (
                        <label key={a} className={cn(
                          "flex-1 flex items-center justify-center gap-2 p-3 rounded-[6px] border cursor-pointer transition-all",
                          action === a
                            ? a === "buy" ? "border-[#10B981] bg-[rgba(16,185,129,0.04)] text-[#10B981]" : "border-[#EF4444] bg-[rgba(239,68,68,0.04)] text-[#EF4444]"
                            : "border-[#E5E7EB] text-[#9CA3AF]"
                        )}>
                          <input type="radio" name="action" value={a} checked={action === a} onChange={() => setAction(a)} className="hidden" />
                          <span className="text-[14px] font-semibold capitalize">{a}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Quantity Toggle */}
                  <div className="flex flex-col gap-1.5">
                    <div className="flex items-center justify-between">
                      <label className="text-[13px] font-medium text-[#9CA3AF]">Quantity</label>
                      <div className="flex gap-1 bg-[#F1F5F9] rounded-[6px] p-0.5">
                        {(["shares", "dollars"] as const).map((m) => (
                          <button key={m} onClick={() => setInputMode(m)}
                            className={cn("px-2 py-1 rounded-[4px] text-[11px] font-medium transition-all",
                              inputMode === m ? "bg-white text-[#1F2937] shadow-sm" : "text-[#9CA3AF]"
                            )}>
                            {m === "shares" ? "Shares" : "$"}
                          </button>
                        ))}
                      </div>
                    </div>
                    <input
                      type="number"
                      value={quantity}
                      onChange={(e) => setQuantity(e.target.value)}
                      className="h-10 px-3 rounded-[6px] border border-[#E5E7EB] bg-white text-[14px] text-[#1F2937] focus:outline-none focus:border-[#1E40AF]"
                      placeholder={inputMode === "shares" ? "10" : "1500"}
                    />
                    <div className="flex items-center justify-between text-[12px] text-[#9CA3AF]">
                      <span>Fee: <span className="text-[#10B981] font-medium">Free</span></span>
                      <span>≈ {shares} shares × {formatCurrency(price)}</span>
                    </div>
                  </div>

                  {/* Market / Limit */}
                  <div className="flex flex-col gap-1.5">
                    <label className="text-[13px] font-medium text-[#9CA3AF]">Execution</label>
                    <div className="flex gap-2">
                      {(["market", "limit"] as const).map((t) => (
                        <button key={t} onClick={() => setOrderType(t)}
                          className={cn("flex-1 p-2.5 rounded-[6px] border text-[13px] font-medium transition-all capitalize",
                            orderType === t ? "border-[#1E40AF] text-[#1E40AF] bg-[rgba(30,64,175,0.04)]" : "border-[#E5E7EB] text-[#9CA3AF]"
                          )}>
                          {t}
                        </button>
                      ))}
                    </div>
                    {orderType === "limit" && (
                      <input type="number" value={limitPrice} onChange={(e) => setLimitPrice(e.target.value)}
                        className="h-10 px-3 rounded-[6px] border border-[#E5E7EB] bg-white text-[14px] text-[#1F2937] mt-2 focus:outline-none focus:border-[#1E40AF]"
                        placeholder="Limit price" />
                    )}
                    <p className="text-[11px] text-[#9CA3AF]">Estimated execution: Immediate fill (simulated)</p>
                  </div>
                </div>
              </CardBody>
            </Card>

            {/* Risk Context */}
            {shares > 0 && (
              <div className="grid grid-cols-2 gap-4 mt-4">
                <Card>
                  <CardBody>
                    <p className="text-[12px] font-medium text-[#9CA3AF] mb-2">Portfolio after trade</p>
                    <div className="h-4 bg-[#F1F5F9] rounded-full overflow-hidden flex">
                      <div className="h-full bg-[#1E40AF]" style={{ width: `${Math.min(positionPercent, 100)}%` }} />
                      <div className="h-full bg-[#06B6D4]" style={{ width: `${Math.min(existingSectorPercent - positionPercent, 50)}%` }} />
                    </div>
                    <p className="text-[11px] text-[#9CA3AF] mt-2">
                      {symbol}: {positionPercent.toFixed(1)}% of portfolio
                    </p>
                    {existingSectorPercent > 40 && (
                      <p className="text-[11px] text-[#F59E0B] font-medium mt-1">
                        ⚠ Tech sector would exceed 40% — diversification risk
                      </p>
                    )}
                  </CardBody>
                </Card>
                <Card>
                  <CardBody>
                    <p className="text-[12px] font-medium text-[#9CA3AF] mb-2">Position size</p>
                    <p className="text-[16px] font-bold text-[#1F2937]">{positionPercent.toFixed(1)}%</p>
                    <p className="text-[11px] text-[#9CA3AF]">of total portfolio</p>
                    {isLargePosition && (
                      <p className="text-[11px] text-[#F59E0B] font-medium mt-2">
                        ⚠ This would be a large position for a beginner
                      </p>
                    )}
                  </CardBody>
                </Card>
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="mt-4 p-3 rounded-[6px] bg-[rgba(239,68,68,0.1)] border border-[#EF4444]/30 text-[13px] text-[#EF4444] text-center">
                {error}
              </div>
            )}

            {/* CTA Buttons */}
            <div className="flex gap-3 mt-5">
              <Button variant="primary" size="lg" className="flex-1" onClick={handleReview}>
                Review Order
              </Button>
              <Button variant="secondary" size="lg" onClick={() => router.back()}>
                Cancel
              </Button>
            </div>
          </div>
        </main>
      </div>

      {/* Review Modal */}
      <Modal isOpen={showReview} onClose={() => setShowReview(false)} title="Review Order">
        <div className="flex flex-col gap-4">
          <div className="p-4 rounded-[8px] bg-[#F8FAFC] border border-[#E5E7EB]">
            <div className="grid grid-cols-2 gap-y-2 text-[13px]">
              <span className="text-[#9CA3AF]">Ticker</span>
              <span className="text-right font-semibold text-[#1F2937]">{symbol}</span>
              <span className="text-[#9CA3AF]">Action</span>
              <span className={cn("text-right font-semibold capitalize", action === "buy" ? "text-[#10B981]" : "text-[#EF4444]")}>{action}</span>
              <span className="text-[#9CA3AF]">Shares</span>
              <span className="text-right font-semibold text-[#1F2937]">{shares}</span>
              <span className="text-[#9CA3AF]">Price</span>
              <span className="text-right font-semibold text-[#1F2937]">{formatCurrency(price)}</span>
              <span className="text-[#9CA3AF]">Total</span>
              <span className="text-right text-[16px] font-bold text-[#1F2937]">{formatCurrency(total)}</span>
            </div>
            {highRiskFlags.length > 0 && (
              <div className="mt-3 pt-3 border-t border-[#E5E7EB]">
                <p className="text-[11px] text-[#F59E0B] font-medium">
                  ⚠ {highRiskFlags.length} high-risk flag{highRiskFlags.length > 1 ? "s" : ""} active
                </p>
              </div>
            )}
          </div>

          <label className="flex items-start gap-2 cursor-pointer">
            <input type="checkbox" checked={reviewConfirmed} onChange={(e) => setReviewConfirmed(e.target.checked)}
              className="mt-0.5 w-4 h-4 rounded accent-[#1E40AF]" />
            <span className="text-[12px] text-[#1F2937]">
              I&apos;ve read the risk information and understand this is simulated
            </span>
          </label>

          <div className="flex gap-3">
            <Button variant="secondary" className="flex-1" onClick={() => setShowReview(false)}>
              Back
            </Button>
            <Button variant="primary" className="flex-1" disabled={!reviewConfirmed} onClick={handleConfirm}>
              Confirm Order
            </Button>
          </div>
        </div>
      </Modal>
    </>
  );
}
