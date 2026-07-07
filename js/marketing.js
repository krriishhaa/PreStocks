/**
 * Marketing & Growth Module
 * Waitlist, referral program, Product Hunt, social media, email onboarding
 */

// ─── WAITLIST MANAGER ───
class WaitlistManager {
  constructor() {
    this.form = document.getElementById('waitlist-form');
    this.successEl = document.getElementById('waitlist-success');
    if (this.form) this._init();
  }

  _init() {
    this.form.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = this.form.querySelector('input[type="email"]').value;
      this.join(email);
    });
  }

  async join(email) {
    const position = Math.floor(Math.random() * 500) + 10000;
    const referralCode = this._generateReferralCode(email);

    // Store locally
    localStorage.setItem('ps_waitlist', JSON.stringify({ email, position, referralCode, joinedAt: new Date().toISOString() }));

    // Attempt API call
    try {
      await fetch('/api/waitlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, referral_source: this._getReferralSource() })
      });
    } catch (e) { /* offline-friendly */ }

    this._showSuccess(position, referralCode);
    this._triggerEmailSequence(email);
    this._trackEvent('waitlist_join', { position });
  }

  _showSuccess(position, code) {
    if (this.form) this.form.hidden = true;
    if (this.successEl) {
      this.successEl.hidden = false;
      const posEl = document.getElementById('waitlist-position');
      if (posEl) posEl.textContent = position.toLocaleString();
      const linkEl = document.getElementById('referral-link');
      if (linkEl) linkEl.value = `https://prestocks.io/r/${code}`;
    }
  }

  _generateReferralCode(email) {
    const hash = email.split('').reduce((a, c) => ((a << 5) - a + c.charCodeAt(0)) | 0, 0);
    return Math.abs(hash).toString(36).slice(0, 8);
  }

  _getReferralSource() {
    const params = new URLSearchParams(window.location.search);
    return params.get('ref') || params.get('utm_source') || 'direct';
  }

  _triggerEmailSequence(email) {
    EmailOnboarding.scheduleSequence(email);
  }

  _trackEvent(event, data) {
    if (window.gtag) gtag('event', event, data);
    if (window.mixpanel) mixpanel.track(event, data);
  }
}


// ─── REFERRAL PROGRAM ───
class ReferralProgram {
  static TIERS = [
    { referrals: 3, reward: '1 month Pro free', badge: 'early-supporter' },
    { referrals: 10, reward: '3 months Pro free', badge: 'champion' },
    { referrals: 25, reward: 'Lifetime Pro', badge: 'founding-member' }
  ];

  static getStatus() {
    const data = JSON.parse(localStorage.getItem('ps_referral') || '{}');
    return {
      code: data.code || '',
      referrals: data.count || 0,
      currentTier: this._getCurrentTier(data.count || 0),
      nextTier: this._getNextTier(data.count || 0),
      positionBoost: (data.count || 0) * 100
    };
  }

  static trackReferral(code) {
    const data = JSON.parse(localStorage.getItem('ps_referral') || '{ "count": 0 }');
    data.count = (data.count || 0) + 1;
    data.code = code;
    localStorage.setItem('ps_referral', JSON.stringify(data));
  }

  static _getCurrentTier(count) {
    return [...this.TIERS].reverse().find(t => count >= t.referrals) || null;
  }

  static _getNextTier(count) {
    return this.TIERS.find(t => count < t.referrals) || null;
  }
}


// ─── EMAIL ONBOARDING ───
class EmailOnboarding {
  static SEQUENCE = [
    { day: 0, subject: "Welcome to PreStocks!", template: "welcome" },
    { day: 1, subject: "How PreStocks works (2 min read)", template: "how_it_works" },
    { day: 3, subject: "Your first AI company analysis", template: "first_analysis" },
    { day: 5, subject: "3 pre-IPO companies to watch this week", template: "weekly_picks" },
    { day: 7, subject: "Set up your paper trading portfolio", template: "paper_trading" },
    { day: 10, subject: "You're #{{position}} — refer friends to move up", template: "referral_nudge" },
    { day: 14, subject: "Exclusive: Our IPO prediction model results", template: "social_proof" },
  ];

  static scheduleSequence(email) {
    const scheduled = this.SEQUENCE.map(step => ({
      ...step, email, scheduledAt: new Date(Date.now() + step.day * 86400000).toISOString(), sent: false
    }));
    localStorage.setItem('ps_email_sequence', JSON.stringify(scheduled));
  }

  static getNextEmail() {
    const seq = JSON.parse(localStorage.getItem('ps_email_sequence') || '[]');
    return seq.find(s => !s.sent && new Date(s.scheduledAt) <= new Date());
  }

  static markSent(index) {
    const seq = JSON.parse(localStorage.getItem('ps_email_sequence') || '[]');
    if (seq[index]) { seq[index].sent = true; localStorage.setItem('ps_email_sequence', JSON.stringify(seq)); }
  }
}


