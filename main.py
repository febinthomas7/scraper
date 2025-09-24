from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


app = FastAPI()

@app.get("/scrape")
def scrape_who_news():
    try:
     # Selenium options
        chrome_options = Options()
        chrome_options.binary_location = "/usr/bin/chromium"  # for Render
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
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
        
        articles = []
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

            articles.append({
                "heading": heading,
                "link": link,
                "thumbnail": thumbnail,
                "date": date,
            })
        
        return {"count": len(articles), "articles": articles}

    except Exception as e:
        return {"error": str(e)}
    finally:
        if driver:
            driver.quit()