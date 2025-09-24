# from fastapi import FastAPI
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from bs4 import BeautifulSoup
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# import sys


# app = FastAPI()

# @app.get("/")
# def hello():
#     return {"message": "Hello, World!"}

# @app.get("/scrape")
# def scrape_who_news():
#     try:
#         chrome_options = Options()
        
#         if sys.platform == "linux":
#           chrome_options.binary_location = "/usr/bin/chromium"  # for Render/Linux
#         chrome_options.add_argument("--headless")
#         chrome_options.add_argument("--disable-gpu")
#         chrome_options.add_argument("--no-sandbox")  # needed on Linux servers like Render
#         driver = webdriver.Chrome(
#             options=chrome_options
#         )
#         driver.get("https://www.who.int/news")

#         # Wait until the news content loads
#         wait = WebDriverWait(driver, 10)
#         wait.until(EC.presence_of_element_located((By.CLASS_NAME, "k-listview-content")))

#         # Wait for page to load (you may need WebDriverWait for dynamic content)
#         html = driver.page_source
#         soup = BeautifulSoup(html, "html.parser")
        
#         # now you can safely find the divs
#         hub = soup.find("div", class_="hubfiltering")
#         list_view_content = hub.find("div", class_="k-listview-content")
#         news_divs = list_view_content.find_all("div", class_="list-view--item vertical-list-item")
        
#         news = []
#         for div in news_divs:
#             a_tag = div.find("a")
#             link =  a_tag.get("href") if a_tag and a_tag.get("href") else None

#             image_div = div.find("div", attrs={"data-image": True})
#             thumbnail = image_div["data-image"] if image_div else None
#             if thumbnail and thumbnail.startswith("/"):
#                 thumbnail = thumbnail

#             date_tag = div.find("span", class_="timestamp") or div.find("time")
#             date = date_tag.get_text(strip=True) if date_tag else None

#             heading_tag = div.find("p")
#             heading = heading_tag.get_text(strip=True) if heading_tag else None

#             news.append({
#                 "heading": heading,
#                 "link": link,
#                 "thumbnail": thumbnail,
#                 "date": date,
#             })
        
#         driver.quit()
#         return {"count": len(news), "news": news}

#     except Exception as e:
#         return {"error": str(e)}
#     finally:
#         if driver:
#             driver.quit()




from fastapi import FastAPI
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio

app = FastAPI()

@app.get("/")
async def hello():
    return {"message": "Hello, World!"}

@app.get("/scrape")
async def scrape_who_news():
    news = []
    # Use async with for automatic browser management
    async with async_playwright() as p:
        try:
            # Launch the browser with necessary arguments for server environments
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            page = await browser.new_page()
            await page.goto("https://www.who.int/news")

            # Wait until the news content loads
            await page.wait_for_selector(".k-listview-content", timeout=10000)

            # Get the page content and parse with BeautifulSoup
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")

            # Find the news divs
            hub = soup.find("div", class_="hubfiltering")
            list_view_content = hub.find("div", class_="k-listview-content")
            if list_view_content:
                news_divs = list_view_content.find_all("div", class_="list-view--item vertical-list-item")
                
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

            return {"count": len(news), "news": news}

        except Exception as e:
            # Return a clear error message
            return {"error": str(e)}
