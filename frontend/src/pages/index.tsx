import React, { useState } from "react";
import Head from "next/head";
import Link from "next/link";
import { Button } from "@/components/common/Button";

const features = [
  {
    icon: "🚩",
    title: "Risk Flag Engine",
    description: "Know the risks before you buy. Every stock gets a transparent composite risk score based on 8 factors.",
  },
  {
    icon: "🎓",
    title: "Tiered Learning",
    description: "Access content matched to your level — not complexity dumped on beginners or oversimplified for pros.",
  },
  {
    icon: "🔍",
    title: "Full Transparency",
    description: "See exactly where your orders go. No payment for order flow, no hidden practices.",
  },
];

const comparison = [
  { feature: "Risk score on every stock", prestocks: true, robinhood: false, webull: false },
  { feature: "Tiered educational content", prestocks: true, robinhood: false, webull: false },
  { feature: "Gamification of learning (not trading)", prestocks: true, robinhood: false, webull: false },
  { feature: "Cooling-off prompts before volatile trades", prestocks: true, robinhood: false, webull: false },
  { feature: "Paper trading mode", prestocks: true, robinhood: false, webull: true },
  { feature: "Commission-free trading", prestocks: true, robinhood: true, webull: true },
];

const testimonials = [
  {
    quote: "I finally understand what I'm buying. The risk flags saved me from a bad FOMO trade.",
    name: "Sarah K.",
    role: "Beginner Investor",
  },
  {
    quote: "The structured modules taught me more in 2 weeks than months of YouTube videos.",
    name: "Marcus T.",
    role: "College Student",
  },
];

const faqs = [
  {
    q: "Is PreStocks free?",
    a: "Yes. Paper trading and learning modules are completely free. We'll introduce premium features in the future but the core product stays free.",
  },
  {
    q: "Is this real money?",
    a: "Not yet. PreStocks starts as a paper trading platform with virtual $100,000. We plan to introduce real-money trading in Phase 2.",
  },
  {
    q: "How is the risk score calculated?",
    a: "Our composite risk score analyzes 8 factors: volatility, valuation, balance sheet health, earnings consistency, analyst consensus, sector exposure, concentration risk, and momentum divergence.",
  },
  {
    q: "What makes this different from Robinhood?",
    a: "We prioritize education and risk awareness over engagement. No confetti, no gamified trading. Instead: risk flags, learning gates, and cooling-off prompts.",
  },
  {
    q: "Do I need investing experience?",
    a: "No. Our onboarding assigns you a tier (Beginner/Intermediate/Advanced) and shows you content and features appropriate for your level.",
  },
];

