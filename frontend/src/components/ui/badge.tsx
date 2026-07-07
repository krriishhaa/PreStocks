import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-badge px-2 py-0.5 text-[11px] font-semibold transition-colors",
  {
    variants: {
      variant: {
        default: "border border-border bg-background-secondary text-neutral-dark",
        primary: "bg-primary-light text-primary border border-primary/20",
        success: "bg-success-light text-success border border-success/20",
        warning: "bg-warning-light text-warning border border-warning/20",
        danger: "bg-alert-light text-alert border border-alert/20",
        info: "bg-secondary-light text-secondary border border-secondary/20",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
