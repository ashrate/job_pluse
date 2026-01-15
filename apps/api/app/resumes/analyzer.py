"""
Resume Analysis Service - OpenAI 기반 이력서 분석
"""
import os
import json
import logging
from typing import Optional, Dict, Any
from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

# OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

ANALYSIS_SYSTEM_PROMPT = """당신은 전문 커리어 컨설턴트이자 ATS(Applicant Tracking System) 전문가입니다.
이력서를 분석하여 다음 항목에 대해 상세한 피드백을 제공해주세요:

1. ATS 친화도: 자동화된 채용 시스템에서 잘 파싱될 수 있는지
2. 임팩트 표현: 성과가 수치와 함께 구체적으로 표현되었는지
3. 키워드 매칭: 타겟 직무에 적합한 키워드가 포함되었는지
4. 가독성: 문장이 명확하고 간결한지
5. 형식: 레이아웃과 구조가 전문적인지

반드시 JSON 형식으로 응답해주세요."""

ANALYSIS_JSON_SCHEMA = """{
  "overall_score": <0-100 정수>,
  "summary": "<1-2문장의 전체 평가>",
  "sections": {
    "ats_friendly": {
      "score": <0-100>,
      "status": "<good 또는 needs_improvement>",
      "feedback": "<구체적인 피드백 문장>"
    },
    "impact_metrics": {
      "score": <0-100>,
      "status": "<good 또는 needs_improvement>",
      "feedback": "<구체적인 피드백 문장>"
    },
    "keyword_match": {
      "score": <0-100>,
      "status": "<good 또는 needs_improvement>",
      "feedback": "<구체적인 피드백 문장>"
    },
    "readability": {
      "score": <0-100>,
      "status": "<good 또는 needs_improvement>",
      "feedback": "<구체적인 피드백 문장>"
    },
    "format": {
      "score": <0-100>,
      "status": "<good 또는 needs_improvement>",
      "feedback": "<구체적인 피드백 문장>"
    }
  },
  "suggestions": [
    {
      "section": "<해당 섹션명>",
      "original": "<현재 이력서의 문구>",
      "suggested": "<개선된 문구 제안>",
      "reason": "<개선 이유>"
    }
  ],
  "keyword_analysis": {
    "found": ["<발견된 키워드 목록>"],
    "missing": ["<추가하면 좋을 키워드 목록>"],
    "match_rate": <0-100>
  }
}"""


async def analyze_resume_with_ai(
    resume_text: str,
    target_role: Optional[str] = None,
    filename: Optional[str] = None
) -> Dict[str, Any]:
    """
    OpenAI를 사용하여 이력서를 분석합니다.
    
    Args:
        resume_text: 이력서 텍스트 내용
        target_role: 타겟 직무 (선택)
        filename: 파일명 (선택)
    
    Returns:
        분석 결과 딕셔너리
    """
    if not client:
        logger.warning("OpenAI API key not configured, using fallback analysis")
        return generate_fallback_analysis(resume_text, target_role)
    
    try:
        # Build the analysis request
        user_prompt = f"""다음 이력서를 분석해주세요.

{'타겟 직무: ' + target_role if target_role else ''}
{'파일명: ' + filename if filename else ''}

=== 이력서 내용 ===
{resume_text[:8000]}  # Limit to avoid token limits
===

위 이력서를 분석하고 다음 JSON 형식으로 응답해주세요:
{ANALYSIS_JSON_SCHEMA}

반드시 유효한 JSON만 응답하세요. 다른 텍스트는 포함하지 마세요."""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content
        analysis = json.loads(result_text)
        
        # Validate and ensure required fields
        analysis = validate_analysis_result(analysis)
        
        logger.info(f"Resume analysis completed successfully, score: {analysis.get('overall_score')}")
        return analysis
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response as JSON: {e}")
        return generate_fallback_analysis(resume_text, target_role)
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        return generate_fallback_analysis(resume_text, target_role)


