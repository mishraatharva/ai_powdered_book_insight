import os
import time
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


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

def scrape_book_description(driver, url):
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    time.sleep(2)

    try:
        wait.until(EC.presence_of_element_located((By.ID, "bookDescription_feature_div")))
        desc_box = driver.find_element(By.ID, "bookDescription_feature_div")

        try:
            read_more = desc_box.find_element(By.CSS_SELECTOR, "a[data-action='a-expander-toggle']")
            if "read more" in read_more.text.lower():
                driver.execute_script("arguments[0].click();", read_more)
                time.sleep(1)
        except:
            pass

        try:
            desc_elem = desc_box.find_element(By.CSS_SELECTOR, ".a-expander-content")
            description = driver.execute_script("return arguments[0].innerText;", desc_elem).strip()
        except:
            description = driver.execute_script("return arguments[0].innerText;", desc_box).strip()

        return description if description else "N/A"

    except:
        return "N/A"


def scrap_description():
    for key, _ in SEARCH_QUERIES.items():
        file_path = os.path.join("U:\\assignment\\ai_powdered_book_insight\\scraped_data",f"{key}.csv")
        df = pd.read_csv(file_path)
        links = list(df["url"])
        descriptions = []
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.maximize_window()
        
        for link in links:
            description = scrape_book_description(driver, link)
            descriptions.append(description)

        df["description"] = descriptions
        file_path = os.path.join("U:\\assignment\\ai_powdered_book_insight\\with_description",f"{key}.csv")
        df.to_csv(file_path, index=False)
    
        driver.quit()

if __name__ == "__main__":
    scrap_description()