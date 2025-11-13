"""
Stock Assistant Chatbot - Web Version for Render

Features:
- NLP extraction: Finds companies/tickers anywhere in question
- 30-day historical data with Alpha Vantage → Yahoo Finance fallback
- News integration for predictive questions
- Sector analysis
- Smart responses: Simple answers for simple questions, detailed analysis when needed
- Complete source references

Requirements:
    pip install gradio yfinance openai python-dotenv requests yahooquery
"""

import os
import yfinance as yf
import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv
import requests
import json
from datetime import datetime
import time
from yahooquery import Screener

# Load environment variables
load_dotenv(override=True)

# Initialize OpenAI client
def get_openai_client():
    """Initialize OpenAI client with error handling"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    return OpenAI(api_key=api_key)

# Global client
client = None

# API configuration
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

# Simple caching
stock_cache = {}
news_cache = {}
entity_cache = {}
CACHE_DURATION = 3600  # 1 hour

# Yahoo Finance Screener mapping for sectors
SECTOR_SCREENERS = {
    'technology': 'ms_technology',
    'tech': 'ms_technology',
    'finance': 'ms_financial_services',
    'financial': 'ms_financial_services',
    'healthcare': 'ms_healthcare',
    'health': 'ms_healthcare',
    'energy': 'ms_energy',
    'retail': 'ms_consumer_cyclical',
    'consumer': 'ms_consumer_cyclical',
    'industrial': 'ms_industrials',
    'basic_materials': 'ms_basic_materials',
    'materials': 'ms_basic_materials',
    'utilities': 'ms_utilities',
    'real_estate': 'ms_real_estate',
    'communication': 'ms_communication_services',
    'consumer_defensive': 'ms_consumer_defensive',
    'automotive': 'ms_consumer_cyclical',  # Auto stocks under consumer cyclical
    'auto': 'ms_consumer_cyclical'
}

def get_cached(cache_dict, key):
    """Get cached data if valid"""
    if key in cache_dict:
        data, timestamp = cache_dict[key]
        if time.time() - timestamp < CACHE_DURATION:
            return data
    return None

def set_cached(cache_dict, key, data):
    """Cache data"""
    cache_dict[key] = (data, time.time())

def get_sector_tickers(sector_name, max_stocks=5):
    """
    Dynamically retrieve stock tickers for a sector using Yahoo Finance Screener
    Returns a list of ticker symbols
    """
    sector_key = sector_name.lower().strip()
    
    if sector_key not in SECTOR_SCREENERS:
        return None
    
    try:
        screener = Screener()
        screener_key = SECTOR_SCREENERS[sector_key]
        
        print(f"🔍 Retrieving stocks for {sector_name} sector from Yahoo Finance Screener...")
        
        # Get screener data
        data = screener.get_screeners(screener_key, count=max_stocks)
        
        if screener_key in data and 'quotes' in data[screener_key]:
            tickers = [quote['symbol'] for quote in data[screener_key]['quotes'][:max_stocks]]
            print(f"✅ Found {len(tickers)} stocks for {sector_name} sector: {', '.join(tickers)}")
            return tickers
        else:
            print(f"⚠️ No data found for {sector_name} sector")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching sector tickers from screener: {e}")
        return None

def extract_entities(question):
    """Extract companies, tickers, sectors using OpenAI NLP"""
    cached = get_cached(entity_cache, question)
    if cached:
        return cached
    
    global client
    if client is None:
        try:
            client = get_openai_client()
        except:
            return None
    
    prompt = f"""Extract stock market entities from this question:

"{question}"

Return JSON with:
- companies: list of SPECIFIC company names (e.g., "Apple", "Tesla") - DO NOT include generic words like "stocks", "companies", "sector"
- tickers: list of stock tickers (e.g., "AAPL", "TSLA")
- sectors: list of sectors (e.g., "technology", "healthcare", "finance")
- question_type: "stock_specific" if asking about ONE specific company/ticker, "sector" if asking about multiple stocks/sector, or "general"
- main_entity: the primary entity
- needs_analysis: false for simple facts (price, date), true for analysis/recommendations
- needs_news: true if asking about future or mentions news

IMPORTANT: 
- If question mentions "stocks in [sector]", set question_type to "sector"
- Generic words like "stocks", "companies" are NOT company names
- Questions about "top 3 stocks", "declining stocks" are sector questions

