from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote_plus
import time
import pandas as pd
import os



AMAZON_BASE = "https://www.amazon.in"

# SEARCH_QUERIES = {
#     "cpp_books": "c++ books"
# }

SEARCH_QUERIES = {
    "cpp_books": "c++ books",
    "c_books": "c book",
    "python_books": "python programming book",
    "machine_learning_books": "machine learning book",
    "linear_algebra_books": "linear algebra book",
    "selenium_books": "selenium python programming book",
    "tensorflow_books": "tensorflow book",
    "pytorch_books": "pytorch book",
    "data_science_books": "data science book",
    "artificial_intelligence_books": "artificial intelligence book",
    "deep_learning_books": "deep learning book"
}

def scrape_brand_products(key,search_url, driver):
    driver.get(search_url)

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.s-result-item[data-asin]")))
    time.sleep(2)

    # books = driver.find_elements(By.CSS_SELECTOR, "div.s-result-item[data-asin]")

    books = driver.find_elements(
    By.CSS_SELECTOR,
    'div.s-result-item[data-component-type="s-search-result"]'
    )

    books = [
        book for book in books
        if book.get_attribute("data-asin") and book.get_attribute("data-asin").strip() != ""
    ]

    print("Filtered result cards:", len(books))

    data = []

    for i, book in enumerate(books, start=1):
        try:
            asin = book.get_attribute("data-asin")

            # skip empty/non-product blocks
            if not asin or asin.strip() == "":
                print(f"Skipped {i}: empty asin")
                continue

            try:
                title = book.find_element(By.CSS_SELECTOR, "h2 span").text.strip()
            except:
                title = "N/A"

            # URL
            try:
                link = book.find_element(By.CSS_SELECTOR, "h2 a").get_attribute("href")
                if not link:
                    raise Exception("Empty href")
            except:
                try:
                    link = book.find_element(By.CSS_SELECTOR, "a.a-link-normal").get_attribute("href")
                except:
                    link = "N/A"

            # Author
            try:
                author = book.find_element(
                    By.CSS_SELECTOR,
                    "div.a-row.a-size-base.a-color-secondary"
                ).text.strip()
            except:
                try:
                    author = book.find_element(
                        By.CSS_SELECTOR,
                        ".a-color-secondary"
                    ).text.strip()
                except:
                    author = "N/A"

            # Rating
            try:
                rating = book.find_element(By.CSS_SELECTOR, ".a-icon-alt").get_attribute("innerHTML").strip()
            except:
                rating = "N/A"

            # Reviews
            try:
                reviews = book.find_element(
                    By.CSS_SELECTOR,
                    "a[href*='customerReviews'] span"
                ).text.strip()
            except:
                reviews = "N/A"

            data.append({
                "asin": asin,
                "title": title,
                "author": author,
                "rating": rating,
                "reviews": reviews,
                "url": link
            })

        except Exception:
            continue

    # print(data)
    print(f"Total products on this page: {len(data)}")
    df = pd.DataFrame(data)
    file_name = f"{key}.csv"

    file_path = os.path.join("U:\\assignment\\ai_powdered_book_insight\\scraped_data",file_name)
    df.to_csv(file_path, index=False)

def start_scraping():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()

    for key, query in SEARCH_QUERIES.items():
        encoded_query = quote_plus(query)
        search_url = f"{AMAZON_BASE}/s?k={encoded_query}"

        print(f"{key}: {search_url}")
        scrape_brand_products(key,search_url, driver)

    driver.quit()


if __name__ == "__main__":
    start_scraping()





# def print_total_products(driver, search_url):
#     driver.get(search_url)

#     wait = WebDriverWait(driver, 10)
#     wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.s-result-item[data-asin]")))
#     time.sleep(2)

#     books = driver.find_elements(By.CSS_SELECTOR, "div.s-result-item[data-asin]")

#     valid_books = []

#     for book in books:
#         asin = book.get_attribute("data-asin")
#         if asin and asin.strip() != "":
#             valid_books.append(book)

#     print(f"Total products on this page: {len(valid_books)}")