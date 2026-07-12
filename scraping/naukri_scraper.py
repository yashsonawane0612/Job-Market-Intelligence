from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import random
from datetime import datetime
import os

class NaukriScraperV2:
    def __init__(self):
        self.base_url = "https://www.naukri.com"
        self.jobs_data = []
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        print("🔧 Setting up Chrome driver...")
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in background
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Chrome driver ready!\n")
    
    def search_jobs(self, keyword, location, pages=3):
        """Scrape job listings using Selenium"""
        print(f"🔍 Searching for '{keyword}' jobs in '{location}'...")
        
        if not self.driver:
            self.setup_driver()
        
        for page in range(1, pages + 1):
            try:
                # Construct URL
                search_url = f"{self.base_url}/{keyword}-jobs-in-{location}-{page}"
                print(f"\n📄 Scraping page {page}: {search_url}")
                
                # Load page
                self.driver.get(search_url)
                
                # Wait for jobs to load (wait for job cards)
                print("⏳ Waiting for page to load...")
                time.sleep(5)  # Give time for JavaScript to load
                
                # Scroll to load all jobs
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Find job cards - try multiple selectors
                job_cards = []
                
                # Try different selectors
                selectors = [
                    (By.CLASS_NAME, "jobTuple"),
                    (By.CLASS_NAME, "srp-jobtuple-wrapper"),
                    (By.CLASS_NAME, "cust-job-tuple"),
                    (By.CSS_SELECTOR, "article[class*='job']"),
                    (By.CSS_SELECTOR, "div[class*='job-tuple']"),
                ]
                
                for by, selector in selectors:
                    try:
                        job_cards = self.driver.find_elements(by, selector)
                        if job_cards:
                            print(f"✅ Found {len(job_cards)} jobs using selector: {selector}")
                            break
                    except:
                        continue
                
                if not job_cards:
                    print("⚠️ No job cards found with any selector")
                    # Save page source for debugging
                    with open('debug_page.html', 'w', encoding='utf-8') as f:
                        f.write(self.driver.page_source)
                    print("💾 Saved page source to debug_page.html for inspection")
                    continue
                
                # Extract data from each job card
                for idx, job_card in enumerate(job_cards):
                    try:
                        job_data = self.extract_job_details(job_card, keyword, location)
                        if job_data:
                            self.jobs_data.append(job_data)
                    except Exception as e:
                        print(f"⚠️ Error extracting job {idx+1}: {str(e)}")
                        continue
                
                print(f"✅ Page {page}: Extracted {len(job_cards)} jobs")
                
                # Random delay
                delay = random.uniform(3, 5)
                print(f"⏳ Waiting {delay:.1f} seconds...")
                time.sleep(delay)
                
            except Exception as e:
                print(f"❌ Error on page {page}: {str(e)}")
                continue
        
        print(f"\n🎉 Total jobs scraped: {len(self.jobs_data)}")
        return self.jobs_data
    
    def extract_job_details(self, job_card, keyword, location):
        """Extract details from job card using Selenium"""
        try:
            job_data = {}
            
            # Job Title
            try:
                title_elem = job_card.find_element(By.CSS_SELECTOR, "a[class*='title']")
                job_data['job_title'] = title_elem.text.strip()
                job_data['job_url'] = title_elem.get_attribute('href')
            except:
                job_data['job_title'] = 'N/A'
                job_data['job_url'] = 'N/A'
            
            # Company Name
            try:
                company_elem = job_card.find_element(By.CSS_SELECTOR, "a[class*='comp'], div[class*='comp']")
                job_data['company_name'] = company_elem.text.strip()
            except:
                job_data['company_name'] = 'N/A'
            
            # Experience
            try:
                exp_elem = job_card.find_element(By.CSS_SELECTOR, "span[class*='exp'], div[class*='exp']")
                job_data['experience'] = exp_elem.text.strip()
            except:
                job_data['experience'] = 'N/A'
            
            # Salary
            try:
                salary_elem = job_card.find_element(By.CSS_SELECTOR, "span[class*='sal'], div[class*='sal']")
                job_data['salary'] = salary_elem.text.strip()
            except:
                job_data['salary'] = 'Not Disclosed'
            
            # Location
            try:
                loc_elem = job_card.find_element(By.CSS_SELECTOR, "span[class*='loc'], div[class*='loc']")
                job_data['location'] = loc_elem.text.strip()
            except:
                job_data['location'] = location
            
            # Skills
            try:
                skills_elems = job_card.find_elements(By.CSS_SELECTOR, "li[class*='tag'], span[class*='tag']")
                if skills_elems:
                    skills = [elem.text.strip() for elem in skills_elems if elem.text.strip()]
                    job_data['skills'] = ', '.join(skills[:10])  # Limit to 10 skills
                else:
                    job_data['skills'] = 'N/A'
            except:
                job_data['skills'] = 'N/A'
            
            # Description
            try:
                desc_elem = job_card.find_element(By.CSS_SELECTOR, "div[class*='desc']")
                job_data['description'] = desc_elem.text.strip()[:500]
            except:
                job_data['description'] = 'N/A'
            
            # Metadata
            job_data['search_keyword'] = keyword
            job_data['search_location'] = location
            job_data['scraped_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            job_data['source'] = 'Naukri'
            
            return job_data
            
        except Exception as e:
            print(f"⚠️ Error extracting details: {str(e)}")
            return None
    
    def save_to_csv(self, filename='naukri_jobs_selenium.csv'):
        """Save data to CSV"""
        if self.jobs_data:
            df = pd.DataFrame(self.jobs_data)
            os.makedirs('data/raw', exist_ok=True)
            filepath = f'data/raw/{filename}'
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"\n💾 Data saved to {filepath}")
            print(f"📊 Total records: {len(df)}")
            return df
        else:
            print("❌ No data to save!")
            return None
    
    def get_summary(self):
        """Print summary"""
        if self.jobs_data:
            df = pd.DataFrame(self.jobs_data)
            print("\n" + "="*60)
            print("📊 SCRAPING SUMMARY")
            print("="*60)
            print(f"Total Jobs: {len(df)}")
            print(f"\n🏢 Top 10 Companies:")
            print(df['company_name'].value_counts().head(10))
            print(f"\n📍 Locations:")
            print(df['location'].value_counts())
            print("="*60)
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            print("\n🔒 Browser closed")


# MAIN EXECUTION
if __name__ == "__main__":
    print("="*60)
    print("🚀 NAUKRI JOB SCRAPER V2 (Selenium)")
    print("="*60)
    
    scraper = NaukriScraperV2()
    
    try:
        # Search parameters
        keywords = ['data-analyst','data-scientist','business-analyst']
        locations = ['pune','mumbai','bangalore','hyderabad','chennai']
        pages = 5  
        
        for keyword in keywords:
            for location in locations:
                print(f"\n{'='*60}")
                print(f"🎯 {keyword.upper()} in {location.upper()}")
                print(f"{'='*60}")
                scraper.search_jobs(keyword, location, pages=pages)
                time.sleep(3)
        
        # Save and summarize
        scraper.save_to_csv()
        scraper.get_summary()
        
        print("\n✅ Scraping completed!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    finally:
        scraper.close()