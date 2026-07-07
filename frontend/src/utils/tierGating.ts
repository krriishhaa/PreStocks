/**
 * Tier-based access gating for frontend routes.
 * Checks user's tier before allowing access to restricted pages.
 */

type Tier = "beginner" | "intermediate" | "advanced";

const TIER_LEVELS: Record<Tier, number> = {
  beginner: 1,
  intermediate: 2,
  advanced: 3,
};

interface RouteGate {
  pattern: RegExp;
  minimumTier: Tier;
  redirectTo: string;
  message: string;
}

const ROUTE_GATES: RouteGate[] = [
  {
    pattern: /^\/app\/trade/,
    minimumTier: "beginner",
    redirectTo: "/app/learning",
    message: "Complete onboarding to access trading.",
  },
  {
    pattern: /^\/app\/learning\/(options-deep-dive|short-selling|leverage-margin)/,
    minimumTier: "advanced",
    redirectTo: "/app/learning",
    message: "Complete Intermediate modules to unlock Advanced content.",
  },
];

export function checkTierAccess(pathname: string, userTier: Tier | null): { allowed: boolean; redirectTo?: string; message?: string } {
  if (!userTier) {
    return { allowed: false, redirectTo: "/auth/login", message: "Please log in." };
  }

  const userLevel = TIER_LEVELS[userTier] || 1;

  for (const gate of ROUTE_GATES) {
    if (gate.pattern.test(pathname)) {
      const requiredLevel = TIER_LEVELS[gate.minimumTier];
      if (userLevel < requiredLevel) {
        return { allowed: false, redirectTo: gate.redirectTo, message: gate.message };
      }
    }
  }

  return { allowed: true };
}

export function canViewAdvancedFlags(userTier: Tier | null): boolean {
  return TIER_LEVELS[userTier || "beginner"] >= TIER_LEVELS.intermediate;
}

export function canAccessOptionsModules(userTier: Tier | null): boolean {
  return TIER_LEVELS[userTier || "beginner"] >= TIER_LEVELS.advanced;
}

export function canTrade(userTier: Tier | null): boolean {
  return TIER_LEVELS[userTier || "beginner"] >= TIER_LEVELS.beginner;
}
