"""
교회 데이터 기반 스마트 AI 어시스턴트 API 엔드포인트
"""

import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.models.church import Church
from app.services.smart_assistant_service import smart_assistant_service
from app.schemas.smart_assistant import (
    SmartAssistantQuery,
    SmartAssistantResponse,
    QueryAnalysisResponse
)
from app.core.security import decrypt_data
import json

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/query", response_model=SmartAssistantResponse)
async def process_smart_query(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    query: SmartAssistantQuery
):
    """
    교회 데이터를 활용한 스마트 AI 어시스턴트 질의 처리
    
    사용자의 자연어 질문을 분석하여 관련 교회 데이터를 조회하고,
    컨텍스트에 맞는 AI 응답을 생성합니다.
    
    예시:
    - "오늘 심방 일정 알려줘"
    - "이번주 기도제목 뭐가 있어?"
    - "최근 공지사항 정리해줘"
    """
    try:
        logger.info(f"Smart assistant query from user {current_user.id}: {query.message}")
        
        # 교회 정보 및 GPT 설정 조회
        church = db.query(Church).filter(Church.id == current_user.church_id).first()
        if not church:
            raise HTTPException(status_code=404, detail="Church not found")
        
        # GPT 설정 구성
        gpt_config = {
            "model": query.model or church.gpt_model or "gpt-4o-mini",
            "max_tokens": query.max_tokens or church.max_tokens or 2000,
            "temperature": query.temperature or church.temperature or 0.3
        }
        
        # GPT API 키 설정
        api_key = None
        if church.gpt_api_key:
            try:
                api_key = decrypt_data(church.gpt_api_key)
                smart_assistant_service.openai_service = smart_assistant_service.openai_service.__class__(api_key=api_key)
            except Exception as e:
                logger.error(f"Failed to decrypt GPT API key: {e}")
                raise HTTPException(status_code=500, detail="GPT API 키 설정에 문제가 있습니다.")
        
        # 스마트 어시스턴트 쿼리 처리
        result = await smart_assistant_service.process_query(
            user_message=query.message,
            church_id=current_user.church_id,
            user_id=current_user.id,
            db=db,
            gpt_config=gpt_config
        )
        
        # 토큰 사용량 업데이트 (백그라운드)
        if result.get("tokens_used", 0) > 0:
            try:
                church.current_month_tokens = (church.current_month_tokens or 0) + result["tokens_used"]
                cost = smart_assistant_service.openai_service.calculate_cost(
                    result["tokens_used"], 
                    result.get("model", gpt_config["model"])
                )
                church.current_month_cost = (church.current_month_cost or 0) + cost
                db.commit()
            except Exception as e:
                logger.error(f"Failed to update token usage: {e}")
        
        return SmartAssistantResponse(
            response=result["response"],
            query_type=result.get("query_type", "general"),
            data_sources=result.get("data_sources", []),
            tokens_used=result.get("tokens_used", 0),
            model=result.get("model", gpt_config["model"]),
            success=True,
            error_message=result.get("error")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Smart assistant error: {e}")
        return SmartAssistantResponse(
            response="죄송합니다. 질문을 처리하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
            query_type="error",
            data_sources=[],
            tokens_used=0,
            model=gpt_config.get("model", "gpt-4o-mini"),
            success=False,
            error_message=str(e)
        )


@router.post("/analyze", response_model=QueryAnalysisResponse)
async def analyze_query_intent(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    query: SmartAssistantQuery
):
    """
    사용자 질문의 의도를 분석합니다.
    
    실제 AI 응답을 생성하지 않고, 질문 분석 결과만 확인할 때 사용합니다.
    개발 및 디버깅 목적으로도 활용 가능합니다.
    """
    try:
        analysis = smart_assistant_service._analyze_query_intent(query.message)
        
        return QueryAnalysisResponse(
            primary_intent=analysis["primary_intent"],
            secondary_intents=analysis["secondary_intents"],
            time_context=analysis["time_context"],
            confidence=analysis["confidence"],
            detected_keywords=analysis.get("detected_keywords", []),
            suggested_data_sources=smart_assistant_service._get_suggested_data_sources(analysis)
        )
        
    except Exception as e:
        logger.error(f"Query analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"분석 중 오류가 발생했습니다: {str(e)}")


@router.get("/capabilities")
async def get_assistant_capabilities(
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    스마트 어시스턴트가 지원하는 기능 목록을 반환합니다.
    """
    return {
        "supported_queries": {
            "pastoral_visit_schedule": {
                "description": "심방 일정 조회",
                "examples": [
                    "오늘 심방 일정 알려줘",
                    "이번주 심방 예정은?",
                    "내일 방문해야 할 곳 어디야?"
                ]
            },
            "prayer_requests": {
                "description": "중보기도 요청 조회",
                "examples": [
                    "최근 기도제목 뭐가 있어?",
                    "긴급 기도 요청 있나?",
                    "이번주 중보기도 내용"
                ]
            },
            "announcements": {
                "description": "교회 공지사항 조회",
                "examples": [
                    "새로운 공지사항 있어?",
                    "이번주 중요한 안내 사항",
                    "최근 교회 소식 정리해줘"
                ]
            },
            "visit_reports": {
                "description": "심방 보고서 및 기록 조회",
                "examples": [
                    "최근 심방 결과 어때?",
                    "이번달 심방 보고서 요약",
                    "심방 현황 알려줘"
                ]
            },
            "member_info": {
                "description": "성도 정보 요약 (개인정보 보호 적용)",
                "examples": [
                    "우리 교회 성도 현황",
                    "교인 수 얼마나 돼?",
                    "멤버 통계 보여줘"
                ]
            }
        },
        "time_contexts": [
            "오늘", "내일", "이번주", "이번달", "다가오는"
        ],
        "data_sources": [
            "pastoral_care_requests", "prayer_requests", "announcements", 
            "visit_reports", "member_summary", "church_database"
        ],
        "privacy_note": "모든 개인정보는 교회 내부에서만 사용되며, 필요한 범위에서만 제공됩니다."
    }


@router.get("/usage-stats")
async def get_usage_statistics(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """교회의 스마트 어시스턴트 사용 통계"""
    
    # 관리자만 접근 가능
    if current_user.role not in ["admin", "minister"]:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")
    
    church = db.query(Church).filter(Church.id == current_user.church_id).first()
    if not church:
        raise HTTPException(status_code=404, detail="Church not found")
    
    return {
        "church_id": church.id,
        "church_name": church.name,
        "current_month_tokens": church.current_month_tokens or 0,
        "current_month_cost": round(church.current_month_cost or 0, 4),
        "monthly_token_limit": church.monthly_token_limit or 100000,
        "token_usage_percentage": round(
            ((church.current_month_tokens or 0) / (church.monthly_token_limit or 100000)) * 100, 2
        ),
        "gpt_model": church.gpt_model or "gpt-4o-mini",
        "api_key_configured": bool(church.gpt_api_key),
        "subscription_plan": church.subscription_plan or "basic"
    }