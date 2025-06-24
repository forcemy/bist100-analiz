
import streamlit as st
import pandas as pd
import yfinance as yf
import ta
from datetime import datetime

# Başlık
st.title("BIST 100 Teknik Analiz")

# CSV dosyasını oku
try:
    bist100_df = pd.read_csv("bist100.csv")
except FileNotFoundError:
    st.error("CSV dosyası bulunamadı. Lütfen 'bist100.csv' dosyasını yükleyin.")
    st.stop()

# Sembol sütunu var mı kontrol et
if "Sembol" not in bist100_df.columns:
    st.error("'Sembol' adında bir sütun bulunamadı.")
    st.stop()

# Hisse sembollerini al
semboller = bist100_df["Sembol"].dropna().unique().tolist()

# Her sembol için analiz
for sembol in semboller:
    # .IS ekleme kontrolü
    if not sembol.endswith(".IS"):
        yf_sembol = sembol + ".IS"
    else:
        yf_sembol = sembol

    st.markdown(f"⏳ **{sembol}** analiz ediliyor...")

    try:
        data = yf.download(yf_sembol, period="6mo", interval="1d")
        if data.empty:
            st.warning(f"{sembol} için veri bulunamadı.")
            continue

        data.dropna(inplace=True)

        # İndikatörleri hesapla
        data["RSI"] = ta.momentum.RSIIndicator(close=data["Close"]).rsi()
        data["MACD"] = ta.trend.MACD(close=data["Close"]).macd()
        data["Signal"] = ta.trend.MACD(close=data["Close"]).macd_signal()

        latest = data.iloc[-1]

        st.subheader(sembol)
        st.write(f"🔹 RSI: {latest['RSI']:.2f}")
        st.write(f"🔹 MACD: {latest['MACD']:.2f}")
        st.write(f"🔹 Signal: {latest['Signal']:.2f}")

        # Sinyal üretimi
        if latest["RSI"] < 30 and latest["MACD"] > latest["Signal"]:
            st.success("📈 AL Sinyali")
        elif latest["RSI"] > 70 and latest["MACD"] < latest["Signal"]:
            st.error("📉 SAT Sinyali")
        else:
            st.info("⏸️ NÖTR Sinyal")

    except Exception as e:
        st.error(f"{sembol} için analiz hatası: {e}")
