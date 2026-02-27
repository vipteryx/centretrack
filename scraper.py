import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_community_centres():
    url = "https://vancouver.ca/parks-recreation-culture/recreation-facility-hours.aspx"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the community centres table
        tables = soup.find_all('table')
        
        data = {
            "lastUpdated": datetime.utcnow().isoformat() + "Z",
            "centres": {}
        }
        
        # Days mapping: Mon=1, Tue=2, Wed=3, Thu=4, Fri=5, Sat=6, Sun=7
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all('td')
                
                if len(cells) >= 8:
                    # First cell is the name
                    name_cell = cells[0]
                    name_link = name_cell.find('a')
                    name = name_link.get_text(strip=True) if name_link else name_cell.get_text(strip=True)
                    
                    if name and name != "Community centre":
                        # Extract hours for each day
                        hours = {}
                        for i, day in enumerate(day_names):
                            cell_index = i + 1  # Skip first column (name)
                            if cell_index < len(cells):
                                hours[day] = cells[cell_index].get_text(strip=True)
                        
                        data["centres"][name] = hours
        
        return data
    
    except Exception as e:
        print(f"Error scraping data: {e}")
        return None

if __name__ == "__main__":
    data = scrape_community_centres()
    
    if data and data["centres"]:
        with open("data/hours.json", "w") as f:
            json.dump(data, f, indent=2)
        print(f"Successfully scraped {len(data['centres'])} community centres")
    else:
        print("Failed to scrape data")
        exit(1)
