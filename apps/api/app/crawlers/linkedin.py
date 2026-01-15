"""
LinkedIn Crawler - 링크드인 채용정보 크롤러
LinkedIn은 로그인 없이도 일부 공개 채용정보를 조회할 수 있습니다.
주의: LinkedIn은 스크래핑에 매우 민감하므로 주의가 필요합니다.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import re
import logging

from bs4 import BeautifulSoup

from app.crawlers.base import BaseCrawler, JobPosting

logger = logging.getLogger(__name__)


class LinkedInCrawler(BaseCrawler):
    """LinkedIn job crawler - Public jobs only"""
    
    SOURCE_NAME = "linkedin"
    BASE_URL = "https://www.linkedin.com"
    # LinkedIn Jobs 공개 검색 URL
    SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    RATE_LIMIT_SECONDS = 3.0  # LinkedIn은 더 느리게
    MAX_RETRIES = 2
    
    # Location geo IDs for Korea
    LOCATION_GEO_IDS = {
        '한국': '105149562',
        '서울': '105509042',
        '경기': '107178665',
        '부산': '102246151',
        '대구': '100805908',
        '인천': '105169312',
        '대전': '106279546',
    }
    
    def get_headers(self) -> Dict[str, str]:
        """Override headers for LinkedIn"""
        headers = super().get_headers()
        headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate', 
            'Sec-Fetch-Site': 'none',
        })
        return headers
    
    async def search_jobs(
        self,
        keyword: str,
        location: Optional[str] = None,
        experience_level: Optional[str] = None,
        page: int = 1,
        limit: int = 25
    ) -> List[JobPosting]:
        """Search jobs on LinkedIn"""
        
        # Calculate start position (LinkedIn uses 25 per page)
        start = (page - 1) * 25
        
        # Build search URL
        params = {
            'keywords': keyword,
            'location': location or '대한민국',
            'start': start,
            'f_TPR': 'r604800',  # Last week
        }
        
        # Location geo ID
        geo_id = self.LOCATION_GEO_IDS.get(location, self.LOCATION_GEO_IDS['한국'])
        params['geoId'] = geo_id
        
        # Experience level filter
        if experience_level:
            exp_map = {
                '인턴': '1',
                '신입': '2',
                '주니어': '3',
                '중간': '4',
                '시니어': '5',
                '임원': '6',
            }
            if experience_level in exp_map:
                params['f_E'] = exp_map[experience_level]
        
        try:
            response = await self.fetch(self.SEARCH_URL, params=params)
            
            if not response:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            jobs = self._parse_search_results(soup)
            
            return jobs[:limit]
            
        except Exception as e:
            logger.error(f"LinkedIn search error: {e}")
            return []
    
    def _parse_search_results(self, soup: BeautifulSoup) -> List[JobPosting]:
        """Parse LinkedIn search results"""
        jobs = []
        
        # LinkedIn job cards
        job_cards = soup.select('.job-search-card') or \
                   soup.select('.base-card') or \
                   soup.select('li.jobs-search-results__list-item')
        
        for card in job_cards:
            try:
                job = self._parse_job_card(card)
                if job:
                    jobs.append(job)
            except Exception as e:
                logger.warning(f"Failed to parse LinkedIn card: {e}")
                continue
        
        return jobs
    
    def _parse_job_card(self, card) -> Optional[JobPosting]:
        """Parse individual LinkedIn job card"""
        try:
            # Title and link
            title_elem = card.select_one('.base-search-card__title') or \
                        card.select_one('.job-search-card__title') or \
                        card.select_one('h3.base-search-card__title')
            
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            
            # Link
            link_elem = card.select_one('a.base-card__full-link') or \
                       card.select_one('a[data-tracking-control-name]')
            
            href = link_elem.get('href', '') if link_elem else ''
            
            # Extract job ID from URL
            job_id_match = re.search(r'jobs/view/(\d+)', href)
            job_id = job_id_match.group(1) if job_id_match else ''
            
            if not job_id:
                return None
            
            # Company
            company_elem = card.select_one('.base-search-card__subtitle') or \
                          card.select_one('.job-search-card__company-name') or \
                          card.select_one('h4.base-search-card__subtitle')
            company_name = company_elem.get_text(strip=True) if company_elem else ''
            
            # Location
            location_elem = card.select_one('.job-search-card__location') or \
                           card.select_one('.base-search-card__metadata span')
            location = location_elem.get_text(strip=True) if location_elem else ''
            
            # Posted date
            date_elem = card.select_one('.job-search-card__listdate') or \
                       card.select_one('time')
            posted_at = self._parse_posted_date(date_elem)
            
            # Company logo
            logo_elem = card.select_one('.artdeco-entity-image') or \
                       card.select_one('img.company-logo')
            logo_url = ''
            if logo_elem:
                logo_url = logo_elem.get('data-delayed-url', '') or logo_elem.get('src', '')
            
            return JobPosting(
                title=title,
                company_name=company_name,
                source=self.SOURCE_NAME,
                source_url=href.split('?')[0] if href else f"{self.BASE_URL}/jobs/view/{job_id}",
                source_id=job_id,
                location=location,
                company_logo_url=logo_url,
                posted_at=posted_at,
            )
            
        except Exception as e:
            logger.warning(f"LinkedIn card parse error: {e}")
            return None
    
    def _parse_posted_date(self, elem) -> Optional[datetime]:
        """Parse LinkedIn relative date to datetime"""
        if not elem:
            return None
        
        text = elem.get_text(strip=True).lower()
        datetime_attr = elem.get('datetime')
        
        if datetime_attr:
            try:
                return datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
            except:
                pass
        
        # Parse relative dates like "1 day ago", "2 weeks ago"
        now = datetime.utcnow()
        
        patterns = [
            (r'(\d+)\s*분\s*전', lambda m: now - timedelta(minutes=int(m.group(1)))),
            (r'(\d+)\s*시간\s*전', lambda m: now - timedelta(hours=int(m.group(1)))),
            (r'(\d+)\s*일\s*전', lambda m: now - timedelta(days=int(m.group(1)))),
            (r'(\d+)\s*주\s*전', lambda m: now - timedelta(weeks=int(m.group(1)))),
            (r'(\d+)\s*개월\s*전', lambda m: now - timedelta(days=int(m.group(1))*30)),
            (r'(\d+)\s*minute', lambda m: now - timedelta(minutes=int(m.group(1)))),
            (r'(\d+)\s*hour', lambda m: now - timedelta(hours=int(m.group(1)))),
            (r'(\d+)\s*day', lambda m: now - timedelta(days=int(m.group(1)))),
            (r'(\d+)\s*week', lambda m: now - timedelta(weeks=int(m.group(1)))),
            (r'(\d+)\s*month', lambda m: now - timedelta(days=int(m.group(1))*30)),
        ]
        
        for pattern, handler in patterns:
            match = re.search(pattern, text)
            if match:
                return handler(match)
        
        return None
    
    async def get_job_detail(self, job_id: str) -> Optional[JobPosting]:
        """Get detailed job information from LinkedIn"""
        # LinkedIn job detail page (public view)
        url = f"{self.BASE_URL}/jobs/view/{job_id}"
        
        try:
            response = await self.fetch(url)
            
            if not response:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Title
            title_elem = soup.select_one('.top-card-layout__title') or \
                        soup.select_one('h1.topcard__title')
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # Company
            company_elem = soup.select_one('.topcard__org-name-link') or \
                          soup.select_one('.top-card-layout__second-subline a')
            company_name = company_elem.get_text(strip=True) if company_elem else ''
            
            # Location
            location_elem = soup.select_one('.topcard__flavor--bullet') or \
                           soup.select_one('.top-card-layout__first-subline span')
            location = location_elem.get_text(strip=True) if location_elem else ''
            
            # Description
            desc_elem = soup.select_one('.description__text') or \
                       soup.select_one('.show-more-less-html__markup')
            description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            # Criteria (experience, employment type, etc.)
            criteria = {}
            criteria_list = soup.select('.description__job-criteria-item') or \
                           soup.select('.job-criteria__item')
            
            for item in criteria_list:
                label = item.select_one('.description__job-criteria-subheader, h3')
                value = item.select_one('.description__job-criteria-text, span')
                if label and value:
                    criteria[label.get_text(strip=True)] = value.get_text(strip=True)
            
            return JobPosting(
                title=title,
                company_name=company_name,
                source=self.SOURCE_NAME,
                source_url=url,
                source_id=job_id,
                location=location,
                description=description,
                experience_level=criteria.get('경력 수준', criteria.get('Seniority level', '')),
                employment_type=criteria.get('고용 형태', criteria.get('Employment type', '')),
                job_category=criteria.get('직무', criteria.get('Job function', '')),
                raw_data={'criteria': criteria}
            )
            
        except Exception as e:
            logger.error(f"LinkedIn detail error for {job_id}: {e}")
            return None
