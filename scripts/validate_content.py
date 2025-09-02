#!/usr/bin/env python3
"""
TechRadar Advanced - Content Validation Script
Validates generated content for quality and consistency
"""

import os
import json
import re
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContentValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_json_syntax(self, file_path: str) -> bool:
        """Validate JSON file syntax"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            logger.info(f"✅ JSON syntax valid: {file_path}")
            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON syntax error in {file_path}: {e}")
            return False
        except FileNotFoundError:
            self.warnings.append(f"File not found: {file_path}")
            return False
    
    def validate_markdown_structure(self, file_path: str) -> bool:
        """Validate markdown file structure"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required sections
            required_sections = [
                '# 🚀 TechRadar Update:',
                '## 🔥 Breaking This Hour',
                '## 📰 Top Stories',
                '## 📈 Trend Analysis'
            ]
            
            missing_sections = []
            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)
            
            if missing_sections:
                self.warnings.append(f"Missing sections in {file_path}: {missing_sections}")
            
            # Check for proper timestamp format
            timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC'
            if not re.search(timestamp_pattern, content):
                self.warnings.append(f"No valid timestamp found in {file_path}")
            
            # Check for broken links
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            links = re.findall(link_pattern, content)
            broken_links = []
            
            for link_text, link_url in links:
                if link_url.startswith('http') and not link_url.startswith('https://'):
                    broken_links.append(f"{link_text}: {link_url}")
            
            if broken_links:
                self.warnings.append(f"Potentially broken links in {file_path}: {broken_links}")
            
            logger.info(f"✅ Markdown structure validated: {file_path}")
            return True
            
        except FileNotFoundError:
            self.warnings.append(f"File not found: {file_path}")
            return False
        except Exception as e:
            self.errors.append(f"Error validating {file_path}: {e}")
            return False
    
    def validate_trending_data(self, trending_data: Dict) -> bool:
        """Validate trending data structure"""
        required_fields = ['timestamp', 'trending_topics', 'top_companies']
        
        for field in required_fields:
            if field not in trending_data:
                self.errors.append(f"Missing required field in trending data: {field}")
                return False
        
        # Validate trending topics structure
        for topic in trending_data.get('trending_topics', []):
            topic_fields = ['topic', 'mentions', 'change', 'sentiment']
            for field in topic_fields:
                if field not in topic:
                    self.errors.append(f"Missing field in trending topic: {field}")
                    return False
        
        # Validate company data structure
        for company in trending_data.get('top_companies', []):
            company_fields = ['name', 'mentions', 'sentiment']
            for field in company_fields:
                if field not in company:
                    self.errors.append(f"Missing field in company data: {field}")
                    return False
        
        logger.info("✅ Trending data structure validated")
        return True
    
    def validate_article_data(self, articles: List[Dict]) -> bool:
        """Validate article data structure"""
        required_fields = ['id', 'title', 'source', 'url', 'categories', 'sentiment', 'impact_score']
        
        for i, article in enumerate(articles):
            for field in required_fields:
                if field not in article:
                    self.errors.append(f"Missing field in article {i}: {field}")
                    return False
            
            # Validate sentiment range
            sentiment = article.get('sentiment', 0)
            if not (0 <= sentiment <= 1):
                self.errors.append(f"Invalid sentiment value in article {i}: {sentiment}")
                return False
            
            # Validate impact score range
            impact_score = article.get('impact_score', 0)
            if not (0 <= impact_score <= 10):
                self.errors.append(f"Invalid impact score in article {i}: {impact_score}")
                return False
        
        logger.info(f"✅ Article data validated for {len(articles)} articles")
        return True
    
    def check_file_sizes(self) -> bool:
        """Check if files are within reasonable size limits"""
        file_limits = {
            'today/latest.md': 50000,  # 50KB
            'today/trending.json': 10000,  # 10KB
            'data/processed-articles.json': 1000000,  # 1MB
            'data/raw-feeds.json': 2000000  # 2MB
        }
        
        for file_path, max_size in file_limits.items():
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                if file_size > max_size:
                    self.warnings.append(f"File {file_path} is large ({file_size} bytes)")
                else:
                    logger.info(f"✅ File size OK: {file_path} ({file_size} bytes)")
            else:
                self.warnings.append(f"File not found: {file_path}")
        
        return True
    
    def validate_all(self) -> bool:
        """Run all validation checks"""
        logger.info("Starting content validation...")
        
        # Validate JSON files
        json_files = [
            'today/trending.json',
            'data/processed-articles.json',
            'data/raw-feeds.json'
        ]
        
        for json_file in json_files:
            self.validate_json_syntax(json_file)
        
        # Validate markdown files
        markdown_files = [
            'today/latest.md'
        ]
        
        for md_file in markdown_files:
            self.validate_markdown_structure(md_file)
        
        # Validate trending data structure
        try:
            with open('today/trending.json', 'r', encoding='utf-8') as f:
                trending_data = json.load(f)
            self.validate_trending_data(trending_data)
        except Exception as e:
            self.errors.append(f"Error validating trending data: {e}")
        
        # Validate article data structure
        try:
            with open('data/processed-articles.json', 'r', encoding='utf-8') as f:
                processed_data = json.load(f)
            articles = processed_data.get('articles', [])
            self.validate_article_data(articles)
        except Exception as e:
            self.errors.append(f"Error validating article data: {e}")
        
        # Check file sizes
        self.check_file_sizes()
        
        # Report results
        if self.errors:
            logger.error(f"❌ Validation failed with {len(self.errors)} errors:")
            for error in self.errors:
                logger.error(f"  - {error}")
            return False
        
        if self.warnings:
            logger.warning(f"⚠️  Validation completed with {len(self.warnings)} warnings:")
            for warning in self.warnings:
                logger.warning(f"  - {warning}")
        else:
            logger.info("✅ All validations passed successfully!")
        
        return True

def main():
    """Main function to validate content"""
    validator = ContentValidator()
    
    try:
        success = validator.validate_all()
        
        if success:
            logger.info("Content validation completed successfully!")
            exit(0)
        else:
            logger.error("Content validation failed!")
            exit(1)
            
    except Exception as e:
        logger.error(f"Error in validation: {e}")
        exit(1)

if __name__ == "__main__":
    main()
