import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta

st.title("BIST 100 Teknik Analiz")

# CSV dosyasını oku
bist100_df = pd.read_csv("bist100.csv")

# Hisse sembollerini al
semboller = bist100_df["Sembol"].dropna().unique().tolist()

# Gerekirse .IS ekle
semboller = [s if s.endswith(".IS") else s + ".IS" for s in semboller]

for sembol in semboller:
    st.markdown(f"⏳ {sembol} analiz ediliyor...")

    try:
        data = yf.download(sembol, period="6mo", interval="1d")

        if data.empty:
            st.error(f"{sembol} için veri bulunamadı.")
            continue

        # Sadece 'Close' sütunu üzerinden analiz
        close = data["Close"]

        # Teknik indikatör hesapla (örnek: RSI)
        try:
            rsi = ta.rsi(close)
        except Exception as e:
            st.error(f"{sembol} için RSI hesaplanamadı: {e}")
            continue

        # RSI görselleştir
        st.line_chart(rsi, height=150)

    except Exception as e:
        st.error(f"{sembol} için analiz hatası: {e}")
