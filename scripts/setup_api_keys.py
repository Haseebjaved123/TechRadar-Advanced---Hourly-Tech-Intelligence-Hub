#!/usr/bin/env python3
"""
TechRadar Advanced - API Keys Setup Script
Helps users configure API keys for enhanced news fetching
"""

import os
import sys
from pathlib import Path

def setup_newsapi():
    """Setup NewsAPI key"""
    print("\n=== NewsAPI Setup ===")
    print("NewsAPI provides access to thousands of news sources.")
    print("Get your free API key at: https://newsapi.org/")
    print("Free tier: 1000 requests/day")
    
    api_key = input("Enter your NewsAPI key (or press Enter to skip): ").strip()
    if api_key:
        return f"NEWSAPI_KEY={api_key}"
    return None

def setup_github():
    """Setup GitHub token"""
    print("\n=== GitHub API Setup ===")
    print("GitHub token increases rate limits from 60 to 5000 requests/hour.")
    print("Create a token at: https://github.com/settings/tokens")
    print("No special permissions needed for public repositories.")
    
    token = input("Enter your GitHub token (or press Enter to skip): ").strip()
    if token:
        return f"GITHUB_TOKEN={token}"
    return None

def setup_reddit():
    """Setup Reddit API credentials"""
    print("\n=== Reddit API Setup ===")
    print("Reddit API credentials increase rate limits.")
    print("Create an app at: https://www.reddit.com/prefs/apps")
    print("Choose 'script' type application.")
    
    client_id = input("Enter your Reddit client ID (or press Enter to skip): ").strip()
    if client_id:
        client_secret = input("Enter your Reddit client secret: ").strip()
        if client_secret:
            return f"REDDIT_CLIENT_ID={client_id}\nREDDIT_CLIENT_SECRET={client_secret}"
    return None

def setup_product_hunt():
    """Setup Product Hunt token"""
    print("\n=== Product Hunt API Setup ===")
    print("Product Hunt API provides access to trending products.")
    print("Get your token at: https://api.producthunt.com/v2/oauth/applications")
    
    token = input("Enter your Product Hunt token (or press Enter to skip): ").strip()
    if token:
        return f"PRODUCT_HUNT_TOKEN={token}"
    return None

def main():
    """Main setup function"""
    print("TechRadar Advanced - API Keys Setup")
    print("=" * 40)
    print("This script helps you configure API keys for enhanced news fetching.")
    print("All API keys are optional - the system will work without them.")
    print("However, adding them will provide more reliable and frequent updates.")
    
    # Check if .env file already exists
    env_file = Path('.env')
    if env_file.exists():
        print(f"\nFound existing .env file. Backing up to .env.backup")
        env_file.rename('.env.backup')
    
    # Collect API keys
    env_vars = []
    
    # NewsAPI (most important)
    newsapi = setup_newsapi()
    if newsapi:
        env_vars.append(newsapi)
    
    # GitHub
    github = setup_github()
    if github:
        env_vars.append(github)
    
    # Reddit
    reddit = setup_reddit()
    if reddit:
        env_vars.extend(reddit.split('\n'))
    
    # Product Hunt
    ph = setup_product_hunt()
    if ph:
        env_vars.append(ph)
    
    # Add configuration
    env_vars.extend([
        "",
        "# Configuration",
        "MAX_ARTICLES_PER_SOURCE=20",
        "FETCH_TIMEOUT=30",
        "RETRY_ATTEMPTS=3"
    ])
    
    # Write .env file
    if env_vars:
        with open('.env', 'w') as f:
            f.write('\n'.join(env_vars))
        print(f"\n✅ Configuration saved to .env file")
        print(f"Added {len([v for v in env_vars if v and not v.startswith('#')])} API keys")
    else:
        print("\n⚠️  No API keys configured. The system will work with free sources only.")
        print("You can run this script again anytime to add API keys.")
    
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Test the system: python scripts/fetch_news.py")
    print("3. Set up automatic updates (cron job or scheduled task)")

if __name__ == "__main__":
    main()