Examples:
- "What are the 3 stocks in healthcare sector declining?" → {{"companies": [], "sectors": ["healthcare"], "question_type": "sector"}}
- "What is Apple's price?" → {{"companies": ["Apple"], "question_type": "stock_specific"}}

{{
  "companies": [],
  "tickers": [],
  "sectors": [],
  "question_type": "stock_specific",
  "main_entity": "",
  "needs_analysis": false,
  "needs_news": false
}}"""
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=150
        )
        
        content = resp.choices[0].message.content.strip()
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        
        result = json.loads(content)
        set_cached(entity_cache, question, result)
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None

def lookup_ticker(company_name):
    """Convert company name to ticker"""
    try:
        url = "https://query2.finance.yahoo.com/v1/finance/search"
        resp = requests.get(url, params={"q": company_name, "quotes_count": 1}, 
                           headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("quotes"):
            return data["quotes"][0]["symbol"]
    except:
        pass
    return None

def get_30day_alpha(ticker):
    """Get 30-day data from Alpha Vantage"""
    if not ALPHA_VANTAGE_API_KEY:
        return None
    
    key = f"{ticker}_30d"
    cached = get_cached(stock_cache, key)
    if cached:
        return cached
    
    try:
        resp = requests.get(ALPHA_VANTAGE_BASE_URL, params={
            'function': 'TIME_SERIES_DAILY',
            'symbol': ticker,
            'apikey': ALPHA_VANTAGE_API_KEY
        }, timeout=15)
        
        data = resp.json()
        ts = data.get('Time Series (Daily)', {})
        if not ts:
            return None
        
        daily = []
        for date in sorted(ts.keys(), reverse=True)[:30]:
            d = ts[date]
            daily.append({
                'date': date,
                'open': float(d['1. open']),
                'high': float(d['2. high']),
                'low': float(d['3. low']),
                'close': float(d['4. close']),
                'volume': int(d['5. volume'])
            })
        
        closes = [d['close'] for d in daily]
        highs = [d['high'] for d in daily]
        lows = [d['low'] for d in daily]
        
        result = {
            'ticker': ticker,
            'company_name': ticker,
            'daily_data': daily,
            'current_price': closes[0],
            'period_high': max(highs),
            'period_low': min(lows),
            'period_avg': sum(closes) / len(closes),
            'period_change_pct': ((closes[0] - closes[-1]) / closes[-1] * 100),
            'source': 'Alpha Vantage API'
        }
        
        set_cached(stock_cache, key, result)
        return result
    except:
        return None
        
def get_30day_yahoo(ticker):
    """Get 30-day data from Yahoo Finance"""
    key = f"{ticker}_30d"
    cached = get_cached(stock_cache, key)
    if cached:
        return cached
    
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        if hist.empty:
            return None
        
        info = stock.info
        daily = []
        for date, row in hist.iterrows():
            daily.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume'])
            })
        daily.reverse()
        
        closes = [d['close'] for d in daily]
        highs = [d['high'] for d in daily]
        lows = [d['low'] for d in daily]
        
        result = {
            'ticker': ticker,
            'company_name': info.get('longName', ticker),
            'daily_data': daily,
            'current_price': closes[0],
            'period_high': max(highs),
            'period_low': min(lows),
            'period_avg': sum(closes) / len(closes),
            'period_change_pct': ((closes[0] - closes[-1]) / closes[-1] * 100),
            'source': 'Yahoo Finance API'
        }
        
        set_cached(stock_cache, key, result)
        return result
    except:
        return None

def get_stock_data(ticker):
    """Get stock data with fallback"""
    data = get_30day_alpha(ticker)
    if data:
        return data
    print(f"Fallback to Yahoo for {ticker}...")
    return get_30day_yahoo(ticker)

def get_news(ticker):
    """Get news for a ticker"""
    cached = get_cached(news_cache, ticker)
    if cached:
        return cached
    
    # Try Alpha Vantage News
    if ALPHA_VANTAGE_API_KEY:
        try:
            resp = requests.get(ALPHA_VANTAGE_BASE_URL, params={
                'function': 'NEWS_SENTIMENT',
                'tickers': ticker,
                'apikey': ALPHA_VANTAGE_API_KEY,
                'limit': 10
            }, timeout=10)
            
            data = resp.json()
            if 'feed' in data:
                articles = [{
                    'title': item.get('title', ''),
                    'source': item.get('source', ''),
                    'sentiment': item.get('overall_sentiment_label', 'Neutral')
                } for item in data['feed'][:5]]
                
                result = {'articles': articles, 'source': 'Alpha Vantage News API', 'count': len(articles)}
                set_cached(news_cache, ticker, result)
                return result
        except:
            pass
    
    # Fallback to Yahoo News
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        if news:
            articles = [{
                'title': item.get('title', ''),
                'source': item.get('publisher', 'Yahoo')
            } for item in news[:5]]
            
            result = {'articles': articles, 'source': 'Yahoo Finance News', 'count': len(articles)}
            set_cached(news_cache, ticker, result)
            return result
    except:
        pass
    
        return None

def analyze_with_ai(stock_data, news_data, question):
    """Generate AI analysis"""
    global client
    if client is None:
        client = get_openai_client()
    
    context = f"""Stock: {stock_data.get('company_name', stock_data['ticker'])} ({stock_data['ticker']})
