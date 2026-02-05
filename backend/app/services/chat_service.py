"""
AI Chat Service - OpenAI Integration
Handles chat conversations with customer context
Extracts customer preferences automatically
"""
from openai import AsyncOpenAI
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import json

from app.config import settings
from app.models.customer import GlobalCustomer, BranchCustomer
from app.models.preference import CustomerPreference


# System prompt for the restaurant assistant
SYSTEM_PROMPT = """ã‚ãªãŸã¯ã€Œç„¼è‚‰ãƒ¬ã‚¹ãƒˆãƒ©ãƒ³ã€ã®AIã‚¢ã‚·ã‚¹ã‚¿ãƒ³ãƒˆã§ã™ã€‚ä¸å¯§ã§æ¸©ã‹ã„æŽ¥å®¢ã‚’å¿ƒãŒã‘ã¦ãã ã•ã„ã€‚

## åº—èˆ—æƒ…å ±
- åº—å: ç„¼è‚‰ãƒ¬ã‚¹ãƒˆãƒ©ãƒ³ï¼ˆå¹³é–“æœ¬åº—ï¼‰
- ä½æ‰€: ã€’211-0013 ç¥žå¥ˆå·çœŒå·å´Žå¸‚ä¸­åŽŸåŒºä¸Šå¹³é–“
- é›»è©±: 044-789-8413
- å–¶æ¥­æ™‚é–“: 17:00 - 23:00ï¼ˆL.O. 22:30ï¼‰
- å®šä¼‘æ—¥: ç«æ›œæ—¥
- å¸­æ•°: 30å¸­ï¼ˆå€‹å®¤ã‚ã‚Šï¼‰

## ãƒ¡ãƒ‹ãƒ¥ãƒ¼ï¼ˆç¨Žè¾¼ä¾¡æ ¼ï¼‰
ã€æ¥µä¸Šå’Œç‰›ã€‘
- ç‰¹é¸é»’æ¯›å’Œç‰›ã‚«ãƒ«ãƒ“ Â¥2,800
- å’Œç‰›ä¸Šãƒãƒ©ãƒŸ Â¥1,800
- ç‰¹é¸ç››ã‚Šåˆã‚ã› Â¥4,500ã€œ

ã€ã‚¿ãƒ³ãƒ»èµ¤èº«ã€‘
- åŽšåˆ‡ã‚Šä¸Šã‚¿ãƒ³å¡© Â¥2,200
- ä¸Šã‚¿ãƒ³å¡© Â¥1,600
- ç‰›ãƒ’ãƒ¬ Â¥2,400

ã€ãƒ›ãƒ«ãƒ¢ãƒ³ã€‘
- ä¸ŠãƒŸãƒŽ Â¥980
- ã‚·ãƒžãƒãƒ§ã‚¦ Â¥880
- ãƒãƒ„ Â¥780
- ãƒ†ãƒƒãƒãƒ£ãƒ³ Â¥880

ã€ãã®ä»–ã€‘
- ãƒ“ãƒ“ãƒ³ãƒ Â¥980
- å†·éºº Â¥1,100
- å„ç¨®ã‚µãƒ©ãƒ€ Â¥580ã€œ

## ãƒ«ãƒ¼ãƒ«
1. æ—¥æœ¬èªžã§ä¸å¯§ã«å¿œç­”
2. çµµæ–‡å­—ã‚’é©åº¦ã«ä½¿ç”¨ï¼ˆðŸ¥©ðŸ–ðŸ”¥âœ¨ãªã©ï¼‰
3. äºˆç´„ã¯é›»è©±ã¾ãŸã¯ã‚¦ã‚§ãƒ–ã‚µã‚¤ãƒˆã‚’æ¡ˆå†…
4. ãƒ¬ãƒåˆºã—ãªã©ç”Ÿè‚‰ã®æä¾›ã¯æ³•å¾‹ä¸Šã§ããªã„ã“ã¨ã‚’èª¬æ˜Ž
5. ã‚¢ãƒ¬ãƒ«ã‚®ãƒ¼å¯¾å¿œå¯èƒ½ã ãŒã€è©³ç´°ã¯æ¥åº—æ™‚ã«ç¢ºèªã‚’æŽ¨å¥¨
6. è¨˜å¿µæ—¥ãƒ»æŽ¥å¾…ã®ç‰¹åˆ¥å¯¾å¿œå¯èƒ½
7. å›žç­”ã¯ç°¡æ½”ã«ï¼ˆ3-4æ–‡ä»¥å†…ï¼‰
8. ä¸æ˜Žãªè³ªå•ã¯é›»è©±ã§ã®å•ã„åˆã‚ã›ã‚’æ¡ˆå†…

## é¡§å®¢æƒ…å ±
{customer_context}
"""


