import os
import smtplib
import warnings
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import yfinance as yf
from pykrx import stock

warnings.filterwarnings("ignore")

GMAIL_ID = os.getenv("GMAIL_ID")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

portfolio = {
    "360750": "TIGER 미국S&P500",
    "448300": "TIGER 미국나스닥100(H)",
    "402970": "ACE 미국배당다우존스",
    "069500": "KODEX 200",
    "411060": "ACE KRX금현물",
    "305080": "TIGER 미국채10년선물"
}

MARKETS = {
    "S&P500":"^GSPC",
    "NASDAQ":"^IXIC",
    "DOW":"^DJI",
    "VIX":"^VIX",
    "US10Y":"^TNX",
    "USD/KRW":"KRW=X"
}

def send_mail(subject, html):
    msg = MIMEMultipart()
    msg["From"]=GMAIL_ID
    msg["To"]=RECEIVER_EMAIL
    msg["Subject"]=subject
    msg.attach(MIMEText(html,"html"))
    s=smtplib.SMTP("smtp.gmail.com",587)
    s.starttls()
    s.login(GMAIL_ID,GMAIL_APP_PASSWORD)
    s.send_message(msg)
    s.quit()

def us_market():
    out={}
    for n,t in MARKETS.items():
        try:
            df=yf.download(t,period="5d",progress=False,auto_adjust=True)
            c=float(df["Close"].iloc[-1])
            p=float(df["Close"].iloc[-2])
            out[n]=(c,(c-p)/p*100)
        except:
            out[n]=None
    return out

def kr_portfolio():
    day=(datetime.today()-timedelta(days=1)).strftime("%Y%m%d")
    rows=[]
    for code,name in portfolio.items():
        try:
            df=stock.get_market_ohlcv(day,day,code)
            r=df.iloc[-1]
            rows.append((name,int(r["종가"]),float(r["등락률"])))
        except:
            rows.append((name,None,None))
    return rows

def comment(m):
    if m.get("S&P500") and m["S&P500"][1]>1:
        return "🟢 미국 증시가 강세입니다."
    if m.get("S&P500") and m["S&P500"][1]<-1:
        return "🟡 미국 증시가 조정 중입니다."
    return "⚪ 미국 시장은 보합권입니다."

def build():
    m=us_market()
    p=kr_portfolio()
    today=datetime.today().strftime("%Y-%m-%d")
    h=f"<h2>📅 {today} ISA Morning Brief</h2><hr>"
    h+="<h3>🇺🇸 미국시장</h3><table border=1 cellpadding=6><tr><th>지표</th><th>현재</th><th>등락률</th></tr>"
    for k,v in m.items():
        if v is None:
            h+=f"<tr><td>{k}</td><td>-</td><td>-</td></tr>"
        else:
            color="red" if v[1]>=0 else "blue"
            h+=f"<tr><td>{k}</td><td>{v[0]:.2f}</td><td style='color:{color}'>{v[1]:+.2f}%</td></tr>"
    h+="</table><br>"
    h+="<h3>📊 내 포트폴리오</h3><table border=1 cellpadding=6><tr><th>종목</th><th>종가</th><th>등락률</th></tr>"
    for n,c,ch in p:
        if c is None:
            h+=f"<tr><td>{n}</td><td>-</td><td>-</td></tr>"
        else:
            color="red" if ch>=0 else "blue"
            h+=f"<tr><td>{n}</td><td>{c:,}</td><td style='color:{color}'>{ch:+.2f}%</td></tr>"
    h+="</table><br>"
    h+=f"<h3>💬 오늘의 브리핑</h3><p>{comment(m)}</p>"
    h+="<p><small>투자 판단은 본인 책임입니다.</small></p>"
    return h

if __name__=="__main__":
    html=build()
    send_mail(f"[{datetime.today().strftime('%Y-%m-%d')}] ISA Morning Brief",html)