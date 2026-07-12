from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import random
from datetime import datetime
import os


class IndeedScraper:
    def __init__(self):
        self.base_url = "https://in.indeed.com"
        self.jobs_data = []
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome driver"""
        print("🔧 Setting up Chrome driver for Indeed...")
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Chrome driver ready!\n")
    
    def search_jobs(self, keyword, location, pages=3):
        """
        Scrape Indeed job listings
        keyword: 'data analyst' or 'data scientist'
        location: 'Pune' or 'Bangalore'
        pages: number of pages to scrape
        """
        print(f"🔍 Searching for '{keyword}' jobs in '{location}'...")
        
        if not self.driver:
            self.setup_driver()
        
        # Format for URL
        keyword_formatted = keyword.replace(' ', '+')
        location_formatted = location.replace(' ', '+')
        
        for page in range(pages):
            try:
                # Indeed uses 'start' parameter (0, 10, 20, 30...)
                start = page * 10
                
                # Construct Indeed URL
                search_url = f"{self.base_url}/jobs?q={keyword_formatted}&l={location_formatted}&start={start}"
                
                print(f"\n📄 Scraping page {page + 1}: {search_url}")
                
                # Load page
                self.driver.get(search_url)
                time.sleep(random.uniform(3, 5))
                
                # Scroll to load all jobs
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Find job cards
                job_cards = []
                
                # Try multiple selectors
                selectors = [
                    "div.job_seen_beacon",
                    "div.jobsearch-SerpJobCard",
                    "div.slider_item",
                    "td.resultContent"
                ]
                
                for selector in selectors:
                    try:
                        job_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if job_cards:
                            print(f"✅ Found {len(job_cards)} jobs using selector: {selector}")
                            break
                    except:
                        continue
                
                if not job_cards:
                    print("⚠️ No job cards found")
                    continue
                
                # Extract each job
                for idx, job_card in enumerate(job_cards):
                    try:
                        job_data = self.extract_job_details(job_card, keyword, location)
                        if job_data:
                            self.jobs_data.append(job_data)
                            print(f"  ✓ Job {idx + 1}/{len(job_cards)}")
                    except Exception as e:
                        continue
                
                print(f"✅ Page {page + 1}: Extracted {len(job_cards)} jobs")
                
                # Delay between pages
                time.sleep(random.uniform(3, 5))
                
            except Exception as e:
                print(f"❌ Error on page {page + 1}: {str(e)}")
                continue
        
        print(f"\n🎉 Total jobs scraped from Indeed: {len(self.jobs_data)}")
        return self.jobs_data
    
    def extract_job_details(self, job_card, keyword, location):
        """Extract job details from Indeed card"""
        try:
            job_data = {}
            
            # Job Title
            try:
                title_elem = job_card.find_element(By.CSS_SELECTOR, "h2.jobTitle span")
                job_data['job_title'] = title_elem.text.strip()
            except:
                try:
                    title_elem = job_card.find_element(By.CSS_SELECTOR, "a.jcs-JobTitle")
                    job_data['job_title'] = title_elem.text.strip()
                except:
                    job_data['job_title'] = 'N/A'
            
            # Company Name
            try:
                company_elem = job_card.find_element(By.CSS_SELECTOR, "span.companyName")
                job_data['company_name'] = company_elem.text.strip()
            except:
                job_data['company_name'] = 'N/A'
            
            # Location
            try:
                location_elem = job_card.find_element(By.CSS_SELECTOR, "div.companyLocation")
                job_data['location'] = location_elem.text.strip()
            except:
                job_data['location'] = location
            
            # Salary
            try:
                salary_elem = job_card.find_element(By.CSS_SELECTOR, "div.salary-snippet")
                job_data['salary'] = salary_elem.text.strip()
            except:
                job_data['salary'] = 'Not Disclosed'
            
            # Job Description
            try:
                desc_elem = job_card.find_element(By.CSS_SELECTOR, "div.job-snippet")
                job_data['description'] = desc_elem.text.strip()
            except:
                job_data['description'] = 'N/A'
            
            # Job URL
            try:
                link_elem = job_card.find_element(By.CSS_SELECTOR, "a.jcs-JobTitle")
                job_url = link_elem.get_attribute('href')
                job_data['job_url'] = job_url if job_url else 'N/A'
            except:
                job_data['job_url'] = 'N/A'
            
            # Posted Date
            try:
                date_elem = job_card.find_element(By.CSS_SELECTOR, "span.date")
                job_data['posted_date'] = date_elem.text.strip()
            except:
                job_data['posted_date'] = 'N/A'
            
            # Metadata
            job_data['search_keyword'] = keyword
            job_data['search_location'] = location
            job_data['scraped_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            job_data['source'] = 'Indeed'
            
            return job_data
            
        except Exception as e:
            return None
    
    def save_to_csv(self, filename='indeed_jobs.csv'):
        """Save to CSV"""
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
            print("📊 INDEED SCRAPING SUMMARY")
            print("="*60)
            print(f"Total Jobs: {len(df)}")
            print(f"\n🏢 Top 10 Companies:")
            print(df['company_name'].value_counts().head(10))
            print(f"\n📍 Locations:")
            print(df['location'].value_counts().head(10))
            print("="*60)
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            print("\n🔒 Browser closed")


# MAIN EXECUTION
if __name__ == "__main__":
    print("="*60)
    print("🚀 INDEED JOB SCRAPER")
    print("="*60)
    
    scraper = IndeedScraper()
    
    try:
        keywords = ['data analyst', 'data scientist']
        locations = ['Pune', 'Bangalore', 'Mumbai']
        pages = 3  # 3 pages per search
        
        for keyword in keywords:
            for location in locations:
                print(f"\n{'='*60}")
                print(f"🎯 {keyword.upper()} in {location.upper()}")
                print(f"{'='*60}")
                
                scraper.search_jobs(keyword, location, pages=pages)
                time.sleep(3)
        
        scraper.save_to_csv()
        scraper.get_summary()
        print("\n✅ Indeed scraping completed!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    finally:
        scraper.close()