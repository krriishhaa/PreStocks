import React from "react";
import { cn } from "@/components/ui/utils";

/**
 * Skeleton loading component — subtle fade animation, no spinners.
 * Per §6.6: "gray placeholder boxes with fade in/out at 1-second interval"
 */
export function Skeleton({ className }: { className?: string }) {
  return (
    <div className={cn("animate-pulse bg-[#E5E7EB] rounded-[6px]", className)} />
  );
}

export function SkeletonCard() {
  return (
    <div className="p-4 rounded-[8px] border border-[#E5E7EB] bg-white">
      <Skeleton className="h-4 w-3/4 mb-3" />
      <Skeleton className="h-3 w-full mb-2" />
      <Skeleton className="h-3 w-5/6 mb-4" />
      <Skeleton className="h-8 w-1/3" />
    </div>
  );
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="flex flex-col gap-0">
      <div className="flex gap-4 p-3 border-b border-[#E5E7EB]">
        <Skeleton className="h-3 w-16" />
        <Skeleton className="h-3 w-24" />
        <Skeleton className="h-3 w-16" />
        <Skeleton className="h-3 w-16" />
        <Skeleton className="h-3 w-20" />
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4 p-3 border-b border-[#E5E7EB]">
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-3 w-24" />
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-3 w-20" />
        </div>
      ))}
    </div>
  );
}

export function SkeletonChart() {
  return (
    <div className="h-[280px] w-full rounded-[8px] bg-[#F8FAFC] flex items-end gap-1 p-4">
      {Array.from({ length: 20 }).map((_, i) => (
        <Skeleton key={i} className="flex-1" style={{ height: `${30 + Math.random() * 60}%` }} />
      ))}
    </div>
  );
}

/**
 * Empty state component — per §6.6:
 * Large icon (100x100px, light gray), heading, subheading, CTA button
 */
interface EmptyStateProps {
  icon?: React.ReactNode;
  heading: string;
  subheading: string;
  ctaLabel?: string;
  ctaHref?: string;
  onCtaClick?: () => void;
}

export function EmptyState({ icon, heading, subheading, ctaLabel, ctaHref, onCtaClick }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <div className="w-[100px] h-[100px] rounded-full bg-[#F3F4F6] flex items-center justify-center mb-6">
        {icon || (
          <svg className="w-12 h-12 text-[#D1D5DB]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
        )}
      </div>
      <h2 className="text-[20px] font-semibold text-[#1F2937] mb-2 !mt-0">{heading}</h2>
      <p className="text-[14px] text-[#9CA3AF] max-w-sm mb-6">{subheading}</p>
      {ctaLabel && (
        <a href={ctaHref || "#"} onClick={onCtaClick}
          className="inline-flex items-center justify-center h-10 px-5 rounded-[6px] bg-[#1E40AF] text-white text-[14px] font-medium hover:bg-[#1530A8] transition-colors">
          {ctaLabel}
        </a>
      )}
    </div>
  );
}

/**
 * Error state component — per §6.6:
 * Red background, alert icon, error message, retry button
 */
interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
  onGoBack?: () => void;
}

export function ErrorState({ message, onRetry, onGoBack }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
      <div className="w-full max-w-md p-6 rounded-[8px] bg-[#FECACA] border border-[#EF4444]/30">
        <div className="w-12 h-12 rounded-full bg-[#EF4444] flex items-center justify-center mx-auto mb-4">
          <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <p className="text-[15px] font-medium text-[#1F2937] mb-1">
          {message || "Oops, something went wrong. Please try again."}
        </p>
        <div className="flex gap-3 justify-center mt-4">
          {onRetry && (
            <button onClick={onRetry} className="h-9 px-4 rounded-[6px] bg-[#EF4444] text-white text-[13px] font-medium hover:bg-[#DC2626]">
              Retry
            </button>
          )}
          {onGoBack && (
            <button onClick={onGoBack} className="h-9 px-4 rounded-[6px] bg-white text-[#1F2937] text-[13px] font-medium border border-[#E5E7EB] hover:bg-[#F3F4F6]">
              Go back
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
