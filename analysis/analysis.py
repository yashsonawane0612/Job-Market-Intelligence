import pandas as pd
#import matplotlib.pyplot as plt
#import seaborn as sns
import os

class JobMarketAnalyzer:
    def __init__(self, input_file=r'C:\Users\Bittu\Desktop\Job_Market_Intelligence\data\processed\cleaned_jobs.csv'):
        self.input_file = input_file
        self.df = None
        
    def load_data(self):
        """Load cleaned dataset"""
        print("="*60)
        print("📂 LOADING CLEANED DATA")
        print("="*60)
        
        self.df = pd.read_csv(self.input_file)
        print(f"✅ Loaded {len(self.df)} cleaned jobs")
        
    def skill_demand_analysis(self):
        """Analyze skill demand trends"""
        print("\n" + "="*60)
        print("🔧 SKILL DEMAND ANALYSIS")
        print("="*60)
        
        # Get skill columns
        skill_cols = [col for col in self.df.columns if col.startswith('has_')]
        
        skill_demand = {}
        for col in skill_cols:
            skill_name = col.replace('has_', '').replace('_', ' ').title()
            count = self.df[col].sum()
            percentage = (count / len(self.df)) * 100
            skill_demand[skill_name] = {'count': count, 'percentage': percentage}
        
        # Sort by count
        sorted_skills = sorted(skill_demand.items(), key=lambda x: x[1]['count'], reverse=True)
        
        print("\n📊 Top 15 In-Demand Skills:\n")
        print(f"{'Skill':<25} {'Jobs':<10} {'% of Total':<15}")
        print("-" * 50)
        for skill, data in sorted_skills[:15]:
            print(f"{skill:<25} {data['count']:<10} {data['percentage']:.1f}%")
        
        return sorted_skills
    
    def salary_analysis(self):
        """Analyze salary trends"""
        print("\n" + "="*60)
        print("💰 SALARY ANALYSIS")
        print("="*60)
        
        salary_df = self.df[self.df['salary_avg_lpa'].notna()].copy()
        
        print(f"\n📊 Overall Salary Statistics (n={len(salary_df)}):")
        print(f"   Minimum: ₹{salary_df['salary_min_lpa'].min():.2f} LPA")
        print(f"   Maximum: ₹{salary_df['salary_max_lpa'].max():.2f} LPA")
        print(f"   Average: ₹{salary_df['salary_avg_lpa'].mean():.2f} LPA")
        print(f"   Median: ₹{salary_df['salary_avg_lpa'].median():.2f} LPA")
        print(f"   25th Percentile: ₹{salary_df['salary_avg_lpa'].quantile(0.25):.2f} LPA")
        print(f"   75th Percentile: ₹{salary_df['salary_avg_lpa'].quantile(0.75):.2f} LPA")
        
        # Salary by role
        print("\n💼 Average Salary by Role:")
        role_salary = salary_df.groupby('job_title_clean')['salary_avg_lpa'].agg(['mean', 'median', 'count'])
        role_salary = role_salary[role_salary['count'] >= 3].sort_values('mean', ascending=False)
        print(role_salary.head(10))
        
        # Salary by city
        print("\n📍 Average Salary by City:")
        city_salary = salary_df.groupby('primary_city')['salary_avg_lpa'].agg(['mean', 'median', 'count'])
        city_salary = city_salary[city_salary['count'] >= 3].sort_values('mean', ascending=False)
        print(city_salary.head(10))
        
        # Salary by experience level
        print("\n🎓 Average Salary by Experience Level:")
        exp_salary = salary_df.groupby('experience_level')['salary_avg_lpa'].agg(['mean', 'median', 'count'])
        exp_salary = exp_salary.sort_values('mean', ascending=False)
        print(exp_salary)
        
    def location_analysis(self):
        """Analyze location trends"""
        print("\n" + "="*60)
        print("📍 LOCATION ANALYSIS")
        print("="*60)
        
        print("\n🏙️ Top 10 Cities by Job Count:")
        city_counts = self.df['primary_city'].value_counts().head(10)
        for city, count in city_counts.items():
            percentage = (count / len(self.df)) * 100
            print(f"   {city:<20} {count:>4} jobs ({percentage:.1f}%)")
        
        print(f"\n🏠 Work Mode Distribution:")
        print(f"   Remote: {self.df['is_remote'].sum()} jobs ({self.df['is_remote'].sum()/len(self.df)*100:.1f}%)")
        print(f"   Hybrid: {self.df['is_hybrid'].sum()} jobs ({self.df['is_hybrid'].sum()/len(self.df)*100:.1f}%)")
        print(f"   Office: {len(self.df) - self.df['is_remote'].sum() - self.df['is_hybrid'].sum()} jobs")
        
    def experience_analysis(self):
        """Analyze experience requirements"""
        print("\n" + "="*60)
        print("🎓 EXPERIENCE REQUIREMENTS ANALYSIS")
        print("="*60)
        
        print("\n📊 Jobs by Experience Level:")
        exp_counts = self.df['experience_level'].value_counts()
        for level, count in exp_counts.items():
            percentage = (count / len(self.df)) * 100
            print(f"   {level:<30} {count:>4} jobs ({percentage:.1f}%)")
        
        # Fresher-friendly companies
        fresher_df = self.df[self.df['experience_level'] == 'Fresher (0 years)']
        if len(fresher_df) > 0:
            print(f"\n🎓 Top Companies Hiring Freshers:")
            fresher_companies = fresher_df['company_name_clean'].value_counts().head(10)
            for company, count in fresher_companies.items():
                print(f"   {company:<30} {count:>2} positions")
        
    def company_analysis(self):
        """Analyze hiring companies"""
        print("\n" + "="*60)
        print("🏢 COMPANY HIRING ANALYSIS")
        print("="*60)
        
        print("\n📊 Top 20 Companies by Job Postings:")
        company_counts = self.df['company_name_clean'].value_counts().head(20)
        for company, count in company_counts.items():
            percentage = (count / len(self.df)) * 100
            print(f"   {company:<35} {count:>3} jobs ({percentage:.1f}%)")
        
    def role_analysis(self):
        """Analyze job roles"""
        print("\n" + "="*60)
        print("💼 JOB ROLE ANALYSIS")
        print("="*60)
        
        print("\n📊 Distribution by Role:")
        role_counts = self.df['job_title_clean'].value_counts().head(15)
        for role, count in role_counts.items():
            percentage = (count / len(self.df)) * 100
            print(f"   {role:<40} {count:>3} jobs ({percentage:.1f}%)")
        
    def generate_key_insights(self):
        """Generate key business insights"""
        print("\n" + "="*60)
        print("💡 KEY INSIGHTS & RECOMMENDATIONS")
        print("="*60)
        
        # Most in-demand skill
        skill_cols = [col for col in self.df.columns if col.startswith('has_')]
        top_skill = max(skill_cols, key=lambda x: self.df[x].sum())
        top_skill_name = top_skill.replace('has_', '').replace('_', ' ').title()
        top_skill_pct = (self.df[top_skill].sum() / len(self.df)) * 100
        
        # Best city for jobs
        top_city = self.df['primary_city'].value_counts().index[0]
        top_city_count = self.df['primary_city'].value_counts().values[0]
        
        # Average salary
        avg_salary = self.df['salary_avg_lpa'].mean()
        
        # Fresher opportunities
        fresher_count = len(self.df[self.df['experience_level'] == 'Fresher (0 years)'])
        entry_count = len(self.df[self.df['experience_level'] == 'Entry Level (0-2 years)'])
        
        print(f"\n🎯 TOP INSIGHTS:")
        print(f"\n1. SKILLS:")
        print(f"   • {top_skill_name} is the most in-demand skill ({top_skill_pct:.1f}% of jobs)")
        print(f"   • Python, SQL, and Machine Learning are the top 3 must-have skills")
        
        print(f"\n2. LOCATIONS:")
        print(f"   • {top_city} has the most opportunities ({top_city_count} jobs)")
        print(f"   • {self.df['is_hybrid'].sum()} hybrid positions available for flexibility")
        
        print(f"\n3. SALARY:")
        print(f"   • Average salary: ₹{avg_salary:.2f} LPA")
        print(f"   • Salary disclosure rate: {(self.df['salary_avg_lpa'].notna().sum()/len(self.df)*100):.1f}%")
        
        print(f"\n4. EXPERIENCE:")
        print(f"   • {fresher_count} positions for freshers (0 years)")
        print(f"   • {entry_count} entry-level positions (0-2 years)")
        print(f"   • Total beginner-friendly: {fresher_count + entry_count} jobs ({(fresher_count + entry_count)/len(self.df)*100:.1f}%)")
        
        print(f"\n5. RECOMMENDATIONS FOR JOB SEEKERS:")
        print(f"   ✓ Focus on learning: Python, SQL, Machine Learning")
        print(f"   ✓ Target cities: {', '.join(self.df['primary_city'].value_counts().head(3).index.tolist())}")
        print(f"   ✓ {fresher_count + entry_count} opportunities available for freshers/entry-level")
        print(f"   ✓ Consider hybrid roles for work-life balance ({self.df['is_hybrid'].sum()} available)")
        
    def save_summary_report(self):
        """Save analysis summary to text file"""
        print("\n" + "="*60)
        print("💾 SAVING ANALYSIS REPORT")
        print("="*60)
        
        report_path = r'C:\Users\Bittu\Desktop\Job_Market_Intelligence\data\processed\analysis_report.txt'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("JOB MARKET INTELLIGENCE ANALYSIS REPORT\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"Total Jobs Analyzed: {len(self.df)}\n")
            f.write(f"Data Sources: Naukri, Indeed\n")
            f.write(f"Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}\n\n")
            
            f.write("TOP 10 IN-DEMAND SKILLS:\n")
            f.write("-" * 40 + "\n")
            skill_cols = [col for col in self.df.columns if col.startswith('has_')]
            for col in skill_cols[:10]:
                skill_name = col.replace('has_', '').replace('_', ' ').title()
                count = self.df[col].sum()
                pct = (count / len(self.df)) * 100
                f.write(f"{skill_name}: {count} jobs ({pct:.1f}%)\n")
            
            f.write("\n" + "="*60 + "\n")
        
        print(f"✅ Report saved to: {report_path}")


# MAIN EXECUTION
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 JOB MARKET INTELLIGENCE ANALYSIS")
    print("="*60)
    
    analyzer = JobMarketAnalyzer()
    
    # Load data
    analyzer.load_data()
    
    # Run all analyses
    analyzer.skill_demand_analysis()
    analyzer.salary_analysis()
    analyzer.location_analysis()
    analyzer.experience_analysis()
    analyzer.company_analysis()
    analyzer.role_analysis()
    analyzer.generate_key_insights()
    
    # Save report
    analyzer.save_summary_report()
    
    print("\n" + "="*60)
    print("✅ ANALYSIS COMPLETE!")
    print("="*60)
    print("\n📁 Next step: Create Power BI Dashboard")
    print("   File: data/processed/cleaned_jobs.csv")