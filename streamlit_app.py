import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from ws_multi import latest_prices, launch_all_ws
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 10 seconds
st_autorefresh(interval=10 * 1000, key="datarefresh")

# Start WebSockets once
if "ws_started" not in st.session_state:
    launch_all_ws()
    st.session_state["ws_started"] = True

st.title("🚀 Multi-Exchange Crypto Arbitrage Leaderboard (Live)")

tokens = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "DOGEUSDT"]

symbol_map = {
    "BTCUSDT": {"binance": "BTCUSDT", "coinbase": "BTCUSD", "bitfinex": "tBTCUSD", "huobi": "BTCUSDT"},
    "ETHUSDT": {"binance": "ETHUSDT", "coinbase": "ETHUSD",  "bitfinex": "tETHUSD", "huobi": "ETHUSDT"},
    "ADAUSDT": {"binance": "ADAUSDT", "coinbase": "ADAUSD",  "bitfinex": "tADAUSD", "huobi": "ADAUSDT"},
    "SOLUSDT": {"binance": "SOLUSDT", "coinbase": "SOLUSD",  "bitfinex": "tSOLUSD", "huobi": "SOLUSDT"},
    "DOGEUSDT": {"binance": "DOGEUSDT", "coinbase": "DOGEUSD", "bitfinex": "tDOGEUSD", "huobi": "DOGEUSDT"},
}
def smart_round(token, price):
   if token in ["ADA", "DOGE"]:   # low-value tokens
      return round(price, 4)
   else:                          # high-value tokens
      return round(price, 2)

# Keep historical data for sparklines
if "history" not in st.session_state:
    st.session_state["history"] = {t.replace("USDT", ""): [] for t in tokens}

# Collect arbitrage opportunities
arbitrage_data = []
detailed_alerts = []


for token in tokens:
    prices = {}
    for ex, mapping in symbol_map[token].items():
        if mapping in latest_prices[ex]:
            prices[ex] = latest_prices[ex][mapping]

    if len(prices) >= 2:
        min_ex = min(prices, key=prices.get)
        max_ex = max(prices, key=prices.get)
        min_price = prices[min_ex]
        max_price = prices[max_ex]
        profit_pct = ((max_price - min_price) / min_price) * 100

        name = token.replace("USDT", "")
        st.session_state["history"][name].append(profit_pct)
        if len(st.session_state["history"][name]) > 30:  # keep only last 30 points
         st.session_state["history"][name].pop(0)

        name = token.replace("USDT", "")
    
        arbitrage_data.append({
            "Token": name,
            "Buy Exchange": min_ex,
            "Buy Price": smart_round(name, min_price),
            "Sell Exchange": max_ex,
            "Sell Price": smart_round(name, max_price),
            "Profit %": round(profit_pct, 2)
        })

        # Store alerts if profit > 0.15%
        if profit_pct > 0.15:
            detailed_alerts.append(
                f"{token.replace('USDT','')}: Buy on {min_ex} @ {min_price:.2f}, "
                f"Sell on {max_ex} @ {max_price:.2f} → Profit {profit_pct:.2f}%"
            )

# Show Leaderboard
if arbitrage_data:
    df = pd.DataFrame(arbitrage_data)
    df = df.sort_values(by="Profit %", ascending=False)
    st.subheader("📊 Arbitrage Opportunities Leaderboard")

    # Combine formatting + colors into one styled object
    df_styled = (
        df.style
        .format({
            "Buy Price": lambda x: f"{x:.4f}" if df.loc[df["Buy Price"] == x, "Token"].values[0] in ["ADA", "DOGE"] else f"{x:.4f}",
            "Sell Price": lambda x: f"{x:.4f}" if df.loc[df["Sell Price"] == x, "Token"].values[0] in ["ADA", "DOGE"] else f"{x:.4f}",
            "Profit %": "{:.4f}%".format
        })
        .applymap(lambda v: "background-color: green" if v in df["Buy Exchange"].values else "", subset=["Buy Exchange"])
        .applymap(lambda v: "background-color: firebrick" if v in df["Sell Exchange"].values else "", subset=["Sell Exchange"])
        .background_gradient(cmap="Greens", subset=["Profit %"])
    )

    # Display styled dataframe
    st.dataframe(df_styled, use_container_width=True)

    st.subheader("🔥 Arbitrage Profit Heatmap (vs Cheapest Exchange)")

    heatmap_data = []
    for token in tokens:
      row = {"Token": token.replace("USDT", "")}
      prices = {}

      # Collect live prices
      for ex, mapping in symbol_map[token].items():
         if mapping in latest_prices[ex]:
               prices[ex] = float(latest_prices[ex][mapping])

      if prices:
         min_price = min(prices.values())
         # Compute % difference vs cheapest exchange
         for ex in ["binance", "coinbase", "bitfinex", "huobi"]:
               if ex in prices:
                  row[ex] = ((prices[ex] - min_price) / min_price) * 100
               else:
                  row[ex] = np.nan
         heatmap_data.append(row)

    # DataFrame
    heatmap_df = pd.DataFrame(heatmap_data).set_index("Token")

    # Plot heatmap
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.heatmap(
      heatmap_df.astype(float),
      annot=True, fmt=".2f",
      cmap="RdYlGn", linewidths=0.5,
      center=0,  # so 0% = neutral color
      cbar_kws={'label': 'Profit vs Cheapest (%)'}
    ) 

    plt.title("Profit Spread Across Exchanges", fontsize=12)
    st.pyplot(fig)

    st.subheader("📉 Arbitrage Profit Trends (Last ~30s Refreshes)")
   # Grid layout: 2 columns
    cols = st.columns(2)

    for i, token in enumerate(df["Token"]):
      history = st.session_state["history"][token]
      if history:
        fig, ax = plt.subplots(figsize=(2.5, 1))  # much smaller
        ax.plot(history, color="navy", linewidth=1.5)
        ax.fill_between(range(len(history)), history, color="navy", alpha=0.2)  # shade under line
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(token, fontsize=9, pad=2)
        plt.tight_layout(pad=0.1)

        # Put in grid
        cols[i % 2].pyplot(fig)

    # Show detailed alerts
    if detailed_alerts:
        st.error("🚨 Arbitrage Opportunities > 0.15%:")
        for alert in detailed_alerts:
            st.write(alert)

    st.caption(f"Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
else:
    st.info("⏳ Waiting for live prices...")
