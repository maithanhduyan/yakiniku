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
SYSTEM_PROMPT = """あなたは「焼肉ジナン」のAIアシスタントです。丁寧で温かい接客を心がけてください。

## 店舗情報
- 店名: 焼肉ジナン（平間本店）
- 住所: 〒211-0013 神奈川県川崎市中原区上平間
- 電話: 044-789-8413
- 営業時間: 17:00 - 23:00（L.O. 22:30）
- 定休日: 火曜日
- 席数: 30席（個室あり）

## メニュー（税込価格）
【極上和牛】
- 特選黒毛和牛カルビ ¥2,800
- 和牛上ハラミ ¥1,800
- 特選盛り合わせ ¥4,500〜

【タン・赤身】
- 厚切り上タン塩 ¥2,200
- 上タン塩 ¥1,600
- 牛ヒレ ¥2,400

【ホルモン】
- 上ミノ ¥980
- シマチョウ ¥880
- ハツ ¥780
- テッチャン ¥880

【その他】
- ビビンバ ¥980
- 冷麺 ¥1,100
- 各種サラダ ¥580〜

## ルール
1. 日本語で丁寧に応答
2. 絵文字を適度に使用（🥩🍖🔥✨など）
3. 予約は電話またはウェブサイトを案内
4. レバ刺しなど生肉の提供は法律上できないことを説明
5. アレルギー対応可能だが、詳細は来店時に確認を推奨
6. 記念日・接待の特別対応可能
7. 回答は簡潔に（3-4文以内）
8. 不明な質問は電話での問い合わせを案内

## 顧客情報
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
        branch_code: str = "jinan"
    ) -> str:
        """Build customer context string for the AI"""
        if not phone and not name:
            return "新規のお客様です。"

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
                return f"お名前: {name}様（新規のお客様）"
            return "新規のお客様です。"

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

        context_parts = [f"お名前: {global_customer.name}様"]

        if branch_customer:
            context_parts.append(f"来店回数: {branch_customer.visit_count}回")

            if branch_customer.is_vip:
                context_parts.append("VIPのお客様です 🌟")

            if branch_customer.preferences:
                prefs = [p.preference for p in branch_customer.preferences]
                context_parts.append(f"お好みの部位: {', '.join(prefs)}")

                # Add notes
                notes = [p.note for p in branch_customer.preferences if p.note]
                if notes:
                    context_parts.append(f"備考: {'; '.join(notes)}")

        return "\n".join(context_parts)

    async def chat(
        self,
        message: str,
        db: AsyncSession,
        phone: Optional[str] = None,
        customer_name: Optional[str] = None,
        branch_code: str = "jinan",
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
            'おすすめ': '本日のおすすめは：\n\n🥇 特選黒毛和牛カルビ ¥2,800\n🥈 厚切り上タン塩 ¥2,200\n🥉 和牛上ハラミ ¥1,800\n\nどれも新鮮で絶品です！',
            'レバ刺し': '申し訳ございませんが、現在レバ刺しは法律により提供できません。代わりに低温調理のレバーはいかがですか？',
            'アレルギー': 'アレルギー対応可能です。ご来店時にスタッフにお申し付けください。詳細はお電話（044-789-8413）でもご相談いただけます。',
            '記念日': '記念日のご予定ですね！🎉 特別デザートプレート・お花のご用意・個室のご予約など承ります。',
            '予約': 'ご予約はこのページの「ご予約」セクションから、またはお電話（044-789-8413）で承っております。',
            '営業': '営業時間: 17:00 - 23:00（L.O. 22:30）\n定休日: 火曜日\n\n皆様のご来店をお待ちしております！',
            'ホルモン': 'ホルモンメニュー：\n・上ミノ ¥980\n・シマチョウ ¥880\n・ハツ ¥780\n\n新鮮なホルモンをご用意しております！',
            'タン': '厚切り上タン塩（¥2,200）が大人気です！🔥 歯ごたえと肉汁が溢れる逸品です。',
            'カルビ': '特選黒毛和牛カルビ（¥2,800）は口の中でとろける美味しさです！✨',
            '個室': '個室は4名様〜ご利用いただけます。接待やご家族でのお食事に最適です。ご予約時にお申し付けください。',
            'コース': 'コース料理は¥5,000〜ご用意しております。詳細はお電話にてお問い合わせください。',
        }

        for keyword, response in responses.items():
            if keyword in lower:
                return response

        # Default response
        greeting = f"{customer_name}様、" if customer_name else ""
        return f'{greeting}ありがとうございます！ご質問を承りました。\n\n詳しくはお電話（044-789-8413）でお問い合わせください。'


# Singleton instance
chat_service = ChatService()


# ============================================
# INSIGHT EXTRACTION PROMPT
# ============================================
EXTRACTION_PROMPT = """会話からお客様の好みや重要な情報を抽出してください。

抽出するカテゴリ:
- meat: お肉の好み（例: タン好き、ハラミが好き、厚切り派）
- cooking: 調理法の好み（例: レア派、よく焼き、塩派、タレ派）
- allergy: アレルギーや食事制限（例: 甲殻類アレルギー、ベジタリアン）
- occasion: 利用シーン（例: 記念日、接待、家族連れ）
- other: その他の重要情報（例: 個室希望、子供連れ）

会話内容:
{conversation}

JSONで回答してください。該当がなければ空配列を返してください:
{
  "insights": [
    {"preference": "抽出した好み", "category": "カテゴリ", "confidence": 0.0-1.0}
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
            f"{'お客様' if m.get('role') == 'user' else 'スタッフ'}: {m.get('content', '')}"
            for m in messages[-10:]
        ])

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "あなたは顧客分析AIです。会話から顧客の好みを抽出してJSON形式で返してください。"},
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
            'タン': ('タン好き', 'meat'),
            'ハラミ': ('ハラミ好き', 'meat'),
            'カルビ': ('カルビ好き', 'meat'),
            'ホルモン': ('ホルモン好き', 'meat'),
            'ミノ': ('ミノ好き', 'meat'),
            '赤身': ('赤身派', 'meat'),
            '厚切り': ('厚切り派', 'meat'),
            # Cooking preferences
            'レア': ('レア派', 'cooking'),
            'ウェルダン': ('よく焼き派', 'cooking'),
            '塩': ('塩派', 'cooking'),
            'タレ': ('タレ派', 'cooking'),
            '辛い': ('辛いもの好き', 'cooking'),
            # Allergies
            'アレルギー': ('アレルギーあり要確認', 'allergy'),
            'ベジタリアン': ('ベジタリアン', 'allergy'),
            # Occasions
            '記念日': ('記念日利用', 'occasion'),
            '誕生日': ('誕生日利用', 'occasion'),
            '接待': ('接待利用', 'occasion'),
            'デート': ('デート利用', 'occasion'),
            '家族': ('家族連れ', 'occasion'),
            # Other
            '個室': ('個室希望', 'other'),
            '子供': ('子供連れ', 'other'),
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
