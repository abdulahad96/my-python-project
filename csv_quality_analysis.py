#!/usr/bin/env python3
"""
CSV Data Quality Analysis Task
For Abdul Ahad at Dpl

Goal: Load CSV into pandas and check for issues
Focus: Data quality assessment and parsing analysis
"""

import pandas as pd
import numpy as np
import re
from helper_functions import print_llm_response

def analyze_csv_issues():
    """Main function to analyze CSV data quality issues"""
    
    print("🔍 CSV Data Quality Analysis")
    print("=" * 50)
    print("For Abdul Ahad at Dpl")
    print("=" * 50)
    
    # STEP 1: Load CSV with pd.read_csv
    print("\n📊 STEP 1: Loading CSV with pd.read_csv")
    print("-" * 40)
    
    try:
        df = pd.read_csv('data.csv')
        print_llm_response({
            "Status": "CSV loaded successfully",
            "Shape": f"{df.shape[0]} rows × {df.shape[1]} columns",
            "File Size": f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB"
        }, "CSV Loading Results")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return None
    
    # STEP 2: Inspect with .info() and .head()
    print("\n🔍 STEP 2: Basic Inspection")
    print("-" * 40)
    
    print("📋 Dataset Info:")
    df.info()
    
    print("\n📋 First 5 rows:")
    print(df.head())
    
    # STEP 3: Check for specific issues
    print("\n🚨 STEP 3: Data Quality Issues Analysis")
    print("-" * 40)
    
    # Check years_experience for text values
    print("🔍 Years Experience Issues:")
    years_text = df[df['years_experience'].str.contains('[a-zA-Z+]', na=False)]['years_experience'].unique()
    years_issues = {
        "Text Values Found": list(years_text),
        "Count of Text Values": len(years_text),
        "Sample Text Values": list(years_text[:5]) if len(years_text) > 0 else []
    }
    print_llm_response(years_issues, "Years Experience Text Issues")
    
    # Check hourly_rate for currency symbols
    print("\n💰 Hourly Rate Issues:")
    rate_currency = df[df['hourly_rate'].str.contains(r'[$PKR]', na=False)]['hourly_rate'].unique()
    rate_issues = {
        "Currency Symbols Found": list(rate_currency),
        "Count of Currency Values": len(rate_currency),
        "Sample Currency Values": list(rate_currency[:5]) if len(rate_currency) > 0 else []
    }
    print_llm_response(rate_issues, "Hourly Rate Currency Issues")
    
    # Check rating for blanks and out-of-range values
    print("\n⭐ Rating Issues:")
    rating_issues = {
        "Blank/Null Values": df['rating'].isnull().sum(),
        "Out of Range (>5)": len(df[df['rating'] > 5.0]),
        "Out of Range (<1)": len(df[df['rating'] < 1.0]),
        "Valid Range Count": len(df[(df['rating'] >= 1.0) & (df['rating'] <= 5.0)]),
        "Rating Range": f"{df['rating'].min()} - {df['rating'].max()}"
    }
    print_llm_response(rating_issues, "Rating Quality Issues")
    
    # Check subjects for inconsistent casing/spaces
    print("\n📚 Subjects Issues:")
    subjects_sample = df['subjects'].dropna().head(10)
    subjects_issues = {
        "Sample Subjects": subjects_sample.tolist(),
        "Mixed Case Examples": df[df['subjects'].str.contains(r'[A-Z].*[a-z]|[a-z].*[A-Z]', na=False)]['subjects'].unique()[:5].tolist(),
        "Extra Spaces Examples": df[df['subjects'].str.contains(r'\s{2,}', na=False)]['subjects'].unique()[:5].tolist(),
        "Null Values": df['subjects'].isnull().sum()
    }
    print_llm_response(subjects_issues, "Subjects Formatting Issues")
    
    # STEP 4: Apply cleaning methods as suggested
    print("\n🧹 STEP 4: Applying Cleaning Methods")
    print("-" * 40)
    
    df_clean = df.copy()
    
    # Clean years_experience using pd.to_numeric with errors='coerce'
    print("1. Cleaning years_experience with pd.to_numeric(errors='coerce')...")
    
    def clean_years_text(exp):
        """Clean text values in years_experience before numeric conversion"""
        if pd.isna(exp):
            return exp
        
        exp_str = str(exp).lower().strip()
        
        # Handle text-to-number mapping
        text_to_num = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            '—': np.nan
        }
        
        if exp_str in text_to_num:
            return text_to_num[exp_str]
        
        # Handle "X+" patterns
        if '+' in exp_str:
            return int(exp_str.replace('+', ''))
        
        # Handle "X years" patterns
        if 'year' in exp_str:
            return int(exp_str.split()[0])
        
        return exp
    
    # Apply text cleaning first
    df_clean['years_experience'] = df_clean['years_experience'].apply(clean_years_text)
    
    # Then use pd.to_numeric with errors='coerce'
    df_clean['years_experience'] = pd.to_numeric(df_clean['years_experience'], errors='coerce')
    
    # Clean hourly_rate using .str.replace for symbols
    print("2. Cleaning hourly_rate with .str.replace...")
    
    def clean_rate_symbols(rate):
        """Clean currency symbols from hourly_rate"""
        if pd.isna(rate) or str(rate).strip() in ['N/A', '']:
            return np.nan
        
        rate_str = str(rate).strip()
        
        # Remove currency symbols using .str.replace
        rate_str = rate_str.replace('PKR', '').replace('$', '').replace(',', '').replace(' ', '')
        
        # Handle USD conversion
        if 'usd' in rate_str.lower():
            rate_str = rate_str.lower().replace('usd', '')
            try:
                return float(rate_str) * 280  # Convert USD to PKR
            except:
                return np.nan
        
        try:
            return float(rate_str)
        except:
            return np.nan
    
    df_clean['hourly_rate'] = df_clean['hourly_rate'].apply(clean_rate_symbols)
    df_clean['hourly_rate'] = pd.to_numeric(df_clean['hourly_rate'], errors='coerce')
    
    # Clean subjects using .str.strip().str.lower()
    print("3. Cleaning subjects with .str.strip().str.lower()...")
    df_clean['subjects'] = df_clean['subjects'].str.strip().str.lower()
    
    # Clean rating - clip out-of-range values
    print("4. Cleaning rating - clipping out-of-range values...")
    df_clean['rating'] = df_clean['rating'].clip(lower=1.0, upper=5.0)
    
    # STEP 5: Analyze parsing results
    print("\n📊 STEP 5: Parsing Results Analysis")
    print("-" * 40)
    
    # Calculate parsing success rates
    original_rows = len(df)
    
    # Years experience parsing
    years_parsed = df_clean['years_experience'].notna().sum()
    years_failed = original_rows - years_parsed
    years_success_rate = (years_parsed / original_rows) * 100
    
    # Hourly rate parsing
    rate_parsed = df_clean['hourly_rate'].notna().sum()
    rate_failed = original_rows - rate_parsed
    rate_success_rate = (rate_parsed / original_rows) * 100
    
    # Rating parsing
    rating_valid = df_clean['rating'].notna().sum()
    rating_failed = original_rows - rating_valid
    rating_success_rate = (rating_valid / original_rows) * 100
    
    parsing_results = {
        "Total Rows": original_rows,
        "Years Experience": {
            "Successfully Parsed": years_parsed,
            "Failed Parsing": years_failed,
            "Success Rate": f"{years_success_rate:.1f}%"
        },
        "Hourly Rate": {
            "Successfully Parsed": rate_parsed,
            "Failed Parsing": rate_failed,
            "Success Rate": f"{rate_success_rate:.1f}%"
        },
        "Rating": {
            "Valid Values": rating_valid,
            "Invalid/Null": rating_failed,
            "Success Rate": f"{rating_success_rate:.1f}%"
        }
    }
    
    print_llm_response(parsing_results, "Parsing Success Analysis")
    
    # STEP 6: Reflection and Recommendations
    print("\n🤔 STEP 6: Reflection and Recommendations")
    print("-" * 40)
    
    # Calculate overall parsing failure rate
    total_failures = years_failed + rate_failed + rating_failed
    overall_failure_rate = (total_failures / (original_rows * 3)) * 100
    
    reflection = {
        "Overall Parsing Failure Rate": f"{overall_failure_rate:.1f}%",
        "Recommendation": "Coerce rather than drop" if overall_failure_rate < 20 else "Consider dropping bad rows",
        "Reasoning": [
            f"Years experience: {years_success_rate:.1f}% success rate",
            f"Hourly rate: {rate_success_rate:.1f}% success rate", 
            f"Rating: {rating_success_rate:.1f}% success rate",
            f"Total failure rate: {overall_failure_rate:.1f}%"
        ]
    }
    
    print_llm_response(reflection, "Parsing Strategy Recommendation")
    
    # Show sample of cleaned data
    print("\n✅ Sample of Cleaned Data:")
    sample_cleaned = df_clean[['tutor_id', 'name', 'years_experience', 'hourly_rate', 'rating', 'subjects']].head()
    print(sample_cleaned)
    
    # Save cleaned data
    df_clean.to_csv('data_cleaned_analysis.csv', index=False)
    print_llm_response("Cleaned data saved to 'data_cleaned_analysis.csv'", "File Saved")
    
    return df_clean

if __name__ == "__main__":
    print("🚀 Starting CSV Data Quality Analysis...")
    cleaned_data = analyze_csv_issues()
    
    if cleaned_data is not None:
        print("\n" + "="*50)
        print("🎯 ANALYSIS COMPLETE!")
        print("📊 Data quality issues identified and cleaned")
        print("📁 Cleaned data saved to CSV")
        print("="*50)
    else:
        print("\n❌ Analysis failed - check error messages above")
