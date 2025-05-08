from supabase import create_client
import yfinance as yf

# ✅ Connect to Supabase
url = "https://xbadgnlebeopywafixwi.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhiYWRnbmxlYmVvcHl3YWZpeHdpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDE1NTc0ODksImV4cCI6MjA1NzEzMzQ4OX0.i9p_cWHOrNcd8Vdg8I39ZR1RC7BbjjRiWMEgTTlXya4"

supabase = create_client(url, key)

# ✅ Fetch portfolios
response = supabase.table('portfolios').select('id', 'name', 'stocks').execute()

# ✅ Build dictionary: {portfolio id: {name, tickers, stocks}}
portfolio_tickers = {}

for record in response.data:
    portfolio_id = record['id']
    portfolio_name = record['name']
    stocks_list = record['stocks']
    tickers = [stock['symbol'] for stock in stocks_list]
    portfolio_tickers[portfolio_id] = {
        'name': portfolio_name,
        'tickers': tickers,
        'stocks': stocks_list
    }

# ✅ Print tickers per portfolio
for portfolio_id, info in portfolio_tickers.items():
    print(f"Portfolio ID '{portfolio_id}' ('{info['name']}') has {len(info['tickers'])} tickers:")
    print(info['tickers'])
    print("-" * 40)

# ✅ Extract unique tickers
unique_tickers = set()
for info in portfolio_tickers.values():
    unique_tickers.update(info['tickers'])

unique_tickers = list(unique_tickers)
print(f"\n✅ Found {len(unique_tickers)} unique tickers:")
print(unique_tickers)

# ✅ Fetch prices for unique tickers
ticker_prices = {}

for ticker in unique_tickers:
    try:
        data = yf.Ticker(ticker)
        hist = data.history(period="1d")
        if not hist.empty:
            price = hist['Close'].iloc[-1]  # ✅ FIX: use iloc[-1] to avoid FutureWarning
            ticker_prices[ticker] = float(price)
            print(f"✅ {ticker}: {price}")
        else:
            print(f"⚠️ No data found for {ticker}")
    except Exception as e:
        print(f"⚠️ Error fetching {ticker}: {e}")

# ✅ Update stocks JSON with current prices
for portfolio_id, info in portfolio_tickers.items():
    updated_stocks = []
    for stock in info['stocks']:
        symbol = stock['symbol']
        new_price = ticker_prices.get(symbol, None)
        stock['currentPrice'] = new_price  # ✅ update currentPrice (NOT price)
        updated_stocks.append(stock)

    # ✅ Write updated stocks back to Supabase
    result = supabase.table('portfolios').update({'stocks': updated_stocks}).eq('id', portfolio_id).execute()
    print(f"✅ Updated portfolio '{info['name']}' (ID: {portfolio_id}) with latest current prices.")

print("\n🎉 All portfolios updated with current prices in Supabase!")
