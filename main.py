import streamlit as st
import pandas as pd
import yfinance as yf
import ta
from datetime import datetime

st.title("BIST 100 Teknik Analiz")

# CSV dosyasını oku
bist100_df = pd.read_csv("bist100.csv")
semboller = bist100_df["Sembol"].dropna().unique().tolist()

for sembol in semboller:
    st.write(f"⏳ {sembol}.IS analiz ediliyor...")

    try:
        data = yf.download(f"{sembol}.IS", period="6mo", interval="1d")

        if data.empty:
            st.error(f"{sembol}.IS için veri alınamadı.")
            continue

        close = data["Close"]
        if len(close.shape) == 2:
            close = close.squeeze()

        # RSI
        rsi = ta.momentum.RSIIndicator(close=close).rsi()

        # MACD
        macd = ta.trend.MACD(close=close)
        macd_line = macd.macd()
        signal_line = macd.macd_signal()

        st.success(f"{sembol}.IS RSI: {rsi.iloc[-1]:.2f}, MACD: {macd_line.iloc[-1]:.2f}, Signal: {signal_line.iloc[-1]:.2f}")

    except Exception as e:
        st.error(f"{sembol}.IS için analiz hatası: {e}")
