import pandas as pd
import os
from datetime import datetime

class DataCombiner:
    def __init__(self):
        self.raw_data_path =  r'C:\Users\Bittu\Desktop\Job_Market_Intelligence\data\raw\\'
        self.processed_data_path = r'C:\Users\Bittu\Desktop\Job_Market_Intelligence\data\processed\\'
        self.combined_df = None
        
    def load_datasets(self):
        """Load all CSV files from raw data folder"""
        print("="*60)
        print("📂 LOADING DATASETS")
        print("="*60)
        
        datasets = []
        
        # Load Naukri data
        try:
            naukri_file = os.path.join(self.raw_data_path, 'naukri_jobs_selenium.csv')
            if os.path.exists(naukri_file):
                naukri_df = pd.read_csv(naukri_file)
                print(f"✅ Naukri: {len(naukri_df)} jobs loaded")
                datasets.append(naukri_df)
            else:
                print("⚠️ Naukri file not found")
        except Exception as e:
            print(f"❌ Error loading Naukri: {str(e)}")
        
        # Load Indeed data
        try:
            indeed_file = os.path.join(self.raw_data_path, 'indeed_jobs.csv')
            if os.path.exists(indeed_file):
                indeed_df = pd.read_csv(indeed_file)
                print(f"✅ Indeed: {len(indeed_df)} jobs loaded")
                datasets.append(indeed_df)
            else:
                print("⚠️ Indeed file not found")
        except Exception as e:
            print(f"❌ Error loading Indeed: {str(e)}")
        
        return datasets
    
    def combine_datasets(self, datasets):
        """Combine all datasets into one"""
        print("\n" + "="*60)
        print("🔗 COMBINING DATASETS")
        print("="*60)
        
        if not datasets:
            print("❌ No datasets to combine!")
            return None
        
        # Combine all dataframes
        self.combined_df = pd.concat(datasets, ignore_index=True)
        
        print(f"✅ Combined dataset: {len(self.combined_df)} total jobs")
        print(f"\n📊 Jobs by source:")
        print(self.combined_df['source'].value_counts())
        
        return self.combined_df
    
    def remove_duplicates(self):
        """Remove duplicate job postings"""
        print("\n" + "="*60)
        print("🗑️ REMOVING DUPLICATES")
        print("="*60)
        
        initial_count = len(self.combined_df)
        
        # Remove duplicates based on job_title + company_name
        self.combined_df = self.combined_df.drop_duplicates(
            subset=['job_title', 'company_name'], 
            keep='first'
        )
        
        duplicates_removed = initial_count - len(self.combined_df)
        
        print(f"📊 Initial jobs: {initial_count}")
        print(f"🗑️ Duplicates removed: {duplicates_removed}")
        print(f"✅ Unique jobs remaining: {len(self.combined_df)}")
        
        return self.combined_df
    
    def basic_info(self):
        """Display basic information about combined dataset"""
        print("\n" + "="*60)
        print("📊 COMBINED DATASET OVERVIEW")
        print("="*60)
        
        print(f"\n📈 Total Records: {len(self.combined_df)}")
        print(f"\n📋 Columns: {list(self.combined_df.columns)}")
        
        print(f"\n🏢 Top 15 Companies Hiring:")
        print(self.combined_df['company_name'].value_counts().head(15))
        
        print(f"\n📍 Top 10 Locations:")
        print(self.combined_df['location'].value_counts().head(10))
        
        print(f"\n🔍 Jobs by Keyword:")
        print(self.combined_df['search_keyword'].value_counts())
        
        print(f"\n💰 Salary Disclosure:")
        salary_disclosed = self.combined_df[
            (self.combined_df['salary'] != 'Not Disclosed') & 
            (self.combined_df['salary'] != 'N/A')
        ].shape[0]
        print(f"Disclosed: {salary_disclosed} ({salary_disclosed/len(self.combined_df)*100:.1f}%)")
        print(f"Not Disclosed: {len(self.combined_df) - salary_disclosed} ({(len(self.combined_df)-salary_disclosed)/len(self.combined_df)*100:.1f}%)")
        
        print(f"\n📊 Missing Values:")
        missing = self.combined_df.isnull().sum()
        print(missing[missing > 0])
        
    def save_combined_data(self, filename='combined_jobs.csv'):
        """Save combined dataset"""
        print("\n" + "="*60)
        print("💾 SAVING COMBINED DATA")
        print("="*60)
        
        # Create processed folder if doesn't exist
        os.makedirs(self.processed_data_path, exist_ok=True)
        
        filepath = os.path.join(self.processed_data_path, filename)
        self.combined_df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        print(f"✅ Data saved to: {filepath}")
        print(f"📊 Total records: {len(self.combined_df)}")
        
        return filepath


# MAIN EXECUTION
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 JOB DATA COMBINER")
    print("="*60)
    
    combiner = DataCombiner()
    
    # Load datasets
    datasets = combiner.load_datasets()
    
    if datasets:
        # Combine
        combined_df = combiner.combine_datasets(datasets)
        
        if combined_df is not None:
            # Remove duplicates
            combiner.remove_duplicates()
            
            # Show info
            combiner.basic_info()
            
            # Save
            combiner.save_combined_data()
            
            print("\n" + "="*60)
            print("✅ DATA COMBINATION COMPLETE!")
            print("="*60)
            print("\n📁 Next step: Run data cleaning script")
            print("   Command: python analysis\\data_cleaning.py")
        else:
            print("\n❌ Failed to combine datasets")
    else:
        print("\n❌ No datasets found to combine")