export default function HomePage() {
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  return (
    <>
      <Head>
        <title>PreStocks — Invest with Clarity. Not Confetti.</title>
        <meta name="description" content="Paper trade. Learn real risk. Build wealth. PreStocks is the investing platform that prioritizes education and transparency." />
      </Head>

      <div className="min-h-screen bg-white">
        {/* Navbar */}
        <header className="h-16 flex items-center justify-between px-6 md:px-12 border-b border-[#E5E7EB] sticky top-0 bg-white/95 backdrop-blur-sm z-50">
          <span className="text-[22px] font-extrabold text-[#1F2937]">
            Pre<span className="text-[#1E40AF]">Stocks</span>
          </span>
          <div className="flex gap-3">
            <Link href="/auth/login">
              <Button variant="secondary" size="sm">Sign In</Button>
            </Link>
            <Link href="/auth/signup">
              <Button variant="primary" size="sm">Get Started</Button>
            </Link>
          </div>
        </header>

        {/* Hero */}
        <section className="py-24 px-6 md:px-12 text-center max-w-4xl mx-auto">
          <h1 className="text-[48px] md:text-[56px] font-bold text-[#1F2937] leading-[1.1] mb-4">
            Invest with clarity.<br />
            <span className="text-[#1E40AF]">Not confetti.</span>
          </h1>
          <p className="text-[18px] md:text-[20px] text-[#9CA3AF] max-w-xl mx-auto mb-8 leading-relaxed">
            Paper trade. Learn real risk. Build wealth.
          </p>
          <Link href="/auth/signup">
            <Button variant="primary" size="lg" className="text-[16px] px-8 h-14">
              Start Learning (Free)
            </Button>
          </Link>
        </section>

        {/* Feature Cards */}
        <section className="py-16 px-6 md:px-12 bg-[#F8FAFC]">
          <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
            {features.map((f) => (
              <div
                key={f.title}
                className="p-6 rounded-[8px] border border-[#E5E7EB] bg-white shadow-[0px_1px_3px_rgba(0,0,0,0.1)] hover:shadow-[0px_4px_12px_rgba(0,0,0,0.1)] transition-shadow"
              >
                <span className="text-[32px] block mb-3">{f.icon}</span>
                <h3 className="text-[18px] font-semibold text-[#1F2937] mb-2">{f.title}</h3>
                <p className="text-[14px] text-[#9CA3AF] leading-relaxed">{f.description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Comparison Table */}
        <section className="py-16 px-6 md:px-12">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-[24px] font-semibold text-[#1F2937] text-center mb-8">
              How We Compare
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-[14px]">
                <thead>
                  <tr className="border-b border-[#E5E7EB]">
                    <th className="py-3 pr-4 text-[13px] font-medium text-[#9CA3AF]">Feature</th>
                    <th className="py-3 px-4 text-center text-[13px] font-semibold text-[#1E40AF]">PreStocks</th>
                    <th className="py-3 px-4 text-center text-[13px] font-medium text-[#9CA3AF]">Robinhood</th>
                    <th className="py-3 px-4 text-center text-[13px] font-medium text-[#9CA3AF]">Webull</th>
                  </tr>
                </thead>
                <tbody>
                  {comparison.map((row) => (
                    <tr key={row.feature} className="border-b border-[#E5E7EB]">
                      <td className="py-3 pr-4 text-[#1F2937]">{row.feature}</td>
                      <td className="py-3 px-4 text-center">
                        {row.prestocks ? <span className="text-[#10B981] font-bold">✓</span> : <span className="text-[#9CA3AF]">—</span>}
                      </td>
                      <td className="py-3 px-4 text-center">
                        {row.robinhood ? <span className="text-[#10B981]">✓</span> : <span className="text-[#9CA3AF]">—</span>}
                      </td>
                      <td className="py-3 px-4 text-center">
                        {row.webull ? <span className="text-[#10B981]">✓</span> : <span className="text-[#9CA3AF]">—</span>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* Testimonials */}
        <section className="py-16 px-6 md:px-12 bg-[#F8FAFC]">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-[24px] font-semibold text-[#1F2937] text-center mb-8">
              What Users Say
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {testimonials.map((t) => (
                <div
                  key={t.name}
                  className="p-6 rounded-[8px] border border-[#E5E7EB] bg-white"
                >
                  <p className="text-[15px] text-[#1F2937] leading-relaxed mb-4 italic">
                    &ldquo;{t.quote}&rdquo;
                  </p>
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-[#F1F5F9] flex items-center justify-center text-[12px] font-bold text-[#1E40AF]">
                      {t.name.charAt(0)}
                    </div>
                    <div>
                      <p className="text-[13px] font-semibold text-[#1F2937]">{t.name}</p>
                      <p className="text-[11px] text-[#9CA3AF]">{t.role}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* FAQ */}
        <section className="py-16 px-6 md:px-12">
          <div className="max-w-2xl mx-auto">
            <h2 className="text-[24px] font-semibold text-[#1F2937] text-center mb-8">
              Frequently Asked Questions
            </h2>
            <div className="flex flex-col gap-2">
              {faqs.map((faq, i) => (
                <div
                  key={i}
                  className="border border-[#E5E7EB] rounded-[8px] overflow-hidden"
                >
                  <button
                    onClick={() => setOpenFaq(openFaq === i ? null : i)}
                    className="w-full flex items-center justify-between p-4 text-left hover:bg-[#F8FAFC] transition-colors"
                  >
                    <span className="text-[14px] font-medium text-[#1F2937]">{faq.q}</span>
                    <svg
                      className={`w-4 h-4 text-[#9CA3AF] transition-transform ${openFaq === i ? "rotate-180" : ""}`}
                      fill="none" viewBox="0 0 24 24" stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  {openFaq === i && (
                    <div className="px-4 pb-4 text-[13px] text-[#9CA3AF] leading-relaxed">
                      {faq.a}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="py-12 px-6 md:px-12 border-t border-[#E5E7EB] bg-[#F8FAFC]">
          <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <span className="text-[18px] font-extrabold text-[#1F2937]">
                Pre<span className="text-[#1E40AF]">Stocks</span>
              </span>
              <p className="text-[12px] text-[#9CA3AF] mt-2 leading-relaxed">
                Educational investing platform. Paper trading only. Not financial advice.
              </p>
            </div>
            <div>
              <h4 className="text-[13px] font-semibold text-[#1F2937] mb-3">Product</h4>
              <div className="flex flex-col gap-2 text-[13px] text-[#9CA3AF]">
                <Link href="/app/dashboard" className="hover:text-[#1E40AF]">Dashboard</Link>
                <Link href="/app/learning" className="hover:text-[#1E40AF]">Learning</Link>
                <Link href="/app/trade" className="hover:text-[#1E40AF]">Paper Trading</Link>
              </div>
            </div>
            <div>
              <h4 className="text-[13px] font-semibold text-[#1F2937] mb-3">Company</h4>
              <div className="flex flex-col gap-2 text-[13px] text-[#9CA3AF]">
                <span>About</span>
                <span>Careers</span>
                <span>Blog</span>
              </div>
            </div>
            <div>
              <h4 className="text-[13px] font-semibold text-[#1F2937] mb-3">Legal</h4>
              <div className="flex flex-col gap-2 text-[13px] text-[#9CA3AF]">
                <span>Terms of Service</span>
                <span>Privacy Policy</span>
                <span>Disclosures</span>
              </div>
            </div>
          </div>
          <div className="max-w-5xl mx-auto mt-8 pt-6 border-t border-[#E5E7EB] text-[11px] text-[#9CA3AF]">
            <p>
              PreStocks is an educational platform. All trading is simulated with virtual currency.
              Nothing on this platform constitutes financial advice. Past performance is not indicative of future results.
            </p>
            <p className="mt-2">© {new Date().getFullYear()} PreStocks. All rights reserved.</p>
          </div>
        </footer>
      </div>
    </>
  );
}
