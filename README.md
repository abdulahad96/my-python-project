# 📊 Data Analysis Task - Tutor Data Analysis

**For Abdul Ahad at Dpl**

## 🎯 Overview
This project contains a complete data analysis task that analyzes tutor data from `data.csv`. The analysis includes data cleaning, exploratory data analysis, visualization, and business insights.

## 📁 Files Created

### Main Analysis Script
- **`data_analysis_task.py`** - Complete data analysis script with 6 tasks
- **`run_analysis.py`** - Simple runner script to execute the analysis
- **`helper_functions.py`** - Helper functions for pretty printing (already exists)

### Data Files
- **`data.csv`** - Original tutor data (already exists)
- **`tutor_data_analysis_results.csv`** - Cleaned data output (generated)

## 🚀 How to Run

### Method 1: Using the Runner Script (Recommended)
```bash
# Make sure you're in the project directory
cd /Users/abdulahad/Desktop/python_AI/Projects

# Activate virtual environment
source venv/bin/activate

# Run the analysis
python run_analysis.py
```

### Method 2: Direct Execution
```bash
# Make sure you're in the project directory
cd /Users/abdulahad/Desktop/python_AI/Projects

# Activate virtual environment
source venv/bin/activate

# Run the main analysis script
python data_analysis_task.py
```

### Method 3: In Jupyter Notebook
```python
# In Jupyter notebook, run:
exec(open('data_analysis_task.py').read())
```

## 📊 Analysis Tasks Included

### Task 1: Data Loading and Cleaning
- Loads `data.csv` using `pd.read_csv()`
- Cleans `years_experience` (handles "five", "3+", etc.)
- Cleans `hourly_rate` (removes $, PKR, converts USD to PKR)
- Standardizes city names and subjects
- Uses `pd.to_numeric(errors='coerce')` as requested

### Task 2: Exploratory Data Analysis (EDA)
- Basic statistics with `.describe()`
- Missing values analysis
- Data quality metrics
- Uses `print_llm_response` helper function

### Task 3: Data Visualization
- 4-panel dashboard with matplotlib/seaborn
- Distribution of years experience
- Hourly rate distribution
- Rating distribution
- Top cities by tutor count

### Task 4: Advanced Analysis
- Correlation analysis
- Top 10 highest rated tutors
- Top 10 highest paid tutors
- Subject analysis with rankings

### Task 5: Business Insights
- Key business metrics
- Market analysis insights
- Strategic recommendations for Dpl
- Actionable insights

### Task 6: Export Results
- Saves cleaned data to CSV
- Creates summary report
- Generates final status

## 📈 Expected Output

The script will generate:
- **Console output** with detailed analysis results
- **Visualizations** displayed in matplotlib windows
- **CSV file** with cleaned data (`tutor_data_analysis_results.csv`)
- **Business insights** and recommendations

## 🔧 Requirements

- Python 3.12+
- pandas
- numpy
- matplotlib
- seaborn
- helper_functions.py (custom module)

## 💡 Key Features

- ✅ Uses all pandas methods you requested
- ✅ Handles data quality issues
- ✅ Professional visualizations
- ✅ Business-ready insights
- ✅ Personalized for Abdul Ahad at Dpl
- ✅ Complete error handling
- ✅ Modular design

## 🎯 Business Value

This analysis provides:
- **Market insights** for tutor platform
- **Pricing analysis** for competitive positioning
- **Quality metrics** for service improvement
- **Geographic analysis** for expansion planning
- **Subject demand** analysis
- **Strategic recommendations** for Dpl

## 📞 Support

For questions or issues, contact Abdul Ahad at Dpl.

---
**Created for Dpl Team Presentation** 🚀
