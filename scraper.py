from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time

BASE_URL = "https://aqarmap.com.eg"


def make_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    # Railway default chromedriver path
    service = Service("/usr/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=options)
    return driver



def scroll_page(driver, times=4, delay=1.5):
    for _ in range(times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay)


def extract_compound_links(driver, url):
    print(f"[+] Collecting listings from: {url}")
    driver.get(url)
    time.sleep(4)
    scroll_page(driver, 5)

    cards = driver.find_elements(By.CSS_SELECTOR, ".search-listing-card")
    links = []

    for c in cards:
        try:
            l = c.find_element(By.CSS_SELECTOR, ".search-listing-card__container__link").get_attribute("href")
            links.append(l)
        except:
            pass

    return links


def scrape_compound(driver, url):
    print(f"[+] Scraping compound: {url}")
    driver.get(url)
    time.sleep(3)

    compound = {
        "url": url,
        "type": None,
        "date": None,
        "title": None,
        "location": None,
        "starting_price": None,
        "description": None,
        "developer_name": None,
        "developer_joined": None,
        "developer_stats_raw": None
    }

    # HEADER
    try:
        header = driver.find_element(By.CSS_SELECTOR, ".listing-details-page__project-title-section")

        # type + date
        try:
            sub = header.find_elements(By.CSS_SELECTOR, ".listing-details-page__title-section__sub span")
            if len(sub) >= 1:
                compound["type"] = sub[0].text.strip()
            if len(sub) >= 2:
                compound["date"] = sub[1].text.strip()
        except:
            pass

        # title
        try:
            compound["title"] = header.find_element(
                By.CSS_SELECTOR,
                ".listing-details-page__project-title-section__title"
            ).text.strip()
        except:
            pass

        # location
        try:
            compound["location"] = header.find_element(
                By.CSS_SELECTOR,
                ".listing-details-page__project-title-section__address"
            ).text.replace("\n", " ").strip()
        except:
            pass

        # starting price
        try:
            compound["starting_price"] = header.find_element(
                By.CSS_SELECTOR,
                ".listing-details-page__project-title-section__starting-price"
            ).text.strip()
        except:
            pass

    except:
        pass

    # DESCRIPTION
    try:
        try:
            more = driver.find_element(By.ID, "seeMoreParagraph")
            driver.execute_script("arguments[0].click();", more)
            time.sleep(1)
        except:
            pass

        desc_box = driver.find_element(By.ID, "listingDescriptionText")
        compound["description"] = desc_box.get_attribute("innerText").strip()

    except:
        compound["description"] = None

    # DEVELOPER
    try:
        info = driver.find_element(By.CSS_SELECTOR, ".listing-info-container")

        try:
            compound["developer_name"] = info.find_element(
                By.CSS_SELECTOR,
                ".user-card__name-text"
            ).text.strip()
        except:
            pass

        try:
            compound["developer_joined"] = info.find_element(
                By.CSS_SELECTOR,
                ".user-card__joined-text"
            ).text.strip()
        except:
            pass

        try:
            stats = info.find_elements(By.CSS_SELECTOR, ".projects-details")
            all_stats = []
            for st in stats:
                count = st.find_element(By.CSS_SELECTOR, ".count").text.strip()
                txt = st.find_element(By.CSS_SELECTOR, ".sub-text").text.strip()
                all_stats.append(f"{txt}:{count}")
            compound["developer_stats_raw"] = " | ".join(all_stats)
        except:
            pass

    except:
        pass

    # UNITS
    units = []
    scroll_page(driver, 3)

    unit_containers = driver.find_elements(By.CSS_SELECTOR, ".units-container")

    for cont in unit_containers:

        try:
            category = cont.find_element(By.CSS_SELECTOR, ".units-container__title").text.strip()
        except:
            category = None

        try:
            anc = cont.find_element(By.XPATH,
                "ancestor::div[@id='pills-primary' or @id='pills-resale' or @id='pills-rent']"
            )
            sec_id = anc.get_attribute("id")
            if sec_id == "pills-primary":
                mode = "primary_sale"
            elif sec_id == "pills-resale":
                mode = "resale_sale"
            elif sec_id == "pills-rent":
                mode = "rent"
            else:
                mode = None
        except:
            mode = None

        unit_links = cont.find_elements(By.CSS_SELECTOR, ".units-list__item.unit")
        for u in unit_links:
            try:
                area = u.find_element(By.CSS_SELECTOR, ".unit__area").text.strip()
            except:
                area = None

            try:
                price = u.find_element(By.CSS_SELECTOR, ".unit__price").text.strip()
            except:
                price = None

            try:
                link = u.get_attribute("href")
                if link and link.startswith("/"):
                    link = BASE_URL + link
            except:
                link = None

            units.append({
                "compound_url": url,
                "compound_title": compound["title"],
                "mode": mode,
                "category": category,
                "area": area,
                "price": price,
                "url": link
            })

    return compound, units
