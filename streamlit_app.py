import streamlit as st
import pandas as pd
from data_fetcher import fetch_prices   # our parallel fetcher

# Title
st.title("Crypto Arbitrage Dashboard")

# Sidebar for token selection
st.sidebar.header("Select Currency")
tokens = ["BTC", "ETH", "USDT", "BNB", "ADA", "DOGE", "SOL", "DOT"]
selected_token = st.sidebar.selectbox("Choose a token", tokens)

# Fetch live prices (all exchanges)
prices_by_exchange = fetch_prices()

# Collect prices for the selected token across exchanges
token_prices = {}
for ex, ex_data in prices_by_exchange.items():
    if selected_token in ex_data:
        token_prices[ex] = ex_data[selected_token]

# Show results
if token_prices:
    # Display in a table
    df = pd.DataFrame(list(token_prices.items()), columns=["Exchange", "Price (USD)"])
    st.subheader(f"Live Prices for {selected_token}")
    st.table(df)

    # Arbitrage detection: min vs max
    min_ex = min(token_prices, key=token_prices.get)
    max_ex = max(token_prices, key=token_prices.get)
    min_price = token_prices[min_ex]
    max_price = token_prices[max_ex]

    if max_price > min_price:
        profit_pct = ((max_price - min_price) / min_price) * 100
        st.success(
            f"💰 Arbitrage: Buy on {min_ex} @ {min_price:.2f}, "
            f"Sell on {max_ex} @ {max_price:.2f} → Profit = {profit_pct:.2f}%"
        )
    else:
        st.info("No arbitrage opportunity right now.")
else:
    st.error(f"No price data available for {selected_token}.")
