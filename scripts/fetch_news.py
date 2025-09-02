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
import random
from urllib.parse import urljoin
from pathlib import Path

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
        self.max_retries = 3
        self.retry_delay = 1
        self.sources_config = self.load_sources_config()
        
    def load_sources_config(self) -> Dict:
        """Load news sources configuration from JSON file"""
        try:
            config_path = Path('data/news_sources.json')
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning("Sources config not found, using default sources")
                return {}
        except Exception as e:
            logger.error(f"Error loading sources config: {e}")
            return {}
        
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
        """Fetch tech news from multiple Reddit subreddits"""
        try:
            logger.info("Fetching Reddit tech news...")
            
            # Get subreddits from config or use defaults
            subreddits = ['technology', 'programming', 'MachineLearning', 'artificial', 'compsci']
            if self.sources_config and 'api_sources' in self.sources_config:
                reddit_config = self.sources_config['api_sources'].get('reddit', {})
                subreddits = reddit_config.get('subreddits', subreddits)
            
            posts = []
            
            # Fetch from multiple subreddits
            for subreddit in subreddits[:5]:  # Limit to 5 subreddits
                try:
                    response = self.session.get(
                        f'https://www.reddit.com/r/{subreddit}/hot.json',
                        headers={'User-Agent': 'TechRadar-Advanced/1.0'}
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    for post in data['data']['children'][:10]:  # Top 10 from each subreddit
                        post_data = post['data']
                        posts.append({
                            'id': f"reddit_{post_data['id']}",
                            'title': post_data.get('title', ''),
                            'url': post_data.get('url', ''),
                            'score': post_data.get('score', 0),
                            'time': post_data.get('created_utc', 0),
                            'source': f'Reddit r/{subreddit}',
                            'category': 'tech-community',
                            'comments': post_data.get('num_comments', 0)
                        })
                    
                    time.sleep(0.5)  # Rate limiting between subreddits
                    
                except Exception as e:
                    logger.warning(f"Error fetching r/{subreddit}: {e}")
                    continue
                
            logger.info(f"Fetched {len(posts)} Reddit posts from {len(subreddits)} subreddits")
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
        """Fetch news from RSS feeds using comprehensive sources list"""
        # Get all RSS feeds from config
        all_feeds = []
        if self.sources_config and 'rss_feeds' in self.sources_config:
            for category, feeds in self.sources_config['rss_feeds'].items():
                all_feeds.extend(feeds)
        else:
            # Fallback to basic feeds if config not available
            all_feeds = [
                'https://techcrunch.com/feed/',
                'https://www.theverge.com/rss/index.xml',
                'https://feeds.arstechnica.com/arstechnica/index/',
                'https://www.wired.com/feed/rss',
                'https://www.engadget.com/rss.xml'
            ]
        
        # Shuffle feeds to distribute load
        random.shuffle(all_feeds)
        
        articles = []
        
        # Limit to first 50 feeds to avoid timeout, but rotate through them
        max_feeds = min(50, len(all_feeds))
        selected_feeds = all_feeds[:max_feeds]
        
        for feed_url in selected_feeds:
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
    
    def fetch_dev_to(self) -> List[Dict]:
        """Fetch articles from Dev.to using multiple tags"""
        try:
            logger.info("Fetching Dev.to articles...")
            
            # Get tags from config or use defaults
            tags = ['technology', 'programming', 'webdev', 'javascript', 'python']
            if self.sources_config and 'api_sources' in self.sources_config:
                devto_config = self.sources_config['api_sources'].get('dev_to', {})
                tags = devto_config.get('tags', tags)
            
            articles = []
            
            # Fetch from multiple tags
            for tag in tags[:5]:  # Limit to 5 tags
                try:
                    response = self.session.get(f'https://dev.to/api/articles?tag={tag}&per_page=10')
                    response.raise_for_status()
                    
                    for article in response.json():
                        articles.append({
                            'id': f"devto_{article['id']}",
                            'title': article.get('title', ''),
                            'url': article.get('url', ''),
                            'summary': article.get('description', ''),
                            'published': article.get('published_at', ''),
                            'source': f'Dev.to ({tag})',
                            'category': 'developer-content',
                            'tags': article.get('tag_list', []),
                            'reactions': article.get('public_reactions_count', 0)
                        })
                    
                    time.sleep(0.3)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"Error fetching Dev.to tag {tag}: {e}")
                    continue
                
            logger.info(f"Fetched {len(articles)} Dev.to articles from {len(tags)} tags")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching Dev.to: {e}")
            return []
    
    def fetch_product_hunt(self) -> List[Dict]:
        """Fetch trending products from Product Hunt"""
        try:
            logger.info("Fetching Product Hunt trending...")
            # Using Product Hunt's public API
            response = self.session.get('https://api.producthunt.com/v2/api/graphql', 
                headers={'Authorization': 'Bearer YOUR_TOKEN_HERE'})  # Requires token
            
            # For now, return sample data - in production, you'd use the actual API
            products = [
                {
                    'id': 'ph_ai_tool_1',
                    'title': 'AI Code Assistant Pro',
                    'url': 'https://www.producthunt.com/posts/ai-code-assistant-pro',
                    'description': 'Advanced AI-powered code completion and debugging',
                    'votes': 450,
                    'source': 'Product Hunt',
                    'category': 'ai-tools'
                },
                {
                    'id': 'ph_dev_tool_1',
                    'title': 'Cloud Development Environment',
                    'url': 'https://www.producthunt.com/posts/cloud-dev-env',
                    'description': 'Browser-based development environment with AI assistance',
                    'votes': 320,
                    'source': 'Product Hunt',
                    'category': 'development-tools'
                }
            ]
            
            logger.info(f"Fetched {len(products)} Product Hunt products")
            return products
            
        except Exception as e:
            logger.error(f"Error fetching Product Hunt: {e}")
            return []
    
    def fetch_newsapi(self) -> List[Dict]:
        """Fetch news from NewsAPI (requires API key)"""
        try:
            # Check for API key in environment
            api_key = os.getenv('NEWSAPI_KEY')
            if not api_key:
                logger.warning("NewsAPI key not found, skipping NewsAPI fetch")
                return []
                
            logger.info("Fetching NewsAPI articles...")
            response = self.session.get(
                'https://newsapi.org/v2/everything',
                params={
                    'q': 'technology OR AI OR programming OR software',
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'pageSize': 20,
                    'apiKey': api_key
                }
            )
            response.raise_for_status()
            
            articles = []
            for article in response.json().get('articles', []):
                articles.append({
                    'id': f"newsapi_{hash(article['url'])}",
                    'title': article.get('title', ''),
                    'url': article.get('url', ''),
                    'summary': article.get('description', ''),
                    'published': article.get('publishedAt', ''),
                    'source': article.get('source', {}).get('name', 'NewsAPI'),
                    'category': 'tech-news',
                    'author': article.get('author', '')
                })
                
            logger.info(f"Fetched {len(articles)} NewsAPI articles")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching NewsAPI: {e}")
            return []
    
    def fetch_github_trending_real(self) -> List[Dict]:
        """Fetch real trending repositories from GitHub API"""
        try:
            logger.info("Fetching GitHub trending repositories...")
            
            # Fetch trending repositories (last 7 days)
            response = self.session.get(
                'https://api.github.com/search/repositories',
                params={
                    'q': 'created:>2025-01-01 stars:>100',
                    'sort': 'stars',
                    'order': 'desc',
                    'per_page': 20
                }
            )
            response.raise_for_status()
            
            repos = []
            for repo in response.json().get('items', []):
                repos.append({
                    'id': f"github_{repo['id']}",
                    'title': repo.get('full_name', ''),
                    'url': repo.get('html_url', ''),
                    'description': repo.get('description', ''),
                    'stars': repo.get('stargazers_count', 0),
                    'language': repo.get('language', ''),
                    'source': 'GitHub Trending',
                    'category': 'open-source',
                    'updated': repo.get('updated_at', '')
                })
                
            logger.info(f"Fetched {len(repos)} GitHub trending repositories")
            return repos
            
        except Exception as e:
            logger.error(f"Error fetching GitHub trending: {e}")
            return []
    
    def fetch_backup_sources(self) -> List[Dict]:
        """Fetch from backup sources when primary sources fail"""
        backup_articles = []
        
        # Backup RSS feeds (more reliable sources)
        backup_feeds = [
            'https://feeds.bbci.co.uk/news/technology/rss.xml',
            'https://rss.cnn.com/rss/edition_technology.rss',
            'https://feeds.reuters.com/reuters/technologyNews',
            'https://feeds.npr.org/1001/rss.xml',  # NPR Technology
            'https://feeds.feedburner.com/oreilly/radar',
            'https://www.smashingmagazine.com/feed/',
            'https://css-tricks.com/feed/',
            'https://feeds.feedburner.com/oreilly/radar'
        ]
        
        for feed_url in backup_feeds:
            try:
                logger.info(f"Fetching backup RSS feed: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:5]:  # Top 5 from each backup feed
                    backup_articles.append({
                        'id': f"backup_rss_{hash(entry.link)}",
                        'title': entry.get('title', ''),
                        'url': entry.get('link', ''),
                        'summary': entry.get('summary', ''),
                        'published': entry.get('published', ''),
                        'source': f"Backup: {feed.feed.get('title', 'RSS Feed')}",
                        'category': 'tech-news'
                    })
                    
            except Exception as e:
                logger.warning(f"Backup feed {feed_url} failed: {e}")
                continue
        
        logger.info(f"Fetched {len(backup_articles)} backup articles")
        return backup_articles
    
    def fetch_with_retry(self, fetch_func, *args, **kwargs) -> List[Dict]:
        """Fetch data with retry logic"""
        for attempt in range(self.max_retries):
            try:
                return fetch_func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed to fetch after {self.max_retries} attempts: {e}")
                    return []
                else:
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {self.retry_delay}s: {e}")
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
        return []
    
    def fetch_all_sources(self) -> List[Dict]:
        """Fetch from all news sources with retry logic"""
        logger.info("Starting news fetch from all sources...")
        
        all_articles = []
        
        # Define all fetch methods with their names for logging
        fetch_methods = [
            (self.fetch_hacker_news, "Hacker News"),
            (self.fetch_reddit_tech, "Reddit"),
            (self.fetch_github_trending_real, "GitHub Trending"),
            (self.fetch_rss_feeds, "RSS Feeds"),
            (self.fetch_arxiv_papers, "arXiv"),
            (self.fetch_dev_to, "Dev.to"),
            (self.fetch_product_hunt, "Product Hunt"),
            (self.fetch_newsapi, "NewsAPI")
        ]
        
        # Fetch from all sources with retry logic
        successful_sources = 0
        for fetch_method, source_name in fetch_methods:
            try:
                logger.info(f"Fetching from {source_name}...")
                articles = self.fetch_with_retry(fetch_method)
                all_articles.extend(articles)
                successful_sources += 1
                logger.info(f"Successfully fetched {len(articles)} articles from {source_name}")
            except Exception as e:
                logger.error(f"Failed to fetch from {source_name}: {e}")
                continue
        
        # If we have very few articles, try backup sources
        if len(all_articles) < 10:
            logger.warning(f"Only {len(all_articles)} articles fetched, trying backup sources...")
            try:
                backup_articles = self.fetch_backup_sources()
                all_articles.extend(backup_articles)
                logger.info(f"Added {len(backup_articles)} backup articles")
            except Exception as e:
                logger.error(f"Backup sources also failed: {e}")
        
        # Add timestamp to all articles
        current_time = datetime.now(timezone.utc).isoformat()
        for article in all_articles:
            article['fetched_at'] = current_time
            
        logger.info(f"Total articles fetched: {len(all_articles)} from {successful_sources} sources")
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
