#!/usr/bin/env python3
"""
TechRadar Advanced - Analytics Update Script
Updates analytics and metrics from processed news data
"""

import os
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AnalyticsUpdater:
    def __init__(self):
        self.current_time = datetime.now(timezone.utc)
    
    def load_processed_data(self) -> Dict:
        """Load processed news data"""
        try:
            with open('data/processed-articles.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("Processed data file not found")
            return {}
        except Exception as e:
            logger.error(f"Error loading processed data: {e}")
            return {}
    
    def load_existing_analytics(self) -> Dict:
        """Load existing analytics data"""
        try:
            with open('analysis/sentiment-trends.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'trends': [], 'daily_stats': {}}
        except Exception as e:
            logger.error(f"Error loading analytics: {e}")
            return {'trends': [], 'daily_stats': {}}
    
    def calculate_daily_stats(self, articles: List[Dict]) -> Dict:
        """Calculate daily statistics"""
        today = self.current_time.strftime('%Y-%m-%d')
        
        # Basic counts
        total_articles = len(articles)
        
        # Category distribution
        category_counts = {}
        for article in articles:
            for category in article.get('categories', []):
                category_counts[category] = category_counts.get(category, 0) + 1
        
        # Company mentions
        company_counts = {}
        for article in articles:
            for company in article.get('companies', []):
                company_counts[company] = company_counts.get(company, 0) + 1
        
        # Sentiment analysis
        sentiments = [article.get('sentiment', 0.5) for article in articles]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.5
        
        # Impact scores
        impact_scores = [article.get('impact_score', 0) for article in articles]
        avg_impact = sum(impact_scores) / len(impact_scores) if impact_scores else 0
        
        # Source distribution
        source_counts = {}
        for article in articles:
            source = article.get('source', 'Unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        return {
            'date': today,
            'total_articles': total_articles,
            'category_distribution': category_counts,
            'top_companies': dict(sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            'average_sentiment': round(avg_sentiment, 2),
            'average_impact': round(avg_impact, 2),
            'source_distribution': source_counts,
            'high_impact_articles': len([a for a in articles if a.get('impact_score', 0) >= 8.0])
        }
    
    def update_sentiment_trends(self, articles: List[Dict], existing_analytics: Dict) -> Dict:
        """Update sentiment trends over time"""
        today = self.current_time.strftime('%Y-%m-%d')
        
        # Calculate today's sentiment by category
        category_sentiments = {}
        for article in articles:
            for category in article.get('categories', []):
                if category not in category_sentiments:
                    category_sentiments[category] = []
                category_sentiments[category].append(article.get('sentiment', 0.5))
        
        # Calculate averages
        avg_sentiments = {}
        for category, sentiments in category_sentiments.items():
            avg_sentiments[category] = round(sum(sentiments) / len(sentiments), 2)
        
        # Add to trends
        trends = existing_analytics.get('trends', [])
        trends.append({
            'date': today,
            'category_sentiments': avg_sentiments,
            'overall_sentiment': round(sum(avg_sentiments.values()) / len(avg_sentiments), 2) if avg_sentiments else 0.5
        })
        
        # Keep only last 30 days
        trends = trends[-30:]
        
        return {
            'trends': trends,
            'daily_stats': existing_analytics.get('daily_stats', {})
        }
    
    def update_company_mentions(self, articles: List[Dict]) -> Dict:
        """Update company mentions tracking"""
        company_data = {}
        
        for article in articles:
            for company in article.get('companies', []):
                if company not in company_data:
                    company_data[company] = {
                        'total_mentions': 0,
                        'positive_mentions': 0,
                        'negative_mentions': 0,
                        'avg_sentiment': 0,
                        'recent_articles': []
                    }
                
                company_data[company]['total_mentions'] += 1
                
                sentiment = article.get('sentiment', 0.5)
                if sentiment > 0.6:
                    company_data[company]['positive_mentions'] += 1
                elif sentiment < 0.4:
                    company_data[company]['negative_mentions'] += 1
                
                # Update recent articles (last 5)
                company_data[company]['recent_articles'].append({
                    'title': article.get('title', ''),
                    'url': article.get('url', ''),
                    'sentiment': sentiment,
                    'date': article.get('timestamp', '')
                })
                company_data[company]['recent_articles'] = company_data[company]['recent_articles'][-5:]
        
        # Calculate average sentiment for each company
        for company, data in company_data.items():
            sentiments = [article['sentiment'] for article in data['recent_articles']]
            if sentiments:
                data['avg_sentiment'] = round(sum(sentiments) / len(sentiments), 2)
        
        return company_data
    
    def generate_technology_radar(self, articles: List[Dict]) -> str:
        """Generate technology radar markdown"""
        # Analyze technology mentions and trends
        tech_mentions = {}
        tech_sentiments = {}
        
        for article in articles:
            for tech in article.get('technologies', []):
                if tech not in tech_mentions:
                    tech_mentions[tech] = 0
                    tech_sentiments[tech] = []
                
                tech_mentions[tech] += 1
                tech_sentiments[tech].append(article.get('sentiment', 0.5))
        
        # Calculate average sentiment for each technology
        tech_analysis = {}
        for tech, mentions in tech_mentions.items():
            sentiments = tech_sentiments[tech]
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.5
            
            # Determine adoption stage based on mentions and sentiment
            if mentions >= 10 and avg_sentiment >= 0.7:
                stage = "Adopt"
            elif mentions >= 5 and avg_sentiment >= 0.6:
                stage = "Trial"
            elif mentions >= 3:
                stage = "Assess"
            else:
                stage = "Hold"
            
            tech_analysis[tech] = {
                'mentions': mentions,
                'sentiment': round(avg_sentiment, 2),
                'stage': stage
            }
        
        # Generate markdown
        content = "# 🎯 Technology Radar\n\n"
        content += f"*Last updated: {self.current_time.strftime('%B %d, %Y %H:%M UTC')}*\n\n"
        
        # Group by adoption stage
        stages = {'Adopt': [], 'Trial': [], 'Assess': [], 'Hold': []}
        for tech, data in tech_analysis.items():
            stages[data['stage']].append((tech, data))
        
        for stage, technologies in stages.items():
            if technologies:
                content += f"## {stage}\n\n"
                # Sort by mentions
                technologies.sort(key=lambda x: x[1]['mentions'], reverse=True)
                
                for tech, data in technologies:
                    sentiment_emoji = "😊" if data['sentiment'] > 0.6 else "😐" if data['sentiment'] > 0.4 else "😞"
                    content += f"- **{tech}** {sentiment_emoji} ({data['mentions']} mentions, {data['sentiment']} sentiment)\n"
                content += "\n"
        
        return content
    
    def save_analytics(self, sentiment_trends: Dict, company_mentions: Dict, tech_radar: str):
        """Save all analytics data"""
        try:
            os.makedirs('analysis', exist_ok=True)
            
            # Save sentiment trends
            with open('analysis/sentiment-trends.json', 'w', encoding='utf-8') as f:
                json.dump(sentiment_trends, f, indent=2, ensure_ascii=False)
            
            # Save company mentions
            with open('analysis/company-mentions.json', 'w', encoding='utf-8') as f:
                json.dump(company_mentions, f, indent=2, ensure_ascii=False)
            
            # Save technology radar
            with open('analysis/technology-radar.md', 'w', encoding='utf-8') as f:
                f.write(tech_radar)
            
            logger.info("Analytics data saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving analytics: {e}")

def main():
    """Main function to update analytics"""
    updater = AnalyticsUpdater()
    
    try:
        # Load processed data
        processed_data = updater.load_processed_data()
        if not processed_data or 'articles' not in processed_data:
            logger.error("No processed data to analyze")
            return
        
        articles = processed_data['articles']
        logger.info(f"Updating analytics for {len(articles)} articles")
        
        # Load existing analytics
        existing_analytics = updater.load_existing_analytics()
        
        # Calculate daily stats
        daily_stats = updater.calculate_daily_stats(articles)
        existing_analytics['daily_stats'][daily_stats['date']] = daily_stats
        
        # Update sentiment trends
        sentiment_trends = updater.update_sentiment_trends(articles, existing_analytics)
        
        # Update company mentions
        company_mentions = updater.update_company_mentions(articles)
        
        # Generate technology radar
        tech_radar = updater.generate_technology_radar(articles)
        
        # Save analytics
        updater.save_analytics(sentiment_trends, company_mentions, tech_radar)
        
        logger.info("Analytics update completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main()