// ─── PRODUCT HUNT LAUNCH ───
class ProductHuntLaunch {
  static CONFIG = {
    launchDate: '2026-08-01T08:00:00Z',
    tagline: 'AI-powered pre-IPO research & paper trading',
    topics: ['Investing', 'Artificial Intelligence', 'Fintech'],
    makerComment: `Hey Product Hunt! 👋

We built PreStocks because we were frustrated that pre-IPO investing research was either:
- Behind expensive paywalls ($10k+/year)
- Scattered across 20 different sources
- Missing proper risk analysis

PreStocks combines AI research, risk scoring, and paper trading in one platform. Think Bloomberg Terminal meets Robinhood — but for private companies.

Key features:
🤖 Ask "Analyze Stripe" → get a complete AI breakdown
🎯 Composite risk scores (0-100) for every company
📊 Paper trade pre-IPO companies risk-free
📈 Real-time funding rounds & valuation data

We're currently in beta with 10,000+ on our waitlist. Would love your feedback!`,
    assets: {
      thumbnail: '/assets/ph-thumbnail.png',
      gallery: ['/assets/ph-1.png', '/assets/ph-2.png', '/assets/ph-3.png']
    }
  };

  static getDaysUntilLaunch() {
    const diff = new Date(this.CONFIG.launchDate) - new Date();
    return Math.max(0, Math.ceil(diff / 86400000));
  }

  static getCountdown() {
    const diff = new Date(this.CONFIG.launchDate) - new Date();
    if (diff <= 0) return { days: 0, hours: 0, minutes: 0, launched: true };
    return {
      days: Math.floor(diff / 86400000),
      hours: Math.floor((diff % 86400000) / 3600000),
      minutes: Math.floor((diff % 3600000) / 60000),
      launched: false
    };
  }
}


// ─── SOCIAL MEDIA STRATEGY ───
class SocialMediaStrategy {
  static PLATFORMS = {
    twitter: {
      handle: '@PreStocks',
      contentPillars: ['Pre-IPO analysis', 'Risk education', 'Platform updates', 'Market news'],
      postingSchedule: { frequency: 'daily', bestTimes: ['9:00 AM', '12:30 PM', '5:00 PM'] },
      templates: [
        { type: 'analysis', format: '📊 {company} Deep Dive:\n\n• Valuation: {valuation}\n• Risk Score: {risk}/100\n• IPO Probability: {ipo_prob}%\n\nFull analysis → {link}' },
        { type: 'thread', format: '🧵 Thread: {title}\n\n1/ {hook}' },
        { type: 'engagement', format: '❓ {question}\n\nDrop your answer below 👇' }
      ]
    },
    linkedin: {
      strategy: 'Thought leadership + product updates',
      frequency: '3x/week',
      contentMix: { thought_leadership: 40, product: 20, analysis: 30, engagement: 10 }
    },
    reddit: {
      subreddits: ['r/investing', 'r/startups', 'r/fintech', 'r/wallstreetbets'],
      strategy: 'Value-first, no spam. Share genuine analysis and engage in discussions.'
    }
  };

  static generatePost(platform, type, data) {
    const config = this.PLATFORMS[platform];
    if (!config || !config.templates) return null;
    const template = config.templates.find(t => t.type === type);
    if (!template) return null;
    let post = template.format;
    Object.entries(data).forEach(([key, val]) => { post = post.replace(`{${key}}`, val); });
    return post;
  }
}


// ─── SEO UTILITIES ───
class SEOManager {
  static generateMeta(page, data = {}) {
    const configs = {
      landing: {
        title: 'PreStocks — Pre-IPO Investment Intelligence Platform',
        description: 'Research, track, and paper-trade pre-IPO companies with AI-powered risk analysis. Join 10,000+ investors.',
        keywords: 'pre-IPO investing, private companies, paper trading, risk analysis, AI investing'
      },
      blog: {
        title: `${data.title || 'Blog'} — PreStocks`,
        description: data.excerpt || 'Expert insights on pre-IPO investing from the PreStocks team.',
        keywords: `pre-IPO, ${data.tags || 'investing, analysis'}`
      },
      company: {
        title: `${data.name || 'Company'} — Pre-IPO Analysis | PreStocks`,
        description: `AI-powered analysis of ${data.name}: risk score, valuation, funding history, and IPO probability.`,
        keywords: `${data.name}, pre-IPO, analysis, risk score, valuation`
      }
    };
    return configs[page] || configs.landing;
  }

  static generateSitemap() {
    const pages = [
      { url: '/', priority: 1.0, changefreq: 'daily' },
      { url: '/landing.html', priority: 0.9, changefreq: 'weekly' },
      { url: '/blog.html', priority: 0.8, changefreq: 'daily' },
      { url: '/index.html', priority: 0.7, changefreq: 'weekly' },
    ];
    let xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n';
    pages.forEach(p => {
      xml += `  <url>\n    <loc>https://krriishhaa.github.io/PreStocks${p.url}</loc>\n    <priority>${p.priority}</priority>\n    <changefreq>${p.changefreq}</changefreq>\n  </url>\n`;
    });
    xml += '</urlset>';
    return xml;
  }
}


// ─── INIT ───
document.addEventListener('DOMContentLoaded', () => {
  new WaitlistManager();

  // Check for referral in URL
  const params = new URLSearchParams(window.location.search);
  const ref = params.get('ref');
  if (ref) ReferralProgram.trackReferral(ref);

  // Mobile menu toggle
  const toggle = document.querySelector('.mobile-menu-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (toggle && navLinks) {
    toggle.addEventListener('click', () => {
      const expanded = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', !expanded);
      navLinks.style.display = expanded ? 'none' : 'flex';
    });
  }

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
    });
  });
});

// Export for testing
if (typeof module !== 'undefined') {
  module.exports = { WaitlistManager, ReferralProgram, EmailOnboarding, ProductHuntLaunch, SocialMediaStrategy, SEOManager };
}
