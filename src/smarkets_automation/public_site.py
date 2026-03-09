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


def load_event_page_html(event_url: str) -> str:
    return load_public_page_html(event_url)


def load_search_results_html(query: str) -> str:
    normalized_query = query.strip()
    if not normalized_query:
        raise ValueError("query must not be empty")

    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(BASE_URL, wait_until="domcontentloaded")
            page.get_by_role("button").filter(has=page.locator("input")).click()
            search_input = page.locator("input.Search_searchInput__cye5E").first
            search_input.fill(normalized_query)
            page.wait_for_selector('[role="dialog"] a[href]')
            dialog = page.locator('[role="dialog"]').first
            return dialog.inner_html()
        finally:
            browser.close()
