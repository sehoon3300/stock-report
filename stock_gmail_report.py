import os, smtplib, requests
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from xml.etree import ElementTree as ET
import yfinance as yf
from pykrx import stock

GMAIL_ID=os.getenv("GMAIL_ID")
GMAIL_APP_PASSWORD=os.getenv("GMAIL_APP_PASSWORD")
RECEIVER_EMAIL=os.getenv("RECEIVER_EMAIL")

portfolio={
"360750":"TIGER 미국S&P500",
"448300":"TIGER 미국나스닥100(H)",
"402970":"ACE 미국배당다우존스",
"069500":"KODEX 200",
"411060":"ACE KRX금현물",
"305080":"TIGER 미국채10년선물"
}
markets={"S&P500":"^GSPC","NASDAQ":"^IXIC","DOW":"^DJI","VIX":"^VIX","US10Y":"^TNX","USD/KRW":"KRW=X"}

def send(subject,html):
    m=MIMEMultipart()
    m["From"]=GMAIL_ID;m["To"]=RECEIVER_EMAIL;m["Subject"]=subject
    m.attach(MIMEText(html,"html"))
    s=smtplib.SMTP("smtp.gmail.com",587)
    s.starttls();s.login(GMAIL_ID,GMAIL_APP_PASSWORD)
    s.send_message(m);s.quit()

def market():
    r={}
    for n,t in markets.items():
        try:
            df=yf.download(t,period="5d",progress=False,auto_adjust=True)
            c=float(df.Close.iloc[-1]);p=float(df.Close.iloc[-2])
            r[n]=(c,(c-p)/p*100)
        except:r[n]=None
    return r

def kr():
    d=(datetime.today()-timedelta(days=1)).strftime("%Y%m%d")
    out=[]
    for c,n in portfolio.items():
        try:
            row=stock.get_market_ohlcv(d,d,c).iloc[-1]
            out.append((n,int(row["종가"]),float(row["등락률"])))
        except:
            out.append((n,None,None))
    return out

def news():
    try:
        xml=requests.get("https://feeds.reuters.com/reuters/businessNews",timeout=10).text
        root=ET.fromstring(xml)
        return [i.findtext("title") for i in root.findall("./channel/item")[:5]]
    except:
        return ["뉴스를 가져오지 못했습니다."]

def html():
    m=market();p=kr();n=news()
    h=f"<h2>{datetime.today():%Y-%m-%d} ISA Morning Brief</h2>"
    h+="<h3>미국시장</h3><ul>"
    for k,v in m.items():
        if v:h+=f"<li>{k}: {v[0]:.2f} ({v[1]:+.2f}%)</li>"
    h+="</ul><h3>포트폴리오</h3><ul>"
    for name,close,ch in p:
        h+=f"<li>{name}: {close if close else '-'} / {ch:+.2f}%</li>" if close else f"<li>{name}: -</li>"
    h+="</ul><h3>주요 뉴스</h3><ul>"
    for t in n:h+=f"<li>{t}</li>"
    h+="</ul>"
    return h

if __name__=="__main__":
    send(f"[{datetime.today():%Y-%m-%d}] ISA Morning Brief",html())