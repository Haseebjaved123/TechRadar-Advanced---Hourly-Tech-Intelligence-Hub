# 🤝 Contributing to TechRadar Advanced

Thank you for your interest in contributing to TechRadar Advanced! This document provides guidelines for contributing to our hourly tech intelligence hub.

## 🎯 How to Contribute

### 🐛 Reporting Issues

If you find a bug or have a suggestion:

1. **Check existing issues** first to avoid duplicates
2. **Use the issue templates** provided
3. **Provide detailed information**:
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Screenshots if applicable
   - System information

### 📰 Adding News Sources

We welcome new tech news sources! To suggest a source:

1. **Open an issue** with the "New Source" label
2. **Include**:
   - Source name and URL
   - RSS feed URL (if available)
   - API documentation (if applicable)
   - Why it's valuable for tech news

### 🧠 Improving Analysis

Help us improve our NLP and categorization:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b improve-analysis`
3. **Make your changes** to the processing scripts
4. **Test thoroughly** with sample data
5. **Submit a pull request**

### 📊 Creating Visualizations

We need better data visualizations:

1. **Check the analysis/ directory** for data
2. **Create visualizations** using matplotlib, plotly, or other tools
3. **Add to the repository** in the analysis/ directory
4. **Update documentation** to reference new visualizations

## 🛠️ Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/Haseebjaved123/TechRadar-Advanced---Hourly-Tech-Intelligence-Hub.git
cd TechRadar-Advanced---Hourly-Tech-Intelligence-Hub

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (if needed)
npm install
```

### Running Locally

```bash
# Fetch news data
python scripts/fetch_news.py

# Process the data
python scripts/process_news.py

# Generate content
python scripts/generate_content.py

# Update analytics
python scripts/update_analytics.py

# Validate content
python scripts/validate_content.py
```

### Testing

```bash
# Run validation tests
python scripts/validate_content.py

# Run report generation
python scripts/generate_report.py
```

## 📝 Code Style Guidelines

### Python

- Follow PEP 8 style guidelines
- Use type hints where possible
- Add docstrings to functions and classes
- Keep functions focused and small

### Markdown

- Use proper heading hierarchy
- Include emojis for visual appeal
- Keep lines under 100 characters
- Use consistent formatting

### JSON

- Use 2-space indentation
- Sort keys alphabetically
- Include comments where helpful
- Validate syntax before committing

## 🔧 Configuration

### Environment Variables

Create a `.env` file for local development:

```env
# API Keys (get from respective services)
NEWS_API_KEY=your_news_api_key
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
GITHUB_TOKEN=your_github_token

# Optional webhooks
SLACK_WEBHOOK_URL=your_slack_webhook_url
DISCORD_WEBHOOK_URL=your_discord_webhook_url
```

### GitHub Secrets

For the automated workflow, add these secrets to your repository:

- `NEWS_API_KEY`: NewsAPI.org API key
- `REDDIT_CLIENT_ID`: Reddit API client ID
- `REDDIT_CLIENT_SECRET`: Reddit API client secret
- `GITHUB_TOKEN`: GitHub personal access token

## 📋 Pull Request Process

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Add tests** if applicable
5. **Update documentation** if needed
6. **Commit your changes**: `git commit -m 'Add amazing feature'`
7. **Push to your branch**: `git push origin feature/amazing-feature`
8. **Open a Pull Request**

### PR Guidelines

- **Use descriptive titles**
- **Reference related issues**
- **Include screenshots** for UI changes
- **Update documentation** as needed
- **Ensure all tests pass**

## 🏷️ Issue Labels

We use the following labels to categorize issues:

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `new source`: New news source suggestion
- `priority: high`: High priority issue
- `priority: low`: Low priority issue

## 📚 Resources

### Documentation

- [README.md](README.md) - Main project documentation
- [API Documentation](docs/api.md) - API usage guide
- [Deployment Guide](docs/deployment.md) - How to deploy

### External Resources

- [NewsAPI Documentation](https://newsapi.org/docs)
- [Reddit API Documentation](https://www.reddit.com/dev/api/)
- [GitHub API Documentation](https://docs.github.com/en/rest)

## 🎉 Recognition

Contributors will be recognized in:

- [CONTRIBUTORS.md](CONTRIBUTORS.md) file
- Release notes for significant contributions
- Social media mentions (with permission)

## 📞 Getting Help

- **GitHub Discussions**: For questions and general discussion
- **GitHub Issues**: For bug reports and feature requests
- **Email**: [Contact information]

## 📜 License

By contributing to TechRadar Advanced, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to TechRadar Advanced! 🚀
