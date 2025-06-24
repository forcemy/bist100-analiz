import streamlit as st
import pandas as pd
import yfinance as yf
from ta.momentum import RSIIndicator, StochRSIIndicator
from ta.trend import MACD, ADXIndicator
from ta.volatility import BollingerBands
from ta.volume import OnBalanceVolumeIndicator
from datetime import datetime

st.title("BIST100 Teknik Analiz")
st.write("Günlük AL/SAT sinyali üreten sistem")

# Hisse listesini CSV'den oku
df = pd.read_csv("bist100.csv")
bist100 = df["symbol"].tolist()

al_sinyali_gelenler = []
log_list = []

for sembol in bist100:
    try:
        st.write(f"⏳ {sembol} analiz ediliyor...")

        data = yf.download(sembol, period="6mo", interval="1d", progress=False)
        if data.empty:
            st.warning(f"{sembol} için veri bulunamadı.")
            continue

        # RSI
        data["rsi"] = RSIIndicator(close=data["Close"]).rsi()

        # MACD
        macd = MACD(close=data["Close"])
        data["macd"] = macd.macd()
        data["macd_signal"] = macd.macd_signal()

        # Bollinger Bands
        bb = BollingerBands(close=data["Close"])
        data["bb_lower"] = bb.bollinger_lband()

        # StochRSI
        data["stochrsi"] = StochRSIIndicator(close=data["Close"]).stochrsi_k()

        # MA20 - MA50
        data["ma20"] = data["Close"].rolling(20).mean()
        data["ma50"] = data["Close"].rolling(50).mean()

        # Volume MA20 ve OBV
        data["volume_ma20"] = data["Volume"].rolling(20).mean()
        data["obv"] = OnBalanceVolumeIndicator(close=data["Close"], volume=data["Volume"]).on_balance_volume()

        # ADX
        data["adx"] = ADXIndicator(high=data["High"], low=data["Low"], close=data["Close"]).adx()

        latest = data.iloc[-1]
        puan = 0
        if latest["rsi"] < 30: puan += 1
        if latest["macd"] > latest["macd_signal"]: puan += 1
        if latest["Close"] < latest["bb_lower"]: puan += 1
        if latest["stochrsi"] < 20: puan += 1
        if latest["ma20"] > latest["ma50"]: puan += 1
        if latest["Volume"] > latest["volume_ma20"]: puan += 1
        if latest["adx"] > 20: puan += 1

        if puan >= 5:
            sinyal = "GÜÇLÜ AL"
            al_sinyali_gelenler.append(sembol)
        elif puan == 4:
            sinyal = "AL"
            al_sinyali_gelenler.append(sembol)
        elif puan == 3:
            sinyal = "NÖTR"
        elif puan == 2:
            sinyal = "SAT"
        else:
            sinyal = "GÜÇLÜ SAT"

        st.success(f"{sembol}: {sinyal} ({puan} puan)")

        log_list.append({
            "Tarih": datetime.now().strftime("%Y-%m-%d"),
            "Symbol": sembol,
            "Close": latest["Close"],
            "RSI": latest["rsi"],
            "MACD": latest["macd"],
            "MACD_Sinyal": latest["macd_signal"],
            "StochRSI": latest["stochrsi"],
            "MA20": latest["ma20"],
            "MA50": latest["ma50"],
            "BB_Lower": latest["bb_lower"],
            "Volume": latest["Volume"],
            "Volume_MA20": latest["volume_ma20"],
            "OBV": latest["obv"],
            "ADX": latest["adx"],
            "Skor": puan,
            "Sinyal": sinyal
        })

    except Exception as e:
        st.error(f"{sembol} için analiz hatası: {e}")

# Özet
st.write("## 📊 AL Sinyali Gelen Hisseler")
if al_sinyali_gelenler:
    for hisse in al_sinyali_gelenler:
        st.write(f"✅ {hisse}")
else:
    st.write("📭 Bugün AL sinyali veren hisse bulunamadı.")

# CSV kaydet
log_df = pd.DataFrame(log_list)
log_df.to_csv("günlük_analiz_log.csv", index=False)
st.success("💾 'günlük_analiz_log.csv' olarak kayıt yapıldı.")
