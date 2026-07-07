import React from "react";
import Link from "next/link";
import { useRouter } from "next/router";
import { cn } from "@/components/ui/utils";
import { useAppSelector } from "@/store/store";
import { formatCurrency, formatPercent } from "@/utils/formatting";

const navLinks = [
  { href: "/app/dashboard", label: "Dashboard", icon: "📊" },
  { href: "/app/portfolio", label: "Portfolio", icon: "💼" },
  { href: "/app/trade", label: "Trade", icon: "📈" },
  { href: "/app/learning", label: "Learn", icon: "🎓" },
  { href: "/app/social", label: "Social", icon: "👥" },
];

export function Navbar() {
  const router = useRouter();
  const portfolio = useAppSelector((state) => state.portfolio.portfolio);
  const isPositive = portfolio.dayChange >= 0;

  return (
    <header className="h-16 bg-white border-b border-[#E5E7EB] flex items-center justify-between px-6 shadow-[0px_1px_3px_rgba(0,0,0,0.05)] sticky top-0 z-50">
      <Link href="/" className="flex items-center gap-2">
        <span className="text-2xl">🏹</span>
        <span className="text-[22px] font-extrabold tracking-tight text-[#1F2937]">
          Pre<span className="text-[#1E40AF]">Stocks</span>
        </span>
      </Link>

      <nav className="flex gap-1 h-full">
        {navLinks.map(({ href, label, icon }) => {
          const isActive = router.pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-2 px-4 text-[14px] font-medium text-[#9CA3AF] border-b-[3px] border-transparent transition-all hover:text-[#1F2937]",
                isActive && "text-[#1E40AF] border-b-[#1E40AF]"
              )}
            >
              <span>{icon}</span>
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="flex gap-6">
        <div className="flex flex-col items-end">
          <span className="text-[10px] uppercase text-[#9CA3AF] tracking-wide font-medium">
            Portfolio
          </span>
          <span className="text-[15px] font-bold text-[#1F2937]">
            {formatCurrency(portfolio.totalValue)}
          </span>
        </div>
        <div className="flex flex-col items-end">
          <span className="text-[10px] uppercase text-[#9CA3AF] tracking-wide font-medium">
            Day P&L
          </span>
          <span className={cn("text-[15px] font-bold", isPositive ? "text-[#10B981]" : "text-[#EF4444]")}>
            {formatPercent(portfolio.dayChangePercent)}
          </span>
        </div>
      </div>
    </header>
  );
}
