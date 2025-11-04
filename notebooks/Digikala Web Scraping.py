import time
import csv
import os

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def to_persian_digit(en_digit_str):
    """Converts English digits to Persian digits for XPath selection."""
    persian_digits = {'0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴', '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'}
    return "".join(persian_digits[char] for char in str(en_digit_str))


def scrape_comments_for_product(driver, product_url, max_comments_per_product=500):
    """Scrapes comments for a single product URL."""
    wait = WebDriverWait(driver, 10)
    comments_data = []
    driver.get(product_url)
    print(f"Product page opened: {product_url}")
    print("Scrolling to the comments section...")

    try:
        # Wait for the comment section to be present and scroll to it
        comment_section = wait.until(EC.presence_of_element_located((By.ID, "commentSection")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", comment_section)
        time.sleep(5)
    except TimeoutException:
        print(f"Comment section not found on page {product_url}. Skipping to the next product.")
        return []

    print("--- Starting Phase 1: Loading initial comments ---")
    while True:
        try:
            # Find and click the "Load More" button until it's no longer available
            load_more_button = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[data-cro-id='pdp-comments-more']")
            ))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", load_more_button)
            time.sleep(1)
            load_more_button.click()
            print("Clicked on the 'More Comments' button...")
            time.sleep(2)
        except TimeoutException:
            print("The 'More Comments' button no longer exists. End of Phase 1.")
            break
        except Exception as e:
            print(f"An error occurred while clicking 'More Comments': {e}")
            break

    print("\n--- Starting Phase 2: Paginating through comments ---")
    current_page = 1
    while len(comments_data) < max_comments_per_product:
        print(f"Processing content of page {current_page}...")

        try:
            # Ensure the comment section is loaded on the new page
            wait.until(EC.presence_of_element_located((By.ID, "commentSection")))
            time.sleep(1)
        except TimeoutException:
            print("Comment section did not load on the new page.")
            break

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        comment_articles = soup.select("article.py-3")

        if not comment_articles and current_page > 1:
            print("No comments found to extract on this page.")
            break

        new_comments_added = 0
        for article in comment_articles:
            comment_text_tag = article.find('p', class_='text-body-1')
            comment_text = comment_text_tag.text.strip() if comment_text_tag else ""

            user_info_div = article.find('div', class_='flex items-center')
            date_tag = user_info_div.find_all('p')[-1] if user_info_div else None
            date = date_tag.text.strip() if date_tag else ""

            # Extract rating based on the width of the rating bar
            rating_div = article.find('div', {'style': lambda value: value and 'width' in value})
            rating = "N/A"
            if rating_div and 'width' in rating_div['style']:
                width_str = rating_div['style'].split('width:')[1].replace('%', '').replace(';', '').strip()
                try:
                    # The rating is out of 5, and the width is a percentage (e.g., 100% = 5 stars)
                    rating_value = float(width_str) / 20
                    rating = f"{rating_value:.1f}"
                except ValueError:
                    rating = "Parsing Error"

            comment_obj = {"rating": rating, "date": date, "comment": comment_text, "product_url": product_url}

            # Add comment only if it's not already in the list
            if comment_obj not in comments_data:
                comments_data.append(comment_obj)
                new_comments_added += 1

        print(f"{new_comments_added} new comments extracted from page {current_page}. Total for this product: {len(comments_data)}")

        if len(comments_data) >= max_comments_per_product:
            print(f"Reached the desired number of comments for product {product_url}.")
            break

        try:
            # Navigate to the next page
            next_page_number = current_page + 1
            persian_next_page = to_persian_digit(next_page_number)
            next_page_button_xpath = f"//span[contains(@class, 'styles_PageNumberButton__yPGpm') and span/text()='{persian_next_page}']"
            next_page_button = wait.until(EC.element_to_be_clickable((By.XPATH, next_page_button_xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_page_button)
            time.sleep(1)
            next_page_button.click()
            print(f"Successfully navigated to page {next_page_number}.")
            current_page = next_page_number
            time.sleep(3)
        except TimeoutException:
            print(f"Page button for page {next_page_number} not found. Reached the end of pages for this product.")
            break
        except Exception as e:
            print(f"An error occurred while navigating to the next page: {e}")
            break

    return comments_data


def scrape_multiple_products(product_urls, total_max_comments=2000, max_comments_per_product=400):
    """Initializes the web driver and scrapes comments from a list of product URLs."""
    driver = webdriver.Chrome()
    driver.maximize_window()
    all_comments = []

    for url in product_urls:
        print(f"\n{'='*20} Starting process for product: {url} {'='*20}")
        try:
            product_comments = scrape_comments_for_product(driver, url, max_comments_per_product)
            all_comments.extend(product_comments)
            print(f"{'-'*20} Finished process for product: {url} | Total comments collected: {len(all_comments)} {'-'*20}\n")

            if len(all_comments) >= total_max_comments:
                print(f"Exceeded the overall limit of {total_max_comments} comments. Terminating operation.")
                break

        except Exception as e:
            print(f"!! An unexpected error occurred while processing product {url}: {e}")
            print("!! Continuing with the next product...")
            continue

    driver.quit()

    if all_comments:
        print(f"\nProcess completed. A total of {len(all_comments)} comments were extracted and saved.")

        # Define the output directory and create it if it doesn't exist
        output_dir = os.path.join('..', 'data')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'digikala_comments.csv')

        # Write the collected data to a CSV file
        fieldnames = ['rating', 'date', 'comment', 'product_url']
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_comments)
        print(f"Data successfully saved to {output_path}.")
    else:
        print("No comments to save! Sorry :(")


