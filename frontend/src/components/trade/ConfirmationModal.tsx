import React from "react";
import { Modal } from "@/components/common/Modal";
import { Button } from "@/components/common/Button";
import { formatCurrency } from "@/utils/formatting";

interface ConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  action: "buy" | "sell";
  symbol: string;
  shares: number;
  price: number;
}

export function ConfirmationModal({
  isOpen,
  onClose,
  onConfirm,
  action,
  symbol,
  shares,
  price,
}: ConfirmationModalProps) {
  const total = shares * price;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Confirm Order">
      <div className="flex flex-col gap-4">
        <div className="p-4 rounded-[8px] bg-[#F8FAFC] border border-[#E5E7EB]">
          <div className="flex justify-between mb-2">
            <span className="text-[13px] text-[#9CA3AF]">Action</span>
            <span className={`text-[13px] font-semibold ${action === "buy" ? "text-[#10B981]" : "text-[#EF4444]"}`}>
              {action.toUpperCase()}
            </span>
          </div>
          <div className="flex justify-between mb-2">
            <span className="text-[13px] text-[#9CA3AF]">Symbol</span>
            <span className="text-[13px] font-semibold text-[#1F2937]">{symbol}</span>
          </div>
          <div className="flex justify-between mb-2">
            <span className="text-[13px] text-[#9CA3AF]">Shares</span>
            <span className="text-[13px] font-semibold text-[#1F2937]">{shares}</span>
          </div>
          <div className="flex justify-between mb-2">
            <span className="text-[13px] text-[#9CA3AF]">Price</span>
            <span className="text-[13px] font-semibold text-[#1F2937]">
              {formatCurrency(price)}
            </span>
          </div>
          <hr className="border-[#E5E7EB] my-2" />
          <div className="flex justify-between">
            <span className="text-[14px] font-medium text-[#1F2937]">Total</span>
            <span className="text-[16px] font-bold text-[#1F2937]">
              {formatCurrency(total)}
            </span>
          </div>
        </div>

        <div className="flex gap-3">
          <Button variant="secondary" className="flex-1" onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant={action === "buy" ? "primary" : "danger"}
            className="flex-1"
            onClick={onConfirm}
          >
            Confirm {action === "buy" ? "Buy" : "Sell"}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
