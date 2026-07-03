import os
print("DEBUG: 스크립트 시작")

GMAIL_ID = os.getenv('GMAIL_ID')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')
os.environ['KRX_ID'] = os.getenv('KRX_ID', '')
os.environ['KRX_PW'] = os.getenv('KRX_PW', '')

print("DEBUG: GMAIL_ID 설정됨:", bool(GMAIL_ID))
print("DEBUG: KRX_ID 설정됨:", bool(os.getenv('KRX_ID')))

from pykrx import stock
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import warnings
warnings.filterwarnings('ignore')

# (나머지 send_gmail and get_morning_report 함수는 이전 코드와 동일)

if __name__ == "__main__":
    get_morning_report()
