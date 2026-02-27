from playwright.sync_api import sync_playwright
import json
from datetime import datetime

def scrape_community_centres():
    url = "https://vancouver.ca/parks-recreation-culture/recreation-facility-hours.aspx"
    
    try:
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Navigate to the page
            print(f"Fetching {url}...")
            page.goto(url, wait_until='networkidle')
            
            # Wait for the table to load
            page.wait_for_selector('table')
            
            data = {
                "lastUpdated": datetime.utcnow().isoformat() + "Z",
                "centres": {}
            }
            
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            
            # Find all tables
            tables = page.query_selector_all('table')
            
            for table in tables:
                rows = table.query_selector_all('tr')
                
                for row in rows:
                    cells = row.query_selector_all('td')
                    
                    if len(cells) >= 8:
                        # First cell is the name
                        name_cell = cells[0]
                        name_link = name_cell.query_selector('a')
                        name = name_link.inner_text().strip() if name_link else name_cell.inner_text().strip()
                        
                        # Skip header rows
                        if name and name != "Community centre" and not name.startswith("Fitness"):
                            # Extract hours for each day
                            hours = {}
                            for i, day in enumerate(day_names):
                                cell_index = i + 1  # Skip first column (name)
                                if cell_index < len(cells):
                                    hours[day] = cells[cell_index].inner_text().strip()
                            
                            data["centres"][name] = hours
            
            browser.close()
            
            print(f"Found {len(data['centres'])} community centres")
            return data
    
    except Exception as e:
        print(f"Error scraping data: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    data = scrape_community_centres()
    
    if data and data["centres"]:
        with open("data/hours.json", "w") as f:
            json.dump(data, f, indent=2)
        print(f"Successfully scraped {len(data['centres'])} community centres")
        print("Data saved to data/hours.json")
    else:
        print("Failed to scrape data")
        exit(1)
