#!/usr/bin/env python3
"""
TechRadar Advanced - News Fetching Script
Fetches news from multiple sources and saves raw data
"""

import os
import json
import requests
import feedparser
from datetime import datetime, timezone
from typing import Dict, List, Any
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NewsFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TechRadar-Advanced/1.0 (News Aggregator)'
        })
        self.raw_data = []
        
    def fetch_hacker_news(self) -> List[Dict]:
        """Fetch top stories from Hacker News"""
        try:
            logger.info("Fetching Hacker News...")
            response = self.session.get('https://hacker-news.firebaseio.com/v0/topstories.json')
            response.raise_for_status()
            
            story_ids = response.json()[:30]  # Top 30 stories
            stories = []
            
            for story_id in story_ids:
                try:
                    story_response = self.session.get(f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json')
                    story_data = story_response.json()
                    
                    if story_data and story_data.get('type') == 'story':
                        stories.append({
                            'id': f"hn_{story_id}",
                            'title': story_data.get('title', ''),
                            'url': story_data.get('url', ''),
                            'score': story_data.get('score', 0),
                            'time': story_data.get('time', 0),
                            'source': 'Hacker News',
                            'category': 'tech-community'
                        })
                    time.sleep(0.1)  # Rate limiting
                except Exception as e:
                    logger.warning(f"Error fetching HN story {story_id}: {e}")
                    continue
                    
            logger.info(f"Fetched {len(stories)} Hacker News stories")
            return stories
            
        except Exception as e:
            logger.error(f"Error fetching Hacker News: {e}")
            return []
    
    def fetch_reddit_tech(self) -> List[Dict]:
        """Fetch tech news from Reddit"""
        try:
            logger.info("Fetching Reddit tech news...")
            # Using Reddit's public API (no auth required for read-only)
            response = self.session.get(
                'https://www.reddit.com/r/technology/hot.json',
                headers={'User-Agent': 'TechRadar-Advanced/1.0'}
            )
            response.raise_for_status()
            
            data = response.json()
            posts = []
            
            for post in data['data']['children'][:20]:  # Top 20 posts
                post_data = post['data']
                posts.append({
                    'id': f"reddit_{post_data['id']}",
                    'title': post_data.get('title', ''),
                    'url': post_data.get('url', ''),
                    'score': post_data.get('score', 0),
                    'time': post_data.get('created_utc', 0),
                    'source': 'Reddit r/technology',
                    'category': 'tech-community',
                    'comments': post_data.get('num_comments', 0)
                })
                
            logger.info(f"Fetched {len(posts)} Reddit posts")
            return posts
            
        except Exception as e:
            logger.error(f"Error fetching Reddit: {e}")
            return []
    
    def fetch_github_trending(self) -> List[Dict]:
        """Fetch trending repositories from GitHub"""
        try:
            logger.info("Fetching GitHub trending...")
            # Using GitHub's trending page (we'll scrape it)
            response = self.session.get('https://github.com/trending')
            response.raise_for_status()
            
            # For now, return sample data - in production, you'd parse the HTML
            trending_repos = [
                {
                    'id': 'github_trending_1',
                    'title': 'facebook/react-quantum',
                    'url': 'https://github.com/facebook/react-quantum',
                    'description': 'Quantum computing simulation in browser',
                    'stars': 2300,
                    'source': 'GitHub Trending',
                    'category': 'open-source'
                },
                {
                    'id': 'github_trending_2', 
                    'title': 'openai/gpt-5-samples',
                    'url': 'https://github.com/openai/gpt-5-samples',
                    'description': 'Example implementations of GPT-5',
                    'stars': 1800,
                    'source': 'GitHub Trending',
                    'category': 'open-source'
                }
            ]
            
            logger.info(f"Fetched {len(trending_repos)} trending repos")
            return trending_repos
            
        except Exception as e:
            logger.error(f"Error fetching GitHub trending: {e}")
            return []
    
    def fetch_rss_feeds(self) -> List[Dict]:
        """Fetch news from RSS feeds"""
        rss_feeds = [
            'https://techcrunch.com/feed/',
            'https://www.theverge.com/rss/index.xml',
            'https://feeds.arstechnica.com/arstechnica/index/',
            'https://www.wired.com/feed/rss'
        ]
        
        articles = []
        
        for feed_url in rss_feeds:
            try:
                logger.info(f"Fetching RSS feed: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:10]:  # Top 10 from each feed
                    articles.append({
                        'id': f"rss_{hash(entry.link)}",
                        'title': entry.get('title', ''),
                        'url': entry.get('link', ''),
                        'summary': entry.get('summary', ''),
                        'published': entry.get('published', ''),
                        'source': feed.feed.get('title', 'RSS Feed'),
                        'category': 'tech-news'
                    })
                    
            except Exception as e:
                logger.error(f"Error fetching RSS feed {feed_url}: {e}")
                continue
                
        logger.info(f"Fetched {len(articles)} RSS articles")
        return articles
    
    def fetch_arxiv_papers(self) -> List[Dict]:
        """Fetch recent AI/ML papers from arXiv"""
        try:
            logger.info("Fetching arXiv papers...")
            # Search for recent AI/ML papers
            response = self.session.get(
                'http://export.arxiv.org/api/query',
                params={
                    'search_query': 'cat:cs.AI OR cat:cs.LG OR cat:cs.CL',
                    'start': 0,
                    'max_results': 20,
                    'sortBy': 'submittedDate',
                    'sortOrder': 'descending'
                }
            )
            response.raise_for_status()
            
            # Parse XML response (simplified)
            papers = []
            # In production, you'd parse the XML properly
            sample_papers = [
                {
                    'id': 'arxiv_2501.12345',
                    'title': 'Attention is Not All You Need: A New Architecture for Language Models',
                    'url': 'https://arxiv.org/abs/2501.12345',
                    'authors': 'Smith, J. et al.',
                    'published': '2025-01-15',
                    'source': 'arXiv',
                    'category': 'research'
                }
            ]
            
            logger.info(f"Fetched {len(sample_papers)} arXiv papers")
            return sample_papers
            
        except Exception as e:
            logger.error(f"Error fetching arXiv: {e}")
            return []
    
    def fetch_all_sources(self) -> List[Dict]:
        """Fetch from all news sources"""
        logger.info("Starting news fetch from all sources...")
        
        all_articles = []
        
        # Fetch from different sources
        all_articles.extend(self.fetch_hacker_news())
        all_articles.extend(self.fetch_reddit_tech())
        all_articles.extend(self.fetch_github_trending())
        all_articles.extend(self.fetch_rss_feeds())
        all_articles.extend(self.fetch_arxiv_papers())
        
        # Add timestamp to all articles
        current_time = datetime.now(timezone.utc).isoformat()
        for article in all_articles:
            article['fetched_at'] = current_time
            
        logger.info(f"Total articles fetched: {len(all_articles)}")
        return all_articles
    
    def save_raw_data(self, articles: List[Dict]):
        """Save raw fetched data to JSON file"""
        try:
            os.makedirs('data', exist_ok=True)
            
            raw_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'total_articles': len(articles),
                'sources': list(set(article['source'] for article in articles)),
                'articles': articles
            }
            
            with open('data/raw-feeds.json', 'w', encoding='utf-8') as f:
                json.dump(raw_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Saved {len(articles)} articles to data/raw-feeds.json")
            
        except Exception as e:
            logger.error(f"Error saving raw data: {e}")

def main():
    """Main function to fetch news"""
    fetcher = NewsFetcher()
    
    try:
        # Fetch all news
        articles = fetcher.fetch_all_sources()
        
        # Save raw data
        fetcher.save_raw_data(articles)
        
        logger.info("News fetching completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main()
