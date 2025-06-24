import streamlit as st
import pandas as pd
import yfinance as yf
import ta  # pandas_ta değil, ta kütüphanesi
from datetime import datetime

st.set_page_config(layout="wide")
st.title("BIST 100 Teknik Analiz Uygulaması")

# BIST 100 sembol listesini oku
bist100_df = pd.read_csv("bist100.csv")  # doğru dosya adı olduğundan emin ol
semboller = bist100_df["Sembol"].dropna().unique().tolist()

# Başla
for sembol in semboller:
    st.markdown(f"🔍 `{sembol}` analiz ediliyor...")
    try:
        data = yf.download(f"{sembol}.IS", period="6mo", interval="1d")
        if data.empty or len(data) < 50:
            st.error(f"{sembol} verisi yetersiz.")
            continue

        # Göstergeleri hesapla
        data["RSI"] = ta.momentum.RSIIndicator(close=data["Close"]).rsi()
        data["MACD"] = ta.trend.MACD(close=data["Close"]).macd()
        data["MACD_signal"] = ta.trend.MACD(close=data["Close"]).macd_signal()
        data["EMA_20"] = ta.trend.EMAIndicator(close=data["Close"], window=20).ema_indicator()
        data["EMA_50"] = ta.trend.EMAIndicator(close=data["Close"], window=50).ema_indicator()

        # Basit al-sat sinyali
        rsi = data["RSI"].iloc[-1]
        macd = data["MACD"].iloc[-1]
        macd_signal = data["MACD_signal"].iloc[-1]
        ema_20 = data["EMA_20"].iloc[-1]
        ema_50 = data["EMA_50"].iloc[-1]
        close_price = data["Close"].iloc[-1]

        sinyal = "NÖTR"
        if rsi < 30 and macd > macd_signal and ema_20 > ema_50:
            sinyal = "💚 AL"
        elif rsi > 70 and macd < macd_signal and ema_20 < ema_50:
            sinyal = "💔 SAT"

        st.success(f"{sembol} için sinyal: **{sinyal}**\nFiyat: {close_price:.2f}₺")

    except Exception as e:
        st.error(f"{sembol} analiz hatası: {str(e)}")