def validate_analysis_result(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """분석 결과의 필수 필드를 검증하고 보완합니다."""
    
    # Ensure overall_score
    if "overall_score" not in analysis:
        analysis["overall_score"] = 70
    else:
        analysis["overall_score"] = max(0, min(100, int(analysis["overall_score"])))
    
    # Ensure sections
    default_sections = {
        "ats_friendly": {"score": 70, "status": "good", "feedback": "분석 완료"},
        "impact_metrics": {"score": 65, "status": "needs_improvement", "feedback": "분석 완료"},
        "keyword_match": {"score": 70, "status": "good", "feedback": "분석 완료"},
        "readability": {"score": 70, "status": "good", "feedback": "분석 완료"},
        "format": {"score": 70, "status": "good", "feedback": "분석 완료"}
    }
    
    if "sections" not in analysis:
        analysis["sections"] = default_sections
    else:
        for key in default_sections:
            if key not in analysis["sections"]:
                analysis["sections"][key] = default_sections[key]
            else:
                section = analysis["sections"][key]
                if "score" not in section:
                    section["score"] = 70
                if "status" not in section:
                    section["status"] = "good" if section["score"] >= 70 else "needs_improvement"
                if "feedback" not in section:
                    section["feedback"] = "분석 완료"
    
    # Ensure suggestions
    if "suggestions" not in analysis:
        analysis["suggestions"] = []
    
    # Ensure keyword_analysis
    if "keyword_analysis" not in analysis:
        analysis["keyword_analysis"] = {
            "found": [],
            "missing": [],
            "match_rate": 60
        }
    
    return analysis


def generate_fallback_analysis(
    resume_text: str,
    target_role: Optional[str] = None
) -> Dict[str, Any]:
    """
    API 사용 불가 시 텍스트 기반 기본 분석을 수행합니다.
    """
    text_lower = resume_text.lower()
    word_count = len(resume_text.split())
    
    # Simple heuristic analysis
    has_numbers = any(char.isdigit() for char in resume_text)
    has_percentages = '%' in resume_text or '퍼센트' in resume_text
    has_bullet_points = '•' in resume_text or '·' in resume_text or '-' in resume_text
    
    # Common tech keywords
    tech_keywords = ['python', 'javascript', 'react', 'java', 'sql', 'aws', 'docker', 
                     'kubernetes', 'git', 'node', 'typescript', 'vue', 'angular',
                     '파이썬', '자바스크립트', '리액트', '데이터', '분석', '개발']
    found_keywords = [kw for kw in tech_keywords if kw in text_lower]
    
    # Calculate scores based on heuristics
    ats_score = 70
    if has_bullet_points:
        ats_score += 10
    if word_count > 200:
        ats_score += 5
    
    impact_score = 55
    if has_numbers:
        impact_score += 15
    if has_percentages:
        impact_score += 15
    
    keyword_score = min(90, 50 + len(found_keywords) * 5)
    
    readability_score = 65
    if 100 < word_count < 1000:
        readability_score += 10
    
    format_score = 70
    if has_bullet_points:
        format_score += 10
    
    overall_score = int((ats_score + impact_score + keyword_score + readability_score + format_score) / 5)
    
    # Generate appropriate feedback based on scores and content
    suggestions = []
    
    if not has_numbers:
        suggestions.append({
            "section": "경력",
            "original": "프로젝트를 수행했습니다",
            "suggested": "프로젝트를 수행하여 매출 20% 증가에 기여했습니다",
            "reason": "성과를 수치로 표현하면 임팩트가 높아집니다"
        })
    
    if not has_percentages:
        suggestions.append({
            "section": "성과",
            "original": "업무 효율을 개선했습니다",
            "suggested": "업무 효율을 30% 개선하여 비용 절감에 기여했습니다",
            "reason": "구체적인 퍼센트 수치 추가"
        })
    
    if len(found_keywords) < 3:
        suggestions.append({
            "section": "스킬",
            "original": "다양한 기술 스택을 활용한 경험이 있습니다",
            "suggested": f"Python, React, AWS 등 {'타겟 직무(' + target_role + ')에 맞는' if target_role else ''} 기술 스택을 활용한 경험이 있습니다",
            "reason": "구체적인 기술명을 명시하세요"
        })
    
    return {
        "overall_score": overall_score,
        "summary": f"{'좋은' if overall_score >= 70 else '개선이 필요한'} 이력서입니다. {'수치화된 성과 표현을 추가하면 더 좋아집니다.' if not has_numbers else ''}",
        "sections": {
            "ats_friendly": {
                "score": min(100, ats_score),
                "status": "good" if ats_score >= 70 else "needs_improvement",
                "feedback": "글머리 기호와 명확한 섹션 구분이 있어 ATS 파싱에 적합합니다." if has_bullet_points else "글머리 기호(•)를 사용하여 내용을 구분하면 ATS 친화도가 높아집니다."
            },
            "impact_metrics": {
                "score": min(100, impact_score),
                "status": "good" if impact_score >= 70 else "needs_improvement",
                "feedback": "성과가 수치로 잘 표현되어 있습니다." if has_numbers and has_percentages else "성과를 '매출 20% 증가', '처리 시간 50% 단축'처럼 수치로 표현하세요."
            },
            "keyword_match": {
                "score": min(100, keyword_score),
                "status": "good" if keyword_score >= 70 else "needs_improvement",
                "feedback": f"{'타겟 직무(' + target_role + ')와 관련된' if target_role else ''} 키워드가 {len(found_keywords)}개 발견되었습니다. {'더 많은 기술 키워드를 추가하세요.' if len(found_keywords) < 5 else '적절한 키워드가 포함되어 있습니다.'}"
            },
            "readability": {
                "score": min(100, readability_score),
                "status": "good" if readability_score >= 70 else "needs_improvement",
                "feedback": "문장이 적절한 길이로 작성되어 있습니다." if 100 < word_count < 1000 else "이력서 길이를 조절하세요. 너무 짧거나 길면 가독성이 떨어집니다."
            },
            "format": {
                "score": min(100, format_score),
                "status": "good" if format_score >= 70 else "needs_improvement",
                "feedback": "깔끔한 형식으로 구성되어 있습니다." if has_bullet_points else "글머리 기호와 들여쓰기를 활용하여 형식을 개선하세요."
            }
        },
        "suggestions": suggestions,
        "keyword_analysis": {
            "found": found_keywords[:10],
            "missing": [kw for kw in ["SQL", "Git", "협업", "문제해결", "커뮤니케이션"] if kw.lower() not in text_lower][:5],
            "match_rate": min(100, len(found_keywords) * 10)
        }
    }


async def extract_text_from_file(file_path: str) -> str:
    """
    파일에서 텍스트를 추출합니다.
    PDF와 DOCX 파일 지원.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def extract_text_from_pdf(file_path: str) -> str:
    """PDF에서 텍스트 추출"""
    try:
        from pypdf import PdfReader
        
        reader = PdfReader(file_path)
        text_parts = []
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        
        return "\n".join(text_parts)
    except Exception as e:
        logger.error(f"PDF text extraction failed: {e}")
        return ""


def extract_text_from_docx(file_path: str) -> str:
    """DOCX에서 텍스트 추출"""
    try:
        from docx import Document
        
        doc = Document(file_path)
        text_parts = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        
        return "\n".join(text_parts)
    except Exception as e:
        logger.error(f"DOCX text extraction failed: {e}")
        return ""
