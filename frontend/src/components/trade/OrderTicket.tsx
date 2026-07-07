import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/common/Button";
import { usePortfolio } from "@/hooks/usePortfolio";
import { formatCurrency } from "@/utils/formatting";
import { cn } from "@/components/ui/utils";

const orderSchema = z.object({
  quantity: z.number().min(1, "Min 1 share"),
});

type OrderData = z.infer<typeof orderSchema>;

interface OrderTicketProps {
  symbol: string;
  name: string;
  price: number;
  onSuccess?: () => void;
}

export function OrderTicket({ symbol, name, price, onSuccess }: OrderTicketProps) {
  const [action, setAction] = useState<"buy" | "sell">("buy");
  const { portfolio, buyStock, sellStock } = usePortfolio();
  const [error, setError] = useState("");

  const { register, handleSubmit, watch, formState: { errors } } = useForm<OrderData>({
    resolver: zodResolver(orderSchema),
    defaultValues: { quantity: 1 },
  });

  const quantity = watch("quantity") || 0;
  const total = quantity * price;

  const onSubmit = (data: OrderData) => {
    setError("");
    try {
      if (action === "buy") {
        buyStock(symbol, name, data.quantity, price);
      } else {
        sellStock(symbol, data.quantity, price);
      }
      onSuccess?.();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="rounded-[8px] border border-[#E5E7EB] bg-white shadow-[0px_1px_3px_rgba(0,0,0,0.1)] overflow-hidden">
      <div className="flex border-b border-[#E5E7EB]">
        {(["buy", "sell"] as const).map((a) => (
          <button
            key={a}
            onClick={() => setAction(a)}
            className={cn(
              "flex-1 py-3 text-[14px] font-semibold text-center transition-all",
              action === a
                ? a === "buy"
                  ? "text-[#10B981] border-b-2 border-b-[#10B981] bg-[rgba(16,185,129,0.04)]"
                  : "text-[#EF4444] border-b-2 border-b-[#EF4444] bg-[rgba(239,68,68,0.04)]"
                : "text-[#9CA3AF]"
            )}
          >
            {a.toUpperCase()}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="p-5 flex flex-col gap-4">
        <div className="flex justify-between items-center">
          <span className="text-[14px] text-[#9CA3AF]">Symbol</span>
          <span className="text-[15px] font-bold text-[#1F2937] bg-[#F1F5F9] px-2 py-1 rounded-[6px]">
            {symbol}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-[14px] text-[#9CA3AF]">Price</span>
          <span className="text-[15px] font-semibold text-[#1F2937]">
            {formatCurrency(price)}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <label className="text-[14px] text-[#9CA3AF]">Shares</label>
          <input
            type="number"
            {...register("quantity", { valueAsNumber: true })}
            className="w-24 h-9 px-3 text-right rounded-[6px] border border-[#E5E7EB] text-[15px] font-semibold text-[#1F2937] focus:outline-none focus:border-[#1E40AF]"
          />
        </div>
        {errors.quantity && (
          <span className="text-[12px] text-[#EF4444] text-right">
            {errors.quantity.message}
          </span>
        )}

        <hr className="border-[#E5E7EB]" />

        <div className="flex justify-between items-center">
          <span className="text-[14px] text-[#9CA3AF]">Estimated Total</span>
          <span className="text-[20px] font-bold text-[#1F2937]">
            {formatCurrency(total)}
          </span>
        </div>

        {error && (
          <div className="p-2 rounded-[6px] bg-[rgba(239,68,68,0.1)] border border-[#EF4444]/30 text-[12px] text-[#EF4444] text-center">
            {error}
          </div>
        )}

        <Button
          type="submit"
          variant={action === "buy" ? "primary" : "danger"}
          size="lg"
          className="w-full"
        >
          {action === "buy" ? "Buy" : "Sell"} {symbol}
        </Button>

        <p className="text-[11px] text-[#9CA3AF] text-center">
          Cash available: {formatCurrency(portfolio?.cash ?? 0)}
        </p>
      </form>
    </div>
  );
}
