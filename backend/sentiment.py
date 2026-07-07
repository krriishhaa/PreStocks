import os
import torch

# Global model pointers for lazy loading
_tokenizer = None
_model = None
_is_finbert_loaded = False

def load_finbert():
    global _tokenizer, _model, _is_finbert_loaded
    if _is_finbert_loaded:
        return True
    
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        print("Initializing FinBERT model (ProsusAI/finbert)...")
        # Load tokenizer and model
        _tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        _model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
        _is_finbert_loaded = True
        print("FinBERT model loaded successfully.")
        return True
    except Exception as e:
        print(f"Failed to load FinBERT model: {e}. Falling back to rule-based lexicon sentiment.")
        _is_finbert_loaded = False
        return False

def get_sentiment_score(text: str) -> dict:
    """
    Scoring input text.
    Returns:
        {
            "positive": float,
            "neutral": float,
            "negative": float,
            "score": float (from -100 to 100),
            "label": str ("Bullish", "Bearish", "Neutral"),
            "source": str ("FinBERT" or "Lexicon Fallback")
        }
    """
    # Try loading FinBERT
    if load_finbert():
        try:
            inputs = _tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
            with torch.no_grad():
                outputs = _model(**inputs)
            
            # Apply softmax to get probabilities
            probs = torch.softmax(outputs.logits, dim=1)[0].tolist()
            positive, negative, neutral = probs[0], probs[1], probs[2]
            
            # FinBERT labels order: positive, negative, neutral
            # Calculate a net sentiment score from -100 to 100
            score = (positive - negative) * 100
            
            if score > 15:
                label = "Bullish"
            elif score < -15:
                label = "Bearish"
            else:
                label = "Neutral"
                
            return {
                "positive": round(positive, 3),
                "negative": round(negative, 3),
                "neutral": round(neutral, 3),
                "score": round(score, 1),
                "label": label,
                "source": "FinBERT"
            }
        except Exception as e:
            print(f"Error during FinBERT inference: {e}. Using Lexicon fallback.")
            
    # Lexicon Fallback (VADER-lite rules-based)
    text_lower = text.lower()
    
    # Financial Sentiment Words
    bull_words = [
        "breakthrough", "cut", "cools", "growth", "surges", "deal", "rises", "success", 
        "innovate", "approval", "merger", "earnings beat", "upgrade", "outperform", 
        "profit", "positive", "strong", "gains", "partnership", "expansion"
    ]
    bear_words = [
        "tariffs", "wars", "ban", "breakdown", "crisis", "hike", "strict", "inflation", 
        "drop", "fines", "limits", "shortage", "misses", "downgrade", "underperform", 
        "loss", "negative", "weak", "slump", "lawsuit", "disrupt", "layoffs"
    ]
    
    bull_count = sum(1 for w in bull_words if w in text_lower)
    bear_count = sum(1 for w in bear_words if w in text_lower)
    
    total = bull_count + bear_count
    if total == 0:
        pos, neg, neu = 0.1, 0.1, 0.8
        score = 0.0
        label = "Neutral"
    else:
        pos = bull_count / total
        neg = bear_count / total
        neu = 0.0
        
        # Soften edges
        pos = pos * 0.9 + 0.05
        neg = neg * 0.9 + 0.05
        neu = 0.1
        score = (pos - neg) * 100
        
        if score > 10:
            label = "Bullish"
        elif score < -10:
            label = "Bearish"
        else:
            label = "Neutral"
            
    return {
        "positive": round(pos, 3),
        "negative": round(neg, 3),
        "neutral": round(neu, 3),
        "score": round(score, 1),
        "label": label,
        "source": "Lexicon Fallback"
    }
