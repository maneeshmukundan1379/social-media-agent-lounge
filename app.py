"""
Stock Genie - Hugging Face Spaces Version

A comprehensive stock analysis tool that:
- Converts company names to ticker symbols using Yahoo Finance API
- Fetches real-time stock data using Alpha Vantage API
- Uses OpenAI LLM for analytical questions
- Provides a user-friendly Gradio interface

This version is optimized for Hugging Face Spaces deployment.
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
        raise ValueError("OPENAI_API_KEY environment variable is not set. Please configure it in Hugging Face Spaces Settings → Repository secrets")
    return OpenAI(api_key=api_key)

# Global client instance
client = None

# Alpha Vantage API configuration
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

# Data caching to reduce API calls
stock_data_cache = {}
CACHE_DURATION = 300  # 5 minutes in seconds

# Mapping of user-friendly sector names to Yahoo Finance screener keys
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
}

def get_sector_tickers(sector_name, max_stocks=10):
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
        
        print(f"🔍 Retrieving stocks for {sector_name} sector from Yahoo Finance...")
        
        # Get screener data
        data = screener.get_screeners(screener_key, count=max_stocks)
        
        if screener_key in data and 'quotes' in data[screener_key]:
            tickers = [quote['symbol'] for quote in data[screener_key]['quotes'][:max_stocks]]
            print(f"✅ Found {len(tickers)} stocks for {sector_name} sector")
            return tickers
        else:
            print(f"⚠️  No data found for {sector_name} sector")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching sector tickers: {e}")
        return None

def is_cache_valid(ticker):
    """Check if cached data is still valid"""
    if ticker not in stock_data_cache:
        return False
    
    cache_time = stock_data_cache[ticker].get('timestamp', 0)
    current_time = time.time()
    return (current_time - cache_time) < CACHE_DURATION

def get_cached_data(ticker):
    """Get data from cache if valid"""
    if is_cache_valid(ticker):
        return stock_data_cache[ticker].get('data')
    return None

def set_cached_data(ticker, data):
    """Store data in cache with timestamp"""
    stock_data_cache[ticker] = {
        'data': data,
        'timestamp': time.time()
    }

def search_company_ticker(company_name):
    """
    Search for ticker symbol using runtime API calls
    Retrieves company information dynamically without hardcoded mappings
    """
    # First, try yfinance API (most reliable for ticker lookup)
    try:
        ticker_obj = yf.Ticker(company_name.upper())
        info = ticker_obj.info
        if info and 'symbol' in info:
            print(f"✅ Found ticker via yfinance: {info['symbol']}")
            return info['symbol']
    except Exception as e:
        print(f"yfinance lookup failed: {e}")
    
    # Second, try Yahoo Finance Search API
    try:
        url = "https://query2.finance.yahoo.com/v1/finance/search"
        params = {
            "q": company_name,
            "quotes_count": 5,
            "country": "United States"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "quotes" in data and len(data["quotes"]) > 0:
            ticker = data["quotes"][0]["symbol"]
            print(f"✅ Found ticker via Yahoo Finance API: {ticker}")
            return ticker
            
    except Exception as e:
        print(f"Yahoo Finance API lookup failed: {e}")
    
    # If all methods fail, return None
    print(f"❌ Could not find ticker for: {company_name}")
    return None

def get_ticker_from_input(user_input):
    """
    Extract ticker from user input. If it looks like a company name, 
    try to find the corresponding ticker using Yahoo Finance API.
    """
    input_clean = user_input.strip()
    
    # If it's already a ticker-like format (1-5 uppercase letters), return as is
    if len(input_clean) <= 5 and input_clean.isalpha() and input_clean.isupper():
        return input_clean
    
    # Try Yahoo Finance API search for company name
    ticker = search_company_ticker(input_clean)
    return ticker

def get_historical_data(ticker, days=30):
    """
    Fetch historical daily OHLCV (Open, High, Low, Close, Volume) data
    Returns a structured dictionary with daily data for AI analysis
    """
    if not ALPHA_VANTAGE_API_KEY:
        return None
    
    try:
        url = ALPHA_VANTAGE_BASE_URL
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': ticker,
            'apikey': ALPHA_VANTAGE_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Check for errors
        if 'Error Message' in data or 'Note' in data or 'Information' in data:
            return None
        
        time_series = data.get('Time Series (Daily)', {})
        if not time_series:
            return None
        
        # Convert to list of daily data (most recent first)
        daily_data = []
        for date_str in sorted(time_series.keys(), reverse=True)[:days]:
            day_data = time_series[date_str]
            daily_data.append({
                'date': date_str,
                'open': float(day_data.get('1. open', 0)),
                'high': float(day_data.get('2. high', 0)),
                'low': float(day_data.get('3. low', 0)),
                'close': float(day_data.get('4. close', 0)),
                'volume': int(day_data.get('5. volume', 0))
            })
        
        if not daily_data:
            return None
        
        # Calculate useful statistics
        closes = [d['close'] for d in daily_data]
        highs = [d['high'] for d in daily_data]
        lows = [d['low'] for d in daily_data]
        
        historical_summary = {
            'daily_data': daily_data,
            'period_days': len(daily_data),
            'period_high': max(highs),
            'period_low': min(lows),
            'period_avg': sum(closes) / len(closes),
            'first_close': daily_data[-1]['close'],  # Oldest
            'last_close': daily_data[0]['close'],    # Most recent
            'period_change': daily_data[0]['close'] - daily_data[-1]['close'],
            'period_change_pct': ((daily_data[0]['close'] - daily_data[-1]['close']) / daily_data[-1]['close'] * 100)
        }
        
        return historical_summary
        
    except Exception as e:
        print(f"⚠️ Could not fetch historical data: {e}")
        return None

def get_stock_data_yfinance(ticker):
    """
    Fallback: Fetch stock data using yfinance library
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1mo")
        
        if hist.empty or not info:
            return None
        
        # Get current data
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        previous_close = info.get('previousClose', 0)
        
        if current_price == 0:
            # Try from history
            current_price = hist['Close'].iloc[-1]
        
        if previous_close == 0:
            previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        
        # Calculate 30-day stats from history
        period_high = hist['High'].max()
        period_low = hist['Low'].min()
        period_avg = hist['Close'].mean()
        first_close = hist['Close'].iloc[0]
        last_close = hist['Close'].iloc[-1]
        
        # Build daily data
        daily_data = []
        for date, row in hist.iterrows():
            daily_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume'])
            })
        
        daily_data.reverse()  # Most recent first
        
        historical_summary = {
            'daily_data': daily_data,
            'period_days': len(daily_data),
            'period_high': float(period_high),
            'period_low': float(period_low),
            'period_avg': float(period_avg),
            'first_close': float(first_close),
            'last_close': float(last_close),
            'period_change': float(last_close - first_close),
            'period_change_pct': float((last_close - first_close) / first_close * 100)
        }
        
        stock_data = {
            'ticker': ticker,
            'current_price': float(current_price),
            'open_price': float(hist['Open'].iloc[-1]),
            'close_price': float(current_price),
            'previous_close': float(previous_close),
            'volume': int(hist['Volume'].iloc[-1]),
            'company_name': info.get('longName', ticker),
            'market_cap': info.get('marketCap'),
            'pe_ratio': info.get('trailingPE'),
            'day_change': float(current_price - previous_close),
            'day_change_pct': float((current_price - previous_close) / previous_close * 100) if previous_close else 0,
            'historical_data': historical_summary,
            'source': 'Yahoo Finance (yfinance)'
        }
        
        print(f"✅ Successfully fetched data for {ticker} from yfinance")
        return stock_data
        
    except Exception as e:
        print(f"⚠️ yfinance fallback failed: {e}")
        return None

