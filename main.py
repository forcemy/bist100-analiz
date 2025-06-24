import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import ta
from datetime import datetime

st.title("📊 BIST100 Teknik Analiz")
st.write("Günlük AL/SAT sinyali üreten sistem")

# Hisse listesini CSV'den al
df = pd.read_csv("bist100.csv")
bist100 = df["symbol"].tolist()

al_sinyali_gelenler = []
log_list = []

for sembol in bist100:
    try:
        st.write(f"\n⏳ {sembol} analiz ediliyor...")

        data = yf.download(sembol, period="6mo", interval="1d", progress=False)
        if data.empty:
            st.write(f"⚠️ {sembol} için veri bulunamadı.")
            continue

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # RSI & MACD
        data.ta.rsi(length=14, append=True)
        data.ta.macd(append=True)

        # Bollinger Bands
        bb = ta.volatility.BollingerBands(close=data["Close"])
        data["bb_upper"] = bb.bollinger_hband().squeeze()
        data["bb_middle"] = bb.bollinger_mavg().squeeze()
        data["bb_lower"] = bb.bollinger_lband().squeeze()

        # StochRSI
        stochrsi = ta.momentum.StochRSIIndicator(close=data["Close"])
        data["stochrsi"] = stochrsi.stochrsi_k().squeeze()

        # MA20 - MA50
        data["ma20"] = data["Close"].rolling(window=20).mean()
        data["ma50"] = data["Close"].rolling(window=50).mean()

        # Volume ve OBV
        data["volume_ma20"] = data["Volume"].rolling(window=20).mean()
        obv = ta.volume.OnBalanceVolumeIndicator(close=data["Close"], volume=data["Volume"])
        data["obv"] = obv.on_balance_volume().squeeze()

        # ADX
        adx = ta.trend.ADXIndicator(high=data["High"], low=data["Low"], close=data["Close"])
        data["adx"] = adx.adx().squeeze()

        latest = data.iloc[-1]
        puan = 0
        if latest['RSI_14'] < 30: puan += 1
        if latest['MACD_12_26_9'] > latest['MACDs_12_26_9']: puan += 1
        if latest['Close'] < latest['bb_lower']: puan += 1
        if latest['stochrsi'] < 0.2: puan += 1
        if latest['ma20'] > latest['ma50']: puan += 1
        if latest['Volume'] > latest['volume_ma20']: puan += 1
        if latest['adx'] > 20: puan += 1

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

        st.write(f"📈 Sinyal: {sinyal} ({puan} puan)")

        log_list.append({
            "Tarih": datetime.now().strftime("%Y-%m-%d"),
            "Symbol": sembol,
            "Close": latest['Close'],
            "RSI": latest['RSI_14'],
            "MACD": latest['MACD_12_26_9'],
            "MACD_Sinyal": latest['MACDs_12_26_9'],
            "StochRSI": latest['stochrsi'],
            "MA20": latest['ma20'],
            "MA50": latest['ma50'],
            "BB_Lower": latest['bb_lower'],
            "Volume": latest['Volume'],
            "Volume_MA20": latest['volume_ma20'],
            "OBV": latest['obv'],
            "ADX": latest['adx'],
            "Skor": puan,
            "Sinyal": sinyal
        })

    except Exception as e:
        st.error(f"{sembol} için analiz hatası: {e}")

# Özet
st.subheader("📋 Özet")
if al_sinyali_gelenler:
    st.write("✅ **AL Sinyali Gelen Hisseler:**")
    for hisse in al_sinyali_gelenler:
        st.write(f"• {hisse}")
else:
    st.write("📭 Bugün AL sinyali veren hisse bulunamadı.")

# CSV log dosyasını kaydet
log_df = pd.DataFrame(log_list)
log_df.to_csv("günlük_analiz_log.csv", index=False)
st.success("💾 Günlük analiz sonuçları 'günlük_analiz_log.csv' olarak kaydedildi.")
