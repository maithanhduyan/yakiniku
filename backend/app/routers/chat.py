"""
Chat Router - AI-powered customer chat with automatic insight extraction
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional

from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import chat_service, insight_extractor
from app.models.customer import BranchCustomer, GlobalCustomer

router = APIRouter()


async def get_branch_customer_id(
    db: AsyncSession,
    phone: Optional[str],
    branch_code: str = "hirama"
) -> Optional[str]:
    """Get branch_customer_id from phone number"""
    if not phone:
        return None

    # Get global customer by phone
    result = await db.execute(
        select(GlobalCustomer).where(GlobalCustomer.phone == phone)
    )
    global_customer = result.scalar_one_or_none()
    if not global_customer:
        return None

    # Get branch customer for this global customer and branch
    result = await db.execute(
        select(BranchCustomer)
        .where(BranchCustomer.global_customer_id == global_customer.id)
        .where(BranchCustomer.branch_code == branch_code)
    )
    bc = result.scalar_one_or_none()
    return bc.id if bc else None


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Process a chat message and return AI response.

    - Uses OpenAI GPT for intelligent responses
    - Falls back to keyword matching if OpenAI unavailable
    - Includes customer context for personalized responses
    - Extracts customer preferences automatically
    """
    # Convert conversation history to dict format
    history = None
    if request.conversation_history:
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]

    # Get AI response
    response_text = await chat_service.chat(
        message=request.message,
        db=db,
        phone=request.customer_phone,
        customer_name=request.customer_name,
        branch_code=request.branch_code,
        conversation_history=history,
    )

    # Check if customer was recognized
    customer_recognized = False
    insights_extracted = 0

    if request.customer_phone or request.customer_name:
        customer_recognized = True

        # Extract insights from conversation (including current message)
        if request.customer_phone:
            try:
                # Build full conversation for extraction
                messages_for_extraction = history or []
                messages_for_extraction.append({
                    "role": "user",
                    "content": request.message
                })

                # Extract insights
                insights = await insight_extractor.extract_insights(
                    messages=messages_for_extraction
                )

                # Save if customer exists
                if insights:
                    branch_customer_id = await get_branch_customer_id(
                        db=db,
                        phone=request.customer_phone,
                        branch_code=request.branch_code or "hirama"
                    )

                    if branch_customer_id:
                        insights_extracted = await insight_extractor.save_insights(
                            db=db,
                            branch_customer_id=branch_customer_id,
                            insights=insights
                        )

            except Exception as e:
                print(f"Insight extraction failed: {e}")

    return ChatResponse(
        response=response_text,
        customer_recognized=customer_recognized,
        customer_name=request.customer_name,
        insights_extracted=insights_extracted,
    )


@router.get("/health")
async def chat_health():
    """Check if chat service is available"""
    has_openai = chat_service.client is not None
    return {
        "status": "healthy",
        "openai_configured": has_openai,
        "fallback_available": True,
    }