Current: ${stock_data['current_price']:.2f}
30-Day High/Low: ${stock_data['period_high']:.2f} / ${stock_data['period_low']:.2f}
30-Day Change: {stock_data['period_change_pct']:+.2f}%
"""
    
    if news_data:
        context += f"\nRecent News:\n"
        for i, art in enumerate(news_data['articles'], 1):
            context += f"{i}. {art['title']}"
            if art.get('sentiment'):
                context += f" (Sentiment: {art['sentiment']})"
            context += "\n"
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"{context}\n\nQuestion: {question}\n\nProvide analysis citing the data."}],
            temperature=0.3,
            max_tokens=600
        )
        return resp.choices[0].message.content.strip()
    except:
        return "Error generating analysis"

def process_question(question, history):
    """Main handler"""
    global client
    
    if not question.strip():
        return history, ""
    
    entities = extract_entities(question)
    if not entities:
        return history + [{"role": "user", "content": question}, 
                        {"role": "assistant", "content": "❌ Could not understand question"}], ""
    
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Stock questions
    if entities['question_type'] == 'stock_specific':
        ticker = entities['tickers'][0] if entities['tickers'] else None
        if not ticker and entities['companies']:
            ticker = lookup_ticker(entities['companies'][0])
        
        if not ticker:
            return history + [{"role": "user", "content": question},
                            {"role": "assistant", "content": f"❌ Could not find ticker for '{entities['main_entity']}'"}], ""
        
        stock_data = get_stock_data(ticker)
        if not stock_data:
            return history + [{"role": "user", "content": question},
                            {"role": "assistant", "content": f"❌ Could not retrieve data for {ticker}"}], ""
        
        company = stock_data.get('company_name', ticker)
        
        # Simple answer or full analysis?
        if not entities.get('needs_analysis', True):
            # Simple factual answer
            resp = f"""📊 **{company} ({ticker})**

💰 Current Price: ${stock_data['current_price']:.2f}
📈 30-Day High: ${stock_data['period_high']:.2f}
📉 30-Day Low: ${stock_data['period_low']:.2f}
📊 30-Day Change: {stock_data['period_change_pct']:+.2f}%

📡 Source: {stock_data['source']}
_Retrieved at {ts}_"""
        else:
            # Full analysis
            news = None
            if entities.get('needs_news'):
                news = get_news(ticker)
            
            analysis = analyze_with_ai(stock_data, news, question)
            
            resp = f"""📊 **{company} ({ticker}) - Analysis**

{analysis}

