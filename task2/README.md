# Financial Analysis Chatbot Documentation

## Overview
The Financial Analysis Chatbot is a Flask-based application that analyzes financial data for companies and provides insights through natural language queries. It supports both custom data upload (CSV/JSON) and includes a sample dataset featuring Apple, Microsoft, and Tesla.

## Data Requirements
The input data must contain the following columns:
- Company (company names)
- Year (fiscal years)
- Total Revenue
- Net Income
- Total Assets
- Total Liabilities
- Cash Flow from Operating Activities

## Supported Queries

### 1. Company Comparison
- Query: "Compare companies"
- Returns a comparison of all companies' profit margins, asset turnover, and operating cash flow

### 2. Growth Analysis
- Query: "What is [Company]'s growth?"
- Example: "What is Apple's growth?"
- Returns revenue growth analysis including:
  - Average revenue growth
  - Growth range (min/max)
  - Trend assessment

### 3. Profitability Analysis
- Query: "Show [Company]'s profit margins"
- Example: "Show Microsoft's profit margins"
- Provides:
  - Average profit margin
  - Range of profit margins
  - Performance assessment

### 4. Risk Assessment
- Query: "What is [Company]'s risk profile?"
- Example: "What is Tesla's risk profile?"
- Analyzes company risk factors

### 5. Industry Trends
- Query: "Show industry trends"
- Provides:
  - Latest industry revenue
  - Year-over-year growth
  - Operating cash flow trends

### 6. Financial Health
- Query: "How is [Company]'s financial health?"
- Example: "How is Apple's financial health?"
- Returns:
  - Operational efficiency
  - Profitability metrics
  - Cash flow strength
  - Overall financial assessment

## Usage Instructions

1. **Data Loading**:
   - Click "Use Sample Data" to use pre-loaded data, OR
   - Upload your own CSV/JSON file with the required columns

2. **Querying**:
   - Type your query in the input box
   - Use the predefined query formats listed above
   - Type "help" to see available commands

## Limitations
1. Only supports CSV and JSON file formats
2. Maximum file size: 16MB
3. Requires specific column names as listed above
4. Limited to predefined query patterns
5. Financial metrics are calculated using basic formulas
6. Historical analysis limited to available years in dataset

## Error Handling
- Provides feedback for invalid file formats
- Returns error messages for missing data
- Validates data structure before processing
- Handles query processing errors gracefully
