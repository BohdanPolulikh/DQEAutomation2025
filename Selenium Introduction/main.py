import time
import os
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class WebDriverManager:
    def __init__(self, headless=True): 
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless") 
        options.add_argument("--allow-file-access-from-files")
        options.add_argument("--window-size=1920,1028") 
        self.options = options
        self.driver = None

    def __enter__(self):
        """WebDriver Initialization"""
        print("WebDriver Initialization...")
        try:
            self.driver = webdriver.Chrome(options=self.options)
            return self.driver
        except Exception as e:
            print(f"WebDriver Initialization error: {e}")
            return None 

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit WebDriver."""
        if self.driver:
            print("Closing WebDriver...")
            self.driver.quit()
        return False 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_HTML_PATH = os.path.join(BASE_DIR, "report.html")
LOCAL_HTML_URL = f"file:///{LOCAL_HTML_PATH}"

LEGEND_SELECTORS = {
    "Clinic": ".legend g.traces:nth-child(1) rect.legendtoggle", 
    "Hospital": ".legend g.traces:nth-child(2) rect.legendtoggle",
    "Specialty Center": ".legend g.traces:nth-child(3) rect.legendtoggle"
}

# Sequence of actions for filtering
SEQUENCE_OF_FILTER_ACTIONS = [
    ["Clinic"],
    ["Hospital"],
    ["Specialty Center"],
    ["Clinic"],
    ["Hospital"],
    ["Clinic"],
    ["Clinic", "Hospital", "Specialty Center"]
]

def save_plotly_table_csv_dom_extraction(driver):
    """
    Extracts table data using Plotly SVG structure.
    """
    column_selector = 'g.table-control-view g.y-column'
    
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, column_selector))
        )
        column_elements = driver.find_elements(By.CSS_SELECTOR, column_selector)
    except TimeoutException:
        print(f"Error: Could not find column containers by CSS Selector: {column_selector}.")
        return

    print(f"Found {len(column_elements)} elements 'y-column'.")
    
    columns_data = []
    
    for col_element in column_elements:
        header_name = ""

        header_block = col_element.find_element(By.ID, 'header')
        header_text_element = header_block.find_element(By.CSS_SELECTOR, 'g.cell-text-holder text.cell-text')
            
        header_name = header_text_element.text
        
        data_cells_selector = 'g[id^="cells"] g.column-cells g.column-cell g.cell-text-holder text.cell-text'
        data_text_elements = col_element.find_elements(By.CSS_SELECTOR, data_cells_selector)
        
        column_values = [el.text.strip() for el in data_text_elements if el.text.strip()]
        
        columns_data.append({
            'header': header_name,
            'values': column_values
        })
        
    row_count = min(len(col['values']) for col in columns_data)
    final_headers = [col['header'] for col in columns_data]
    
    table_rows = list()
    for i in range(row_count):
        row = [col['values'][i] for col in columns_data]
        table_rows.append(row)

    df = pd.DataFrame(table_rows, columns=final_headers)
    df.to_csv('table.csv', index=False, encoding='utf-8')
    
    print(f"Table data is stored in table.csv. Collected {row_count} rows.")


def save_plotly_chart_csv(driver, index):
    """
    Extracts data from a pie chart
    """
    csv_name = f'doughnut{index}.csv'
    data_list = []
    slice_text_selector = "g.slicetext text"
    
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'svg.main-svg')))
        slice_texts = driver.find_elements(By.CSS_SELECTOR, slice_text_selector)
        
        for text_element in slice_texts:
            unformatted_data = text_element.get_attribute("data-unformatted")
            if unformatted_data:
                parts = unformatted_data.split('<br>')
                if len(parts) == 2:
                    facility_type = parts[0].strip()
                    value = parts[1].strip()
                    data_list.append([facility_type, value])
            
    except TimeoutException:
        print(f"Waiting time for the elements has expired.")
    except Exception as e:
        print(f"Critical data extraction error: {e}")
    
    header = ['Facility Type', 'Min Average Time Spent']

    df = pd.DataFrame(data_list, columns=header)
    df.to_csv(csv_name, index=False, encoding='utf-8')

    print(f"The data in the chart is stored in {csv_name}.")


def extract_table_data(driver, url):
    """Extracts data from a table."""
    driver.get(url) 
    
    time.sleep(10) 
    
    save_plotly_table_csv_dom_extraction(driver)
        
def interact_with_chart(driver):
    """
    Performs initial screenshot and extraction, including filtering steps.
    """
    current_index = 0
    driver.save_screenshot(f'screenshot{current_index}.png')
    save_plotly_chart_csv(driver, current_index)

    for step_index, actions in enumerate(SEQUENCE_OF_FILTER_ACTIONS, 1):
        current_index = step_index
        print(f"\nStep #{current_index}: Filtration ---")
        
        for facility_type in actions:
            selector = LEGEND_SELECTORS.get(facility_type)
            by_method = By.CSS_SELECTOR
            
            if not selector:
                print(f"Error: No selector found for facility type: {facility_type}")
                continue
                
            print(f"Action: Click on '{facility_type}' (Selector: {selector})")
            
            try:
                legend_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((by_method, selector))
                )
                
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", legend_element)
                time.sleep(1) 
                
                legend_element.click()
                
                print(f"Successful click on '{facility_type}'")
                time.sleep(3) 
                
            except TimeoutException:
                print(f"Error: Could not find legend item '{facility_type}' by selector.")

            except Exception as e:
                print(f"Error when clicking: {e}")

        driver.save_screenshot(f'screenshot{current_index}.png')
        save_plotly_chart_csv(driver, current_index)
        print(f"Saved screenshot{current_index}.png and doughnut{current_index}.csv")

    print("\nIteration completed: Generated 8 files\n")
    
if __name__ == "__main__":
    if not os.path.exists(LOCAL_HTML_PATH):
        print(f"Error: File report.html is not found in path: {LOCAL_HTML_PATH}")
    
    with WebDriverManager(headless=True) as driver: 
        extract_table_data(driver, LOCAL_HTML_URL)
        interact_with_chart(driver)

    print("\nAutomation successfully completed!\n")
