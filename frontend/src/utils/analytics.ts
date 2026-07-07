/**
 * Analytics event tracking utility.
 * Tracks key user actions per §8 Success Metrics.
 *
 * In production, replace with Plausible, Fathom, or PostHog.
 */

type EventName =
  | "user_signup"
  | "user_login"
  | "user_completed_module"
  | "user_placed_order"
  | "user_clicked_flag"
  | "user_clicked_explain_flag"
  | "user_viewed_stock"
  | "user_posted_social"
  | "user_liked_post"
  | "page_view";

interface EventProperties {
  [key: string]: string | number | boolean | undefined;
}

class Analytics {
  private enabled: boolean;

  constructor() {
    this.enabled = typeof window !== "undefined" && process.env.NODE_ENV === "production";
  }

  track(event: EventName, properties?: EventProperties) {
    if (typeof window === "undefined") return;

    const payload = {
      event,
      properties: {
        ...properties,
        timestamp: new Date().toISOString(),
        url: window.location.pathname,
      },
    };

    // Development: log to console
    if (process.env.NODE_ENV === "development") {
      console.log("[Analytics]", payload);
    }

    // Production: send to analytics provider
    if (this.enabled) {
      // Plausible
      if ((window as any).plausible) {
        (window as any).plausible(event, { props: properties });
      }
      // Fathom
      if ((window as any).fathom) {
        (window as any).fathom.trackEvent(event, properties);
      }
    }
  }

  // Convenience methods for common events
  signup() {
    this.track("user_signup");
  }

  login() {
    this.track("user_login");
  }

  completedModule(moduleId: string, passed: boolean) {
    this.track("user_completed_module", { module_id: moduleId, passed });
  }

  placedOrder(ticker: string, quantity: number, orderType: string) {
    this.track("user_placed_order", { ticker, quantity, order_type: orderType });
  }

  clickedFlag(flagType: string, ticker: string) {
    this.track("user_clicked_flag", { flag_type: flagType, ticker });
  }

  clickedExplainFlag(flagType: string, ticker: string, responseTimeMs: number) {
    this.track("user_clicked_explain_flag", {
      flag_type: flagType,
      ticker,
      agent_response_time_ms: responseTimeMs,
    });
  }

  viewedStock(ticker: string) {
    this.track("user_viewed_stock", { ticker });
  }

  postedSocial(ticker: string) {
    this.track("user_posted_social", { ticker });
  }

  likedPost(postId: string) {
    this.track("user_liked_post", { post_id: postId });
  }

  pageView(path: string) {
    this.track("page_view", { path });
  }
}

export const analytics = new Analytics();
