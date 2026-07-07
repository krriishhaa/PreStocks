// Learning Academy Lessons and Quizzes Data

export const LESSONS = [
  {
    id: "stocks-101",
    title: "Stocks 101",
    icon: "📈",
    tagline: "The fundamentals of ownership and equity markets.",
    description: "Learn how companies raise money, what buying a share actually means, and how you earn returns through price changes and dividends.",
    lessons: [
      {
        title: "What is a Stock?",
        content: "A stock (also called equity) represents a fraction of ownership in a corporation. When you buy a stock of a company like Apple or Tesla, you are buying a tiny piece of that company. If the company grows and becomes more profitable, the value of your piece increases. If it does poorly, your piece loses value.",
        bullets: [
          "Equity represents fractional ownership.",
          "Stock price is driven by market supply and demand.",
          "Companies issue shares to raise money for growth."
        ]
      },
      {
        title: "Market Capitalization",
        content: "Market Cap is the total value of all of a company's outstanding shares. It is calculated by multiplying the total number of outstanding shares by the current share price. This determines if a company is Small-cap ($300M - $2B), Mid-cap ($2B - $10B), or Large-cap (over $10B).",
        bullets: [
          "Formula: Share Price × Total Shares Outstanding.",
          "Indicates the size and risk level of a company.",
          "Mega-caps (e.g. Nvidia, Microsoft) exceed trillions of dollars."
        ]
      },
      {
        title: "Order Types: Market vs. Limit",
        content: "When you want to invest, you send orders to the exchange. A Market Order buys or sells stock immediately at the best available current price. A Limit Order sets a specific price at which you are willing to buy or sell; it only executes if the stock hits your target price.",
        bullets: [
          "Market Order: Guarantees speed, but not exact price.",
          "Limit Order: Guarantees price, but not execution speed.",
          "Use Limit Orders during high market volatility."
        ]
      },
      {
        title: "Earning Money: Dividends & Growth",
        content: "Investors make money in two ways: Capital Appreciation (selling the stock for more than you paid) and Dividends (cash payments sent to shareholders from the company's profits, usually quarterly). Not all companies pay dividends; tech giants often reinvest all profits to speed up growth.",
        bullets: [
          "Capital Appreciation is profit from buying low and selling high.",
          "Dividends represent a stream of regular passive income.",
          "Growth stocks focus on price gains; Value stocks focus on dividends."
        ]
      }
    ],
    quiz: [
      {
        question: "If you buy 100 shares of a company that has 10,000 total shares, what do you own?",
        options: [
          "You own 10% of the company's actual physical buildings.",
          "You own a 1% equity stake in the company.",
          "You own 100% of their customer service department.",
          "Nothing, stocks are just paper and don't represent real ownership."
        ],
        answer: 1,
        explanation: "100 shares out of 10,000 total shares represents a 1% equity stake (100 / 10,000 = 0.01 or 1%). This gives you 1% ownership of the company's equity."
      },
      {
        question: "What is the difference between a Market Order and a Limit Order?",
        options: [
          "Market orders are only executed on weekends.",
          "Market orders guarantee execution price; Limit orders guarantee speed.",
          "Market orders buy immediately at current prices; Limit orders execute only at a specified price.",
          "Limit orders can only be placed by professional floor traders."
        ],
        answer: 2,
        explanation: "A Market order executes immediately at the current market price, prioritizing speed. A Limit order executes only if the stock reaches your specified price limit, prioritizing price control."
      },
      {
        question: "How is a company's Market Capitalization calculated?",
        options: [
          "By adding its assets and subtracting its liabilities.",
          "By multiplying the current stock price by the total number of outstanding shares.",
          "By taking the average stock price over the last 365 days.",
          "By looking at the company's net quarterly profit."
        ],
        answer: 1,
        explanation: "Market Cap = Current Stock Price × Outstanding Shares. It is the total market value of a company's equity."
      }
    ]
  },
  {
    id: "trading-masterclass",
    title: "Trading Masterclass",
    icon: "🕯️",
    tagline: "Short-term strategies, charts, and risk control.",
    description: "Understand candlestick charts, basic indicators, short-selling, and how to manage risk so that a single bad trade does not wipe you out.",
    lessons: [
      {
        title: "Longing vs. Shorting",
        content: "Going Long means buying an asset hoping its price will rise so you can sell it for a profit. Going Short (Short Selling) means borrowing shares you don't own, selling them, and hoping the price falls so you can buy them back cheaper to return them, keeping the difference as profit.",
        bullets: [
          "Long: Bullish stance (profit when prices go up).",
          "Short: Bearish stance (profit when prices go down).",
          "Shorting theoretically has unlimited risk if the stock price keeps rising."
        ]
      },
      {
        title: "Reading Candlestick Charts",
        content: "Unlike line charts, Candlesticks display four values for a timeframe: Open, Close, High, and Low (OCHL). A green (or hollow) candle means the price closed higher than it opened. A red (or filled) candle means the price closed lower. The thin lines on top/bottom are called 'wicks' or 'shadows' and show price extremes.",
        bullets: [
          "Candle Body: Shows the range between Open and Close.",
          "Wicks: Show the highest and lowest prices reached during that period.",
          "Patterns help traders guess short-term price direction."
        ]
      },
      {
        title: "Support and Resistance",
        content: "Support is a price level where a stock struggles to fall below because buyers step in. Resistance is a price level where a stock struggles to rise above because sellers take profits. Traders use these levels to plan entry and exit points.",
        bullets: [
          "Support acts as a 'floor' for stock prices.",
          "Resistance acts as a 'ceiling' for stock prices.",
          "A breakout occurs when a stock pushes past these psychological barriers."
        ]
      },
      {
        title: "Risk Management & Stop Losses",
        content: "Successful trading is not about being right 100% of the time; it is about keeping losses small. A Stop-Loss Order automatically sells your stock if it drops to a certain price, cutting off further losses. A common rule is never to risk more than 1% to 2% of your total capital on a single trade.",
        bullets: [
          "Stop-loss: Automatic safety net to prevent disaster.",
          "Risk-to-Reward Ratio: Target a setup where potential profit is at least 2x the potential loss.",
          "Emotional discipline is more important than indicators."
        ]
      }
    ],
    quiz: [
      {
        question: "What does the 'wick' (shadow) of a candlestick represent?",
        options: [
          "The average price of the stock over the day.",
          "The volume of shares traded.",
          "The highest and lowest prices reached during the time period.",
          "The opening and closing prices."
        ],
        answer: 2,
        explanation: "The body of the candle represents the open and close, while the wicks extending from the top and bottom represent the high and low prices hit during the period."
      },
      {
        question: "If you borrow 10 shares of stock at $50, sell them, and later buy them back at $30 to return them, what is your net profit?",
        options: [
          "$200 profit",
          "$200 loss",
          "$500 profit",
          "$30 profit"
        ],
        answer: 0,
        explanation: "You sold the borrowed shares for $500 ($50 × 10). You bought them back for $300 ($30 × 10) to close the position. Your profit is $500 - $300 = $200."
      },
      {
        question: "Why is a Stop-Loss order critical for traders?",
        options: [
          "It guarantees that every trade will be profitable.",
          "It automatically limits potential losses on a trade if the market moves against you.",
          "It allows you to trade when the exchanges are closed.",
          "It doubles your purchasing power through leverage."
        ],
        answer: 1,
        explanation: "A Stop-Loss order acts as an automated risk management tool, selling your asset if it falls below a set threshold, stopping further losses."
      }
    ]
  },
  {
    id: "sip-calculator",
    title: "SIP & Long-Term Wealth",
    icon: "🐷",
    tagline: "The magic of compounding and Systematic Investment Plans.",
    description: "Learn how consistent, disciplined investing beats trying to time the market, and use our simulator to visualize compounding growth over decades.",
    lessons: [
      {
        title: "What is a SIP?",
        content: "A Systematic Investment Plan (SIP) is a strategy where you invest a fixed amount of money at regular intervals (usually monthly) into a stock or mutual fund, rather than investing a lump sum all at once. This instills financial discipline and takes emotion out of investing.",
        bullets: [
          "Fixed amounts invested regularly (e.g., $100 every month).",
          "Fosters savings habits and long-term asset building.",
          "Removes the stress of trying to buy at the 'perfect' bottom."
        ]
      },
      {
        title: "Rupee/Dollar Cost Averaging",
        content: "Because you invest the same amount of money every month, you naturally buy more shares when prices are low and fewer shares when prices are high. Over time, this lowers your average cost per share, helping you ride out market downturns smoothly.",
        bullets: [
          "High Stock Price = You purchase fewer shares.",
          "Low Stock Price = You purchase more shares.",
          "Averages out purchase prices automatically without timing indicators."
        ]
      },
      {
        title: "The Power of Compound Interest",
        content: "Compounding is when you earn returns on your previous returns. Over 5 or 10 years, the growth seems modest. But over 20, 30, or 40 years, the compounding effect creates an exponential curve. It is often called the '8th wonder of the world'.",
        bullets: [
          "Earnings generate their own earnings.",
          "Time in the market is more important than timing the market.",
          "Starting 5 years earlier can double your retirement nest egg."
        ]
      },
      {
        title: "Passive Index Investing",
        content: "Instead of picking individual stocks, long-term investors often buy Index Funds (like SPY, which tracks the S&P 500). Historically, the US stock market has returned about 8% to 10% annually on average over long periods. Index funds offer low fees and automatic diversification.",
        bullets: [
          "Index funds hold shares in hundreds of companies at once.",
          "Low fees (expense ratios) leave more money to compound.",
          "Over 90% of professional stock-pickers fail to beat the index over 15 years."
        ]
      }
    ],
    quiz: [
      {
        question: "How does Dollar-Cost Averaging work in a SIP?",
        options: [
          "It converts all your money to US Dollars for safety.",
          "You buy more shares when prices are low, and fewer when prices are high, lowering your average cost.",
          "It guarantees that you will never buy a stock during a market downturn.",
          "It forces the brokerage to give you a discount on stock purchases."
        ],
        answer: 1,
        explanation: "By investing a fixed dollar amount regularly, your money buys more units/shares when the price is low, and fewer units when the price is high, lowering the overall average cost per share over time."
      },
      {
        question: "What is the primary driver of the compound interest curve over long periods?",
        options: [
          "High annual management fees.",
          "Trading stocks daily to capture short swings.",
          "Time and the reinvestment of earnings/dividends.",
          "Picking only small penny-stocks."
        ],
        answer: 2,
        explanation: "Time is the key catalyst. Reinvesting earnings allows your returns to generate further returns, leading to exponential growth over decades."
      }
    ]
  },
  {
    id: "macro-global",
    title: "Global Trade & Macro",
    icon: "🌍",
    tagline: "How central banks and global events move markets.",
    description: "Learn to trace the links between interest rates, global trade blockades, inflation, and how they hit your portfolio's stock prices.",
    lessons: [
      {
        title: "Interest Rates & Central Banks",
        content: "Central banks (like the Federal Reserve in the US) set benchmark interest rates. When inflation is high, they raise rates to cool down the economy by making borrowing expensive. High interest rates make bonds attractive, increase borrowing costs for businesses, and usually cause stock prices to contract.",
        bullets: [
          "Low Rates = Cheap money, expansion, bullish for stocks.",
          "High Rates = Expensive money, contraction, bearish for stocks.",
          "Growth stocks suffer most when interest rates spike."
        ]
      },
      {
        title: "Inflation and Consumer Power",
        content: "Inflation is the rate at which prices rise, eroding purchasing power. If prices of raw materials rise, company margins shrink unless they can pass the cost to consumers. High inflation forces central banks to raise interest rates, creating a double-hit on stock markets.",
        bullets: [
          "Core Inflation (CPI) measures price changes of goods.",
          "Value stocks (energy, staples) handle inflation better than tech.",
          "Consumer spending drives 70% of the US economy."
        ]
      },
      {
        title: "Global Trade & Tariffs",
        content: "In today's global economy, companies rely on international trade. Tariffs (taxes on imports/exports) make supply chains expensive. For example, trade tensions between the US and China can increase costs for companies like Apple (which builds iPhones in China) or semiconductor firms, hurting their profits.",
        bullets: [
          "Tariffs increase manufacturing and component costs.",
          "Trade blockades or shipping route disruptions fuel inflation.",
          "Multinational stocks are highly sensitive to trade policies."
        ]
      },
      {
        title: "Global Exchange Rates",
        content: "When currency values fluctuate, it affects international sales. A strong US Dollar makes US exports expensive abroad, decreasing foreign sales, and reduces the converted value of international earnings. Conversely, a weaker dollar boosts multinational profits abroad.",
        bullets: [
          "Strong Domestic Currency = Exporters suffer, importers benefit.",
          "Weak Domestic Currency = Exporters benefit, importers suffer.",
          "Currency risk is a key factor in global equity portfolios."
        ]
      }
    ],
    quiz: [
      {
        question: "Why does the Federal Reserve usually raise interest rates?",
        options: [
          "To speed up the stock market when it is falling.",
          "To combat high inflation and cool down an overheating economy.",
          "To lower the tax burden on wealthy corporations.",
          "To decrease the value of the US Dollar."
        ],
        answer: 1,
        explanation: "The Fed raises rates to make borrowing expensive, which slows spending and investment, thereby cooling economic activity and bringing high inflation back to target levels."
      },
      {
        question: "How do trade tariffs generally affect multinational technology stocks?",
        options: [
          "They boost stock prices by removing international competition completely.",
          "They have zero impact since tech is digital and has no supply chains.",
          "They increase component costs and disrupt supply chains, dragging down profit margins.",
          "They automatically eliminate interest rate risk."
        ],
        answer: 2,
        explanation: "Tariffs increase the costs of physical components (like chips, screens, metals) and disrupt global assembly lines, lowering corporate profits and driving stock prices down."
      }
    ]
  }
];