class ChatService:
    """AI-powered chat service with customer context"""

    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def get_customer_context(
        self,
        db: AsyncSession,
        phone: Optional[str] = None,
        name: Optional[str] = None,
        branch_code: str = "hirama"
    ) -> str:
        """Build customer context string for the AI"""
        if not phone and not name:
            return "æ–°è¦ã®ãŠå®¢æ§˜ã§ã™ã€‚"

        # Try to find customer by phone first
        query = select(GlobalCustomer)
        if phone:
            query = query.where(GlobalCustomer.phone == phone)
        elif name:
            query = query.where(GlobalCustomer.name.ilike(f"%{name}%"))

        result = await db.execute(query)
        global_customer = result.scalar_one_or_none()

        if not global_customer:
            if name:
                return f"ãŠåå‰: {name}æ§˜ï¼ˆæ–°è¦ã®ãŠå®¢æ§˜ï¼‰"
            return "æ–°è¦ã®ãŠå®¢æ§˜ã§ã™ã€‚"

        # Get branch-specific data
        result = await db.execute(
            select(BranchCustomer)
            .options(selectinload(BranchCustomer.preferences))
            .where(
                BranchCustomer.global_customer_id == global_customer.id,
                BranchCustomer.branch_code == branch_code
            )
        )
        branch_customer = result.scalar_one_or_none()

        context_parts = [f"ãŠåå‰: {global_customer.name}æ§˜"]

        if branch_customer:
            context_parts.append(f"æ¥åº—å›žæ•°: {branch_customer.visit_count}å›ž")

            if branch_customer.is_vip:
                context_parts.append("VIPã®ãŠå®¢æ§˜ã§ã™ ðŸŒŸ")

            if branch_customer.preferences:
                prefs = [p.preference for p in branch_customer.preferences]
                context_parts.append(f"ãŠå¥½ã¿ã®éƒ¨ä½: {', '.join(prefs)}")

                # Add notes
                notes = [p.note for p in branch_customer.preferences if p.note]
                if notes:
                    context_parts.append(f"å‚™è€ƒ: {'; '.join(notes)}")

        return "\n".join(context_parts)

    async def chat(
        self,
        message: str,
        db: AsyncSession,
        phone: Optional[str] = None,
        customer_name: Optional[str] = None,
        branch_code: str = "hirama",
        conversation_history: Optional[List[dict]] = None
    ) -> str:
        """
        Process a chat message and return AI response.
        Falls back to keyword matching if OpenAI is not configured.
        """
        # Get customer context
        customer_context = await self.get_customer_context(
            db, phone, customer_name, branch_code
        )

        # If no OpenAI key, use fallback
        if not self.client:
            return self._fallback_response(message, customer_name)

        # Build messages for OpenAI
        system_message = SYSTEM_PROMPT.format(customer_context=customer_context)

        messages = [{"role": "system", "content": system_message}]

        # Add conversation history (last 10 messages)
        if conversation_history:
            for msg in conversation_history[-10:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        # Add current message
        messages.append({"role": "user", "content": message})

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                max_tokens=500,
                temperature=0.7,
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"OpenAI error: {e}")
            return self._fallback_response(message, customer_name)

    def _fallback_response(self, message: str, customer_name: Optional[str] = None) -> str:
        """Keyword-based fallback when OpenAI is unavailable"""
        lower = message.lower()

        responses = {
            'ãŠã™ã™ã‚': 'æœ¬æ—¥ã®ãŠã™ã™ã‚ã¯ï¼š\n\nðŸ¥‡ ç‰¹é¸é»’æ¯›å’Œç‰›ã‚«ãƒ«ãƒ“ Â¥2,800\nðŸ¥ˆ åŽšåˆ‡ã‚Šä¸Šã‚¿ãƒ³å¡© Â¥2,200\nðŸ¥‰ å’Œç‰›ä¸Šãƒãƒ©ãƒŸ Â¥1,800\n\nã©ã‚Œã‚‚æ–°é®®ã§çµ¶å“ã§ã™ï¼',
            'ãƒ¬ãƒåˆºã—': 'ç”³ã—è¨³ã”ã–ã„ã¾ã›ã‚“ãŒã€ç¾åœ¨ãƒ¬ãƒåˆºã—ã¯æ³•å¾‹ã«ã‚ˆã‚Šæä¾›ã§ãã¾ã›ã‚“ã€‚ä»£ã‚ã‚Šã«ä½Žæ¸©èª¿ç†ã®ãƒ¬ãƒãƒ¼ã¯ã„ã‹ãŒã§ã™ã‹ï¼Ÿ',
            'ã‚¢ãƒ¬ãƒ«ã‚®ãƒ¼': 'ã‚¢ãƒ¬ãƒ«ã‚®ãƒ¼å¯¾å¿œå¯èƒ½ã§ã™ã€‚ã”æ¥åº—æ™‚ã«ã‚¹ã‚¿ãƒƒãƒ•ã«ãŠç”³ã—ä»˜ã‘ãã ã•ã„ã€‚è©³ç´°ã¯ãŠé›»è©±ï¼ˆ044-789-8413ï¼‰ã§ã‚‚ã”ç›¸è«‡ã„ãŸã ã‘ã¾ã™ã€‚',
            'è¨˜å¿µæ—¥': 'è¨˜å¿µæ—¥ã®ã”äºˆå®šã§ã™ã­ï¼ðŸŽ‰ ç‰¹åˆ¥ãƒ‡ã‚¶ãƒ¼ãƒˆãƒ—ãƒ¬ãƒ¼ãƒˆãƒ»ãŠèŠ±ã®ã”ç”¨æ„ãƒ»å€‹å®¤ã®ã”äºˆç´„ãªã©æ‰¿ã‚Šã¾ã™ã€‚',
            'äºˆç´„': 'ã”äºˆç´„ã¯ã“ã®ãƒšãƒ¼ã‚¸ã®ã€Œã”äºˆç´„ã€ã‚»ã‚¯ã‚·ãƒ§ãƒ³ã‹ã‚‰ã€ã¾ãŸã¯ãŠé›»è©±ï¼ˆ044-789-8413ï¼‰ã§æ‰¿ã£ã¦ãŠã‚Šã¾ã™ã€‚',
            'å–¶æ¥­': 'å–¶æ¥­æ™‚é–“: 17:00 - 23:00ï¼ˆL.O. 22:30ï¼‰\nå®šä¼‘æ—¥: ç«æ›œæ—¥\n\nçš†æ§˜ã®ã”æ¥åº—ã‚’ãŠå¾…ã¡ã—ã¦ãŠã‚Šã¾ã™ï¼',
            'ãƒ›ãƒ«ãƒ¢ãƒ³': 'ãƒ›ãƒ«ãƒ¢ãƒ³ãƒ¡ãƒ‹ãƒ¥ãƒ¼ï¼š\nãƒ»ä¸ŠãƒŸãƒŽ Â¥980\nãƒ»ã‚·ãƒžãƒãƒ§ã‚¦ Â¥880\nãƒ»ãƒãƒ„ Â¥780\n\næ–°é®®ãªãƒ›ãƒ«ãƒ¢ãƒ³ã‚’ã”ç”¨æ„ã—ã¦ãŠã‚Šã¾ã™ï¼',
            'ã‚¿ãƒ³': 'åŽšåˆ‡ã‚Šä¸Šã‚¿ãƒ³å¡©ï¼ˆÂ¥2,200ï¼‰ãŒå¤§äººæ°—ã§ã™ï¼ðŸ”¥ æ­¯ã”ãŸãˆã¨è‚‰æ±ãŒæº¢ã‚Œã‚‹é€¸å“ã§ã™ã€‚',
            'ã‚«ãƒ«ãƒ“': 'ç‰¹é¸é»’æ¯›å’Œç‰›ã‚«ãƒ«ãƒ“ï¼ˆÂ¥2,800ï¼‰ã¯å£ã®ä¸­ã§ã¨ã‚ã‘ã‚‹ç¾Žå‘³ã—ã•ã§ã™ï¼âœ¨',
            'å€‹å®¤': 'å€‹å®¤ã¯4åæ§˜ã€œã”åˆ©ç”¨ã„ãŸã ã‘ã¾ã™ã€‚æŽ¥å¾…ã‚„ã”å®¶æ—ã§ã®ãŠé£Ÿäº‹ã«æœ€é©ã§ã™ã€‚ã”äºˆç´„æ™‚ã«ãŠç”³ã—ä»˜ã‘ãã ã•ã„ã€‚',
            'ã‚³ãƒ¼ã‚¹': 'ã‚³ãƒ¼ã‚¹æ–™ç†ã¯Â¥5,000ã€œã”ç”¨æ„ã—ã¦ãŠã‚Šã¾ã™ã€‚è©³ç´°ã¯ãŠé›»è©±ã«ã¦ãŠå•ã„åˆã‚ã›ãã ã•ã„ã€‚',
        }

        for keyword, response in responses.items():
            if keyword in lower:
                return response

        # Default response
        greeting = f"{customer_name}æ§˜ã€" if customer_name else ""
        return f'{greeting}ã‚ã‚ŠãŒã¨ã†ã”ã–ã„ã¾ã™ï¼ã”è³ªå•ã‚’æ‰¿ã‚Šã¾ã—ãŸã€‚\n\nè©³ã—ãã¯ãŠé›»è©±ï¼ˆ044-789-8413ï¼‰ã§ãŠå•ã„åˆã‚ã›ãã ã•ã„ã€‚'


