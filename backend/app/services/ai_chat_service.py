"""
AI Chat Service — Conversational interface for research and portfolio questions.
Maintains conversation history, routes to appropriate engines.
"""

from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import uuid
import time

from app.models.ai import AIConversation, AIMessage, AIPromptTemplate
from app.schemas.ai import AIChatResponse


class AIChatService:
    def __init__(self, db: Session):
        self.db = db

    def process_message(
        self,
        user_id: int,
        message: str,
        conversation_id: Optional[str] = None,
        company_id: Optional[int] = None,
        context_type: str = "general"
    ) -> AIChatResponse:
        start = time.time()

        conversation = self._get_or_create_conversation(
            user_id, conversation_id, company_id, context_type
        )

        user_msg = AIMessage(
            conversation_id=conversation.id,
            role="user",
            content=message,
            model_used=None
        )
        self.db.add(user_msg)

        response_text = self._generate_response(message, conversation, context_type, company_id)

        latency = int((time.time() - start) * 1000)

        assistant_msg = AIMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=response_text,
            model_used="prestocks-ai-v1",
            tokens_input=len(message.split()) * 2,
            tokens_output=len(response_text.split()) * 2,
            latency_ms=latency
        )
        self.db.add(assistant_msg)

        conversation.updated_at = datetime.utcnow()
        self.db.commit()

        return AIChatResponse(
            conversation_id=str(conversation.id),
            message=response_text,
            model_used="prestocks-ai-v1",
            tokens_used=(assistant_msg.tokens_input or 0) + (assistant_msg.tokens_output or 0),
            latency_ms=latency,
            sources=[]
        )

    def _get_or_create_conversation(self, user_id, conversation_id, company_id, context_type):
        if conversation_id:
            conv = self.db.query(AIConversation).filter(
                AIConversation.id == conversation_id,
                AIConversation.user_id == user_id
            ).first()
            if conv:
                return conv

        conv = AIConversation(
            id=uuid.uuid4(),
            user_id=user_id,
            company_id=company_id,
            context_type=context_type,
            title=f"Chat - {datetime.utcnow().strftime('%b %d, %H:%M')}"
        )
        self.db.add(conv)
        self.db.flush()
        return conv

    def _generate_response(self, message: str, conversation, context_type: str, company_id: Optional[int]) -> str:
        """
        Route to appropriate response generation based on context.
        In production, this calls Claude API. For now, uses intelligent templates.
        """
        msg_lower = message.lower()

        if any(word in msg_lower for word in ["analyze", "research", "tell me about", "what is"]):
            return self._research_response(message, company_id)
        elif any(word in msg_lower for word in ["portfolio", "diversif", "rebalance", "holdings"]):
            return self._portfolio_response(message)
        elif any(word in msg_lower for word in ["risk", "flag", "danger", "warning"]):
            return self._risk_response(message, company_id)
        elif any(word in msg_lower for word in ["buy", "sell", "trade", "invest"]):
            return self._trade_response(message)
        else:
            return self._general_response(message)

    def _research_response(self, message: str, company_id: Optional[int]) -> str:
        if company_id:
            from app.models.company import Company
            company = self.db.query(Company).filter(Company.id == company_id).first()
            if company:
                return (
                    f"Here's what I know about {company.name}:\n\n"
                    f"**Company:** {company.name} ({company.ticker or 'Private'})\n"
                    f"**Industry:** {company.industry or 'N/A'}\n"
                    f"**Type:** {company.company_type}\n\n"
                    f"For a full analysis including risks, opportunities, financial health, "
                    f"funding history, and competitor mapping, use the Research endpoint "
                    f"(`POST /ai/research`) with this company's ID.\n\n"
                    f"Would you like me to explain any specific aspect — risks, financials, "
                    f"or competitive positioning?"
                )
        return (
            "I can help you research any company. To get started:\n\n"
            "1. **Search** for a company using the search endpoint\n"
            "2. **Request a full analysis** — I'll evaluate risks, opportunities, "
            "financials, funding, competitors, and IPO probability\n"
            "3. **Ask follow-up questions** about any aspect\n\n"
            "What company would you like to analyze?"
        )

    def _portfolio_response(self, message: str) -> str:
        return (
            "I can analyze your portfolio's health across several dimensions:\n\n"
            "• **Diversification Score** — How well-spread your positions are\n"
            "• **Concentration Risk** — Whether any single position is too large\n"
            "• **Missing Sectors** — Gaps in your sector exposure\n"
            "• **Rebalancing Suggestions** — Specific actions to improve\n\n"
            "Use `POST /ai/portfolio-advice` for a full weekly review, "
            "or ask me specific questions about your holdings."
        )

    def _risk_response(self, message: str, company_id: Optional[int]) -> str:
        return (
            "PreStocks tracks 8 types of risk flags for every company:\n\n"
            "1. **Volatility** — Price swings vs sector median\n"
            "2. **Valuation** — P/E and P/S percentile in historical range\n"
            "3. **Financial Leverage** — Debt-to-equity and interest coverage\n"
            "4. **Insider Activity** — Unusual selling patterns\n"
            "5. **Momentum** — Trend exhaustion signals\n"
            "6. **Sentiment** — News and social sentiment analysis\n"
            "7. **Concentration** — Portfolio overweight in single position\n"
            "8. **Liquidity** — Volume and spread concerns\n\n"
            "Each flag has a severity score (0-100) and plain-English explanation. "
            "Would you like me to explain a specific flag?"
        )

    def _trade_response(self, message: str) -> str:
        return (
            "Before making any trade, I recommend:\n\n"
            "1. **Check risk flags** — Review all active warnings for the stock\n"
            "2. **Understand position size** — Will this trade make any single "
            "position >25% of your portfolio?\n"
            "3. **Consider your learning tier** — Make sure you've completed "
            "the relevant learning modules\n\n"
            "Remember: This is paper trading for education. The goal is to "
            "build good habits, not maximize returns.\n\n"
            "What stock are you considering?"
        )

    def _general_response(self, message: str) -> str:
        return (
            "I'm PreStocks AI — your research and portfolio analysis assistant. "
            "I can help you with:\n\n"
            "• **Company Research** — \"Analyze Stripe\" or \"Tell me about NVDA\"\n"
            "• **Portfolio Health** — \"How diversified am I?\" or \"Rebalance suggestions\"\n"
            "• **Risk Explanation** — \"What does the volatility flag mean?\"\n"
            "• **Trading Guidance** — \"Should I buy more AAPL?\" (education, not advice)\n"
            "• **Learning** — \"Explain P/E ratio\" or \"What's market cap?\"\n\n"
            "What would you like to explore?"
        )
