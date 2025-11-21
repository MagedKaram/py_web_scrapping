from fastapi import FastAPI
from scraper import make_driver, extract_compound_links, scrape_compound

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Aqarmap Scraper API is running"}


@app.get("/scrape")
def scrape(page: int = 2):
    page_url = f"https://aqarmap.com.eg/en/compounds/?page={page}"

    driver = make_driver()
    links = extract_compound_links(driver, page_url)

    all_compounds = []
    all_units = []

    for link in links:
        comp, units = scrape_compound(driver, link)
        all_compounds.append(comp)
        all_units.extend(units)

    driver.quit()

    return {
        "count": len(all_compounds),
        "compounds": all_compounds,
        "units": all_units
    }
