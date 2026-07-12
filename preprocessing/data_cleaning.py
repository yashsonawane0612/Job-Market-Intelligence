import pandas as pd
import re
import os

class DataCleaner:
    def __init__(self, input_file=r'C:\Users\Bittu\Desktop\Job_Market_Intelligence\data\processed\combined_jobs.csv'):
        self.input_file = input_file
        self.df = None
        
    def load_data(self):
        """Load combined dataset"""
        print("="*60)
        print("📂 LOADING DATA")
        print("="*60)
        
        self.df = pd.read_csv(self.input_file)
        print(f"✅ Loaded {len(self.df)} jobs")
        print(f"📋 Columns: {list(self.df.columns)}")
        
    def clean_job_titles(self):
        """Standardize job titles"""
        print("\n" + "="*60)
        print("🏷️ CLEANING JOB TITLES")
        print("="*60)
        
        # Remove extra spaces
        self.df['job_title'] = self.df['job_title'].str.strip()
        
        # Standardize common variations
        title_mapping = {
            'Data Analyst': ['data analyst', 'data analytics', 'analyst - data', 'data-analyst'],
            'Data Scientist': ['data scientist', 'data science', 'scientist - data', 'data-scientist'],
            'Business Analyst': ['business analyst', 'ba -', 'business analytics', 'business-analyst'],
            'Senior Data Analyst': ['senior data analyst', 'sr. data analyst', 'sr data analyst'],
            'Junior Data Analyst': ['junior data analyst', 'jr. data analyst', 'jr data analyst']
        }
        
        def standardize_title(title):
            if pd.isna(title) or title == 'N/A':
                return 'N/A'
            
            title_lower = title.lower()
            for standard, variations in title_mapping.items():
                for variation in variations:
                    if variation in title_lower:
                        return standard
            return title
        
        self.df['job_title_clean'] = self.df['job_title'].apply(standardize_title)
        
        print(f"✅ Job titles cleaned")
        print(f"\n📊 Top 10 standardized titles:")
        print(self.df['job_title_clean'].value_counts().head(10))
        
    def clean_company_names(self):
        """Clean company names"""
        print("\n" + "="*60)
        print("🏢 CLEANING COMPANY NAMES")
        print("="*60)
        
        # Remove extra spaces and special characters
        self.df['company_name_clean'] = self.df['company_name'].str.strip()
        self.df['company_name_clean'] = self.df['company_name_clean'].str.replace(r'\s+', ' ', regex=True)
        
        # Replace N/A with 'Unknown'
        self.df['company_name_clean'] = self.df['company_name_clean'].replace('N/A', 'Unknown')
        
        print(f"✅ Company names cleaned")
        print(f"\n📊 Top 10 companies:")
        print(self.df['company_name_clean'].value_counts().head(10))
        
    def extract_salary_info(self):
        """Extract and standardize salary information"""
        print("\n" + "="*60)
        print("💰 EXTRACTING SALARY INFORMATION")
        print("="*60)
        
        def extract_salary_range(salary_text):
            """Extract min and max salary from text"""
            if pd.isna(salary_text) or salary_text in ['Not Disclosed', 'N/A']:
                return None, None
            
            # Remove currency symbols and extra text
            salary_text = str(salary_text).upper()
            
            # Extract numbers (handles formats like "3-5 Lacs", "₹3L-5L", "300000-500000")
            numbers = re.findall(r'(\d+\.?\d*)', salary_text)
            
            if len(numbers) >= 2:
                min_sal = float(numbers[0])
                max_sal = float(numbers[1])
                
                # Convert to lakhs if needed
                if 'LAC' in salary_text or 'LPA' in salary_text or 'L' in salary_text:
                    # Already in lakhs
                    pass
                elif min_sal > 100:  # Likely in thousands
                    min_sal = min_sal / 100000
                    max_sal = max_sal / 100000
                
                return min_sal, max_sal
            elif len(numbers) == 1:
                sal = float(numbers[0])
                if 'LAC' in salary_text or 'LPA' in salary_text:
                    return sal, sal
                elif sal > 100:
                    sal = sal / 100000
                    return sal, sal
                return sal, sal
            
            return None, None
        
        # Extract salary ranges
        salary_info = self.df['salary'].apply(extract_salary_range)
        self.df['salary_min_lpa'] = salary_info.apply(lambda x: x[0] if x else None)
        self.df['salary_max_lpa'] = salary_info.apply(lambda x: x[1] if x else None)
        self.df['salary_avg_lpa'] = (self.df['salary_min_lpa'] + self.df['salary_max_lpa']) / 2
        
        disclosed_count = self.df['salary_min_lpa'].notna().sum()
        print(f"✅ Salary information extracted")
        print(f"📊 Salaries disclosed: {disclosed_count} ({disclosed_count/len(self.df)*100:.1f}%)")
        
        if disclosed_count > 0:
            print(f"\n💰 Salary Statistics (LPA):")
            print(f"   Min: ₹{self.df['salary_min_lpa'].min():.2f}")
            print(f"   Max: ₹{self.df['salary_max_lpa'].max():.2f}")
            print(f"   Average: ₹{self.df['salary_avg_lpa'].mean():.2f}")
            print(f"   Median: ₹{self.df['salary_avg_lpa'].median():.2f}")
        
    def extract_experience(self):
        """Extract experience requirements"""
        print("\n" + "="*60)
        print("📊 EXTRACTING EXPERIENCE REQUIREMENTS")
        print("="*60)
        
        def parse_experience(exp_text):
            """Extract min and max experience from text"""
            if pd.isna(exp_text) or exp_text == 'N/A':
                return None, None
            
            exp_text = str(exp_text).lower()
            
            # Extract numbers
            numbers = re.findall(r'(\d+)', exp_text)
            
            if len(numbers) >= 2:
                return int(numbers[0]), int(numbers[1])
            elif len(numbers) == 1:
                return int(numbers[0]), int(numbers[0])
            elif 'fresher' in exp_text or 'entry' in exp_text:
                return 0, 0
            
            return None, None
        
        exp_info = self.df['experience'].apply(parse_experience)
        self.df['exp_min_years'] = exp_info.apply(lambda x: x[0] if x else None)
        self.df['exp_max_years'] = exp_info.apply(lambda x: x[1] if x else None)
        
        # Categorize experience level
        def categorize_experience(min_exp):
            if pd.isna(min_exp):
                return 'Not Specified'
            elif min_exp == 0:
                return 'Fresher (0 years)'
            elif min_exp <= 2:
                return 'Entry Level (0-2 years)'
            elif min_exp <= 5:
                return 'Mid Level (3-5 years)'
            else:
                return 'Senior Level (5+ years)'
        
        self.df['experience_level'] = self.df['exp_min_years'].apply(categorize_experience)
        
        print(f"✅ Experience requirements extracted")
        print(f"\n📊 Jobs by Experience Level:")
        print(self.df['experience_level'].value_counts())
        
    def clean_locations(self):
        """Standardize location names"""
        print("\n" + "="*60)
        print("📍 CLEANING LOCATIONS")
        print("="*60)
        
        # Extract primary city from location string
        def extract_primary_city(location):
            if pd.isna(location) or location == 'N/A':
                return 'Unknown'
            
            location = str(location)
            
            # Common city mappings
            city_mapping = {
                'pune': 'Pune',
                'bangalore': 'Bangalore',
                'bengaluru': 'Bangalore',
                'mumbai': 'Mumbai',
                'delhi': 'Delhi',
                'ncr': 'Delhi NCR',
                'noida': 'Delhi NCR',
                'gurugram': 'Delhi NCR',
                'gurgaon': 'Delhi NCR',
                'hyderabad': 'Hyderabad',
                'chennai': 'Chennai',
                'kolkata': 'Kolkata'
            }
            
            location_lower = location.lower()
            
            for key, value in city_mapping.items():
                if key in location_lower:
                    return value
            
            # If no match, return first part before comma
            return location.split(',')[0].strip()
        
        self.df['primary_city'] = self.df['location'].apply(extract_primary_city)
        
        # Identify remote/hybrid jobs
        self.df['is_remote'] = self.df['location'].str.contains('remote', case=False, na=False)
        self.df['is_hybrid'] = self.df['location'].str.contains('hybrid', case=False, na=False)
        
        print(f"✅ Locations cleaned")
        print(f"\n📊 Top 10 Cities:")
        print(self.df['primary_city'].value_counts().head(10))
        print(f"\n🏠 Remote jobs: {self.df['is_remote'].sum()}")
        print(f"🏢 Hybrid jobs: {self.df['is_hybrid'].sum()}")
        
    def extract_skills(self):
        """Extract common skills from job descriptions and skills field"""
        print("\n" + "="*60)
        print("🔧 EXTRACTING SKILLS")
        print("="*60)
        
        # Common data analyst skills
        skill_keywords = {
            'Python': ['python'],
            'SQL': ['sql', 'mysql', 'postgresql', 'oracle'],
            'Excel': ['excel', 'spreadsheet'],
            'Power BI': ['power bi', 'powerbi'],
            'Tableau': ['tableau'],
            'R': [' r ', 'r programming'],
            'Statistics': ['statistics', 'statistical'],
            'Machine Learning': ['machine learning', 'ml'],
            'Data Visualization': ['data visualization', 'data viz'],
            'ETL': ['etl'],
            'Pandas': ['pandas'],
            'NumPy': ['numpy'],
            'Scikit-learn': ['scikit', 'sklearn'],
            'AWS': ['aws', 'amazon web services'],
            'Azure': ['azure'],
            'Big Data': ['big data', 'hadoop', 'spark']
        }
        
        # Combine description and skills fields
        self.df['text_to_search'] = (
            self.df['description'].fillna('') + ' ' + 
            self.df['skills'].fillna('')
        ).str.lower()
        
        # Extract each skill
        for skill, keywords in skill_keywords.items():
            self.df[f'has_{skill.lower().replace(" ", "_")}'] = False
            for keyword in keywords:
                self.df[f'has_{skill.lower().replace(" ", "_")}'] |= self.df['text_to_search'].str.contains(keyword, case=False, na=False)
        
        # Count total skills per job
        skill_columns = [col for col in self.df.columns if col.startswith('has_')]
        self.df['total_skills_mentioned'] = self.df[skill_columns].sum(axis=1)
        
        print(f"✅ Skills extracted")
        print(f"\n📊 Most In-Demand Skills:")
        skill_counts = {}
        for skill in skill_keywords.keys():
            col_name = f'has_{skill.lower().replace(" ", "_")}'
            count = self.df[col_name].sum()
            skill_counts[skill] = count
        
        # Sort and display
        sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
        for skill, count in sorted_skills[:15]:
            percentage = (count / len(self.df)) * 100
            print(f"   {skill}: {count} ({percentage:.1f}%)")
        
    def add_metadata(self):
        """Add useful metadata columns"""
        print("\n" + "="*60)
        print("📝 ADDING METADATA")
        print("="*60)
        
        # Add cleaned timestamp
        self.df['cleaned_at'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Add job posting age (if scraped_at exists)
        if 'scraped_at' in self.df.columns:
            self.df['scraped_at'] = pd.to_datetime(self.df['scraped_at'])
            self.df['days_since_scraped'] = (pd.Timestamp.now() - self.df['scraped_at']).dt.days
        
        print(f"✅ Metadata added")
        
    def save_cleaned_data(self, filename='cleaned_jobs.csv'):
        """Save cleaned dataset"""
        print("\n" + "="*60)
        print("💾 SAVING CLEANED DATA")
        print("="*60)
        
        filepath = r'C:\Users\Bittu\Desktop\Job_Market_Intelligence\data\processed\\' + filename
        self.df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        print(f"✅ Cleaned data saved to: {filepath}")
        print(f"📊 Total records: {len(self.df)}")
        print(f"📋 Total columns: {len(self.df.columns)}")
        
        return filepath
    
    def generate_summary_report(self):
        """Generate summary report"""
        print("\n" + "="*60)
        print("📊 CLEANING SUMMARY REPORT")
        print("="*60)
        
        print(f"\n✅ Total Jobs Cleaned: {len(self.df)}")
        print(f"\n📋 New Columns Created:")
        new_columns = [
            'job_title_clean', 'company_name_clean', 
            'salary_min_lpa', 'salary_max_lpa', 'salary_avg_lpa',
            'exp_min_years', 'exp_max_years', 'experience_level',
            'primary_city', 'is_remote', 'is_hybrid',
            'total_skills_mentioned'
        ]
        for col in new_columns:
            if col in self.df.columns:
                print(f"   ✓ {col}")
        
        print(f"\n📊 Data Quality:")
        print(f"   Complete records: {self.df.dropna().shape[0]}")
        print(f"   Records with salary: {self.df['salary_avg_lpa'].notna().sum()}")
        print(f"   Records with experience: {self.df['exp_min_years'].notna().sum()}")
        
        print("\n" + "="*60)


# MAIN EXECUTION
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 JOB DATA CLEANING")
    print("="*60)
    
    cleaner = DataCleaner()
    
    # Load data
    cleaner.load_data()
    
    # Clean each aspect
    cleaner.clean_job_titles()
    cleaner.clean_company_names()
    cleaner.extract_salary_info()
    cleaner.extract_experience()
    cleaner.clean_locations()
    cleaner.extract_skills()
    cleaner.add_metadata()
    
    # Save cleaned data
    cleaner.save_cleaned_data()
    
    # Generate report
    cleaner.generate_summary_report()
    
    print("\n" + "="*60)
    print("✅ DATA CLEANING COMPLETE!")
    print("="*60)
    print("\n📁 Next step: Analysis & Insights")