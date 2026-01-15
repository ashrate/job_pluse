"""
Wanted Crawler - 원티드 채용정보 크롤러
원티드는 공개 API를 제공하므로 비교적 안정적으로 데이터를 가져올 수 있습니다.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from app.crawlers.base import BaseCrawler, JobPosting

logger = logging.getLogger(__name__)


class WantedCrawler(BaseCrawler):
    """Wanted job crawler using their public API"""
    
    SOURCE_NAME = "wanted"
    BASE_URL = "https://www.wanted.co.kr"
    API_URL = "https://www.wanted.co.kr/api/v4"
    RATE_LIMIT_SECONDS = 1.5
    
    # 직군 카테고리 매핑
    JOB_CATEGORIES = {
        'frontend': 669,
        'backend': 872,
        'fullstack': 873,
        'mobile': 677,
        'data': 655,
        'ml': 1634,
        'devops': 674,
        'security': 671,
        'qa': 676,
        'embedded': 658,
        'game': 1026,
    }
    
    # 경력 레벨 매핑
    EXPERIENCE_LEVELS = {
        '신입': 0,
        '1년': 1,
        '2년': 2,
        '3년': 3,
        '4년': 4,
        '5년': 5,
        '6년': 6,
        '7년': 7,
        '8년': 8,
        '9년': 9,
        '10년이상': 10,
    }
    
    async def search_jobs(
        self,
        keyword: str,
        location: Optional[str] = None,
        experience_level: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> List[JobPosting]:
        """Search jobs on Wanted"""
        
        # Build API URL
        offset = (page - 1) * limit
        
        # 검색 API 엔드포인트
        url = f"{self.API_URL}/jobs"
        
        params = {
            'country': 'kr',
            'job_sort': 'job.latest_order',
            'locations': 'all',
            'years': -1,
            'limit': limit,
            'offset': offset,
        }
        
        # 키워드 검색
        if keyword:
            params['search'] = keyword
        
        # 지역 필터
        if location:
            location_map = {
                '서울': 'seoul.all',
                '경기': 'gyeonggi.all',
                '인천': 'incheon.all',
                '부산': 'busan.all',
                '대구': 'daegu.all',
                '대전': 'daejeon.all',
                '광주': 'gwangju.all',
            }
            params['locations'] = location_map.get(location, 'all')
        
        # 경력 필터
        if experience_level and experience_level in self.EXPERIENCE_LEVELS:
            params['years'] = self.EXPERIENCE_LEVELS[experience_level]
        
        try:
            data = await self.fetch_json(url, params=params)
            
            if not data or 'data' not in data:
                return []
            
            jobs = []
            for item in data.get('data', []):
                job = self._parse_job_item(item)
                if job:
                    jobs.append(job)
            
            return jobs
            
        except Exception as e:
            logger.error(f"Wanted search error: {e}")
            return []
    
    def _parse_job_item(self, item: Dict[str, Any]) -> Optional[JobPosting]:
        """Parse job item from API response"""
        try:
            job_id = str(item.get('id', ''))
            
            # 스킬 태그 추출
            skills = []
            if 'skill_tags' in item:
                skills = [tag.get('title', '') for tag in item.get('skill_tags', [])]
            
            return JobPosting(
                title=item.get('position', ''),
                company_name=item.get('company', {}).get('name', ''),
                source=self.SOURCE_NAME,
                source_url=f"{self.BASE_URL}/wd/{job_id}",
                source_id=job_id,
                location=item.get('address', {}).get('full_location', ''),
                experience_level=self._parse_experience(item),
                employment_type='정규직',  # Wanted는 대부분 정규직
                job_category=item.get('category', {}).get('name', ''),
                skills=skills,
                company_logo_url=item.get('company', {}).get('logo_img', {}).get('origin', ''),
                posted_at=None,  # API에서 제공 안함
                raw_data=item
            )
        except Exception as e:
            logger.warning(f"Failed to parse Wanted job item: {e}")
            return None
    
    def _parse_experience(self, item: Dict[str, Any]) -> str:
        """Parse experience requirement"""
        years_min = item.get('years', {}).get('min', 0)
        years_max = item.get('years', {}).get('max', 0)
        
        if years_min == 0 and years_max == 0:
            return '신입'
        elif years_min == 0:
            return f'신입~{years_max}년'
        elif years_max == 0 or years_max == -1:
            return f'{years_min}년 이상'
        else:
            return f'{years_min}~{years_max}년'
    
    async def get_job_detail(self, job_id: str) -> Optional[JobPosting]:
        """Get detailed job information"""
        url = f"{self.API_URL}/jobs/{job_id}"
        
        try:
            data = await self.fetch_json(url)
            
            if not data or 'job' not in data:
                return None
            
            job_data = data['job']
            
            # 스킬 태그 추출
            skills = []
            if 'skill_tags' in job_data:
                skills = [tag.get('title', '') for tag in job_data.get('skill_tags', [])]
            
            return JobPosting(
                title=job_data.get('position', ''),
                company_name=job_data.get('company', {}).get('name', ''),
                source=self.SOURCE_NAME,
                source_url=f"{self.BASE_URL}/wd/{job_id}",
                source_id=job_id,
                location=job_data.get('address', {}).get('full_location', ''),
                experience_level=self._parse_experience(job_data),
                employment_type='정규직',
                job_category=job_data.get('category', {}).get('name', ''),
                skills=skills,
                description=job_data.get('detail', {}).get('intro', ''),
                requirements=job_data.get('detail', {}).get('requirements', ''),
                benefits=job_data.get('detail', {}).get('benefits', ''),
                company_logo_url=job_data.get('company', {}).get('logo_img', {}).get('origin', ''),
                deadline=self._parse_deadline(job_data),
                raw_data=job_data
            )
            
        except Exception as e:
            logger.error(f"Wanted detail error for {job_id}: {e}")
            return None
    
    def _parse_deadline(self, item: Dict[str, Any]) -> Optional[datetime]:
        """Parse deadline from job data"""
        due_date = item.get('due_time')
        if due_date:
            try:
                return datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except:
                pass
        return None
