"""
JobPlanet Crawler - 잡플래닛 채용정보 크롤러
HTML 파싱 기반으로 동작합니다.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import re
import logging

from bs4 import BeautifulSoup

from app.crawlers.base import BaseCrawler, JobPosting

logger = logging.getLogger(__name__)


class JobPlanetCrawler(BaseCrawler):
    """JobPlanet job crawler using HTML parsing"""
    
    SOURCE_NAME = "jobplanet"
    BASE_URL = "https://www.jobplanet.co.kr"
    SEARCH_URL = "https://www.jobplanet.co.kr/job"
    RATE_LIMIT_SECONDS = 2.5
    
    async def search_jobs(
        self,
        keyword: str,
        location: Optional[str] = None,
        experience_level: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> List[JobPosting]:
        """Search jobs on JobPlanet"""
        
        # Build search URL
        params = {
            'q': keyword,
            'page': page,
        }
        
        # 지역 필터
        if location:
            location_map = {
                '서울': 'seoul',
                '경기': 'gyeonggi',
                '인천': 'incheon',
                '부산': 'busan',
                '대구': 'daegu',
                '대전': 'daejeon',
                '광주': 'gwangju',
            }
            if location in location_map:
                params['loc'] = location_map[location]
        
        # 경력 필터
        if experience_level:
            if '신입' in experience_level:
                params['career'] = 'entry'
            elif '경력' in experience_level:
                params['career'] = 'experienced'
        
        try:
            response = await self.fetch(self.SEARCH_URL, params=params)
            
            if not response:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            jobs = self._parse_search_results(soup)
            
            return jobs[:limit]
            
        except Exception as e:
            logger.error(f"JobPlanet search error: {e}")
            return []
    
    def _parse_search_results(self, soup: BeautifulSoup) -> List[JobPosting]:
        """Parse search result page"""
        jobs = []
        
        # 채용공고 리스트 찾기
        job_list = soup.select('.job-list-item') or \
                   soup.select('.recruit-item') or \
                   soup.select('.position-item')
        
        for item in job_list:
            try:
                job = self._parse_job_item(item)
                if job:
                    jobs.append(job)
            except Exception as e:
                logger.warning(f"Failed to parse JobPlanet item: {e}")
                continue
        
        return jobs
    
    def _parse_job_item(self, item) -> Optional[JobPosting]:
        """Parse individual job item"""
        try:
            # 제목과 링크
            title_elem = item.select_one('.position-title a') or \
                        item.select_one('.job-title a') or \
                        item.select_one('h3 a')
            
            if not title_elem:
                title_elem = item.select_one('a')
            
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            href = title_elem.get('href', '')
            
            # job_id 추출
            job_id_match = re.search(r'/job/(\d+)', href)
            job_id = job_id_match.group(1) if job_id_match else ''
            
            if not job_id:
                job_id = re.sub(r'[^0-9]', '', href)[:10]
            
            # 회사명
            company_elem = item.select_one('.company-name') or \
                          item.select_one('.corp-name') or \
                          item.select_one('.company a')
            company_name = company_elem.get_text(strip=True) if company_elem else ''
            
            # 위치
            location_elem = item.select_one('.location') or item.select_one('.area')
            location = location_elem.get_text(strip=True) if location_elem else ''
            
            # 경력
            career_elem = item.select_one('.career') or item.select_one('.experience')
            experience = career_elem.get_text(strip=True) if career_elem else ''
            
            # 스킬 태그
            skills = []
            skill_elems = item.select('.skill-tag') or item.select('.tag')
            for elem in skill_elems:
                skill = elem.get_text(strip=True)
                if skill:
                    skills.append(skill)
            
            # 회사 로고
            logo_elem = item.select_one('.company-logo img') or item.select_one('.logo img')
            logo_url = logo_elem.get('src', '') if logo_elem else ''
            
            source_url = href if href.startswith('http') else f"{self.BASE_URL}{href}"
            
            return JobPosting(
                title=title,
                company_name=company_name,
                source=self.SOURCE_NAME,
                source_url=source_url,
                source_id=job_id,
                location=location,
                experience_level=experience,
                skills=skills,
                company_logo_url=logo_url,
            )
            
        except Exception as e:
            logger.warning(f"Parse error: {e}")
            return None
    
    async def get_job_detail(self, job_id: str) -> Optional[JobPosting]:
        """Get detailed job information"""
        url = f"{self.BASE_URL}/job/{job_id}"
        
        try:
            response = await self.fetch(url)
            
            if not response:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 제목
            title_elem = soup.select_one('.position-title') or soup.select_one('h1')
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # 회사명
            company_elem = soup.select_one('.company-name') or soup.select_one('.corp-name')
            company_name = company_elem.get_text(strip=True) if company_elem else ''
            
            # 상세 내용
            desc_elem = soup.select_one('.job-description') or soup.select_one('.description')
            description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            # 자격 요건
            req_elem = soup.select_one('.requirements') or soup.select_one('.qualification')
            requirements = req_elem.get_text(strip=True) if req_elem else ''
            
            # 복리후생
            benefit_elem = soup.select_one('.benefits') or soup.select_one('.welfare')
            benefits = benefit_elem.get_text(strip=True) if benefit_elem else ''
            
            # 기타 정보
            info = {}
            info_rows = soup.select('.info-table tr') or soup.select('.detail-info li')
            for row in info_rows:
                label = row.select_one('th, .label')
                value = row.select_one('td, .value')
                if label and value:
                    info[label.get_text(strip=True)] = value.get_text(strip=True)
            
            # 스킬 태그
            skills = []
            skill_elems = soup.select('.skill-tag') or soup.select('.tech-stack span')
            for elem in skill_elems:
                skill = elem.get_text(strip=True)
                if skill:
                    skills.append(skill)
            
            return JobPosting(
                title=title,
                company_name=company_name,
                source=self.SOURCE_NAME,
                source_url=url,
                source_id=job_id,
                location=info.get('근무지역', info.get('위치', '')),
                experience_level=info.get('경력', ''),
                employment_type=info.get('고용형태', ''),
                salary=info.get('급여', info.get('연봉', '')),
                description=description,
                requirements=requirements,
                benefits=benefits,
                skills=skills,
                raw_data={'info': info}
            )
            
        except Exception as e:
            logger.error(f"JobPlanet detail error for {job_id}: {e}")
            return None