def get_stock_data_alpha_vantage(ticker):
    """
    Fetch real-time stock data using Alpha Vantage API
    Includes monthly high/low if available
    """
    if not ALPHA_VANTAGE_API_KEY:
        print("❌ Alpha Vantage API key not found. Please set ALPHA_VANTAGE_API_KEY in your .env file")
        return None
    
    try:
        url = ALPHA_VANTAGE_BASE_URL
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': ticker,
            'apikey': ALPHA_VANTAGE_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Check for API errors
        if 'Error Message' in data:
            print(f"❌ Alpha Vantage error: {data['Error Message']}")
            return None
        
        if 'Note' in data:
            print(f"❌ Alpha Vantage limit reached: {data['Note']}")
            return None
        
        # Extract data from Alpha Vantage response
        quote_data = data.get('Global Quote', {})
        
        if not quote_data:
            print(f"❌ No data found for ticker {ticker}")
            return None
        
        # Parse the data (Alpha Vantage returns strings)
        current_price = float(quote_data.get('05. price', 0))
        open_price = float(quote_data.get('02. open', 0))
        previous_close = float(quote_data.get('08. previous close', 0))
        volume = int(quote_data.get('06. volume', 0))
        
        # Calculate changes
        day_change = current_price - previous_close
        day_change_pct = (day_change / previous_close * 100) if previous_close else 0
        
        # Fetch historical data (30 days) for comprehensive analysis
        historical_data = get_historical_data(ticker, days=30)
        
        stock_data = {
            'ticker': ticker,
            'current_price': current_price,
            'open_price': open_price,
            'close_price': current_price,  # Alpha Vantage doesn't separate close/current
            'previous_close': previous_close,
            'volume': volume,
            'company_name': ticker,  # Alpha Vantage doesn't provide company name in quote
            'market_cap': None,  # Not available in basic quote
            'pe_ratio': None,  # Not available in basic quote
            'day_change': day_change,
            'day_change_pct': day_change_pct,
            'historical_data': historical_data,  # Full historical data for AI analysis
            'source': 'Alpha Vantage'
        }
        
        return stock_data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data from Alpha Vantage: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def get_stock_data(ticker):
    """
    Fetch real-time stock data using 2-tier fallback system:
    1. Alpha Vantage API (primary - includes 30-day history)
    2. Yahoo Finance API (yfinance library - includes 30-day history)
    3. Return None (all methods failed)
    """
    # Check cache first
    cached_data = get_cached_data(ticker)
    if cached_data:
        print(f"📋 Using cached data for {ticker}")
        return cached_data
    
    # Tier 1: Try Alpha Vantage API (primary source with full historical data)
    print(f"🔄 Checking Alpha Vantage API for {ticker}...")
    stock_data = get_stock_data_alpha_vantage(ticker)
    
    if stock_data:
        set_cached_data(ticker, stock_data)
        return stock_data
    
    # Tier 2: Try Yahoo Finance API (yfinance library)
    print(f"🔄 Checking Yahoo Finance API for {ticker}...")
    stock_data = get_stock_data_yfinance(ticker)
    
    if stock_data:
        set_cached_data(ticker, stock_data)
        return stock_data
    
    # All methods failed
    print(f"❌ Unable to retrieve data for {ticker}")
    return None

