from fastapi import FastAPI
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import traceback

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello, World!"}

@app.get("/title")
def get_title():
    url = "https://www.who.int/news"
    return {"title": get_page_title(url)}

def get_page_title(url: str) -> str:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded")
            title = page.title()
            browser.close()
            return title
    except Exception as e:
        return f"Error: {e}"

@app.get("/scrape")
def scrape_who_news():
    news = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            page = browser.new_page()
            page.goto("https://www.who.int/news")

            # Wait until at least one news card is loaded
            page.wait_for_selector(".list-view--item.vertical-list-item", timeout=15000)

            html = page.content()
            soup = BeautifulSoup(html, "html.parser")

            hub = soup.find("div", class_="hubfiltering")
            list_view_content = hub.find("div", class_="k-listview-content") if hub else None
            news_divs = list_view_content.find_all("div", class_="list-view--item vertical-list-item") if list_view_content else []

            for div in news_divs:
                a_tag = div.find("a")
                link = a_tag.get("href") if a_tag and a_tag.get("href") else None

                image_div = div.find("div", attrs={"data-image": True})
                thumbnail = image_div["data-image"] if image_div else None
                if thumbnail and thumbnail.startswith("/"):
                    thumbnail = "https://www.who.int" + thumbnail

                date_tag = div.find("span", class_="timestamp") or div.find("time")
                date = date_tag.get_text(strip=True) if date_tag else None

                heading_tag = div.find("p")
                heading = heading_tag.get_text(strip=True) if heading_tag else None

                news.append({
                    "heading": heading,
                    "link": link,
                    "thumbnail": thumbnail,
                    "date": date,
                })

            browser.close()
        return {"count": len(news), "news": news}

    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}
