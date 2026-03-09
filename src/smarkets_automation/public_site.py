BASE_URL = "https://smarkets.com"


def absolute_smarkets_url(path: str) -> str:
    if path.startswith(("http://", "https://")):
        return path
    return f"{BASE_URL}{path}"


def load_public_page_html(url: str) -> str:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(absolute_smarkets_url(url), wait_until="domcontentloaded")
            return page.content()
        finally:
            browser.close()