def get_sector_data(sector_name):
    """
    Fetch data for all major stocks in a sector
    Dynamically retrieves sector constituents from Yahoo Finance
    Returns summary with monthly high/low for each stock
    """
    sector_key = sector_name.lower().strip()
    
    # Get tickers dynamically from Yahoo Finance
    tickers = get_sector_tickers(sector_key, max_stocks=10)
    
    if not tickers:
        return None
    
    sector_data = {
        'sector': sector_name.title(),
        'stocks': [],
        'summary': {}
    }
    
    print(f"\n📊 Fetching data for {len(tickers)} stocks in {sector_name} sector...")
    
    for ticker in tickers:
        try:
            stock_data = get_stock_data(ticker)
            if stock_data and stock_data.get('historical_data'):
                hist = stock_data['historical_data']
                stock_summary = {
                    'ticker': ticker,
                    'current_price': stock_data['current_price'],
                    'previous_close': stock_data['previous_close'],
                    'day_change_pct': stock_data['day_change_pct'],
                    'period_high': hist['period_high'],
                    'period_low': hist['period_low'],
                    'period_change_pct': hist['period_change_pct'],
                    'period_avg': hist['period_avg']
                }
                sector_data['stocks'].append(stock_summary)
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        except Exception as e:
            print(f"⚠️  Error fetching {ticker}: {e}")
            continue
    
    # Calculate sector summary
    if sector_data['stocks']:
        avg_change = sum(s['period_change_pct'] for s in sector_data['stocks']) / len(sector_data['stocks'])
        avg_day_change = sum(s['day_change_pct'] for s in sector_data['stocks']) / len(sector_data['stocks'])
        
        sector_data['summary'] = {
            'total_stocks': len(sector_data['stocks']),
            'avg_period_change': avg_change,
            'avg_day_change': avg_day_change,
            'best_performer': max(sector_data['stocks'], key=lambda x: x['period_change_pct']),
            'worst_performer': min(sector_data['stocks'], key=lambda x: x['period_change_pct'])
        }
    
    return sector_data

