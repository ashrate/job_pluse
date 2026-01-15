"""
JobKorea Crawler - 잡코리아 채용정보 크롤러
HTML 파싱 기반으로 동작합니다.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import re
import logging

from bs4 import BeautifulSoup

from app.crawlers.base import BaseCrawler, JobPosting

logger = logging.getLogger(__name__)


class JobKoreaCrawler(BaseCrawler):
    """JobKorea job crawler using HTML parsing"""
    
    SOURCE_NAME = "jobkorea"
    BASE_URL = "https://www.jobkorea.co.kr"
    SEARCH_URL = "https://www.jobkorea.co.kr/Search"
    RATE_LIMIT_SECONDS = 2.0
    
    # 경력 레벨 매핑
    EXPERIENCE_CODES = {
        '신입': '1',
        '경력': '2',
        '신입/경력': '0',
    }
    
    async def search_jobs(
        self,
        keyword: str,
        location: Optional[str] = None,
        experience_level: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> List[JobPosting]:
        """Search jobs on JobKorea"""
        
        # Build search URL
        params = {
            'stext': keyword,
            'tabType': 'recruit',
            'Page_No': page,
        }
        
        # 경력 필터
        if experience_level and experience_level in self.EXPERIENCE_CODES:
            params['careerType'] = self.EXPERIENCE_CODES[experience_level]
        
        # 지역 필터 (잡코리아 지역 코드)
        if location:
            location_codes = {
                '서울': 'I000',
                '경기': 'B000',
                '인천': 'I010',
                '부산': 'H000',
                '대구': 'C000',
                '대전': 'D000',
                '광주': 'F000',
            }
            if location in location_codes:
                params['local'] = location_codes[location]
        
        try:
            response = await self.fetch(f"{self.SEARCH_URL}", params=params)
            
            if not response:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            jobs = self._parse_search_results(soup)
            
            return jobs[:limit]
            
        except Exception as e:
            logger.error(f"JobKorea search error: {e}")
            return []
    
    def _parse_search_results(self, soup: BeautifulSoup) -> List[JobPosting]:
        """Parse search result page"""
        jobs = []
        
        # 채용공고 리스트 찾기
        job_list = soup.select('.recruit-info .list-default .list-post')
        
        if not job_list:
            # 다른 셀렉터 시도
            job_list = soup.select('.list-section .list-item')
        
        if not job_list:
            job_list = soup.select('.list-recruit .list-item')
        
        for item in job_list:
            try:
                job = self._parse_job_item(item)
                if job:
                    jobs.append(job)
            except Exception as e:
                logger.warning(f"Failed to parse JobKorea item: {e}")
                continue
        
        return jobs
    
    def _parse_job_item(self, item) -> Optional[JobPosting]:
        """Parse individual job item"""
        try:
            # 제목과 링크
            title_elem = item.select_one('.post-list-info .title a') or \
                        item.select_one('.info-title a') or \
                        item.select_one('.title a')
            
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            href = title_elem.get('href', '')
            
            # job_id 추출
            job_id_match = re.search(r'Oem_GI_ID=(\d+)', href) or \
                          re.search(r'/Recruit/GI_Read/(\d+)', href)
            job_id = job_id_match.group(1) if job_id_match else ''
            
            if not job_id:
                # URL에서 다른 방식으로 ID 추출 시도
                job_id = re.sub(r'[^0-9]', '', href)[:10]
            
            # 회사명
            company_elem = item.select_one('.post-list-corp .name a') or \
                          item.select_one('.corp-name a') or \
                          item.select_one('.company a')
            company_name = company_elem.get_text(strip=True) if company_elem else ''
            
            # 지역
            location_elem = item.select_one('.post-list-info .option span') or \
                           item.select_one('.info-local')
            location = location_elem.get_text(strip=True) if location_elem else ''
            
            # 경력
            exp_elem = item.select_one('.exp') or item.select_one('.career')
            experience = exp_elem.get_text(strip=True) if exp_elem else ''
            
            # 마감일
            date_elem = item.select_one('.date') or item.select_one('.deadline')
            deadline_text = date_elem.get_text(strip=True) if date_elem else ''
            
            source_url = href if href.startswith('http') else f"{self.BASE_URL}{href}"
            
            return JobPosting(
                title=title,
                company_name=company_name,
                source=self.SOURCE_NAME,
                source_url=source_url,
                source_id=job_id,
                location=location,
                experience_level=experience,
                employment_type=self._extract_employment_type(item),
                skills=self._extract_skills(item),
            )
            
        except Exception as e:
            logger.warning(f"Parse error: {e}")
            return None
    
    def _extract_employment_type(self, item) -> str:
        """Extract employment type"""
        type_elem = item.select_one('.option .type') or item.select_one('.employment-type')
        if type_elem:
            return type_elem.get_text(strip=True)
        return ''
    
    def _extract_skills(self, item) -> List[str]:
        """Extract skill tags"""
        skills = []
        skill_elems = item.select('.skill-tag') or item.select('.keyword-wrap .keyword')
        for elem in skill_elems:
            skill = elem.get_text(strip=True)
            if skill:
                skills.append(skill)
        return skills
    
    async def get_job_detail(self, job_id: str) -> Optional[JobPosting]:
        """Get detailed job information"""
        url = f"{self.BASE_URL}/Recruit/GI_Read/{job_id}"
        
        try:
            response = await self.fetch(url)
            
            if not response:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 제목
            title_elem = soup.select_one('.tit') or soup.select_one('.title')
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # 회사명
            company_elem = soup.select_one('.coName a') or soup.select_one('.company-name')
            company_name = company_elem.get_text(strip=True) if company_elem else ''
            
            # 상세 내용
            desc_elem = soup.select_one('.tbContentReadDetail') or soup.select_one('.job-detail')
            description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            # 조건들
            conditions = {}
            condition_table = soup.select('.tbList tbody tr')
            for row in condition_table:
                th = row.select_one('th')
                td = row.select_one('td')
                if th and td:
                    key = th.get_text(strip=True)
                    value = td.get_text(strip=True)
                    conditions[key] = value
            
            return JobPosting(
                title=title,
                company_name=company_name,
                source=self.SOURCE_NAME,
                source_url=url,
                source_id=job_id,
                location=conditions.get('근무지역', ''),
                experience_level=conditions.get('경력', ''),
                employment_type=conditions.get('고용형태', ''),
                salary=conditions.get('급여', ''),
                description=description,
                raw_data={'conditions': conditions}
            )
            
        except Exception as e:
            logger.error(f"JobKorea detail error for {job_id}: {e}")
            return None
