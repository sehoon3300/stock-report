import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pykrx import stock
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

# ================== 설정 ==================
GMAIL_ID = os.getenv('GMAIL_ID')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')

# KRX 로그인
os.environ['KRX_ID'] = os.getenv('KRX_ID', '')
os.environ['KRX_PW'] = os.getenv('KRX_PW', '')

portfolio = {
    '360750': 'TIGER 미국S&P500',
    '448300': 'TIGER 미국나스닥100(H)',
    '402970': 'ACE 미국배당다우존스',
    '069500': 'KODEX 200',
    '411060': 'ACE KRX금현물',
    '305080': 'TIGER 미국채10년선물'
}
# =========================================

def send_gmail(subject, body):
    msg = MIMEMultipart()
    msg['From'] = GMAIL_ID
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_ID, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("✅ Gmail 전송 완료!")
    except Exception as e:
        print("❌ Gmail 전송 실패:", str(e))

def get_morning_report():
    today = datetime.today().strftime('%Y-%m-%d')
    yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y%m%d')
    
    html = f"""
    <h2>📅 {today} 아침 포트폴리오 브리핑</h2>
    <p><b>전일({yesterday}) 기준</b></p>
    <hr>
    <h3>📊 포트폴리오 현황</h3>
    <table border="1" cellpadding="8" style="border-collapse: collapse;">
        <tr><th>종목</th><th>종가</th><th>등락률</th></tr>
    """

    for ticker, name in portfolio.items():
        try:
            df = stock.get_market_ohlcv(yesterday, yesterday, ticker)
            if not df.empty:
                row = df.iloc[-1]
                close = int(row['종가'])
                change = row['등락률']
                html += f"<tr><td>{name}</td><td>{close:,}</td><td>{change:+.2f}%</td></tr>"
            else:
                html += f"<tr><td>{name}</td><td>데이터 없음</td><td>-</td></tr>"
        except Exception as e:
            html += f"<tr><td>{name}</td><td>오류</td><td>-</td></tr>"

    html += "</table>"

    html += "<p><small>⚠️ 참고용 자료입니다. 실제 투자 판단은 본인 책임입니다.</small></p>"

    send_gmail(f"[{today}] 아침 포트폴리오 브리핑", html)

if __name__ == "__main__":
    get_morning_report()
