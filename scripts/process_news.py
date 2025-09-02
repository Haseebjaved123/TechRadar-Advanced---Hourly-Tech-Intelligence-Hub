#!/usr/bin/env python3
"""
TechRadar Advanced - News Processing Script
Processes raw news data, categorizes, and analyzes sentiment
"""

import os
import json
import re
from datetime import datetime, timezone
from typing import Dict, List, Any, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NewsProcessor:
    def __init__(self):
        self.categories = {
            'ai-ml': ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 'neural network', 'gpt', 'llm', 'transformer', 'openai', 'chatgpt'],
            'quantum-computing': ['quantum', 'qubit', 'superconductor', 'quantum computer', 'quantum algorithm', 'ibm quantum', 'google quantum'],
            'blockchain-web3': ['blockchain', 'cryptocurrency', 'bitcoin', 'ethereum', 'web3', 'defi', 'nft', 'smart contract', 'crypto'],
            'cybersecurity': ['security', 'cybersecurity', 'hack', 'breach', 'vulnerability', 'malware', 'ransomware', 'zero-day'],
            'biotech': ['biotech', 'biotechnology', 'genetics', 'dna', 'gene therapy', 'crispr', 'pharmaceutical', 'medical device'],
            'robotics': ['robot', 'robotics', 'automation', 'tesla', 'optimus', 'boston dynamics', 'autonomous vehicle', 'drone'],
            'space-tech': ['space', 'nasa', 'spacex', 'satellite', 'rocket', 'mars', 'space station', 'astronaut'],
            'emerging-tech': ['ar', 'vr', 'metaverse', 'iot', '5g', '6g', 'neuromorphic', 'edge computing', 'cloud computing']
        }
        
        self.companies = [
            'openai', 'google', 'microsoft', 'apple', 'meta', 'tesla', 'amazon', 'nvidia', 'intel', 'amd',
            'ibm', 'oracle', 'salesforce', 'netflix', 'uber', 'airbnb', 'twitter', 'linkedin', 'github',
            'docker', 'kubernetes', 'redis', 'mongodb', 'elasticsearch', 'apache', 'linux', 'ubuntu'
        ]
        
        self.technologies = [
            'python', 'javascript', 'react', 'vue', 'angular', 'node.js', 'docker', 'kubernetes',
            'aws', 'azure', 'gcp', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
            'git', 'github', 'gitlab', 'jenkins', 'terraform', 'ansible', 'prometheus', 'grafana'
        ]
    
    def load_raw_data(self) -> Dict:
        """Load raw news data"""
        try:
            with open('data/raw-feeds.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("Raw data file not found. Run fetch_news.py first.")
            return {}
        except Exception as e:
            logger.error(f"Error loading raw data: {e}")
            return {}
    
    def categorize_article(self, title: str, content: str = "") -> List[str]:
        """Categorize article based on title and content"""
        text = ((title or "") + " " + (content or "")).lower()
        categories = []
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in text:
                    categories.append(category)
                    break
        
        # Default category if no match
        if not categories:
            categories = ['emerging-tech']
            
        return categories
    
    def extract_entities(self, title: str, content: str = "") -> Dict[str, List[str]]:
        """Extract companies and technologies mentioned"""
        text = ((title or "") + " " + (content or "")).lower()
        
        mentioned_companies = []
        mentioned_technologies = []
        
        for company in self.companies:
            if company in text:
                mentioned_companies.append(company.title())
        
        for tech in self.technologies:
            if tech in text:
                mentioned_technologies.append(tech)
        
        return {
            'companies': list(set(mentioned_companies)),
            'technologies': list(set(mentioned_technologies))
        }
    
    def calculate_sentiment(self, title: str, content: str = "") -> float:
        """Simple sentiment analysis (0.0 = negative, 1.0 = positive)"""
        text = ((title or "") + " " + (content or "")).lower()
        
        positive_words = [
            'breakthrough', 'revolutionary', 'innovative', 'advanced', 'successful',
            'achievement', 'milestone', 'progress', 'improvement', 'enhancement',
            'launch', 'release', 'announce', 'unveil', 'introduce', 'develop',
            'create', 'build', 'achieve', 'succeed', 'win', 'gain', 'increase',
            'grow', 'expand', 'upgrade', 'optimize', 'efficient', 'fast', 'powerful'
        ]
        
        negative_words = [
            'hack', 'breach', 'vulnerability', 'security', 'attack', 'malware',
            'bug', 'error', 'failure', 'problem', 'issue', 'concern', 'risk',
            'threat', 'danger', 'crisis', 'decline', 'decrease', 'loss', 'damage',
            'broken', 'failed', 'unsuccessful', 'disappointing', 'concerning'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        total_words = positive_count + negative_count
        if total_words == 0:
            return 0.5  # Neutral sentiment
        
        sentiment = positive_count / total_words
        return round(sentiment, 2)
    
    def calculate_impact_score(self, article: Dict) -> float:
        """Calculate impact score based on various factors"""
        score = 0.0
        
        # Source credibility
        source_scores = {
            'Hacker News': 0.8,
            'TechCrunch': 0.9,
            'The Verge': 0.8,
            'Ars Technica': 0.8,
            'Wired': 0.8,
            'arXiv': 0.9,
            'Reddit r/technology': 0.6,
            'GitHub Trending': 0.7
        }
        
        source = article.get('source', '')
        score += source_scores.get(source, 0.5)
        
        # Engagement metrics
        if 'score' in article:
            score += min(article['score'] / 1000, 0.3)  # Cap at 0.3
        
        if 'comments' in article:
            score += min(article['comments'] / 100, 0.2)  # Cap at 0.2
        
        # Keywords that indicate high impact
        high_impact_keywords = [
            'breakthrough', 'revolutionary', 'first', 'new', 'announce', 'launch',
            'release', 'unveil', 'discover', 'achieve', 'milestone', 'record'
        ]
        
        title = article.get('title', '').lower()
        for keyword in high_impact_keywords:
            if keyword in title:
                score += 0.1
                break
        
        return min(round(score, 1), 10.0)  # Cap at 10.0
    
    def generate_summary(self, title: str, content: str = "") -> str:
        """Generate a brief summary of the article"""
        # Simple extractive summary (first sentence or key points)
        if content:
            sentences = content.split('.')
            if len(sentences) > 1:
                return sentences[0].strip() + "."
        
        # Fallback to title-based summary
        return f"Latest development in {title.lower()}"
    
    def extract_keywords(self, title: str, content: str = "") -> List[str]:
        """Extract relevant keywords"""
        text = ((title or "") + " " + (content or "")).lower()
        
        # Common tech keywords
        keywords = []
        tech_keywords = [
            'ai', 'ml', 'quantum', 'blockchain', 'crypto', 'security', 'cloud',
            'mobile', 'web', 'app', 'software', 'hardware', 'data', 'analytics',
            'automation', 'robotics', 'iot', 'ar', 'vr', '5g', 'api', 'database'
        ]
        
        for keyword in tech_keywords:
            if keyword in text:
                keywords.append(keyword)
        
        return keywords[:5]  # Limit to 5 keywords
    
    def process_articles(self, raw_data: Dict) -> List[Dict]:
        """Process all articles from raw data"""
        if not raw_data or 'articles' not in raw_data:
            logger.error("No articles found in raw data")
            return []
        
        processed_articles = []
        
        for article in raw_data['articles']:
            try:
                title = article.get('title', '')
                content = article.get('summary', '') or article.get('description', '')
                
                # Process the article
                processed_article = {
                    'id': article.get('id', ''),
                    'timestamp': article.get('fetched_at', datetime.now(timezone.utc).isoformat()),
                    'title': title,
                    'source': article.get('source', ''),
                    'url': article.get('url', ''),
                    'categories': self.categorize_article(title, content),
                    'sentiment': self.calculate_sentiment(title, content),
                    'impact_score': self.calculate_impact_score(article),
                    'summary': self.generate_summary(title, content),
                    'keywords': self.extract_keywords(title, content)
                }
                
                # Extract entities
                entities = self.extract_entities(title, content)
                processed_article.update(entities)
                
                # Add original data
                processed_article['original_data'] = article
                
                processed_articles.append(processed_article)
                
            except Exception as e:
                logger.error(f"Error processing article {article.get('id', 'unknown')}: {e}")
                continue
        
        logger.info(f"Processed {len(processed_articles)} articles")
        return processed_articles
    
    def save_processed_data(self, articles: List[Dict]):
        """Save processed articles to JSON file"""
        try:
            os.makedirs('data', exist_ok=True)
            
            processed_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'total_articles': len(articles),
                'articles': articles
            }
            
            with open('data/processed-articles.json', 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Saved {len(articles)} processed articles to data/processed-articles.json")
            
        except Exception as e:
            logger.error(f"Error saving processed data: {e}")

def main():
    """Main function to process news"""
    processor = NewsProcessor()
    
    try:
        # Load raw data
        raw_data = processor.load_raw_data()
        if not raw_data:
            logger.error("No raw data to process")
            return
        
        # Process articles
        processed_articles = processor.process_articles(raw_data)
        
        # Save processed data
        processor.save_processed_data(processed_articles)
        
        logger.info("News processing completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main()