---
📈 Stats: ${stock_data['current_price']:.2f} | 30-Day: {stock_data['period_change_pct']:+.2f}%
📡 Sources: {stock_data['source']}"""
            if news:
                resp += f", {news['source']}"
            resp += f", OpenAI GPT-4o-mini\n_Generated at {ts}_"
        
        return history + [{"role": "user", "content": question}, {"role": "assistant", "content": resp}], ""
    
    # Sector questions
    elif entities['question_type'] == 'sector':
        sector = entities['sectors'][0] if entities['sectors'] else entities['main_entity']
        
        # Use Yahoo Finance Screener to get sector stocks dynamically
        tickers = get_sector_tickers(sector, max_stocks=5)
        
        if not tickers:
            available_sectors = ', '.join(sorted(set(SECTOR_SCREENERS.keys())))
            return history + [{"role": "user", "content": question},
                            {"role": "assistant", "content": f"❌ Sector '{sector}' not found. Available sectors: {available_sectors}"}], ""
        
        # Get data for stocks
        stocks = []
        for t in tickers:
            d = get_stock_data(t)
            if d:
                stocks.append(d)
                time.sleep(0.5)
        
        if not stocks:
            return history + [{"role": "user", "content": question},
                            {"role": "assistant", "content": "❌ Could not retrieve sector data"}], ""
        
        # Use AI to answer the specific question
        if client is None:
            client = get_openai_client()
        
        stock_list = ""
        for s in sorted(stocks, key=lambda x: x['period_change_pct'], reverse=True):
            stock_list += f"\n- {s['ticker']} ({s.get('company_name', s['ticker'])}): {s['period_change_pct']:+.2f}%"
        
        sector_prompt = f"""Sector: {sector.title()}
Stocks:{stock_list}

Question: {question}

Answer the EXACT question. If asking for declining stocks, list those with negative/lowest performance. If asking for top performers, list highest gains."""
        
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": sector_prompt}],
                temperature=0.3,
                max_tokens=400
            )
            
            analysis = resp.choices[0].message.content.strip()
            response = f"""🏢 **{sector.title()} Sector**

{analysis}

📡 Sources: Alpha Vantage API, Yahoo Finance API, OpenAI GPT-4o-mini
_Generated at {ts}_"""
            
            return history + [{"role": "user", "content": question}, {"role": "assistant", "content": response}], ""
        except Exception as e:
            return history + [{"role": "user", "content": question},
                            {"role": "assistant", "content": f"❌ Error: {str(e)}"}], ""
    
    # General questions
    else:
        if client is None:
            client = get_openai_client()
        
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"Answer this stock market question: {question}"}],
                temperature=0.3,
                max_tokens=300
            )
            answer = resp.choices[0].message.content.strip()
            response = f"""{answer}

📚 Source: OpenAI GPT-4o-mini
_Generated at {ts}_"""
            return history + [{"role": "user", "content": question}, {"role": "assistant", "content": response}], ""
        except:
            return history + [{"role": "user", "content": question},
                            {"role": "assistant", "content": "❌ Error processing question"}], ""

def create_interface():
    """Create Gradio UI"""
    with gr.Blocks(title="Stock Assistant", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 📊 Stock Assistant
        
        **Ask any question about stocks - get smart answers!**
        
        ### Features:
        - 🧠 Finds companies anywhere in your question
        - 📈 30-day historical data
        - 📰 News for predictive questions
        - 🏢 Sector analysis
        - 💡 Simple answers for simple questions
        
        **Try:** "What's Tesla's price?" or "Should I buy Microsoft?" or "Healthcare stocks declining this month?"
        """)
        
        chatbot = gr.Chatbot(label="Chat", height=550, type='messages', show_copy_button=True)
        
        with gr.Row():
            msg = gr.Textbox(placeholder="Ask about any stock...", label="Question", scale=4)
            btn = gr.Button("Ask", variant="primary", scale=1)
        
        clear = gr.Button("Clear", variant="secondary")
        
        btn.click(process_question, [msg, chatbot], [chatbot, msg])
        msg.submit(process_question, [msg, chatbot], [chatbot, msg])
        clear.click(lambda: ([], ""), outputs=[chatbot, msg])
        
        gr.Examples([
            "What's Apple's price?",
            "Should I buy Tesla?",
            "Healthcare stocks declining this month?",
            "When was NVIDIA highest?"
        ], inputs=msg)

    return demo

# Module-level demo for deployment
demo = create_interface()

def main():
    """Launch app - Configured for Render hosting"""
    print("🚀 Starting Stock Assistant...")
    # Get port from environment variable (set by Render)
    port = int(os.environ.get("PORT", 7860))
    demo.launch(
        server_name="0.0.0.0",  # Bind to all interfaces for hosting
        server_port=port,
        share=False,  # Don't use share=True on hosting platforms
        show_error=True
    )

if __name__ == "__main__":
    main()