# Singleton instance
chat_service = ChatService()


# ============================================
# INSIGHT EXTRACTION PROMPT
# ============================================
EXTRACTION_PROMPT = """ä¼šè©±ã‹ã‚‰ãŠå®¢æ§˜ã®å¥½ã¿ã‚„é‡è¦ãªæƒ…å ±ã‚’æŠ½å‡ºã—ã¦ãã ã•ã„ã€‚

æŠ½å‡ºã™ã‚‹ã‚«ãƒ†ã‚´ãƒª:
- meat: ãŠè‚‰ã®å¥½ã¿ï¼ˆä¾‹: ã‚¿ãƒ³å¥½ãã€ãƒãƒ©ãƒŸãŒå¥½ãã€åŽšåˆ‡ã‚Šæ´¾ï¼‰
- cooking: èª¿ç†æ³•ã®å¥½ã¿ï¼ˆä¾‹: ãƒ¬ã‚¢æ´¾ã€ã‚ˆãç„¼ãã€å¡©æ´¾ã€ã‚¿ãƒ¬æ´¾ï¼‰
- allergy: ã‚¢ãƒ¬ãƒ«ã‚®ãƒ¼ã‚„é£Ÿäº‹åˆ¶é™ï¼ˆä¾‹: ç”²æ®»é¡žã‚¢ãƒ¬ãƒ«ã‚®ãƒ¼ã€ãƒ™ã‚¸ã‚¿ãƒªã‚¢ãƒ³ï¼‰
- occasion: åˆ©ç”¨ã‚·ãƒ¼ãƒ³ï¼ˆä¾‹: è¨˜å¿µæ—¥ã€æŽ¥å¾…ã€å®¶æ—é€£ã‚Œï¼‰
- other: ãã®ä»–ã®é‡è¦æƒ…å ±ï¼ˆä¾‹: å€‹å®¤å¸Œæœ›ã€å­ä¾›é€£ã‚Œï¼‰

ä¼šè©±å†…å®¹:
{conversation}

JSONã§å›žç­”ã—ã¦ãã ã•ã„ã€‚è©²å½“ãŒãªã‘ã‚Œã°ç©ºé…åˆ—ã‚’è¿”ã—ã¦ãã ã•ã„:
{
  "insights": [
    {"preference": "æŠ½å‡ºã—ãŸå¥½ã¿", "category": "ã‚«ãƒ†ã‚´ãƒª", "confidence": 0.0-1.0}
  ]
}
"""


