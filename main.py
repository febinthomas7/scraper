from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import sys
import traceback

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello, World!"}

@app.get("/scrape")
def scrape_who_news():
    driver = None
    try:
        chrome_options = Options()
        
        if sys.platform == "linux":
          chrome_options.binary_location = "/usr/bin/chromium"  # for Render/Linux
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")  # needed on Linux servers like Render
        driver = webdriver.Chrome(
            options=chrome_options
        )
        driver.get("https://www.who.int/news")

        # Wait until the news content loads
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "k-listview-content")))

        # Wait for page to load (you may need WebDriverWait for dynamic content)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        
        # now you can safely find the divs
        hub = soup.find("div", class_="hubfiltering")
        list_view_content = hub.find("div", class_="k-listview-content")
        news_divs = list_view_content.find_all("div", class_="list-view--item vertical-list-item")
        
        news = []
        for div in news_divs:
            a_tag = div.find("a")
            link =  a_tag.get("href") if a_tag and a_tag.get("href") else None

            image_div = div.find("div", attrs={"data-image": True})
            thumbnail = image_div["data-image"] if image_div else None
            if thumbnail and thumbnail.startswith("/"):
                thumbnail = thumbnail

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
        
        return {"count": len(news), "news": news}

    except Exception as e:
            return {"error": str(e), "trace": traceback.format_exc()}
       
    finally:
        if driver is not None:
            driver.quit()