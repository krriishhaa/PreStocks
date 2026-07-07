export type RiskSeverity = "low" | "medium" | "high" | "critical";

export interface RiskFlag {
  id: string;
  symbol: string;
  type: string;
  severity: RiskSeverity;
  title: string;
  description: string;
  explanation: string;
  score: number;
  triggeredAt: string;
  resolved: boolean;
}

export interface CompositeRiskScore {
  symbol: string;
  overallScore: number;
  severity: RiskSeverity;
  factors: {
    category: string;
    score: number;
    weight: number;
  }[];
  flags: RiskFlag[];
}

export interface FlagsState {
  flags: RiskFlag[];
  compositeScores: Record<string, CompositeRiskScore>;
  isLoading: boolean;
  error: string | null;
}
