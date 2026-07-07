import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";
import { Search } from "lucide-react";

const inputVariants = cva(
  "flex w-full border border-border bg-background-primary text-neutral-dark placeholder:text-neutral-light font-sans transition-all duration-200 file:border-0 file:bg-transparent file:text-sm file:font-medium focus-visible:outline-none focus-visible:border-primary focus-visible:shadow-input disabled:cursor-not-allowed disabled:opacity-50",
  {
    variants: {
      inputSize: {
        sm: "h-8 px-3 text-[13px] rounded-input",
        md: "h-10 px-3 text-[14px] rounded-input",
        lg: "h-12 px-4 text-[15px] rounded-input",
      },
    },
    defaultVariants: {
      inputSize: "md",
    },
  }
);

export interface InputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "size">,
    VariantProps<typeof inputVariants> {
  icon?: React.ReactNode;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, inputSize, icon, ...props }, ref) => {
    if (icon || type === "search") {
      return (
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-light">
            {icon || <Search className="h-4 w-4" />}
          </span>
          <input
            type={type}
            className={cn(inputVariants({ inputSize, className }), "pl-9")}
            ref={ref}
            {...props}
          />
        </div>
      );
    }

    return (
      <input
        type={type}
        className={cn(inputVariants({ inputSize, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Input.displayName = "Input";

export { Input, inputVariants };