def ask_llm_about_sector(sector_data, user_question):
    """
    Use OpenAI LLM to answer questions about a sector based on all stocks data
    """
    global client
    if client is None:
        try:
            client = get_openai_client()
        except ValueError as e:
            return f"⚠️ OpenAI API key not configured. Please set OPENAI_API_KEY in Hugging Face Spaces Settings → Repository secrets."
    
    # Format sector data for the prompt
    sector_info = f"""
Sector Analysis: {sector_data['sector']} Sector

Summary Statistics ({sector_data['summary']['total_stocks']} stocks analyzed):
- Average 30-Day Performance: {sector_data['summary']['avg_period_change']:.2f}%
- Average Day Performance: {sector_data['summary']['avg_day_change']:.2f}%
- Best Performer: {sector_data['summary']['best_performer']['ticker']} (+{sector_data['summary']['best_performer']['period_change_pct']:.2f}%)
- Worst Performer: {sector_data['summary']['worst_performer']['ticker']} ({sector_data['summary']['worst_performer']['period_change_pct']:.2f}%)

Individual Stock Performance:
"""
    
    for stock in sector_data['stocks']:
        sector_info += f"\n{stock['ticker']}:\n"
        sector_info += f"  - Current Price: ${stock['current_price']:.2f}\n"
        sector_info += f"  - Day Change: {stock['day_change_pct']:+.2f}%\n"
        sector_info += f"  - 30-Day High: ${stock['period_high']:.2f}\n"
        sector_info += f"  - 30-Day Low: ${stock['period_low']:.2f}\n"
        sector_info += f"  - 30-Day Average: ${stock['period_avg']:.2f}\n"
        sector_info += f"  - 30-Day Change: {stock['period_change_pct']:+.2f}%\n"
    
    prompt = f"""
You are a professional financial analyst specializing in sector analysis. Based on the following comprehensive sector data, provide a detailed, data-driven answer to the user's question.

{sector_info}

User Question: {user_question}

IMPORTANT GUIDELINES:
1. **Use the Data**: Reference specific stocks, percentages, and trends from the data above
2. **Sector Overview**: Analyze the overall sector performance and trends
3. **Compare Stocks**: Identify leaders, laggards, and patterns across stocks
4. **Highlight Outliers**: Note stocks performing significantly better or worse than sector average
5. **Context Matters**: Compare individual stocks to sector averages
6. **Investment Insights**: Provide sector-level investment perspectives
7. **Risk Disclosure**: Remind users that past performance doesn't guarantee future results

For sector investment questions, provide:
- Overall sector health and direction
- Best and worst performers with reasons
- Sector trends and patterns
- Diversification insights within the sector
- Risk considerations at sector level

Be professional, thorough, and back every statement with specific data from above.
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"I apologize, but I'm having trouble processing your request right now. Error: {str(e)}"

def ask_llm_about_stock(stock_data, user_question):
    """
    Use OpenAI LLM to answer analytical questions about the stock
    """
    global client
    if client is None:
        try:
            client = get_openai_client()
        except ValueError as e:
            return f"⚠️ OpenAI API key not configured. Please set OPENAI_API_KEY in Hugging Face Spaces Settings → Repository secrets."
    
    # Format stock data for the prompt
    stock_info = f"""
Stock Information:
- Company: {stock_data['company_name']} ({stock_data['ticker']})
- Current Price: ${stock_data['current_price']:.2f}
- Open Price: ${stock_data['open_price']:.2f}
- Close Price: ${stock_data['close_price']:.2f}
- Previous Close: ${stock_data['previous_close']:.2f}
- Day Change: ${stock_data['day_change']:.2f} ({stock_data['day_change_pct']:.2f}%)
- Volume: {stock_data['volume']:,}
- Market Cap: {stock_data['market_cap'] if stock_data['market_cap'] else 'Not available'}
- P/E Ratio: {stock_data['pe_ratio'] if stock_data['pe_ratio'] else 'Not available'}
"""
    
    # Add historical data analysis if available
    if stock_data.get('historical_data'):
        hist = stock_data['historical_data']
        stock_info += f"\nHistorical Data ({hist['period_days']} days):\n"
        stock_info += f"- Period High: ${hist['period_high']:.2f}\n"
        stock_info += f"- Period Low: ${hist['period_low']:.2f}\n"
        stock_info += f"- Period Average: ${hist['period_avg']:.2f}\n"
        stock_info += f"- Period Change: ${hist['period_change']:.2f} ({hist['period_change_pct']:.2f}%)\n"
        
        # Add recent daily data for trend analysis (last 7 days)
        stock_info += f"\nRecent Daily Closes (Last 7 Days):\n"
        for day in hist['daily_data'][:7]:
            change = day['close'] - day['open']
            change_pct = (change / day['open'] * 100) if day['open'] else 0
            stock_info += f"- {day['date']}: Open ${day['open']:.2f} → Close ${day['close']:.2f} ({change_pct:+.2f}%), Volume {day['volume']:,}\n"
    
    prompt = f"""
You are a professional financial analyst with expertise in technical analysis and market trends. Based on the following comprehensive stock data, provide a detailed, data-driven answer to the user's question.

{stock_info}

User Question: {user_question}

IMPORTANT GUIDELINES:
1. **Use the Data**: Reference specific numbers, dates, and trends from the data above
2. **Be Specific**: Cite actual prices, percentages, and dates in your analysis
3. **Identify Patterns**: Look for trends in the daily data (uptrend, downtrend, consolidation)
4. **Context Matters**: Compare current price to period high/low/average
5. **Multiple Perspectives**: Consider both short-term (recent days) and medium-term (30-day) trends
6. **Risk Disclosure**: Always remind users that past performance doesn't guarantee future results
7. **Actionable Insights**: Provide clear, practical insights based on the data

