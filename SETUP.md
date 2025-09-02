# 🚀 TechRadar Advanced - Setup Guide

This guide will help you set up and run the TechRadar Advanced hourly tech intelligence hub.

## 📋 Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher (optional)
- Git
- GitHub account with repository access

## 🛠️ Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Haseebjaved123/TechRadar-Advanced---Hourly-Tech-Intelligence-Hub.git
cd TechRadar-Advanced---Hourly-Tech-Intelligence-Hub
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Optional: Install Node.js dependencies if you plan to use web scraping
npm install
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# API Keys (get from respective services)
NEWS_API_KEY=your_news_api_key_here
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
GITHUB_TOKEN=your_github_token_here

# Optional webhooks for notifications
SLACK_WEBHOOK_URL=your_slack_webhook_url_here
DISCORD_WEBHOOK_URL=your_discord_webhook_url_here
```

### 4. Set Up GitHub Secrets

For automated hourly updates, add these secrets to your GitHub repository:

1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Add the following secrets:
   - `NEWS_API_KEY`: Your NewsAPI.org API key
   - `REDDIT_CLIENT_ID`: Your Reddit API client ID
   - `REDDIT_CLIENT_SECRET`: Your Reddit API client secret
   - `GITHUB_TOKEN`: Your GitHub personal access token

## 🏃‍♂️ Running Locally

### Manual Execution

You can run the scripts manually to test the system:

```bash
# 1. Fetch news from all sources
python scripts/fetch_news.py

# 2. Process and analyze the news
python scripts/process_news.py

# 3. Generate formatted content
python scripts/generate_content.py

# 4. Update analytics and trends
python scripts/update_analytics.py

# 5. Validate the generated content
python scripts/validate_content.py

# 6. Generate summary reports
python scripts/generate_report.py
```

### Automated Execution

The system is designed to run automatically via GitHub Actions every hour. The workflow is configured in `.github/workflows/news-update.yml`.

## 📊 Understanding the Output

### File Structure

- **`today/latest.md`**: The main news digest for the current hour
- **`today/trending.json`**: Real-time trending topics and company mentions
- **`today/alerts.md`**: Breaking news alerts
- **`data/raw-feeds.json`**: Raw data from all news sources
- **`data/processed-articles.json`**: Processed and analyzed articles
- **`analysis/`**: Analytics, trends, and insights
- **`archives/`**: Historical snapshots organized by date

### Key Metrics

- **Sentiment Score**: 0.0 (negative) to 1.0 (positive)
- **Impact Score**: 0.0 to 10.0 (based on source credibility and engagement)
- **Categories**: AI/ML, Quantum Computing, Blockchain/Web3, Cybersecurity, etc.

## 🔧 Customization

### Adding New News Sources

1. Edit `scripts/fetch_news.py`
2. Add a new method for your source
3. Include it in the `fetch_all_sources()` method
4. Test with `python scripts/fetch_news.py`

### Modifying Categories

1. Edit the `categories` dictionary in `scripts/process_news.py`
2. Add new categories and their keywords
3. Update the README.md to reflect new categories

### Changing Update Frequency

1. Edit `.github/workflows/news-update.yml`
2. Modify the cron schedule (currently `'0 * * * *'` for hourly)
3. Examples:
   - Every 30 minutes: `'0,30 * * * *'`
   - Every 6 hours: `'0 */6 * * *'`
   - Daily at 9 AM: `'0 9 * * *'`

## 🚨 Troubleshooting

### Common Issues

1. **API Rate Limits**: Some APIs have rate limits. The scripts include delays, but you may need to adjust them.

2. **Missing Dependencies**: Make sure all Python packages are installed:
   ```bash
   pip install -r requirements.txt
   ```

3. **Permission Errors**: Ensure the scripts have write permissions to the data directories.

4. **GitHub Actions Failures**: Check the Actions tab in your repository for detailed error logs.

### Debug Mode

Run scripts with debug logging:

```bash
python -u scripts/fetch_news.py 2>&1 | tee debug.log
```

## 📈 Monitoring

### GitHub Actions

- Monitor the Actions tab in your repository
- Check for failed runs and error messages
- Review the commit history to see automated updates

### Local Monitoring

```bash
# Check recent commits
git log --oneline -10

# Monitor file changes
ls -la today/
ls -la data/
```

## 🔄 Maintenance

### Regular Tasks

1. **Weekly**: Review and update news sources
2. **Monthly**: Analyze trending topics and adjust categories
3. **Quarterly**: Update dependencies and review API keys

### Data Cleanup

The system automatically archives old data, but you may want to clean up:

```bash
# Remove old archive files (older than 30 days)
find archives/ -name "*.md" -mtime +30 -delete
```

## 📞 Support

- **Issues**: Create a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check the README.md and CONTRIBUTING.md files

## 🎯 Next Steps

1. **Set up the automated workflow** by pushing to your repository
2. **Monitor the first few runs** to ensure everything works correctly
3. **Customize the sources and categories** to match your interests
4. **Share the repository** with others who might find it useful

---

Happy tech news aggregating! 🚀
