from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
""""
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    def log_route(response):
        if response.request.resource_type == "xhr":
            print("XHR:", response.url)
            # print response body for JSON
            try:
                print(response.json())
            except:
                pass
    page.on("response", log_route)
    page.goto("https://mangafire.to/filter", wait_until="networkidle")
    browser.close()
    
    """

def get_vrf(keyword):
    url = f"https://mangafire.to/filter?keyword={keyword.replace(' ', '+')}"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        html = page.content()
        browser.close()
    soup = BeautifulSoup(html, "lxml")
    results = [
        {
            "title": div.select_one(".info a").text.strip(),
            "url": div.select_one(".poster")["href"],
            "poster": div.select_one("img")["src"]
        }
        for div in soup.select("div.unit")
    ]
    return results

print(get_vrf("one piece"))
