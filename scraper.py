import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_community_centres():
    url = "https://vancouver.ca/parks-recreation-culture/recreation-facility-hours.aspx"
    
    # Add headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
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
                    
                    # Skip header rows
                    if name and name != "Community centre" and not name.startswith("Fitness"):
                        # Extract hours for each day
                        hours = {}
                        for i, day in enumerate(day_names):
                            cell_index = i + 1  # Skip first column (name)
                            if cell_index < len(cells):
                                hours[day] = cells[cell_index].get_text(strip=True)
                        
                        data["centres"][name] = hours
        
        print(f"Found {len(data['centres'])} community centres")
        return data
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response status: {e.response.status_code}")
        print(f"Response content: {e.response.text[:500]}")
        return None
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
