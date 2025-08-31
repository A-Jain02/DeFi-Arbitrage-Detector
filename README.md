# 🚀 Real-Time Crypto Arbitrage Detector

This project is a **real-time cryptocurrency arbitrage detection dashboard** that pulls **live price feeds** from multiple global exchanges and highlights **profitable arbitrage opportunities** instantly.

---

## 🔎 What is Arbitrage?
Arbitrage in crypto means **buying an asset at a lower price on one exchange and selling it at a higher price on another**.  
Since exchanges often differ slightly in prices, arbitrageurs can capture profit from these spreads — sometimes within seconds.

---

## ⚡ Features
- **Live WebSocket Feeds** → Binance, Coinbase, Bitfinex, and Huobi (instant updates).  
- **Profit Leaderboard** → Detects and sorts arbitrage opportunities by profit %.  
- **Custom Alerts** → Flags trades with spreads >0.02%.  
- **Interactive Heatmap** → Visualizes relative profits across exchanges (green = profitable, red = loss).  
- **Sparklines & Trends** → Mini time-series graphs showing profit % trends per token.  
- **Fully Interactive Dashboard** → Built in [Streamlit](https://streamlit.io), runs in the browser.  

---

## 🛠️ How It Works
1. **Data Collection**  
   - `ws_multi.py` opens WebSocket connections to Binance, Coinbase, Bitfinex, and Huobi.  
   - Prices are updated in real time (sub-second latency).  

2. **Arbitrage Detection**  
   - For each token (BTC, ETH, ADA, SOL, DOGE), the system compares prices across exchanges.  
   - Finds **minimum (buy) price** and **maximum (sell) price**.  
   - Calculates spread:  
     ```
     Profit % = ((Sell Price - Buy Price) / Buy Price) * 100
     ```

3. **Visualization**  
   - `streamlit_app.py` displays:  
     - 📊 **Leaderboard table** with Buy/Sell exchange, prices, and profit %.  
     - 🔔 **Alerts** for opportunities above threshold (default: 0.02%).  
     - 🌡 **Heatmap** showing spread across all exchanges.  
     - 📉 **Sparklines** for profit % trends over time.  

---

## 💡 Use Case
- **Traders** can identify profitable arbitrage opportunities in real time.  
- **Researchers** can analyze market efficiency and exchange spreads.  
- **Developers** can extend the system to automatically execute trades via APIs.  

⚠️ **Note:** This project is for educational and research purposes only. It does not execute trades. Real arbitrage involves execution risks, latency, and fees.

---

## 🚀 Getting Started

** 1. Clone the Respository
```bash
git clone https://github.com/yourusername/DeFi-Arbitrage-Detector.git
cd DeFi-Arbitrage-Detector
```

** 2. Create an Environment 
```bash
python3 -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows
```

** 3. Install Dependencies
```bash
pip install -r requirements.txt
```

** 4. Run the Dashboard
```bash
streamlit run streamlit_app.py
```