For investment questions (buy/sell), provide:
- Current price position (relative to high/low/average)
- Recent trend direction and strength
- Key support/resistance levels from the data
- Risk considerations
- Your analysis (with appropriate disclaimers)

Be professional, thorough, and back every statement with data from above.
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"I apologize, but I'm having trouble processing your request right now. Error: {str(e)}"

def process_stock_query(user_input, history):
    """
    Process user input and return appropriate response
    """
    user_input = user_input.strip()
    
    if not user_input:
        return history, ""
    
    # Get ticker from input
    ticker = get_ticker_from_input(user_input)
    
    if not ticker:
        error_msg = f"❌ Company or ticker '{user_input}' not found. Please try a different company name or ticker symbol."
        return history + [{"role": "user", "content": user_input}, {"role": "assistant", "content": error_msg}], ""
    
    # Get stock data
    stock_data = get_stock_data(ticker)
    
    if not stock_data:
        error_msg = f"❌ **Unable to retrieve information for {ticker} at this time. Please try again later.**"
        return history + [{"role": "user", "content": user_input}, {"role": "assistant", "content": error_msg}], ""
    
    # Format the response - Simple display with only current price and previous close
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Simplified stock information
    response = f"""📊 **{stock_data['company_name']} ({stock_data['ticker']})**

💰 **Current Price:** ${stock_data['current_price']:.2f}
📊 **Previous Close:** ${stock_data['previous_close']:.2f}
📈 **Change:** ${stock_data['day_change']:.2f} ({stock_data['day_change_pct']:+.2f}%)

📡 **Data Source:** {stock_data.get('source', 'Alpha Vantage')} API
_Data fetched at {timestamp}_
"""
    
    return history + [{"role": "user", "content": user_input}, {"role": "assistant", "content": response}], f"{ticker} "

def can_answer_with_historical_data(stock_data, question):
    """
    Use OpenAI to determine if a question can be answered with historical stock data
    
    Returns:
        tuple: (can_answer: bool, reasoning: str)
    """
    global client
    if client is None:
        try:
            client = get_openai_client()
        except ValueError as e:
            return False, "OpenAI client unavailable"
    
    # Create a summary of available data
    data_summary = f"""Available data for {stock_data['company_name']} ({stock_data['ticker']}):
- Current Price: ${stock_data['current_price']:.2f}
- Previous Close: ${stock_data['previous_close']:.2f}
- Day Change: {stock_data['day_change_pct']:.2f}%"""
    
    if stock_data.get('historical_data'):
        hist = stock_data['historical_data']
        data_summary += f"""
- 30-Day High: ${hist['period_high']:.2f}
- 30-Day Low: ${hist['period_low']:.2f}
- 30-Day Average: ${hist['period_avg']:.2f}
- 30-Day Change: {hist['period_change_pct']:.2f}%
- Daily price data for last 30 days (open, high, low, close, volume)"""
    
    prompt = f"""You are analyzing whether a user's question can be answered using historical stock data.

{data_summary}

User Question: "{question}"

Determine if this question can be answered using ONLY the historical data provided above (past 30 days of stock performance).

Answer "YES" if:
- Question is about past price movements, trends, volatility
- Question asks about historical highs/lows, averages
- Question can be analyzed using the 30-day data provided
- Question is about recent performance or patterns

Answer "NO" if:
- Question asks about future price predictions
- Question needs information not in the data (company fundamentals, news, earnings dates, etc.)
- Question is about general stock concepts or investment advice
- Question requires external information beyond price history

Respond with ONLY "YES" or "NO" followed by a brief reason (one sentence).
Format: YES/NO - [reason]"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=100
        )
        
        answer = response.choices[0].message.content.strip()
        
        # Parse response
        if answer.upper().startswith("YES"):
            return True, answer
        else:
            return False, answer
            
    except Exception as e:
        # Default to using historical data if analysis fails
        return True, f"Analysis failed: {str(e)}"

def ask_general_stock_question(ticker, company_name, question):
    """
    Ask OpenAI a general question about a stock without using historical data
    For questions that cannot be answered with 30-day price history
    """
    global client
    if client is None:
        try:
            client = get_openai_client()
        except ValueError as e:
            return f"⚠️ OpenAI API key not configured. Please set OPENAI_API_KEY in Hugging Face Spaces Settings → Repository secrets."
    
    prompt = f"""You are a knowledgeable financial assistant. The user is asking about {company_name} ({ticker}).

User Question: {question}