# --- Execution ---
product_pages_list = [
    # You can customize the list of Digikala product URLs here
    "https://www.digikala.com/product/dkp-1716732/%D9%85%D8%AD%D8%A7%D9%81%D8%B8-%D9%84%D9%86%D8%B2-%D8%AF%D9%88%D8%B1%D8%A8%DB%8C%D9%86-%DA%A9%D9%88%D8%A7%D9%84%D8%A7-%D9%85%D8%AF%D9%84-pwt-001-%D9%85%D9%86%D8%A7%D8%B3%D8%A8-%D8%A8%D8%B1%D8%A7%DB%8C-%DA%AF%D9%88%D8%B4%DB%8C-%D9%85%D9%88%D8%A8%D8%A7%DB%8C%D9%84-%D8%B3%D8%A7%D9%85%D8%B3%D9%88%D9%86%DA%AF-galaxy-a30/",
    "https://www.digikala.com/product/dkp-18578421/%D9%BE%D8%A7%D9%88%D8%B1%D8%A8%D8%A7%D9%86%DA%A9-%D8%A7%DA%A9%D8%B3%D8%AA%D8%B1%D9%88%D9%85-%D9%85%D8%AF%D9%84-apb20k22w-b-%D8%B8%D8%B1%D9%81%DB%8C%D8%AA-20000-%D9%85%DB%8C%D9%84%DB%8C-%D8%A2%D9%85%D9%BE%D8%B1-%D8%B3%D8%A7%D8%B9%D8%AA/",
    "https://www.digikala.com/product/dkp-11197647/%D9%81%D9%84%D8%B4-%D9%85%D9%85%D9%88%D8%B1%DB%8C-%DA%A9%D9%88%D8%A6%DB%8C%D9%86-%D8%AA%DA%A9-%D9%85%D8%AF%D9%84-marvel-c-plus-%D8%B8%D8%B1%D9%81%DB%8C%D8%AA-64-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA-%D8%A8%D9%87-%D9%87%D9%85%D8%B1%D8%A7%D9%87-%D9%85%D8%A8%D8%AF%D9%84-usb-type-c/",
    "https://www.digikala.com/product/dkp-14802514/%D8%B3%D8%A7%D8%B9%D8%AA-%D9%87%D9%88%D8%B4%D9%85%D9%86%D8%AF-%D9%88%D8%B1%D9%86%D8%A7-%D9%85%D8%AF%D9%84-t45-pro-max-with-7-bands-%D9%85%D9%86%D8%A7%D8%B3%D8%A8-%D8%A8%D8%B1%D8%A7%DB%8C-%D9%88%D8%B1%D8%B2%D8%B4-%D8%B1%D9%88%D8%B2%D9%85%D8%B1%D9%87-%D8%B1%D8%B3%D9%85%DB%8C-%D8%AF%D8%A7%D8%B1%D8%A7%DB%8C-%D9%82%D8%A7%D8%A8%D9%84%DB%8C%D8%AA%D9%87%D8%A7%DB%8C-%D8%B5%D9%81%D8%AD%D9%87-%D9%86%D9%85%D8%A7%DB%8C%D8%B4-%D8%B1%D9%86%DA%AF%DB%8C-%D9%88-%D9%84%D9%85%D8%B3%DB%8C-%DA%A9%D9%86%D8%AA%D8%B1%D9%84-%D9%85%D9%88%D8%B3%DB%8C%D9%82%DB%8C/",
    "https://www.digikala.com/product/dkp-4367663/%D8%B4%D8%A7%D8%B1%DA%98%D8%B1-%D9%87%D9%85%D8%B1%D8%A7%D9%87-%D9%85%D8%AF%D9%84-a5-%D8%B8%D8%B1%D9%81%DB%8C%D8%AA-3000-%D9%85%DB%8C%D9%84%DB%8C-%D8%A2%D9%85%D9%BE%D8%B1-%D8%B3%D8%A7%D8%B9%D8%AA/",
    "https://www.digikala.com/product/dkp-2161744/%D9%87%D8%AF%D9%81%D9%88%D9%86-%D8%A8%DB%8C-%D8%B3%DB%8C%D9%85-%D8%A2%D9%88%DB%8C-%D9%85%D8%AF%D9%84-a780bl/",
    "https://www.digikala.com/product/dkp-1642737/%DA%A9%D8%A7%D8%A8%D9%84-%D8%B4%D8%A7%D8%B1%DA%98-usb-%D8%A8%D9%87-usb-c-%D9%85%D8%AF%D9%84-ep-dn930cwe-%D8%B7%D9%88%D9%84-12-%D9%85%D8%AA%D8%B1/",
    "https://www.digikala.com/product/dkp-18578421/%D9%BE%D8%A7%D9%88%D8%B1%D8%A8%D8%A7%D9%86%DA%A9-%D8%A7%DA%A9%D8%B3%D8%AA%D8%B1%D9%88%D9%85-%D9%85%D8%AF%D9%84-apb20k22w-b-%D8%B8%D8%B1%D9%81%DB%8C%D8%AA-20000-%D9%85%DB%8C%D9%84%DB%8C-%D8%A2%D9%85%D9%BE%D8%B1-%D8%B3%D8%A7%D8%B9%D8%AA/",
    "https://www.digikala.com/product/dkp-9952634/%D9%85%D8%A8%D8%AF%D9%84-%D8%A8%D8%B1%D9%82-%D9%87%D8%A7%D8%AF%D8%B1%D9%88%D9%86-%D9%85%D8%AF%D9%84-p103/",
    "https://www.digikala.com/product/dkp-5541008/%D9%87%D8%AF%D9%81%D9%88%D9%86-%D8%A8%D9%84%D9%88%D8%AA%D9%88%D8%AB%DB%8C-%D9%85%D8%AF%D9%84-p49v53/",
    "https://www.digikala.com/product/dkp-6891158/%DA%A9%D8%A7%D8%A8%D9%84-%D8%AA%D8%A8%D8%AF%DB%8C%D9%84-type-c-%D8%A8%D9%87-type-c-%D9%85%D8%AF%D9%84-ep-dn970-%D8%B7%D9%88%D9%84-1-%D9%85%D8%AA%D8%B1/",
    "https://www.digikala.com/product/dkp-18802491/%D8%B4%D8%A7%D8%B1%DA%98%D8%B1-%D9%81%D9%86%D8%AF%DA%A9%DB%8C-30-%D9%88%D8%A7%D8%AA-%D9%85%D8%AF%D9%84-ysy-395kc/",
    "https://www.digikala.com/product/dkp-9184198/%D9%87%D8%AF%D9%81%D9%88%D9%86-%D8%A8%D9%84%D9%88%D8%AA%D9%88%D8%AB%DB%8C-%D8%B1%DB%8C%D9%85%DA%A9%D8%B3-%D9%85%D8%AF%D9%84-rb-s1/",
    "https://www.digikala.com/product/dkp-2271206/%D9%BE%D8%A7%D9%88%D8%B1%D8%A8%D8%A7%D9%86%DA%A9-%D8%B4%DB%8C%D8%A7%D8%A6%D9%88%D9%85%DB%8C-%D9%85%D8%AF%D9%84-redmi-%D8%B8%D8%B1%D9%81%DB%8C%D8%AA-20000-%D9%85%DB%8C%D9%84%DB%8C-%D8%A2%D9%85%D9%BE%D8%B1%D8%B3%D8%A7%D8%B9%D8%AA-%D8%A8%D9%87-%D9%87%D9%85%D8%B1%D8%A7%D9%87-%DA%A9%D8%A7%D8%A8%D9%84-%D8%AA%D8%A8%D8%AF%DB%8C%D9%84-microusb/",
    "https://www.digikala.com/product/dkp-2662857/%DA%A9%D8%A7%D9%88%D8%B1-%D9%85%D8%AF%D9%84-pro022-%D9%85%D9%86%D8%A7%D8%B3%D8%A8-%D8%A8%D8%B1%D8%A7%DB%8C-%DA%A9%DB%8C%D8%B3-%D8%A7%D9%BE%D9%84-%D8%A7%DB%8C%D8%B1%D9%BE%D8%A7%D8%AF-%D9%BE%D8%B1%D9%88/",
    "https://www.digikala.com/product/dkp-2240426/%D9%85%D8%AD%D8%A7%D9%81%D8%B8-%D9%84%D9%86%D8%B2-%D8%AF%D9%88%D8%B1%D8%A8%DB%8C%D9%86-%D9%84%D8%A7%DB%8C%D9%86-%DA%A9%DB%8C%D9%86%DA%AF-%D9%85%D8%AF%D9%84-lkl-%D9%85%D9%86%D8%A7%D8%B3%D8%A8-%D8%A8%D8%B1%D8%A7%DB%8C-%DA%AF%D9%88%D8%B4%DB%8C-%D9%85%D9%88%D8%A8%D8%A7%DB%8C%D9%84-%D8%B3%D8%A7%D9%85%D8%B3%D9%88%D9%86%DA%AF-galaxy-a30s/",
    "https://www.digikala.com/product/dkp-17990408/%D9%85%D9%88%D8%AF%D9%85-lte-%D9%82%D8%A7%D8%A8%D9%84-%D8%AD%D9%85%D9%84-%D9%86%D8%AA%D8%B1%D8%A8%DB%8C%D8%AA-%D9%85%D8%AF%D9%84-nwr-940x/",
    "https://www.digikala.com/product/dkp-19067686/%D9%87%D8%AF%D9%81%D9%88%D9%86-%D8%A8%D9%84%D9%88%D8%AA%D9%88%D8%AB%DB%8C-%D8%B1%DB%8C%D9%85%DA%A9%D8%B3-%D9%85%D8%AF%D9%84-cozy-pods-w7n-pro/",
    "https://www.digikala.com/product/dkp-15985727/%D8%B3%D8%A7%D8%B9%D8%AA-%D9%87%D9%88%D8%B4%D9%85%D9%86%D8%AF-%D9%85%D8%AF%D9%84-%D8%A7%D9%88%D9%84%D8%AA%D8%B1%D8%A7-t1000-%D8%AF%D8%A7%D8%B1%D8%A7%DB%8C-%D9%82%D8%A7%D8%A8%D9%84%DB%8C%D8%AA-%D9%87%D8%A7%DB%8C-%D9%82%D8%A7%D8%A8%D9%84%DB%8C%D8%AA-%D9%85%DA%A9%D8%A7%D9%84%D9%85%D9%87-%D9%85%D8%B3%D8%AA%D9%82%DB%8C%D9%85-%D9%82%D8%A7%D8%A8%D9%84%DB%8C%D8%AA-%D9%85%DA%A9%D8%A7%D9%84%D9%85%D9%87-%D8%A7%D8%B2-%D8%B7%D8%B1%DB%8C%D9%82-%D8%A8%D9%84%D9%88%D8%AA%D9%88%D8%AB-%D8%B6%D8%AF-%D8%A2%D8%A8-%D8%A8%D9%86%D8%AF-%D8%B3%DB%8C%D9%84%DB%8C%DA%A9%D9%88%D9%86/",
    "https://www.digikala.com/product/dkp-20011160/%D8%B3%D8%A7%D8%B9%D8%AA-%D9%87%D9%88%D8%B4%D9%85%D9%86%D8%AF-49-%D9%85%DB%8C%D9%84%DB%8C-%D9%85%D8%AA%D8%B1-%D9%87%D8%AF-%D9%85%D8%AF%D9%84-ultra-9-%D8%A8%D8%A7-%D8%A8%D9%86%D8%AF-%D8%B3%DB%8C%D9%84%DB%8C%DA%A9%D9%88%D9%86%DB%8C/"
]

scrape_multiple_products(product_urls=product_pages_list, total_max_comments=200, max_comments_per_product=50)