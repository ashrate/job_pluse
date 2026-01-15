# Job Crawlers Package
from app.crawlers.base import BaseCrawler, JobPosting
from app.crawlers.jobkorea import JobKoreaCrawler
from app.crawlers.wanted import WantedCrawler
from app.crawlers.jobplanet import JobPlanetCrawler
from app.crawlers.linkedin import LinkedInCrawler
from app.crawlers.manager import CrawlerManager

__all__ = [
    'BaseCrawler',
    'JobPosting',
    'JobKoreaCrawler',
    'WantedCrawler',
    'JobPlanetCrawler',
    'LinkedInCrawler',
    'CrawlerManager'
]
