import requests
from bs4 import BeautifulSoup
from collections import Counter
import datetime
from openai import OpenAI  # 수정: 클라이언트 라이브러리 방식
import os

# ====== 환경변수 ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 수정: OpenAI 클라이언트 초기화
client = OpenAI(api_key=OPENAI_API_KEY)

SECTIONS = {
    "정치": "100",
    "경제": "101",
    "사회": "102",
    "생활·문화": "103",
    "세계": "104",
    "스포츠": "105"
}

def get_articles(section_code):
    url = f"https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1={section_code}"
    # 헤더 추가 (네이버 크롤링 시 차단 방지)
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    articles = []
    for a in soup.select("ul.type06_headline li dl dt a")[:10]:
        title = a.text.strip()
        if title:
            articles.append(title)
    return articles

def summarize(text):
    prompt = f"다음 뉴스 제목 키워드들을 종합해 오늘의 주요 흐름을 2~3줄로 요약해줘:\n{text}"
    # 수정: 최신 API 호출 방식
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

def main():
    today = datetime.date.today().strftime("%Y.%m.%d")
    result = [f"[{today} 아침 뉴스 브리핑]\n"]

    for section, code in SECTIONS.items():
        titles = get_articles(code)
        if not titles:
            continue
            
        keywords = Counter(" ".join(titles).split()).most_common(5)
        summary = summarize(" / ".join([k[0] for k in keywords]))

        result.append(f"■ {section}\n{summary}\n")

    if len(result) > 1:
        send_telegram("\n".join(result))

if __name__ == "__main__":
    main()
