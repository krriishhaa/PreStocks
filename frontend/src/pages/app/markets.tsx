import React from "react";
import Head from "next/head";
import Link from "next/link";
import { AppLayout } from "@/components/layout/AppLayout";
import { Card, CardBody } from "@/components/common/Card";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/utils/api";

interface MarketIndex {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
}

interface TrendingCompany {
  id: number;
  name: string;
  ticker: string;
  sector: string;
  mentions: number;
  riskScore?: number;
}

const MOCK_INDICES: MarketIndex[] = [
  { symbol: "SPY", name: "S&P 500", price: 5420.3, change: 27.1, changePercent: 0.5 },
  { symbol: "QQQ", name: "NASDAQ 100", price: 18950.7, change: 151.6, changePercent: 0.81 },
  { symbol: "DIA", name: "Dow Jones", price: 39480.2, change: -45.3, changePercent: -0.11 },
  { symbol: "VIX", name: "Volatility Index", price: 15.2, change: -0.8, changePercent: -5.0 },
  { symbol: "BTC", name: "Bitcoin", price: 62340.0, change: 1240.0, changePercent: 2.03 },
];

const SECTORS = [
  { name: "Technology", change: 1.2, companies: 245 },
  { name: "Healthcare", change: -0.3, companies: 189 },
  { name: "Finance", change: 0.6, companies: 312 },
  { name: "Energy", change: -0.8, companies: 97 },
  { name: "Consumer", change: 0.4, companies: 156 },
  { name: "Industrial", change: 0.1, companies: 134 },
  { name: "AI / ML", change: 2.4, companies: 78 },
  { name: "Crypto / Web3", change: 1.8, companies: 42 },
];

export default function MarketsPage() {
  const { data: trending } = useQuery({
    queryKey: ["trending"],
    queryFn: async () => {
      try {
        const res = await api.get("/search/trending");
        return res.data.trending_companies as TrendingCompany[];
      } catch {
        return [] as TrendingCompany[];
      }
    },
  });

  return (
    <>
      <Head>
        <title>Markets - PreStocks</title>
      </Head>
      <AppLayout>
        {/* Page Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-neutral-900">Markets</h1>
          <p className="text-sm text-neutral-500 mt-1">
            Track indices, sectors, and trending pre-IPO companies in real-time.
          </p>
        </div>

        {/* Market Indices */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
          {MOCK_INDICES.map((idx) => (
            <Card key={idx.symbol}>
              <CardBody className="p-4">
                <p className="text-xs font-medium text-neutral-400 uppercase tracking-wide">
                  {idx.name}
                </p>
                <p className="text-lg font-bold text-neutral-900 mt-1">
                  {idx.price.toLocaleString(undefined, { minimumFractionDigits: 1 })}
                </p>
                <p
                  className={`text-sm font-semibold mt-0.5 ${
                    idx.change >= 0 ? "text-success-500" : "text-alert-500"
                  }`}
                >
                  {idx.change >= 0 ? "+" : ""}
                  {idx.change.toFixed(1)} ({idx.changePercent >= 0 ? "+" : ""}
                  {idx.changePercent.toFixed(2)}%)
                </p>
              </CardBody>
            </Card>
          ))}
        </div>

        {/* Sector Performance */}
        <Card className="mb-8">
          <CardBody>
            <h2 className="text-lg font-semibold text-neutral-900 mb-4">
              Sector Performance (Today)
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {SECTORS.map((sector) => (
                <div
                  key={sector.name}
                  className="flex items-center justify-between p-3 rounded-lg border border-neutral-200 hover:border-primary-800/30 transition-colors cursor-pointer"
                >
                  <div>
                    <p className="text-sm font-medium text-neutral-800">{sector.name}</p>
                    <p className="text-xs text-neutral-400">{sector.companies} companies</p>
                  </div>
                  <span
                    className={`text-sm font-bold ${
                      sector.change >= 0 ? "text-success-500" : "text-alert-500"
                    }`}
                  >
                    {sector.change >= 0 ? "+" : ""}
                    {sector.change.toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        {/* Trending Pre-IPO Companies */}
        <Card>
          <CardBody>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-neutral-900">
                Trending Pre-IPO Companies
              </h2>
              <Link
                href="/app/dashboard"
                className="text-xs text-primary-800 font-medium hover:underline"
              >
                View All →
              </Link>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-neutral-200">
                    <th className="text-left py-3 px-2 text-xs font-semibold text-neutral-400 uppercase">
                      Company
                    </th>
                    <th className="text-left py-3 px-2 text-xs font-semibold text-neutral-400 uppercase">
                      Ticker
                    </th>
                    <th className="text-left py-3 px-2 text-xs font-semibold text-neutral-400 uppercase">
                      Sector
                    </th>
                    <th className="text-right py-3 px-2 text-xs font-semibold text-neutral-400 uppercase">
                      News Mentions (7d)
                    </th>
                    <th className="text-right py-3 px-2 text-xs font-semibold text-neutral-400 uppercase">
                      Risk Score
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {(trending || []).length > 0
                    ? trending!.map((c) => (
                        <tr
                          key={c.id}
                          className="border-b border-neutral-100 hover:bg-neutral-50 transition-colors"
                        >
                          <td className="py-3 px-2 font-medium text-neutral-900">
                            <Link href={`/app/stock/${c.ticker?.toLowerCase() || c.id}`} className="hover:text-primary-800">
                              {c.name}
                            </Link>
                          </td>
                          <td className="py-3 px-2 text-neutral-600 font-mono text-xs">
                            {c.ticker || "—"}
                          </td>
                          <td className="py-3 px-2 text-neutral-500">{c.sector || "—"}</td>
                          <td className="py-3 px-2 text-right font-semibold text-neutral-700">
                            {c.mentions}
                          </td>
                          <td className="py-3 px-2 text-right">
                            <span className="inline-block px-2 py-0.5 rounded text-xs font-semibold bg-success-500/10 text-success-500">
                              {c.riskScore ?? "—"}
                            </span>
                          </td>
                        </tr>
                      ))
                    : Array.from({ length: 5 }).map((_, i) => (
                        <tr key={i} className="border-b border-neutral-100">
                          <td className="py-3 px-2">
                            <div className="h-4 w-32 bg-neutral-100 rounded animate-pulse" />
                          </td>
                          <td className="py-3 px-2">
                            <div className="h-4 w-12 bg-neutral-100 rounded animate-pulse" />
                          </td>
                          <td className="py-3 px-2">
                            <div className="h-4 w-20 bg-neutral-100 rounded animate-pulse" />
                          </td>
                          <td className="py-3 px-2">
                            <div className="h-4 w-8 bg-neutral-100 rounded animate-pulse ml-auto" />
                          </td>
                          <td className="py-3 px-2">
                            <div className="h-4 w-8 bg-neutral-100 rounded animate-pulse ml-auto" />
                          </td>
                        </tr>
                      ))}
                </tbody>
              </table>
            </div>
          </CardBody>
        </Card>
      </AppLayout>
    </>
  );
}
