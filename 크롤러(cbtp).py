import telegram
import urllib3
from bs4 import BeautifulSoup
from datetime import date
import ssl
import asyncio
import re
from urllib3 import PoolManager
from urllib3.exceptions import InsecureRequestWarning

'''
@ start date = 2024-03-07
@ made = seungjun
@ see = "chat Gpt"
'''

# Telegram 봇 설정
TELEGRAM_BOT_TOKEN = "7973551018:AAEQa6GZA0jMnnFcf-bacOjx2NlmBmMn-rY"
CHAT_ID = "5062268014"
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# SSL 경고 비활성화
urllib3.disable_warnings(InsecureRequestWarning)

# 보안 수준을 낮춘 SSLContext 생성
context = ssl.create_default_context()
context.set_ciphers('DEFAULT:@SECLEVEL=1')

# urllib3를 활용한 HTTP 요청 객체 생성
http = PoolManager(ssl_context=context)

# 크롤링할 사이트 목록
SITE_LIST = [
    {"name": "충북 테크노파크 공지 사항", "url": "https://www.cbtp.or.kr/index.php?control=bbs&board_id=news_notice&lm_uid=36"},
    {"name": "충북 테크노파크 사업 공고", "url": "https://www.cbtp.or.kr/index.php?control=bbs&board_id=saup_notice&lm_uid=387"},
    {"name": "충남 테크노파크 지원 사업", "url": "https://www.ctp.or.kr/community/notice.do"},
    {"name": "충북과학기술혁신원 공지 사항", "url": "http://www.cbist.or.kr/home/sub.do?mncd=1129"},
    {"name": "충북과학기술혁신원 사업 공고", "url": "http://www.cbist.or.kr/home/sub.do?mncd=1131"},
    {"name": "충북기업진흥원 공지사항", "url": "https://www.cba.ne.kr/home/sub.php?menukey=140"},
    {"name": "충북기업진흥원 사업공고", "url": "https://www.cba.ne.kr/home/sub.php?menukey=172"},
    {"name": "충남경제진흥원 공지사항", "url": "https://www.cepa.or.kr/notice/notice.do?pm=6&ms=32"},
    {"name": "충남경제진흥원 사업공고", "url": "https://www.cepa.or.kr/business/business.do?pm=4&ms=23"},
    {"name": "충청남도소상공인지원센터 공지사항", "url": "http://sbiz.cepa.or.kr/sosang/notice/notice.do?pm=10&ms=65"},
    {"name": "충청남도소상공인지원센터 사업공고", "url": "http://sbiz.cepa.or.kr/sosang/notice/notice.do?pm=10&ms=66"},
    {"name": "충청북도소상공인지원센터 공지사항", "url": "https://www.cbsb.kr/home/sub.php?menukey=288"},
    {"name": "충청북도소상공인지원센터 사업공고", "url": "https://www.cbsb.kr/home/sub.php?menukey=290"},
]

# 날짜 자동 감지 함수
def extract_date(text):
    date_pattern = r'\d{4}[-./]\d{2}[-./]\d{2}'
    match = re.search(date_pattern, text)
    return match.group(0) if match else None

# 공지사항 확인 비동기 함수
async def check_notices():
    today = date.today().strftime('%Y-%m-%d')
    print(f"📅 오늘 날짜: {today}")
    message = f"📢 **오늘의 공지사항 ({today})**\n\n"

    for site in SITE_LIST:
        try:
            response = http.request("GET", site["url"])
            soup = BeautifulSoup(response.data, "html.parser")

            notices = soup.find_all("tr")
            site_message = f"🔹 **{site['name']}**\n"
            found = False

            for notice in notices:
                date_td = next((td for td in notice.find_all("td") if extract_date(td.text)), None)
                title_td = notice.find("a")

                if date_td and title_td:
                    notice_date = extract_date(date_td.text.strip())
                    title = title_td.text.strip()
                    link = title_td.get("href", "")

                    if notice_date == today:
                        found = True
                        if link.startswith("/"):
                            link = site["url"].split("/index.php")[0] + link
                        site_message += f"  - [{title}]({link})\n"

            if not found:
                site_message += "  - 오늘 공지 없음\n"

            message += site_message + "\n"

        except Exception as e:
            print(f"🚨 [{site['name']}] 크롤링 오류 발생: {e}")
            message += f"🚨 [{site['name']}] 크롤링 오류 발생\n\n"

    # Telegram 메시지 전송
    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

# 메인 실행 함수
if __name__ == "__main__":
    asyncio.run(check_notices())