This question cannot be answered using historical price data alone. Provide helpful information based on general financial knowledge.

IMPORTANT GUIDELINES:
1. **No Price Predictions**: You cannot and should not predict future stock prices
2. **General Knowledge**: Provide general information, context, or factors to consider
3. **Educational**: Explain concepts, factors that affect stock prices, or general market dynamics
4. **Risk Disclosure**: Always remind users that stock prices are unpredictable and past performance doesn't guarantee future results
5. **Factors to Consider**: Discuss general factors like earnings reports, market conditions, industry trends, company news, etc.
6. **No Investment Advice**: Do not tell users to buy, sell, or hold. Only provide educational information.

For questions about future price movements:
- Explain that price predictions are speculative
- Discuss factors that typically influence stock prices (earnings, news, market sentiment, etc.)
- Mention what to watch for (upcoming earnings, product launches, economic indicators)
- Emphasize the importance of doing thorough research and consulting financial advisors

Be professional, honest, and educational. Focus on factors and concepts rather than predictions.
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"I apologize, but I'm having trouble processing your request right now. Error: {str(e)}"

def process_analytical_question(question, history):
    """
    Process analytical questions about the last mentioned stock
    Always fetches data first, then determines if it can answer the question
    """
    global client
    if client is None:
        client = get_openai_client()
    
    # Find the last stock mentioned - first check if ticker is in the current question
    last_ticker = None
    company_name = None
    
    # Check if the question itself starts with a ticker or company name
    # Try to extract ticker/company from the beginning of the question
    words = question.strip().split()
    if words:
        # First, try to find a ticker pattern (all caps in original, 1-5 letters)
        for i, word in enumerate(words[:3]):  # Check first 3 words
            if len(word) <= 5 and word.isalpha() and word.isupper():
                # Original word is all caps - likely a ticker
                # Verify it's not a common word
                common_words = ['WILL', 'WHAT', 'WHEN', 'WHERE', 'WHICH', 'THAT', 'THIS', 'THEN', 'THAN', 'THEY', 'THEM', 'WERE', 'BEEN', 'HAVE', 'FROM', 'WITH']
                if word not in common_words:
                    last_ticker = word
                    company_name = word
                    # Extract the actual question (everything after the ticker)
                    question = ' '.join(words[i+1:]).strip()
                    break
        
        # If no ticker found, try to find company name (lowercase or mixed case)
        if not last_ticker:
            # Try different combinations of first words as company name
            for num_words in [1, 2, 3]:  # Try 1 word first (tesla), then 2, then 3
                if num_words <= len(words):
                    potential_company = ' '.join(words[:num_words])
                    # Skip if it looks like a question word
                    if potential_company.lower() in ['will', 'what', 'when', 'where', 'how', 'why', 'which', 'can', 'should']:
                        continue
                    # Use search_company_ticker to find the ticker
                    ticker_attempt = search_company_ticker(potential_company)
                    if ticker_attempt:
                        last_ticker = ticker_attempt
                        company_name = potential_company
                        question = ' '.join(words[num_words:]).strip()
                        break
    
    # If no ticker found in question, look in history
    if not last_ticker:
        for i in range(len(history) - 1, -1, -1):
            if isinstance(history[i], dict) and "assistant" in history[i].get("role", ""):
                content = history[i].get("content", "")
                if "📊" in content and "**" in content:
                    # Extract ticker from the response
                    try:
                        start = content.find("**") + 2
                        end = content.find("**", start)
                        if end > start:
                            ticker_part = content[start:end]
                            if "(" in ticker_part and ")" in ticker_part:
                                company_name = ticker_part[:ticker_part.find("(")].strip()
                                ticker_start = ticker_part.find("(") + 1
                                ticker_end = ticker_part.find(")")
                                if ticker_end > ticker_start:
                                    last_ticker = ticker_part[ticker_start:ticker_end]
                                    break
                    except:
                        pass
    
    if not last_ticker:
        error_msg = "❌ Please enter a stock ticker/company first, or include it in your question (e.g., 'TSLA will it go up?')"
        return history + [{"role": "user", "content": question}, {"role": "assistant", "content": error_msg}], ""
    
    # ALWAYS fetch historical data first (30-day trends)
    stock_data = get_stock_data(last_ticker)
    
    if not stock_data:
        error_msg = f"❌ Unable to fetch current data for {last_ticker}. Please try again."
        return history + [{"role": "user", "content": question}, {"role": "assistant", "content": error_msg}], ""
    
    # Now determine if the question CAN be answered with this data
    can_answer, reasoning = can_answer_with_historical_data(stock_data, question)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if can_answer:
        # Question CAN be answered with historical data - use data-driven analysis
        answer = ask_llm_about_stock(stock_data, question)
        
        response = f"""🤖 **Analytical Response for {stock_data['company_name']} ({stock_data['ticker']})**

{answer}

📡 **Data Source:** {stock_data.get('source', 'Alpha Vantage')} API
_Answered at {timestamp}_"""
        
    else:
        # Question CANNOT be answered with historical data alone - use general knowledge
        answer = ask_general_stock_question(last_ticker, company_name or last_ticker, question)
        
        response = f"""💡 **General Information for {company_name or last_ticker} ({last_ticker})**

{answer}

---
_Response generated at {timestamp}_
🤖 _Powered by OpenAI GPT-4o-mini_

**Note:** This question cannot be answered using historical price data alone. For data-driven analysis of recent trends, try asking about past performance.
"""
    
    return history + [{"role": "user", "content": question}, {"role": "assistant", "content": response}], f"{last_ticker} "

