#!/usr/bin/env python3
"""
TechRadar Advanced - Report Generation Script
Generates summary reports and metrics
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self):
        self.current_time = datetime.now(timezone.utc)
    
    def load_data(self) -> Dict:
        """Load all available data"""
        data = {}
        
        # Load processed articles
        try:
            with open('data/processed-articles.json', 'r', encoding='utf-8') as f:
                data['articles'] = json.load(f)
        except FileNotFoundError:
            data['articles'] = {}
        
        # Load trending data
        try:
            with open('today/trending.json', 'r', encoding='utf-8') as f:
                data['trending'] = json.load(f)
        except FileNotFoundError:
            data['trending'] = {}
        
        # Load analytics
        try:
            with open('analysis/sentiment-trends.json', 'r', encoding='utf-8') as f:
                data['analytics'] = json.load(f)
        except FileNotFoundError:
            data['analytics'] = {}
        
        return data
    
    def generate_summary_report(self, data: Dict) -> str:
        """Generate a summary report"""
        articles = data.get('articles', {}).get('articles', [])
        trending = data.get('trending', {})
        
        report = f"# 📊 TechRadar Advanced - Summary Report\n\n"
        report += f"**Generated**: {self.current_time.strftime('%B %d, %Y at %H:%M UTC')}\n\n"
        
        # Basic statistics
        total_articles = len(articles)
        report += f"## 📈 Basic Statistics\n\n"
        report += f"- **Total Articles Processed**: {total_articles}\n"
        
        if articles:
            # Category breakdown
            categories = {}
            for article in articles:
                for category in article.get('categories', []):
                    categories[category] = categories.get(category, 0) + 1
            
            report += f"- **Categories Covered**: {len(categories)}\n"
            report += f"- **Top Category**: {max(categories.items(), key=lambda x: x[1])[0] if categories else 'N/A'}\n"
            
            # Sentiment analysis
            sentiments = [article.get('sentiment', 0.5) for article in articles]
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.5
            positive_articles = len([s for s in sentiments if s > 0.6])
            
            report += f"- **Average Sentiment**: {avg_sentiment:.2f}\n"
            report += f"- **Positive Articles**: {positive_articles}/{total_articles} ({positive_articles/total_articles*100:.1f}%)\n"
            
            # Impact analysis
            impact_scores = [article.get('impact_score', 0) for article in articles]
            avg_impact = sum(impact_scores) / len(impact_scores) if impact_scores else 0
            high_impact = len([s for s in impact_scores if s >= 8.0])
            
            report += f"- **Average Impact Score**: {avg_impact:.1f}/10\n"
            report += f"- **High Impact Articles**: {high_impact}/{total_articles} ({high_impact/total_articles*100:.1f}%)\n"
        
        # Trending topics
        if trending.get('trending_topics'):
            report += f"\n## 🔥 Trending Topics\n\n"
            for topic in trending['trending_topics'][:5]:
                report += f"- **{topic['topic']}**: {topic['mentions']} mentions ({topic['change']})\n"
        
        # Top companies
        if trending.get('top_companies'):
            report += f"\n## 🏢 Top Companies\n\n"
            for company in trending['top_companies'][:5]:
                report += f"- **{company['name']}**: {company['mentions']} mentions\n"
        
        # Data quality metrics
        report += f"\n## ✅ Data Quality\n\n"
        
        # Check for required files
        required_files = [
            'today/latest.md',
            'today/trending.json',
            'data/processed-articles.json'
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                report += f"- ✅ {file_path}: {file_size:,} bytes\n"
            else:
                report += f"- ❌ {file_path}: Missing\n"
        
        # Recent activity
        report += f"\n## 📅 Recent Activity\n\n"
        report += f"- **Last Update**: {self.current_time.strftime('%Y-%m-%d %H:%M UTC')}\n"
        report += f"- **Next Scheduled Update**: {(self.current_time.replace(minute=0, second=0, microsecond=0).replace(hour=self.current_time.hour + 1)).strftime('%Y-%m-%d %H:%M UTC')}\n"
        
        return report
    
    def generate_metrics_json(self, data: Dict) -> Dict:
        """Generate metrics in JSON format"""
        articles = data.get('articles', {}).get('articles', [])
        
        metrics = {
            'timestamp': self.current_time.isoformat(),
            'total_articles': len(articles),
            'categories': {},
            'sources': {},
            'sentiment_distribution': {
                'positive': 0,
                'neutral': 0,
                'negative': 0
            },
            'impact_distribution': {
                'high': 0,
                'medium': 0,
                'low': 0
            }
        }
        
        if articles:
            # Category distribution
            for article in articles:
                for category in article.get('categories', []):
                    metrics['categories'][category] = metrics['categories'].get(category, 0) + 1
            
            # Source distribution
            for article in articles:
                source = article.get('source', 'Unknown')
                metrics['sources'][source] = metrics['sources'].get(source, 0) + 1
            
            # Sentiment distribution
            for article in articles:
                sentiment = article.get('sentiment', 0.5)
                if sentiment > 0.6:
                    metrics['sentiment_distribution']['positive'] += 1
                elif sentiment < 0.4:
                    metrics['sentiment_distribution']['negative'] += 1
                else:
                    metrics['sentiment_distribution']['neutral'] += 1
            
            # Impact distribution
            for article in articles:
                impact = article.get('impact_score', 0)
                if impact >= 8.0:
                    metrics['impact_distribution']['high'] += 1
                elif impact >= 5.0:
                    metrics['impact_distribution']['medium'] += 1
                else:
                    metrics['impact_distribution']['low'] += 1
        
        return metrics
    
    def save_reports(self, summary_report: str, metrics: Dict):
        """Save generated reports"""
        try:
            os.makedirs('data', exist_ok=True)
            
            # Save summary report
            with open('data/summary-report.md', 'w', encoding='utf-8') as f:
                f.write(summary_report)
            
            # Save metrics
            with open('data/metrics.json', 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)
            
            logger.info("Reports saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving reports: {e}")

def main():
    """Main function to generate reports"""
    generator = ReportGenerator()
    
    try:
        # Load data
        data = generator.load_data()
        
        # Generate reports
        summary_report = generator.generate_summary_report(data)
        metrics = generator.generate_metrics_json(data)
        
        # Save reports
        generator.save_reports(summary_report, metrics)
        
        logger.info("Report generation completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main()
