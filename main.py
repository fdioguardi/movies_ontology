"""Script entry point."""
from src.scraper import Scraper
from config import URLS


Scraper().scrape(URLS)