class InsightExtractor:
    """Extract customer preferences from chat conversations"""

    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def extract_insights(
        self,
        messages: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """
        Extract customer insights from conversation.
        Returns list of {preference, category, confidence}
        """
        if not self.client or not messages:
            return self._fallback_extract(messages)

        # Build conversation text
        conversation = "\n".join([
            f"{'ãŠå®¢æ§˜' if m.get('role') == 'user' else 'ã‚¹ã‚¿ãƒƒãƒ•'}: {m.get('content', '')}"
            for m in messages[-10:]
        ])

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "ã‚ãªãŸã¯é¡§å®¢åˆ†æžAIã§ã™ã€‚ä¼šè©±ã‹ã‚‰é¡§å®¢ã®å¥½ã¿ã‚’æŠ½å‡ºã—ã¦JSONå½¢å¼ã§è¿”ã—ã¦ãã ã•ã„ã€‚"},
                    {"role": "user", "content": EXTRACTION_PROMPT.format(conversation=conversation)}
                ],
                max_tokens=500,
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            # Clean up potential whitespace issues
            content = content.strip()
            result = json.loads(content)
            return result.get("insights", [])

        except Exception as e:
            print(f"Insight extraction error: {e}")
            return self._fallback_extract(messages)

    def _fallback_extract(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Keyword-based fallback extraction"""
        insights = []

        # Keywords to detect
        keywords = {
            # Meat preferences
            'ã‚¿ãƒ³': ('ã‚¿ãƒ³å¥½ã', 'meat'),
            'ãƒãƒ©ãƒŸ': ('ãƒãƒ©ãƒŸå¥½ã', 'meat'),
            'ã‚«ãƒ«ãƒ“': ('ã‚«ãƒ«ãƒ“å¥½ã', 'meat'),
            'ãƒ›ãƒ«ãƒ¢ãƒ³': ('ãƒ›ãƒ«ãƒ¢ãƒ³å¥½ã', 'meat'),
            'ãƒŸãƒŽ': ('ãƒŸãƒŽå¥½ã', 'meat'),
            'èµ¤èº«': ('èµ¤èº«æ´¾', 'meat'),
            'åŽšåˆ‡ã‚Š': ('åŽšåˆ‡ã‚Šæ´¾', 'meat'),
            # Cooking preferences
            'ãƒ¬ã‚¢': ('ãƒ¬ã‚¢æ´¾', 'cooking'),
            'ã‚¦ã‚§ãƒ«ãƒ€ãƒ³': ('ã‚ˆãç„¼ãæ´¾', 'cooking'),
            'å¡©': ('å¡©æ´¾', 'cooking'),
            'ã‚¿ãƒ¬': ('ã‚¿ãƒ¬æ´¾', 'cooking'),
            'è¾›ã„': ('è¾›ã„ã‚‚ã®å¥½ã', 'cooking'),
            # Allergies
            'ã‚¢ãƒ¬ãƒ«ã‚®ãƒ¼': ('ã‚¢ãƒ¬ãƒ«ã‚®ãƒ¼ã‚ã‚Šè¦ç¢ºèª', 'allergy'),
            'ãƒ™ã‚¸ã‚¿ãƒªã‚¢ãƒ³': ('ãƒ™ã‚¸ã‚¿ãƒªã‚¢ãƒ³', 'allergy'),
            # Occasions
            'è¨˜å¿µæ—¥': ('è¨˜å¿µæ—¥åˆ©ç”¨', 'occasion'),
            'èª•ç”Ÿæ—¥': ('èª•ç”Ÿæ—¥åˆ©ç”¨', 'occasion'),
            'æŽ¥å¾…': ('æŽ¥å¾…åˆ©ç”¨', 'occasion'),
            'ãƒ‡ãƒ¼ãƒˆ': ('ãƒ‡ãƒ¼ãƒˆåˆ©ç”¨', 'occasion'),
            'å®¶æ—': ('å®¶æ—é€£ã‚Œ', 'occasion'),
            # Other
            'å€‹å®¤': ('å€‹å®¤å¸Œæœ›', 'other'),
            'å­ä¾›': ('å­ä¾›é€£ã‚Œ', 'other'),
        }

        # Check all user messages
        for msg in messages:
            if msg.get('role') != 'user':
                continue
            content = msg.get('content', '')

            for keyword, (preference, category) in keywords.items():
                if keyword in content:
                    # Avoid duplicates
                    if not any(i['preference'] == preference for i in insights):
                        insights.append({
                            'preference': preference,
                            'category': category,
                            'confidence': 0.7
                        })

        return insights

    async def save_insights(
        self,
        db: AsyncSession,
        branch_customer_id: str,
        insights: List[Dict[str, Any]],
    ) -> int:
        """Save extracted insights to database. Returns count of new insights."""
        if not insights or not branch_customer_id:
            return 0

        # Get existing preferences
        result = await db.execute(
            select(CustomerPreference.preference)
            .where(CustomerPreference.branch_customer_id == branch_customer_id)
        )
        existing = {row[0] for row in result.fetchall()}

        new_count = 0
        for insight in insights:
            pref_text = insight.get('preference', '')
            if not pref_text or pref_text in existing:
                continue

            new_pref = CustomerPreference(
                branch_customer_id=branch_customer_id,
                preference=pref_text,
                category=insight.get('category', 'other'),
                confidence=insight.get('confidence', 0.8),
                source='chat',
                note='AI extracted from chat'
            )
            db.add(new_pref)
            existing.add(pref_text)
            new_count += 1

        if new_count > 0:
            await db.commit()

        return new_count


# Singleton instance
insight_extractor = InsightExtractor()
