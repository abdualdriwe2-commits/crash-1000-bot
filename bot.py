import requests
import pandas as pd
import time

TOKEN = "7702086689:AAEDgQS1DcdcDEmcpYTzpFvDKlEiIVVfKBU"
CHAT_ID = "1832620697"

last_alert_time = None

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


def get_data():
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=50"
    data = requests.get(url).json()

    df = pd.DataFrame(data, columns=[
        "time","open","high","low","close","volume",
        "close_time","q","n","taker_base","taker_quote","ignore"
    ])

    df["open"] = df["open"].astype(float)
    df["close"] = df["close"].astype(float)
    df["low"] = df["low"].astype(float)

    return df


def check_signal():
    global last_alert_time

    df = get_data()

    df["ema35"] = df["close"].ewm(span=35).mean()
    df["ema220"] = df["close"].ewm(span=220).mean()

    df = df.iloc[::-1]

    current_time = df["time"][1]

    if last_alert_time == current_time:
        return

    isTrendUp = (df["ema35"][1] > df["ema220"][1]) and (df["close"][1] > df["ema35"][1])
    isRed = df["close"][1] < df["open"][1]
    stayAbove = df["low"][1] > df["ema35"][1]

    redSize = df["open"][1] - df["close"][1]

    greenSum = 0
    for i in range(2, 7):
        if df["close"][i] > df["open"][i]:
            greenSum += (df["close"][i] - df["open"][i])

    isSmall = redSize > 0 and redSize <= greenSum

    if isTrendUp and isRed and stayAbove and isSmall:
        price = df["close"][1]

        msg = f"""⚠️ Crash 1000 Alert
شمعة حمراء بعد صعود قوي
السعر: {price}
استعد للدخول"""

        send_telegram(msg)
        last_alert_time = current_time


def main():
    while True:
        try:
            check_signal()
        except Exception as e:
            print(e)

        time.sleep(60)


if name == "main":
    main()
