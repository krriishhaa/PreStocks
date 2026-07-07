import React from "react";
import Link from "next/link";
import { useRouter } from "next/router";
import { cn } from "@/components/ui/utils";
import { useAppSelector } from "@/store/store";
import { formatCurrency, formatPercent } from "@/utils/formatting";

const navLinks = [
  { href: "/app/dashboard", label: "Dashboard", icon: "📊" },
  { href: "/app/markets", label: "Markets", icon: "🌐" },
  { href: "/app/portfolio", label: "Portfolio", icon: "💼" },
  { href: "/app/trade", label: "Trade", icon: "📈" },
  { href: "/app/learning", label: "Learn", icon: "🎓" },
  { href: "/app/social", label: "Social", icon: "👥" },
];

export function Navbar() {
  const router = useRouter();
  const portfolio = useAppSelector((state) => state.portfolio.data);

  const totalValue = portfolio?.total_value ?? 0;
  const pnl = portfolio ? portfolio.total_value - portfolio.initial_capital : 0;
  const pnlPct = portfolio?.initial_capital ? (pnl / portfolio.initial_capital) * 100 : 0;

  return (
    <header className="h-16 bg-white border-b border-neutral-200 flex items-center justify-between px-6 shadow-sm sticky top-0 z-50">
      <Link href="/" className="flex items-center gap-2">
        <span className="text-2xl">🏹</span>
        <span className="text-[22px] font-extrabold tracking-tight text-neutral-900">
          Pre<span className="text-primary-800">Stocks</span>
        </span>
      </Link>

      <nav className="flex gap-1 h-full">
        {navLinks.map(({ href, label, icon }) => {
          const isActive = router.pathname === href || router.pathname.startsWith(href + "/");
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-2 px-4 text-sm font-medium text-neutral-400 border-b-[3px] border-transparent transition-all hover:text-neutral-900",
                isActive && "text-primary-800 border-b-primary-800"
              )}
            >
              <span>{icon}</span>
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="flex gap-6">
        {portfolio && (
          <>
            <div className="flex flex-col items-end">
              <span className="text-[10px] uppercase text-neutral-400 tracking-wide font-medium">
                Net Worth
              </span>
              <span className="text-sm font-bold text-neutral-900">
                {formatCurrency(totalValue)}
              </span>
            </div>
            <div className="flex flex-col items-end">
              <span className="text-[10px] uppercase text-neutral-400 tracking-wide font-medium">
                P&L
              </span>
              <span className={cn("text-sm font-bold", pnl >= 0 ? "text-success-500" : "text-alert-500")}>
                {formatPercent(pnlPct)}
              </span>
            </div>
          </>
        )}
      </div>
    </header>
  );
}
