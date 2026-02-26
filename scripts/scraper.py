import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

# List of URLs to scrape
URLS = [
    "https://gnindia.dronacharya.info/Default.aspx",
    "https://gnindia.dronacharya.info/About-Us.aspx",
    "https://gnindia.dronacharya.info/managementperspective.aspx",
    "https://gnindia.dronacharya.info/academicperspective.aspx",
    "https://gnindia.dronacharya.info/Aicte-Approval.aspx",
    "https://gnindia.dronacharya.info/Affiliating-University.aspx",
    "https://gnindia.dronacharya.info/NBA.aspx",
    "https://gnindia.dronacharya.info/Naac.aspx",
    "https://gnindia.dronacharya.info/Learning-Partners.aspx",
    "https://gnindia.dronacharya.info/academiccalendar.aspx",
    "https://gnindia.dronacharya.info/contact.aspx",
    "https://gnindia.dronacharya.info/Campus-Life.aspx",
    "https://gnindia.dronacharya.info/Clubs.aspx",
    "https://gnindia.dronacharya.info/Safety-and-Security.aspx",
    "https://gnindia.dronacharya.info/rules.aspx",
    "https://gnindia.dronacharya.info/Woman-Development-Cell.aspx",
    "https://gnindia.dronacharya.info/Achievements/Achievements-2025-26.aspx",
    "https://gnindia.dronacharya.info/PlacementStatistics/Batch-wise-record-2025.aspx",
    "https://gnindia.dronacharya.info/PlacementStatistics/Batch-wise-record-2026.aspx",
    "https://gnindia.dronacharya.info/Our-Recruiters.aspx",
    "https://gnindia.dronacharya.info/Placement-Partners.aspx",
    "https://gnindia.dronacharya.info/Summer-Internship.aspx",
    "https://gnindia.dronacharya.info/Career-Development-Centre.aspx",
    "https://gnindia.dronacharya.info/PlacementDesk.aspx",
    "https://gnindia.dronacharya.info/Congratulations-Notice.aspx",
    "https://gnindia.dronacharya.info/Education-Loan.aspx",
    "https://gnindia.dronacharya.info/Financial-Support.aspx",
    "https://gnindia.dronacharya.info/Admissions/FAQs.aspx",
    "https://gnindia.dronacharya.info/Placement/FAQs.aspx",
    "https://gnindia.dronacharya.info/APS/home.aspx",
    "https://gnindia.dronacharya.info/APS/Faculty.aspx",
    "https://gnindia.dronacharya.info/APS/Syllabus.aspx",
    "https://gnindia.dronacharya.info/APS/Time_Table.aspx",
    "https://gnindia.dronacharya.info/CSE/home.aspx",
    "https://gnindia.dronacharya.info/CSE/Faculty.aspx",
    "https://gnindia.dronacharya.info/CSE/Syllabus.aspx",
    "https://gnindia.dronacharya.info/CSEIT/home.aspx",
    "https://gnindia.dronacharya.info/CSEIT/Faculty.aspx",
    "https://gnindia.dronacharya.info/CSEIT/Syllabus.aspx",
    "https://gnindia.dronacharya.info/IT/home.aspx",
    "https://gnindia.dronacharya.info/IT/Faculty.aspx",
    "https://gnindia.dronacharya.info/IT/Syllabus.aspx",
    "https://gnindia.dronacharya.info/ECE/home.aspx",
    "https://gnindia.dronacharya.info/ECE/Faculty.aspx",
    "https://gnindia.dronacharya.info/ECE/Syllabus.aspx",
    "https://gnindia.dronacharya.info/ECS/home.aspx",
    "https://gnindia.dronacharya.info/ECS/Faculty.aspx",
    "https://gnindia.dronacharya.info/ECS/Syllabus.aspx",
    "https://gnindia.dronacharya.info/EEE/home.aspx",
    "https://gnindia.dronacharya.info/EEE/Faculty.aspx",
    "https://gnindia.dronacharya.info/EEE/Syllabus.aspx",
    "https://gnindia.dronacharya.info/ME/home.aspx",
    "https://gnindia.dronacharya.info/ME/Faculty.aspx",
    "https://gnindia.dronacharya.info/ME/Syllabus.aspx",
    "https://gnindia.dronacharya.info/CSE-AI-ML/home.aspx",
    "https://gnindia.dronacharya.info/CSE-AI-ML/Faculty.aspx",
    "https://gnindia.dronacharya.info/CSE-AI-ML/Syllabus.aspx",
    "https://gnindia.dronacharya.info/MBA/home.aspx",
    "https://gnindia.dronacharya.info/MBA/Faculty.aspx",
    "https://gnindia.dronacharya.info/MBA/Syllabus.aspx",
    "https://gnindia.dronacharya.info/Centre-of-Excellence.aspx",
    "https://gnindia.dronacharya.info/Patents-Copyrights.aspx",
    "https://gnindia.dronacharya.info/BookPublished/Book-Published-CSE.aspx",
    "https://gnindia.dronacharya.info/Gate-Qualifiers/Gate-2025.aspx",
    "https://gnindia.dronacharya.info/Toppers/CSE-2024.aspx"
]

# We write to website_data.txt to avoid overwriting the manual college_data.txt
OUTPUT_FILE = "website_data.txt"

def scrape_url(url):
    print(f"Scraping: {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove non-content elements to clean up text
        for element in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            element.decompose()
            
        # Extract Main Text
        text_content = soup.get_text(separator='\n')
        
        # Clean up text (remove excessive newlines)
        lines = (line.strip() for line in text_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Extract Hyperlinks from the body/main area
        links_found = []
        # We search in 'body' since we already decomposed nav/footer
        body = soup.find('body')
        if body:
            for link in body.find_all('a', href=True):
                href = link['href']
                link_text = link.get_text(strip=True)
                
                # Filter out empty links or javascript: calls
                if not href or href.startswith(('javascript:', '#', 'tel:', 'mailto:')):
                    continue
                    
                # Convert relative to absolute
                absolute_url = urljoin(url, href)
                
                if link_text:
                    links_found.append(f"    - Link: {link_text} | URL: {absolute_url}")
        
        # Format the output block
        output = f"================ DATA FROM: {url} ================\n"
        output += f"{clean_text}\n\n"
        
        if links_found:
            output += "    [IMPORTANT LINKS FOUND]\n"
            output += "\n".join(links_found)
            output += "\n"
            
        output += "\n" + "="*80 + "\n\n"
        
        return output

    except Exception as e:
        print(f"ERROR scraping {url}: {e}")
        return f"=== ERROR SCRAPING {url} ===\nError: {str(e)}\n\n"

def main():
    print("Starting Production-Grade Scraper...")
    print(f"Targeting {len(URLS)} URLs.")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        # Write header
        f.write("GENERATED WEBSITE DATA\n")
        f.write("======================\n\n")
        
        for i, url in enumerate(URLS):
            print(f"[{i+1}/{len(URLS)}] Processing...")
            content = scrape_url(url)
            f.write(content)
            time.sleep(1) # Be polite to the server

    print(f"\nSUCCESS! All data saved to {OUTPUT_FILE}")
    print("Please restart your chatbot server to load the new data.")

if __name__ == "__main__":
    main()
