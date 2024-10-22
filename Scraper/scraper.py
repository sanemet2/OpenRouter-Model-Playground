from bs4 import BeautifulSoup
import json
from datetime import datetime
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress WebDriver Manager logs
logging.getLogger('webdriver_manager').setLevel(logging.ERROR)

# Define paths
MODEL_REFERENCE_DIR = "Model_Reference"
MODEL_REFERENCE_FILE = os.path.join(MODEL_REFERENCE_DIR, "model_reference.json")
BACKUPS_DIR = os.path.join(MODEL_REFERENCE_DIR, "Backups")

# Create necessary directories
os.makedirs(MODEL_REFERENCE_DIR, exist_ok=True)
os.makedirs(BACKUPS_DIR, exist_ok=True)

def fetch_webpage_content(url):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--log-level=3')  # This will suppress console logs from ChromeDriver
        
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.get(url)
        
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.XPATH, "//table")))
        
        return driver.page_source
    except Exception as e:
        logging.error(f"Error fetching webpage: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()
    return None

def parse_html(html_content):
    return BeautifulSoup(html_content, 'html.parser')

def extract_model_info(soup):
    models = {'text_models': [], 'media_models': []}
    
    # Extract text models
    text_table = soup.find('table')
    if text_table:
        rows = text_table.find_all('tr')[1:]  # Skip the header row
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 5:
                try:
                    name_id_text = cols[0].get_text(separator='\n').strip()
                    name, id_ = name_id_text.split('\n', 1) if '\n' in name_id_text else (name_id_text, '')
                    model = {
                        'name': name,
                        'id': id_,
                        'prompt_cost': cols[1].get_text(strip=True),
                        'completion_cost': cols[2].get_text(strip=True),
                        'context_length': cols[3].get_text(strip=True),
                        'moderation': cols[4].get_text(strip=True)
                    }
                    models['text_models'].append(model)
                except Exception as e:
                    logging.error(f"Error parsing text model row: {str(e)}")
    
    # Extract media models
    media_section = soup.find(string='Media models')
    if media_section:
        media_div = media_section.find_next('div', class_='text-sm')
        if media_div:
            model_info = media_div.find('div', class_='flex justify-between')
            if model_info:
                name_span = model_info.find('span', class_='block')
                id_code = model_info.find('code', class_='text-xs')
                cost_span = model_info.find_all('span')[-1]  # Last span contains the cost
                
                if name_span and id_code and cost_span:
                    model = {
                        'name': name_span.text.strip(),
                        'id': id_code.text.strip(),
                        'cost': cost_span.text.strip()
                    }
                    models['media_models'].append(model)
    
    return models

def scrape_models(url):
    html_content = fetch_webpage_content(url)
    if html_content:
        soup = parse_html(html_content)
        return extract_model_info(soup)
    return None

def compare_and_update_data(new_data, filename=MODEL_REFERENCE_FILE):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            old_data = json.load(f)
        
        if new_data == old_data:
            logging.info("No changes in scraped data.")
            return False
    
    with open(filename, 'w') as f:
        json.dump(new_data, f, indent=2)
    logging.info(f"Updated scraped data saved to {filename}")
    return True

def job():
    url = "https://openrouter.ai/docs/models"
    scraped_models = scrape_models(url)
    if scraped_models:
        logging.info(f"Successfully scraped {len(scraped_models['text_models'])} text models and {len(scraped_models['media_models'])} media models")
        
        if compare_and_update_data(scraped_models):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = os.path.join(BACKUPS_DIR, f"scraped_models_{timestamp}.json")
            with open(backup_filename, 'w') as f:
                json.dump(scraped_models, f, indent=2)
            logging.info(f"Backup created: {backup_filename}")
        else:
            logging.info("No changes detected, skipping backup creation.")
    else:
        logging.error("Failed to scrape models")

if __name__ == "__main__":
    logging.info("Running scraper")
    job()
