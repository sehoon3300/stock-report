import os
import smtplib
import requests
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from xml.etree import ElementTree as ET

import yfinance as yf
from pykrx import stock

GMAIL_ID = os.getenv("GMAIL_ID")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

portfolio = {
    "360750":"TIGER 미국S&P500",
    "448300":"TIGER 미국나스닥100(H)",
    "402970":"ACE 미국배당다우존스",
    "069500":"KODEX 200",
    "411060":"ACE KRX금현물",
    "305080":"TIGER 미국채10년선물"
}

MARKETS={
"S&P500":"^GSPC","NASDAQ":"^IXIC","DOW":"^DJI",
"VIX":"^VIX","US10Y":"^TNX","USD/KRW":"KRW=X"
}

def send_mail(subject, html):
    msg=MIMEMultipart()
    msg["From"]=GMAIL_ID
    msg["To"]=RECEIVER_EMAIL
    msg["Subject"]=subject
    msg.attach(MIMEText(html,"html"))
    s=smtplib.SMTP("smtp.gmail.com",587)
    s.starttls()
    s.login(GMAIL_ID,GMAIL_APP_PASSWORD)
    s.send_message(msg)
    s.quit()

def get_market():
    out={}
    for n,t in MARKETS.items():
        try:
            df=yf.download(t,period="5d",progress=False,auto_adjust=True)
            c=float(df.Close.iloc[-1]);p=float(df.Close.iloc[-2])
            out[n]={"close":c,"change":(c-p)/p*100}
        except:
            out[n]=None
    return out

def get_portfolio():
    d=(datetime.today()-timedelta(days=1)).strftime("%Y%m%d")
    result=[]
    for code,name in portfolio.items():
        try:
            row=stock.get_market_ohlcv(d,d,code).iloc[-1]
            result.append({"name":name,"close":int(row["종가"]),"change":float(row["등락률"])})
        except:
            result.append({"name":name,"close":None,"change":None})
    return result

def signal(etf,market):
    score=50
    why=[]
    sp=market.get("S&P500")
    vx=market.get("VIX")
    if sp:
        if sp["change"]>1:
            score+=20; why.append("미국 증시 강세")
        elif sp["change"]<-1:
            score-=20; why.append("미국 증시 약세")
    if vx:
        if vx["close"]<18:
            score+=15; why.append("낮은 VIX")
        elif vx["close"]>25:
            score-=15; why.append("높은 VIX")
    score=max(0,min(score,100))
    if score>=70:
        opinion="🟢 장기투자 환경 양호"
    elif score>=40:
        opinion="🟡 평소 적립 유지"
    else:
        opinion="🔴 변동성 주의"
    return score, opinion, ", ".join(why) if why else "특이사항 없음"

def get_news():
    urls=[
        "https://feeds.reuters.com/reuters/businessNews",
        "https://feeds.reuters.com/reuters/worldNews"
    ]
    titles=[]
    for u in urls:
        try:
            root=ET.fromstring(requests.get(u,timeout=8).text)
            for item in root.findall("./channel/item")[:3]:
                t=item.findtext("title")
                if t and t not in titles:
                    titles.append(t)
        except:
            pass
    return titles[:5] or ["뉴스를 가져오지 못했습니다."]

def build_html():
    m=get_market()
    p=get_portfolio()
    news=get_news()

    h=f"<h2>📅 {datetime.today():%Y-%m-%d} ISA Guardian v3</h2><hr>"
    h+="<h3>🇺🇸 미국 시장</h3><ul>"
    for k,v in m.items():
        if v:
            h+=f"<li><b>{k}</b> : {v['close']:.2f} ({v['change']:+.2f}%)</li>"
    h+="</ul>"

    h+="<h3>📊 포트폴리오 시그널</h3>"
    for item in p:
        h+=f"<p><b>{item['name']}</b><br>"
        if item["close"] is None:
            h+="데이터 없음</p>"
            continue
        sc,op,why=signal(item["name"],m)
        h+=f"종가 : {item['close']:,}<br>"
        h+=f"등락률 : {item['change']:+.2f}%<br>"
        h+=f"투자점수 : <b>{sc}/100</b><br>"
        h+=f"{op}<br>"
        h+=f"근거 : {why}</p><hr>"

    h+="<h3>📰 주요 뉴스</h3><ul>"
    for t in news:
        h+=f"<li>{t}</li>"
    h+="</ul><p><small>※ 참고용 리포트입니다.</small></p>"
    return h

if __name__=="__main__":
    send_mail(f"[{datetime.today():%Y-%m-%d}] ISA Guardian v3", build_html())