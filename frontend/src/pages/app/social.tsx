import React, { useState, useEffect, useCallback } from "react";
import Head from "next/head";
import Link from "next/link";
import { Navbar } from "@/components/common/Navbar";
import { Card, CardBody } from "@/components/common/Card";
import { Modal } from "@/components/common/Modal";
import { cn } from "@/components/ui/utils";
import { formatRelativeTime } from "@/utils/formatting";

type FilterType = "all" | "following" | "network";
type SortType = "recent" | "insightful" | "engagement";

interface SocialPost {
  id: string;
  user: { name: string; handle: string; avatar: string };
  reasoning: string;
  ticker: string;
  tickerChange: number;
  riskLevel: "high" | "medium" | "low";
  likes: number;
  comments: number;
  shares: number;
  createdAt: string;
  liked: boolean;
}

const mockPosts: SocialPost[] = [
  { id: "1", user: { name: "Alex Morgan", handle: "@alexm", avatar: "A" }, reasoning: "Sold PLTR because the insider selling pattern has been consistent for 3 months. When executives dump shares at this pace, I pay attention.", ticker: "PLTR", tickerChange: -5.2, riskLevel: "high", likes: 23, comments: 5, shares: 2, createdAt: new Date(Date.now() - 7200000).toISOString(), liked: false },
  { id: "2", user: { name: "Priya Sharma", handle: "@priyas", avatar: "P" }, reasoning: "Added MSFT on the dip. Cloud revenue growth is strong and AI integration is a long-term tailwind. Comfortable holding through volatility.", ticker: "MSFT", tickerChange: -1.4, riskLevel: "medium", likes: 41, comments: 12, shares: 8, createdAt: new Date(Date.now() - 14400000).toISOString(), liked: true },
  { id: "3", user: { name: "Carlos Rivera", handle: "@carlosr", avatar: "C" }, reasoning: "Buying NVDA ahead of earnings. AI demand is not slowing down. Risk is elevated but I'm sizing small — only 5% of portfolio.", ticker: "NVDA", tickerChange: 2.8, riskLevel: "high", likes: 67, comments: 24, shares: 15, createdAt: new Date(Date.now() - 28800000).toISOString(), liked: false },
  { id: "4", user: { name: "Dana Kim", handle: "@danak", avatar: "D" }, reasoning: "Holding JNJ through the dividend. Stable company with low risk. Perfect for my conservative allocation.", ticker: "JNJ", tickerChange: 0.3, riskLevel: "low", likes: 12, comments: 3, shares: 1, createdAt: new Date(Date.now() - 43200000).toISOString(), liked: false },
  { id: "5", user: { name: "Marcus Chen", handle: "@marcusc", avatar: "M" }, reasoning: "Trimmed my TSLA position by 50%. Valuation is stretched and the P/E is over 80. Taking profits while I can.", ticker: "TSLA", tickerChange: -3.1, riskLevel: "high", likes: 55, comments: 18, shares: 9, createdAt: new Date(Date.now() - 57600000).toISOString(), liked: false },
  { id: "6", user: { name: "Fatima Hassan", handle: "@fatimah", avatar: "F" }, reasoning: "Started a position in XLE (energy ETF). Portfolio was 70% tech — need diversification. Energy has low correlation to my existing holdings.", ticker: "XLE", tickerChange: 1.1, riskLevel: "low", likes: 34, comments: 7, shares: 4, createdAt: new Date(Date.now() - 72000000).toISOString(), liked: true },
];

const riskColors: Record<string, string> = { high: "#EF4444", medium: "#F59E0B", low: "#10B981" };
const riskLabels: Record<string, string> = { high: "High Risk", medium: "Med Risk", low: "Low Risk" };
const riskEmoji: Record<string, string> = { high: "🔴", medium: "🟡", low: "🟢" };

