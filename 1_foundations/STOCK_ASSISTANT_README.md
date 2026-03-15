# Stock Assistant Chatbot

The ultimate AI-powered stock analysis tool with news integration and API optimization.

## ✨ Features

### Core Capabilities
- 🧠 **NLP Entity Extraction**: Finds companies/tickers anywhere in your question
- 📈 **30-Day Historical Data**: Complete OHLCV data for comprehensive analysis
- 📰 **News Integration**: Recent articles and sentiment for predictive questions
- 🤖 **AI Analysis**: OpenAI-powered insights combining news + price data
- 📚 **Source References**: Every response cites its data sources

### API Optimizations
- 💾 **Persistent File Caching**: Data survives restarts (1-hour duration)
- ⏱️ **Smart Rate Limiting**: 12s between Alpha Vantage calls
- 🔄 **Batch Processing**: Efficient sector analysis
- 📦 **Data Reuse**: Cached questions = 0 API calls

## 🚀 Quick Start

```bash
cd /Users/maneeshmukundan/projects/agents/1_foundations
python3 stock_assistant_chatbot.py
```

## 📋 Requirements

```bash
pip install gradio yfinance openai python-dotenv requests
```

## 🔧 Environment Variables

Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
NEWS_API_KEY=your_newsapi_key  # Optional
```

## 💡 Example Questions

### Simple Price Questions:
- "What is the price of Tesla?"
- "Show me Apple's current price"

### Trend Analysis:
- "What's the trend for Microsoft?"
- "When was NVIDIA's highest price this month?"

### Investment Decisions (with news):
- "Should I buy Tesla?"
- "Will NVDA go up before earnings?"

### Sector Analysis:
- "What's the trend for healthcare stocks?"
- "How is the technology sector performing?"

## 📊 API Usage Optimization

### Typical API Calls:

| Question Type | API Calls (First Time) | API Calls (Cached) |
|---------------|------------------------|-------------------|
| Simple price | 2-3 calls | 0 calls |
| With news | 3-4 calls | 0 calls |
| Sector (5 stocks) | 5-10 calls | 0-2 calls |

### Free Tier Limits:
- **Alpha Vantage**: 25 calls/day
- **Yahoo Finance**: ~2000 calls/hour

### Expected Usage:
- **Without caching**: ~8 questions/day
- **With caching**: 15-25+ questions/day

## 📁 File Structure

```
1_foundations/
├── stock_assistant_chatbot.py  ← Main file (latest optimized version)
└── stock_cache/                ← Persistent cache directory
    ├── stock_TSLA_30day.pkl
    ├── stock_AAPL_30day.pkl
    └── ...
```

## 🎯 What Makes This Version Special

### All Requirements Met:
✅ No first-word checking - analyzes entire question
✅ 30-day open/close price data
✅ Alpha Vantage → Yahoo Finance fallback
✅ Sector support
✅ OpenAI-powered analysis
✅ Complete source attribution
✅ News integration for predictions
✅ API optimization to avoid rate limits

### Smart Features:
- Detects if question is predictive → fetches news automatically
- Detects if question is simple → skips news (faster)
- Caches everything → massive reduction in API calls
- Graceful degradation → works even if one API fails

## 🔄 Cache Management

### View Cache:
```bash
ls -la stock_cache/
```

### Clear Cache:
```bash
rm -rf stock_cache/*
```

### Cache Behavior:
- Duration: 1 hour
- Survives app restarts
- Reduces API calls by 80-90%

## 🎉 Ready to Use!

The Stock Assistant Chatbot is now consolidated into a single, optimized file with all the latest features!

**Run it with:**
```bash
python3 stock_assistant_chatbot.py
```

Your app will be available at: http://localhost:7865

