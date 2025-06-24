import streamlit as st
import pandas as pd
import yfinance as yf
import ta

st.set_page_config(layout="wide")
st.title("📈 BIST 100 Teknik Analiz")

# CSV dosyasını oku ve sembolleri al
try:
    bist100_df = pd.read_csv("bist100.csv")
    semboller = bist100_df["Sembol"].dropna().unique().tolist()
except Exception as e:
    st.error(f"Sembol dosyası okunamadı: {e}")
    semboller = []

# Yahoo formatına uygun hale getir
def duzelt(sembol):
    if ".IS" in sembol:
        return sembol  # zaten doğru
    return f"{sembol}.IS"

# Teknik indikatörlere göre sinyal üret
def analiz_et(df):
    if df is None or df.empty or len(df) < 50:
        return "Veri yetersiz"
    
    df["rsi"] = ta.momentum.RSIIndicator(close=df["Close"]).rsi()
    macd = ta.trend.MACD(close=df["Close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["ema_9"] = ta.trend.EMAIndicator(close=df["Close"], window=9).ema_indicator()
    df["sma_50"] = ta.trend.SMAIndicator(close=df["Close"], window=50).sma_indicator()

    rsi = df["rsi"].iloc[-1]
    macd_last = df["macd"].iloc[-1]
    macd_sig = df["macd_signal"].iloc[-1]
    price = df["Close"].iloc[-1]
    ema = df["ema_9"].iloc[-1]
    sma = df["sma_50"].iloc[-1]

    if rsi < 30 and macd_last > macd_sig and price > ema > sma:
        return "🔼 Güçlü AL"
    elif rsi > 70 and macd_last < macd_sig and price < ema < sma:
        return "🔽 Güçlü SAT"
    else:
        return "⏸ NÖTR"

# Ana döngü
for sembol in semboller:
    st.markdown(f"⏳ **{sembol}** analiz ediliyor...")
    try:
        yf_sembol = duzelt(sembol)
        data = yf.download(yf_sembol, period="6mo", interval="1d", progress=False)
        sinyal = analiz_et(data)
        st.success(f"✅ {sembol} sinyali: {sinyal}")
    except Exception as e:
        st.error(f"❌ {sembol} için analiz hatası: {str(e)}")
