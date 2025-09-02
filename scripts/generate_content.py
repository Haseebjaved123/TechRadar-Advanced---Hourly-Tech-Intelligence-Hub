#!/usr/bin/env python3
"""
TechRadar Advanced - Content Generation Script
Generates formatted markdown content from processed news data
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContentGenerator:
    def __init__(self):
        self.current_time = datetime.now(timezone.utc)
        self.next_hour = self.current_time.replace(minute=0, second=0, microsecond=0)
        self.next_hour = self.next_hour.replace(hour=self.next_hour.hour + 1)
    
    def load_processed_data(self) -> Dict:
        """Load processed news data"""
        try:
            with open('data/processed-articles.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("Processed data file not found. Run process_news.py first.")
            return {}
        except Exception as e:
            logger.error(f"Error loading processed data: {e}")
            return {}
    
    def get_top_articles(self, articles: List[Dict], limit: int = 10) -> List[Dict]:
        """Get top articles by impact score"""
        return sorted(articles, key=lambda x: x.get('impact_score', 0), reverse=True)[:limit]
    
    def get_breaking_news(self, articles: List[Dict]) -> List[Dict]:
        """Get breaking news (high impact, recent)"""
        breaking = []
        for article in articles:
            if (article.get('impact_score', 0) >= 8.0 and 
                'breakthrough' in article.get('title', '').lower() or
                'announce' in article.get('title', '').lower() or
                'launch' in article.get('title', '').lower()):
                breaking.append(article)
        return breaking[:3]  # Top 3 breaking news
    
    def get_trending_topics(self, articles: List[Dict]) -> Dict[str, Any]:
        """Analyze trending topics from articles"""
        topic_counts = {}
        company_counts = {}
        sentiment_scores = {}
        
        for article in articles:
            # Count categories
            for category in article.get('categories', []):
                topic_counts[category] = topic_counts.get(category, 0) + 1
            
            # Count companies
            for company in article.get('companies', []):
                company_counts[company] = company_counts.get(company, 0) + 1
            
            # Aggregate sentiment by category
            for category in article.get('categories', []):
                if category not in sentiment_scores:
                    sentiment_scores[category] = []
                sentiment_scores[category].append(article.get('sentiment', 0.5))
        
        # Calculate average sentiment
        avg_sentiment = {}
        for category, scores in sentiment_scores.items():
            avg_sentiment[category] = round(sum(scores) / len(scores), 2)
        
        # Sort by count
        trending_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_companies = sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:6]
        
        return {
            'trending_topics': trending_topics,
            'top_companies': top_companies,
            'sentiment_scores': avg_sentiment
        }
    
    def format_article(self, article: Dict, index: int = None) -> str:
        """Format a single article for markdown"""
        title = article.get('title', 'No Title')
        source = article.get('source', 'Unknown Source')
        url = article.get('url', '#')
        categories = ', '.join(article.get('categories', []))
        companies = ', '.join(article.get('companies', []))
        impact_score = article.get('impact_score', 0)
        summary = article.get('summary', '')
        
        # Impact indicator
        if impact_score >= 8:
            impact_emoji = "🔴"
            impact_text = "Critical"
        elif impact_score >= 6:
            impact_emoji = "🟡"
            impact_text = "High"
        else:
            impact_emoji = "🟢"
            impact_text = "Medium"
        
        # Format the article
        formatted = f"### {index + 1 if index is not None else ''} {title}\n"
        formatted += f"**Source**: {source} | **Impact**: {impact_emoji} {impact_text}\n"
        
        if categories:
            formatted += f"**Categories**: {categories}\n"
        if companies:
            formatted += f"**Companies**: {companies}\n"
        
        if summary:
            formatted += f"- {summary}\n"
        
        formatted += f"- [Read More]({url})\n"
        
        return formatted
    
    def generate_latest_md(self, articles: List[Dict]) -> str:
        """Generate the latest.md content"""
        timestamp = self.current_time.strftime("%B %d, %Y - %H:00 UTC")
        next_update = self.next_hour.strftime("%B %d, %Y - %H:00 UTC")
        
        # Get breaking news and top stories
        breaking_news = self.get_breaking_news(articles)
        top_stories = self.get_top_articles(articles, 5)
        
        # Generate content
        content = f"# 🚀 TechRadar Update: {timestamp}\n\n"
        
        # Breaking news section
        if breaking_news:
            content += "## 🔥 Breaking This Hour\n\n"
            for article in breaking_news:
                content += self.format_article(article) + "\n"
        
        # Top stories section
        content += "## 📰 Top Stories\n\n"
        for i, article in enumerate(top_stories):
            content += self.format_article(article, i) + "\n"
        
        # Research papers section
        research_articles = [a for a in articles if 'research' in a.get('categories', []) or 'arxiv' in a.get('source', '').lower()]
        if research_articles:
            content += "## 🔬 Research Papers\n"
            for article in research_articles[:3]:
                content += f"- **\"{article.get('title', '')}\"** - {article.get('source', '')}\n"
            content += "\n"
        
        # Trending repositories section
        github_articles = [a for a in articles if 'github' in a.get('source', '').lower()]
        if github_articles:
            content += "## 💻 Trending Repositories\n"
            for i, article in enumerate(github_articles[:3], 1):
                stars = article.get('original_data', {}).get('stars', 0)
                content += f"{i}. **{article.get('title', '')}** - {article.get('summary', '')} (⭐ {stars} today)\n"
            content += "\n"
        
        # Market movements (placeholder)
        content += "## 📊 Market Movements\n"
        content += "- NVDA ↑ 3.2% (New AI chip announcement)\n"
        content += "- MSFT ↑ 1.8% (Azure Quantum expansion)\n"
        content += "- Crypto: ETH ↑ 5% (Layer 2 breakthrough)\n\n"
        
        # Developer opportunities (placeholder)
        content += "## 🎯 Developer Opportunities\n"
        content += "- **Google** hiring for Quantum ML team (Remote)\n"
        content += "- **OpenAI** Grant program for AGI safety research ($10M)\n"
        content += "- **Hackathon**: NASA Space Apps - AI for Mars exploration\n\n"
        
        # Trend analysis
        content += "## 📈 Trend Analysis\n"
        content += "```mermaid\n"
        content += "graph TD\n"
        content += "    A[AI/ML] --> B[Quantum Computing]\n"
        content += "    A --> C[Neuromorphic Chips]\n"
        content += "    B --> D[Superconductors]\n"
        content += "    C --> E[Edge Computing]\n"
        content += "    D --> F[Energy Efficiency]\n"
        content += "    E --> F\n"
        content += "```\n\n"
        
        # Footer
        content += "---\n"
        content += f"*Last updated: {timestamp}*\n"
        content += f"*Next update: {next_update}*\n"
        
        return content
    
    def generate_trending_json(self, articles: List[Dict]) -> Dict:
        """Generate trending.json data"""
        trending_data = self.get_trending_topics(articles)
        
        # Format trending topics
        formatted_topics = []
        for topic, count in trending_data['trending_topics']:
            sentiment = trending_data['sentiment_scores'].get(topic, 0.5)
            formatted_topics.append({
                'topic': topic.replace('-', ' ').title(),
                'mentions': count,
                'change': f"+{count * 10}%",  # Placeholder calculation
                'sentiment': sentiment,
                'key_articles': [a['title'] for a in articles if topic in a.get('categories', [])][:3]
            })
        
        # Format top companies
        formatted_companies = []
        for company, count in trending_data['top_companies']:
            # Calculate average sentiment for this company
            company_articles = [a for a in articles if company.lower() in [c.lower() for c in a.get('companies', [])]]
            avg_sentiment = sum(a.get('sentiment', 0.5) for a in company_articles) / len(company_articles) if company_articles else 0.5
            
            formatted_companies.append({
                'name': company,
                'mentions': count,
                'sentiment': round(avg_sentiment, 2)
            })
        
        return {
            'timestamp': self.current_time.isoformat(),
            'trending_topics': formatted_topics,
            'top_companies': formatted_companies,
            'emerging_technologies': [
                'DNA Storage',
                'Quantum Internet', 
                'Neural Interfaces',
                'Space-Based Computing',
                'Biocomputing'
            ]
        }
    
    def save_content(self, latest_content: str, trending_data: Dict):
        """Save generated content to files"""
        try:
            # Save latest.md
            with open('today/latest.md', 'w', encoding='utf-8') as f:
                f.write(latest_content)
            logger.info("Saved today/latest.md")
            
            # Save trending.json
            with open('today/trending.json', 'w', encoding='utf-8') as f:
                json.dump(trending_data, f, indent=2, ensure_ascii=False)
            logger.info("Saved today/trending.json")
            
        except Exception as e:
            logger.error(f"Error saving content: {e}")

def main():
    """Main function to generate content"""
    generator = ContentGenerator()
    
    try:
        # Load processed data
        processed_data = generator.load_processed_data()
        if not processed_data or 'articles' not in processed_data:
            logger.error("No processed data to generate content from")
            return
        
        articles = processed_data['articles']
        logger.info(f"Generating content for {len(articles)} articles")
        
        # Generate content
        latest_content = generator.generate_latest_md(articles)
        trending_data = generator.generate_trending_json(articles)
        
        # Save content
        generator.save_content(latest_content, trending_data)
        
        logger.info("Content generation completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main()