export default function SocialPage() {
  const [filter, setFilter] = useState<FilterType>("all");
  const [sort, setSort] = useState<SortType>("recent");
  const [posts, setPosts] = useState<SocialPost[]>(mockPosts);
  const [selectedPost, setSelectedPost] = useState<SocialPost | null>(null);

  const sortedPosts = [...posts].sort((a, b) => {
    if (sort === "recent") return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
    if (sort === "insightful") return b.comments - a.comments;
    return (b.likes + b.comments + b.shares) - (a.likes + a.comments + a.shares);
  });

  const handleLike = (postId: string) => {
    setPosts((prev) =>
      prev.map((p) =>
        p.id === postId
          ? { ...p, liked: !p.liked, likes: p.liked ? p.likes - 1 : p.likes + 1 }
          : p
      )
    );
  };

  return (
    <>
      <Head>
        <title>Social Feed - PreStocks</title>
      </Head>
      <div className="flex h-screen flex-col">
        <Navbar />
        <main className="flex-1 overflow-y-auto bg-[#F8FAFC] p-6">
          <div className="max-w-2xl mx-auto flex flex-col gap-4">
            {/* Header & Controls */}
            <div className="flex items-center justify-between">
              <h1 className="text-[24px] font-bold text-[#1F2937]">Social Feed</h1>
            </div>

            {/* Filter & Sort */}
            <Card>
              <CardBody className="!py-3 !px-4">
                <div className="flex items-center justify-between flex-wrap gap-3">
                  {/* Filter Toggle */}
                  <div className="flex gap-1 bg-[#F1F5F9] rounded-[6px] p-0.5">
                    {([
                      { key: "all" as FilterType, label: "Show all" },
                      { key: "following" as FilterType, label: "Following" },
                      { key: "network" as FilterType, label: "My network" },
                    ]).map(({ key, label }) => (
                      <button key={key} onClick={() => setFilter(key)}
                        className={cn("px-3 py-1.5 rounded-[4px] text-[12px] font-medium transition-all",
                          filter === key ? "bg-white text-[#1F2937] shadow-sm" : "text-[#9CA3AF]"
                        )}>
                        {label}
                      </button>
                    ))}
                  </div>

                  {/* Sort */}
                  <div className="flex items-center gap-2">
                    <span className="text-[12px] text-[#9CA3AF]">Sort:</span>
                    <div className="flex gap-1">
                      {([
                        { key: "recent" as SortType, label: "Recent" },
                        { key: "insightful" as SortType, label: "Most insightful" },
                        { key: "engagement" as SortType, label: "Engagement" },
                      ]).map(({ key, label }) => (
                        <button key={key} onClick={() => setSort(key)}
                          className={cn("px-2.5 py-1 rounded-[4px] text-[11px] font-medium transition-all",
                            sort === key ? "bg-[rgba(30,64,175,0.08)] text-[#1E40AF]" : "text-[#9CA3AF] hover:text-[#1F2937]"
                          )}>
                          {label}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </CardBody>
            </Card>

            {/* Design Principle Notice */}
            <div className="p-3 rounded-[6px] bg-[rgba(6,182,212,0.06)] border border-[#06B6D4]/20">
              <p className="text-[11px] text-[#06B6D4] font-medium">
                💡 This feed surfaces reasoning-based posts, not hype. Posts are ranked by comment quality and thoughtful engagement.
              </p>
            </div>

            {/* Feed */}
            <div className="flex flex-col gap-4">
              {sortedPosts.map((post) => (
                <PostCard key={post.id} post={post} onLike={handleLike} onOpen={setSelectedPost} />
              ))}
            </div>

            {/* Load more */}
            <div className="text-center py-4">
              <button className="text-[13px] text-[#1E40AF] font-medium hover:underline">
                Load more posts...
              </button>
            </div>
          </div>
        </main>
      </div>

      {/* Post Detail Modal */}
      {selectedPost && (
        <Modal isOpen={!!selectedPost} onClose={() => setSelectedPost(null)} title="Post Detail">
          <PostDetail post={selectedPost} onLike={handleLike} />
        </Modal>
      )}
    </>
  );
}

function PostCard({ post, onLike, onOpen }: { post: SocialPost; onLike: (id: string) => void; onOpen: (post: SocialPost) => void }) {
  const riskColor = riskColors[post.riskLevel];

  return (
    <Card className="hover:shadow-[0px_4px_12px_rgba(0,0,0,0.08)] transition-shadow cursor-pointer">
      <CardBody>
        <div onClick={() => onOpen(post)}>
          {/* Header */}
          <div className="flex items-center gap-3 mb-3">
            <div className="w-9 h-9 rounded-full bg-[#F1F5F9] flex items-center justify-center text-[13px] font-bold text-[#1E40AF] shrink-0">
              {post.user.avatar}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-[14px] font-semibold text-[#1F2937]">{post.user.name}</span>
                <span className="text-[12px] text-[#1E40AF]">{post.user.handle}</span>
              </div>
            </div>
            <span className="text-[11px] text-[#9CA3AF] shrink-0">
              {formatRelativeTime(post.createdAt)}
            </span>
          </div>

          {/* Reasoning */}
          <p className="text-[14px] text-[#1F2937] leading-relaxed mb-3">
            &ldquo;{post.reasoning}&rdquo;
          </p>

          {/* Ticker & Risk */}
          <div className="flex items-center gap-3 mb-3 p-2.5 rounded-[6px] bg-[#F8FAFC] border border-[#E5E7EB]">
            <span className="text-[12px] font-bold text-[#1E40AF] bg-[rgba(30,64,175,0.06)] px-2 py-0.5 rounded-[4px]">
              {post.ticker}
            </span>
            <span className={cn("text-[12px] font-semibold",
              post.tickerChange >= 0 ? "text-[#10B981]" : "text-[#EF4444]"
            )}>
              {post.tickerChange >= 0 ? "+" : ""}{post.tickerChange.toFixed(1)}% today
            </span>
            <span className="ml-auto text-[11px] font-medium px-2 py-0.5 rounded-[4px]"
              style={{ color: riskColor, backgroundColor: `${riskColor}12` }}>
              {riskEmoji[post.riskLevel]} {riskLabels[post.riskLevel]}
            </span>
          </div>
        </div>

        {/* Engagement */}
        <div className="flex items-center gap-4 pt-2 border-t border-[#E5E7EB]">
          <button onClick={(e) => { e.stopPropagation(); onLike(post.id); }}
            className={cn("flex items-center gap-1.5 text-[12px] transition-colors",
              post.liked ? "text-[#EF4444]" : "text-[#9CA3AF] hover:text-[#EF4444]"
            )}>
            <span>{post.liked ? "❤️" : "🤍"}</span>
            <span className="font-medium">{post.likes}</span>
          </button>
          <button onClick={() => onOpen(post)}
            className="flex items-center gap-1.5 text-[12px] text-[#9CA3AF] hover:text-[#1E40AF] transition-colors">
            <span>💬</span>
            <span className="font-medium">{post.comments} comments</span>
          </button>
          <button className="flex items-center gap-1.5 text-[12px] text-[#9CA3AF] hover:text-[#06B6D4] transition-colors">
            <span>📤</span>
            <span className="font-medium">{post.shares}</span>
          </button>
        </div>
      </CardBody>
    </Card>
  );
}

function PostDetail({ post, onLike }: { post: SocialPost; onLike: (id: string) => void }) {
  const mockComments = [
    { id: "c1", user: "Jordan T.", text: "Solid reasoning. The insider selling is a red flag I missed.", time: "1h ago" },
    { id: "c2", user: "Sarah L.", text: "Agree on the thesis but I'd wait for the next earnings report before making a decision.", time: "45m ago" },
    { id: "c3", user: "Raj P.", text: "What's your target re-entry price? Interested to hear your downside scenario.", time: "30m ago" },
  ];

  return (
    <div className="flex flex-col gap-4">
      {/* Full post */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-[#F1F5F9] flex items-center justify-center text-[14px] font-bold text-[#1E40AF]">
          {post.user.avatar}
        </div>
        <div>
          <span className="text-[14px] font-semibold text-[#1F2937]">{post.user.name}</span>
          <span className="text-[12px] text-[#1E40AF] ml-2">{post.user.handle}</span>
          <p className="text-[11px] text-[#9CA3AF]">{formatRelativeTime(post.createdAt)}</p>
        </div>
      </div>

      <p className="text-[14px] text-[#1F2937] leading-relaxed">&ldquo;{post.reasoning}&rdquo;</p>

      <div className="flex items-center gap-3 p-2.5 rounded-[6px] bg-[#F8FAFC] border border-[#E5E7EB]">
        <span className="text-[12px] font-bold text-[#1E40AF]">{post.ticker}</span>
        <span className={cn("text-[12px] font-semibold", post.tickerChange >= 0 ? "text-[#10B981]" : "text-[#EF4444]")}>
          {post.tickerChange >= 0 ? "+" : ""}{post.tickerChange.toFixed(1)}%
        </span>
        <span className="text-[11px] font-medium" style={{ color: riskColors[post.riskLevel] }}>
          {riskEmoji[post.riskLevel]} {riskLabels[post.riskLevel]}
        </span>
      </div>

      <div className="flex gap-4 text-[12px]">
        <button onClick={() => onLike(post.id)}
          className={cn("font-medium", post.liked ? "text-[#EF4444]" : "text-[#9CA3AF]")}>
          {post.liked ? "❤️" : "🤍"} {post.likes}
        </button>
        <span className="text-[#9CA3AF]">💬 {post.comments}</span>
        <span className="text-[#9CA3AF]">📤 {post.shares}</span>
      </div>

      {/* Comments */}
      <div className="border-t border-[#E5E7EB] pt-3">
        <h4 className="text-[13px] font-medium text-[#9CA3AF] mb-3">Comments</h4>
        <div className="flex flex-col gap-3">
          {mockComments.map((c) => (
            <div key={c.id} className="flex gap-2.5">
              <div className="w-7 h-7 rounded-full bg-[#F1F5F9] flex items-center justify-center text-[10px] font-bold text-[#1E40AF] shrink-0">
                {c.user[0]}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-[12px] font-semibold text-[#1F2937]">{c.user}</span>
                  <span className="text-[10px] text-[#9CA3AF]">{c.time}</span>
                </div>
                <p className="text-[13px] text-[#1F2937] mt-0.5">{c.text}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Comment Input */}
      <div className="flex gap-2 pt-2 border-t border-[#E5E7EB]">
        <input type="text" placeholder="Add a comment..."
          className="flex-1 h-9 px-3 rounded-[6px] border border-[#E5E7EB] text-[13px] focus:outline-none focus:border-[#1E40AF]" />
        <button className="h-9 px-4 rounded-[6px] bg-[#1E40AF] text-white text-[12px] font-medium hover:bg-[#1e3a8a] transition-colors">
          Post
        </button>
      </div>
    </div>
  );
}