def process_sector_query(sector_name, user_question, history):
    """
    Process sector analysis queries
    """
    # Fetch sector data
    sector_data = get_sector_data(sector_name)
    
    if not sector_data or not sector_data.get('stocks'):
        error_msg = f"❌ Unable to fetch data for {sector_name} sector. Supported sectors: technology, finance, healthcare, energy, retail, automotive."
        return history + [{"role": "user", "content": user_question}, {"role": "assistant", "content": error_msg}], ""
    
    # Format sector summary for display
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary = sector_data['summary']
    
    response = f"""🏢 **{sector_data['sector']} Sector Analysis** ({summary['total_stocks']} stocks)

📊 **Sector Performance:**
- 30-Day Average: {summary['avg_period_change']:+.2f}%
- Today Average: {summary['avg_day_change']:+.2f}%

🏆 **Best Performer:** {summary['best_performer']['ticker']} ({summary['best_performer']['period_change_pct']:+.2f}%)
📉 **Worst Performer:** {summary['worst_performer']['ticker']} ({summary['worst_performer']['period_change_pct']:+.2f}%)

📈 **Individual Stock Monthly Highs/Lows:**
"""
    
    for stock in sector_data['stocks']:
        response += f"\n**{stock['ticker']}**: High ${stock['period_high']:.2f} | Low ${stock['period_low']:.2f} | Change {stock['period_change_pct']:+.2f}%"
    
    response += f"\n\n📡 **Data Source:** Alpha Vantage API\n_Data fetched at {timestamp}_"
    
    # If there's a specific question, use AI to analyze
    if user_question and user_question.lower() != sector_name.lower():
        answer = ask_llm_about_sector(sector_data, user_question)
        response += f"\n\n---\n\n🤖 **AI Analysis:**\n\n{answer}\n\n📡 **Data Source:** Alpha Vantage API\n_Analyzed at {timestamp}_"
    
    return history + [{"role": "user", "content": user_question}, {"role": "assistant", "content": response}], ""

def get_last_query_type(history):
    """
    Determine the type of the last query (stock or sector)
    Returns: 'stock', 'sector', or None
    """
    for i in range(len(history) - 1, -1, -1):
        if isinstance(history[i], dict) and "assistant" in history[i].get("role", ""):
            content = history[i].get("content", "")
            if "Sector Analysis" in content:
                return 'sector'
            elif "📊 **" in content and "(" in content:
                return 'stock'
    return None

