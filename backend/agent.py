import os
import json
import requests
from dotenv import load_dotenv
from backend.database import get_recent_failures

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

def generate_agent_reasoning(ticker: str, macro_rates: int, macro_trade: int, macro_spending: int,
                             headline: str, lstm_result: dict, sentiment_result: dict, 
                             technical_result: dict) -> dict:
    """
    Combines all signals and prompts Claude (or uses a robust local fallback) to make a prediction.
    Returns:
        {
            "decision": str ("BUY", "SELL", "HOLD", "WATCH", "AVOID"),
            "reasoning": str,
            "predicted_move": float (projected 30-day percentage change)
        }
    """
    # 1. Fetch past mistakes for few-shot learning
    failures = get_recent_failures(limit=3)
    failures_str = ""
    if failures:
        failures_str = "Here are some of your past predictions that turned out to be INCORRECT. Use these to calibrate your reasoning and avoid similar biases:\n"
        for i, f in enumerate(failures):
            failures_str += f"- Ticker: {f['ticker']}\n"
            failures_str += f"  Headline: {f['headline']}\n"
            failures_str += f"  Your decision was: {f['agent_decision']}\n"
            failures_str += f"  Your reasoning was: {f['agent_reasoning']}\n"
            failures_str += f"  Target price: ${f['target_price']:.2f}, but actual close was: ${f['actual_close']:.2f}\n\n"
    
    # Map index to readable labels
    rates_lbl = ["Low (Stimulative)", "Medium (Normal)", "High (Restrictive)"][macro_rates]
    trade_lbl = ["Low (Free Trade)", "Moderate", "High (Trade Wars)"][macro_trade]
    spending_lbl = ["Weak (Recessionary)", "Stable", "Strong (Booming)"][macro_spending]
    
    # 2. Formulate Prompt
    prompt = f"""You are the lead AI Market Strategist for PreStocks. Your task is to analyze multiple conflicting signals for the ticker {ticker.upper()} and output a definitive trading decision.

=== MARKET DATA & SIGNALS ===
Ticker: {ticker.upper()}
Macro Conditions:
- Interest Rates: {rates_lbl}
- Trade Tariffs: {trade_lbl}
- Consumer Spending: {spending_lbl}

News Headline: "{headline}"
FinBERT News Sentiment: {sentiment_result['label']} (Positive Prob: {sentiment_result['positive']:.2f}, Negative Prob: {sentiment_result['negative']:.2f}, Score: {sentiment_result['score']})
LSTM 30-Day Forecast: Projected Move of {lstm_result['expected_move']}% (Trend direction: {lstm_result['direction'].upper()})
Technicals: RSI = {technical_result['rsi']} ({technical_result['signal']}), 50-day SMA = {technical_result['sma_50'] or 'N/A'}, 200-day SMA = {technical_result['sma_200'] or 'N/A'}

{failures_str}

=== INSTRUCTIONS ===
1. Reason across conflicting signals. (For example, if LSTM says 'BUY' but technicals say 'OVERBOUGHT', explain which carries more weight and why).
2. Look for nuances (e.g. macro headwinds compressing margins, upcoming implied volatility events, trade tensions hurting hardware supply chains like NVDA/RKLB, or liquidity factors).
3. output a final JSON block at the very end of your response with the following format:
{{
  "decision": "BUY" or "SELL" or "HOLD" or "WATCH" or "AVOID",
  "reasoning": "A concise 2-3 sentence summary of your analysis explaining the conflict resolution.",
  "predicted_move": <float percentage representing expected 30-day change, e.g. 5.4 or -3.2>
}}
Do not write anything else in the JSON block except these three fields.
"""

    if ANTHROPIC_API_KEY:
        try:
            headers = {
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            data = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 1000,
                "temperature": 0.2,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            res = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data, timeout=10)
            if res.status_code == 200:
                response_json = res.json()
                text = response_json["content"][0]["text"]
                
                # Parse JSON out of the response text
                # Find the JSON bracket
                start = text.find("{")
                end = text.rfind("}")
                if start != -1 and end != -1:
                    json_str = text[start:end+1]
                    agent_out = json.loads(json_str)
                    return {
                        "decision": agent_out.get("decision", "HOLD").upper(),
                        "reasoning": agent_out.get("reasoning", text[:300] + "..."),
                        "predicted_move": float(agent_out.get("predicted_move", lstm_result['expected_move']))
                    }
        except Exception as e:
            print(f"Claude API request failed: {e}. Falling back to rule-based agent.")

    # 3. Local Rule-Based Decision Engine (Fallback)
    # This engine resolves conflicts deterministically based on stock sensitivities
    score = sentiment_result['score'] * 0.4 + lstm_result['expected_move'] * 2.0
    
    # Apply macro modifiers
    # NVDA is sensitive to tariffs (-0.6) and rates (-0.1)
    # PLTR is growth sensitive
    # RKLB is capital intensive (rates -0.5, trade -0.3)
    # LUNR is high beta
    
    macro_impact = 0.0
    if macro_rates == 2: # high
        macro_impact -= 10.0
    elif macro_rates == 0: # low
        macro_impact += 10.0
        
    if macro_trade == 2: # high tariffs
        macro_impact -= 15.0
    elif macro_trade == 0:
        macro_impact += 5.0
        
    if macro_spending == 0: # weak
        macro_impact -= 10.0
    elif macro_spending == 2:
        macro_impact += 10.0
        
    score += macro_impact
    
    # Handle Technical indicators conflict
    tech_signal = technical_result['signal']
    rsi = technical_result['rsi']
    
    reasons = []
    if tech_signal == "Overbought" and score > 15:
        # Conflict: Bullish model but overbought technicals
        score = score * 0.5 # suppress bullishness
        decision = "WATCH"
        reasons.append(f"Although LSTM forecast is bullish (+{lstm_result['expected_move']:.1f}%) and news sentiment is positive, technical RSI of {rsi} indicates overbought territory. Resolving conflict in favor of technicals: recommend waiting for a consolidation.")
    elif tech_signal == "Oversold" and score < -15:
        # Conflict: Bearish model but oversold technicals
        score = score * 0.5 # suppress bearishness
        decision = "HOLD"
        reasons.append(f"LSTM points down but oversold RSI ({rsi}) suggests a near-term bounce. Recommending HOLD rather than selling at current lows.")
    elif score > 10:
        decision = "BUY"
        reasons.append(f"Bullish alignment: LSTM model forecasts an upward trend of +{lstm_result['expected_move']:.1f}%, supported by {sentiment_result['label'].lower()} news sentiment and favorable macro liquidity conditions.")
    elif score < -10:
        decision = "AVOID"
        reasons.append(f"Bearish alignment: High restrictive interest rates combined with negative news sentiment ({sentiment_result['label']}) and downward LSTM trajectory ({lstm_result['expected_move']:.1f}%) suggest caution.")
    else:
        decision = "HOLD"
        reasons.append("Signals are mixed or neutral: macroeconomic headwinds offset local positive news events. Recommending HOLD/neutral positioning.")

    # Nuances for NVDA/RKLB/PLTR
    if ticker.upper() == "NVDA" and "earnings" in headline.lower():
        reasons.append("Note: NVDA earnings in 2 weeks → high implied volatility → wait for post-earnings dip.")
        decision = "WATCH"
        score = score * 0.3
        
    predicted_move = score / 5.0
    reasoning_str = " ".join(reasons)
    
    return {
        "decision": decision,
        "reasoning": reasoning_str,
        "predicted_move": round(predicted_move, 2)
    }
