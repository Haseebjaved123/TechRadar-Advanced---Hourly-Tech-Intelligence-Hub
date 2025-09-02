#!/usr/bin/env python3
"""
TechRadar Advanced - Source Testing Script
Tests all news sources to ensure they're working properly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.fetch_news import NewsFetcher
import json
import time

def test_sources():
    """Test all news sources and report results"""
    print("TechRadar Advanced - Source Testing")
    print("=" * 50)
    
    fetcher = NewsFetcher()
    
    # Test individual sources
    sources_to_test = [
        ("Hacker News", fetcher.fetch_hacker_news),
        ("Reddit Tech", fetcher.fetch_reddit_tech),
        ("GitHub Trending", fetcher.fetch_github_trending_real),
        ("RSS Feeds", fetcher.fetch_rss_feeds),
        ("arXiv Papers", fetcher.fetch_arxiv_papers),
        ("Dev.to", fetcher.fetch_dev_to),
        ("Product Hunt", fetcher.fetch_product_hunt),
        ("NewsAPI", fetcher.fetch_newsapi),
        ("Backup Sources", fetcher.fetch_backup_sources)
    ]
    
    results = {}
    total_articles = 0
    
    for source_name, fetch_method in sources_to_test:
        print(f"\nTesting {source_name}...")
        try:
            start_time = time.time()
            articles = fetch_method()
            end_time = time.time()
            
            results[source_name] = {
                'status': 'success',
                'articles_count': len(articles),
                'time_taken': round(end_time - start_time, 2),
                'sample_titles': [article.get('title', 'No title')[:50] + '...' for article in articles[:3]]
            }
            
            total_articles += len(articles)
            print(f"✅ {source_name}: {len(articles)} articles in {results[source_name]['time_taken']}s")
            
        except Exception as e:
            results[source_name] = {
                'status': 'failed',
                'error': str(e),
                'articles_count': 0,
                'time_taken': 0
            }
            print(f"❌ {source_name}: Failed - {e}")
    
    # Test full fetch
    print(f"\n{'='*50}")
    print("Testing full fetch from all sources...")
    try:
        start_time = time.time()
        all_articles = fetcher.fetch_all_sources()
        end_time = time.time()
        
        print(f"✅ Full fetch: {len(all_articles)} total articles in {round(end_time - start_time, 2)}s")
        
        # Save test results
        test_results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'individual_sources': results,
            'full_fetch': {
                'total_articles': len(all_articles),
                'time_taken': round(end_time - start_time, 2),
                'sources_used': list(set(article.get('source', 'Unknown') for article in all_articles))
            }
        }
        
        with open('data/source_test_results.json', 'w') as f:
            json.dump(test_results, f, indent=2)
        
        print(f"\n📊 Test Results Summary:")
        print(f"Total articles fetched: {len(all_articles)}")
        print(f"Sources working: {sum(1 for r in results.values() if r['status'] == 'success')}")
        print(f"Sources failed: {sum(1 for r in results.values() if r['status'] == 'failed')}")
        print(f"Unique sources: {len(test_results['full_fetch']['sources_used'])}")
        
        print(f"\n📁 Results saved to: data/source_test_results.json")
        
    except Exception as e:
        print(f"❌ Full fetch failed: {e}")
    
    return results

if __name__ == "__main__":
    test_sources()