def handle_user_input(user_input, history):
    """
    Main handler for user input - determines if it's a stock query, sector query, or analytical question
    Clears history when switching between stock and sector contexts
    """
    user_input = user_input.strip()
    
    if not user_input:
        return history, ""
    
    # Check if this is a sector query
    sector_keywords = ['sector', 'technology sector', 'tech sector', 'finance sector', 
                      'financial sector', 'healthcare sector', 'energy sector', 
                      'retail sector', 'automotive sector', 'auto sector']
    
    is_sector_query = any(keyword in user_input.lower() for keyword in sector_keywords)
    
    # Check for context switch
    last_query_type = get_last_query_type(history)
    
    if is_sector_query:
        # Clear history if switching from stock to sector
        if last_query_type == 'stock':
            print("🔄 Context switch detected: Stock → Sector. Clearing previous context.")
            history = []
        
        # Extract sector name
        for sector in SECTOR_SCREENERS.keys():
            if sector in user_input.lower():
                return process_sector_query(sector, user_input, history)
        
        # If no specific sector found, show available sectors
        error_msg = "❌ Please specify a sector. Available sectors: Technology, Finance, Healthcare, Energy, Retail, Industrial, Materials, Utilities, Real Estate, Communication, Consumer"
        return history + [{"role": "user", "content": user_input}, {"role": "assistant", "content": error_msg}], ""
    
    # Check if this looks like an analytical question
    analytical_keywords = [
        # Analysis keywords
        "analyze", "analysis", "trend", "trending", "outlook", "forecast", "prediction",
        "pattern", "patterns", "momentum", "direction",
        
        # Investment decision keywords  
        "should i buy", "should i sell", "should i invest", "worth buying", "worth investing",
        "good time to buy", "good time to sell", "good entry point", "good exit point",
        "investment", "recommendation", "advice", "opinion",
        
        # Question keywords
        "why", "how", "what", "when", "where", "which", "is it", "are we", "will it",
        "will we", "will the", "will there", "can we", "can it",
        "explain", "tell me", "show me", "give me", "can you",
        
        # Market keywords
        "bullish", "bearish", "volatile", "volatility", "risk", "risky",
        "uptrend", "downtrend", "support", "resistance", "high", "low",
        
        # Performance keywords
        "performance", "performing", "doing", "moving", "going up", "going down",
        "increasing", "decreasing", "rising", "falling", "growing", "declining",
        
        # Future/prediction keywords
        "will", "going to", "expect", "expecting", "prediction", "predict",
        
        # Insight keywords
        "insights", "thoughts", "view", "perspective", "assessment", "evaluation",
        "opportunity", "potential", "likely"
    ]
    
    is_analytical = any(keyword in user_input.lower() for keyword in analytical_keywords)
    
    if is_analytical:
        return process_analytical_question(user_input, history)
    else:
        # This is a stock query
        # Clear history if switching from sector to stock
        if last_query_type == 'sector':
            print("🔄 Context switch detected: Sector → Stock. Clearing previous context.")
            history = []
        
        return process_stock_query(user_input, history)

def create_gradio_interface():
    """Create and return the Gradio interface"""
    
    # Financial Blue theme (Professional)
    stock_theme = gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="indigo",
        neutral_hue="slate",
    )
    
    with gr.Blocks(title="Stock Genie", theme=stock_theme) as demo:
        gr.Markdown("""
        # 📊 Stock Genie
        
        **Get real-time stock data and AI-powered analysis with 30 days of historical data!**
        
        ### 🚀 How to use:
        1. **Get Stock Data:** Enter a company name (e.g., "Apple") or ticker symbol (e.g., "AAPL") to get current information about the stock
        2. **Ask ANY Question** regarding the stock performance
        3. **Analyze Sectors:** Enter "technology sector", "finance sector", "healthcare sector", etc. Make sure to add the word "sector"
        
        **Supported Sectors:** Technology, Finance, Healthcare, Energy, Retail, Industrial, Materials, Utilities, Real Estate, Communication, Consumer
        """)
        
        chatbot = gr.Chatbot(
            label="Stock Analysis Chat",
            height=500,
            type='messages',
            show_copy_button=True
        )
        
        with gr.Row():
            msg = gr.Textbox(
                placeholder="Enter company name (e.g., 'Apple') or ticker (e.g., 'AAPL')...",
                label="Your Input",
                scale=4
            )
            submit_btn = gr.Button("Send", variant="primary", scale=1)
        
        with gr.Row():
            clear_btn = gr.Button("Clear Chat", variant="secondary")

        # Event handlers
        def user_submit(user_message, chat_history):
            return handle_user_input(user_message, chat_history)
        
        def clear_chat():
            return [], ""

        # Connect events
        submit_btn.click(user_submit, [msg, chatbot], [chatbot, msg])
        msg.submit(user_submit, [msg, chatbot], [chatbot, msg])
        clear_btn.click(clear_chat, outputs=[chatbot, msg])
        
        # Examples
        gr.Examples(
            examples=[
                "Apple",
                "What's the trend?",
                "Technology sector",
                "IBM",
                "What's the highest and lowest this month?",
                "Finance sector",
                "Should I invest in this sector?",
                "Tesla",
                "Healthcare sector"
            ],
            inputs=msg,
            label="Try these examples (stocks, sectors, and questions):"
        )

    return demo

# Create the demo at module level for Hugging Face Spaces
demo = create_gradio_interface()

if __name__ == "__main__":
    # For local testing and gradio deploy
    print("🚀 Starting Stock Genie...")
    print("📊 Features: Yahoo Finance ticker lookup + Alpha Vantage real-time data + AI analysis")
    
    # Check API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("⚠️  OPENAI_API_KEY not found - set it in HF Spaces secrets or .env file")
    
    if not ALPHA_VANTAGE_API_KEY:
        print("⚠️  ALPHA_VANTAGE_API_KEY not found - set it in HF Spaces secrets or .env file")
    
    demo.launch(
        share=False,
        show_error=True
    )
