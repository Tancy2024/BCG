from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store chatbot instance globally
chatbot_instance = None

class FinancialChatbot:
    def __init__(self, data_path, file_type='csv'):
        """Initialize chatbot with data from a file"""
        self.data = self._load_data(data_path, file_type)
        if self.data is not None:
            self.company_metrics = self._calculate_metrics()
            self.industry_trends = self._calculate_industry_trends()
        else:
            raise ValueError("Failed to load data")

    def _load_data(self, data_path, file_type):
        """Load data from CSV or JSON file"""
        try:
            if file_type.lower() == 'csv':
                return pd.read_csv(data_path)
            elif file_type.lower() == 'json':
                return pd.read_json(data_path)
            else:
                raise ValueError("Unsupported file type. Use 'csv' or 'json'.")
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return None

    def _calculate_metrics(self):
        """Calculate financial metrics for each company"""
        metrics = {}
        
        for company in self.data['Company'].unique():
            company_data = self.data[self.data['Company'] == company]
            
            # Calculate growth rates
            revenue_growth = company_data['Total Revenue'].pct_change() * 100
            
            # Calculate other metrics
            profit_margin = (company_data['Net Income'] / company_data['Total Revenue'] * 100)
            asset_turnover = company_data['Total Revenue'] / company_data['Total Assets']
            debt_ratio = (company_data['Total Liabilities'] / company_data['Total Assets'] * 100)
            operating_cash_flow = (company_data['Cash Flow from Operating Activities'] / 
                                 company_data['Total Revenue'] * 100)
            
            metrics[company] = {
                'revenue_growth': {
                    'mean': revenue_growth.mean(),
                    'min': revenue_growth.min(),
                    'max': revenue_growth.max()
                },
                'profit_margin': {
                    'mean': profit_margin.mean(),
                    'min': profit_margin.min(),
                    'max': profit_margin.max()
                },
                'asset_turnover': {
                    'mean': asset_turnover.mean(),
                    'min': asset_turnover.min(),
                    'max': asset_turnover.max()
                },
                'debt_ratio': {
                    'mean': debt_ratio.mean(),
                    'min': debt_ratio.min(),
                    'max': debt_ratio.max()
                },
                'operating_cash_flow': {
                    'mean': operating_cash_flow.mean(),
                    'min': operating_cash_flow.min(),
                    'max': operating_cash_flow.max()
                }
            }
        return metrics

    def _calculate_industry_trends(self):
        """Calculate industry-wide trends by year"""
        trends = {}
        yearly_data = self.data.groupby('Year').agg({
            'Total Revenue': 'sum',
            'Net Income': 'sum',
            'Cash Flow from Operating Activities': 'sum'
        })
        
        for year in yearly_data.index:
            trends[str(year)] = {
                'revenue': yearly_data.loc[year, 'Total Revenue'],
                'net_income': yearly_data.loc[year, 'Net Income'],
                'operating_cash_flow': yearly_data.loc[year, 'Cash Flow from Operating Activities']
            }
        return trends

    def process_query(self, query):
        """Process user queries and return appropriate responses"""
        query = query.lower().strip()
        
        if query == 'help':
            return self._get_help_message()
            
        if "compare" in query and "companies" in query:
            return self.compare_companies()
        
        for company in self.company_metrics.keys():
            if company.lower() in query:
                if "growth" in query:
                    return self.get_growth_analysis(company)
                elif "profit" in query or "margin" in query:
                    return self.get_profitability_analysis(company)
                elif "risk" in query:
                    return self.get_risk_analysis(company)
                elif "financial health" in query or "performance" in query:
                    return self.get_financial_health(company)
        
        if "industry" in query and "trend" in query:
            return self.get_industry_trends()
        
        return self._get_help_message()

    def _get_help_message(self):
        """Return help message with available commands"""
        return ("I can help you with:\n"
                "1. Company comparisons (e.g., 'Compare companies')\n"
                "2. Growth analysis (e.g., 'What is Apple's growth?')\n"
                "3. Profitability analysis (e.g., 'Show Microsoft's profit margins')\n"
                "4. Risk assessment (e.g., 'What is Tesla's risk profile?')\n"
                "5. Industry trends (e.g., 'Show industry trends')\n"
                "6. Financial health (e.g., 'How is Apple's financial health?')")

    def compare_companies(self):
        """Generate a comprehensive comparison of all companies"""
        comparison = "Company Comparison:\n\n"
        
        for metric in ['profit_margin', 'asset_turnover', 'operating_cash_flow']:
            comparison += f"\n{metric.replace('_', ' ').title()}:\n"
            sorted_companies = sorted(self.company_metrics.items(), 
                                   key=lambda x: x[1][metric]['mean'],
                                   reverse=True)
            
            for company, metrics in sorted_companies:
                comparison += f"- {company}: {metrics[metric]['mean']:.2f}%\n"
        return comparison

    def get_growth_analysis(self, company):
        """Provide growth analysis for a specific company"""
        metrics = self.company_metrics[company]['revenue_growth']
        return (f"{company}'s Growth Analysis:\n"
                f"- Average revenue growth: {metrics['mean']:.2f}%\n"
                f"- Range: {metrics['min']:.2f}% to {metrics['max']:.2f}%\n"
                f"- Trend assessment: {self._assess_growth(metrics['mean'])}")

    def get_profitability_analysis(self, company):
        """Analyze profitability metrics for a specific company"""
        metrics = self.company_metrics[company]['profit_margin']
        return (f"{company}'s Profitability Analysis:\n"
                f"- Average profit margin: {metrics['mean']:.2f}%\n"
                f"- Range: {metrics['min']:.2f}% to {metrics['max']:.2f}%\n"
                f"- Performance: {self._assess_profitability(metrics['mean'])}")

    def get_industry_trends(self):
        """Analyze overall industry trends"""
        years = sorted(self.industry_trends.keys())
        latest_year = years[-1]
        prev_year = years[-2]
        
        revenue_growth = ((self.industry_trends[latest_year]['revenue'] / 
                          self.industry_trends[prev_year]['revenue'] - 1) * 100)
        
        return (f"Industry Trends Analysis:\n"
                f"- Latest revenue ({latest_year}): ${self.industry_trends[latest_year]['revenue']:,}\n"
                f"- Year-over-year growth: {revenue_growth:.1f}%\n"
                f"- Operating cash flow trend: "
                f"${self.industry_trends[latest_year]['operating_cash_flow']:,}")

    def get_financial_health(self, company):
        """Provide comprehensive financial health assessment"""
        metrics = self.company_metrics[company]
        
        return (f"{company}'s Financial Health Overview:\n"
                f"- Operational Efficiency: {metrics['asset_turnover']['mean']:.2f}x\n"
                f"- Profitability: {metrics['profit_margin']['mean']:.2f}%\n"
                f"- Cash Flow Strength: {metrics['operating_cash_flow']['mean']:.2f}%\n"
                f"- Overall Assessment: {self._assess_financial_health(metrics)}")

    def _assess_growth(self, growth):
        """Evaluate growth performance"""
        if growth > 5:
            return "Strong growth trajectory"
        elif growth > 0:
            return "Moderate growth"
        else:
            return "Challenging growth environment"

    def _assess_profitability(self, margin):
        """Evaluate profitability levels"""
        if margin > 30:
            return "Excellent profitability"
        elif margin > 20:
            return "Strong profitability"
        elif margin > 10:
            return "Moderate profitability"
        else:
            return "Below average profitability"

    def _assess_financial_health(self, metrics):
        """Provide overall financial health assessment"""
        score = 0
        score += 1 if metrics['profit_margin']['mean'] > 20 else 0
        score += 1 if metrics['asset_turnover']['mean'] > 0.8 else 0
        score += 1 if metrics['operating_cash_flow']['mean'] > 25 else 0
        
        if score == 3:
            return "Strong financial position"
        elif score == 2:
            return "Stable financial position"
        else:
            return "Mixed financial indicators"

@app.route('/')
def home():
    """Render the home page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file and file.filename.endswith(('.csv', '.json')):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Ensure the upload folder exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            # Save the file
            file.save(file_path)
            
            # Initialize chatbot with the uploaded file
            global chatbot_instance
            file_type = 'csv' if filename.endswith('.csv') else 'json'
            chatbot_instance = FinancialChatbot(file_path, file_type)
            
            return jsonify({'message': 'File uploaded successfully'})
        else:
            return jsonify({'error': 'Invalid file type. Please upload CSV or JSON file'}), 400
            
    except Exception as e:
        print(f"Upload error: {str(e)}")  # Server-side logging
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/query', methods=['POST'])
def process_query():
    """Process user queries"""
    if not chatbot_instance:
        return jsonify({'error': 'Please upload a data file first'}), 400
    
    data = request.json
    query = data.get('query', '')
    
    try:
        response = chatbot_instance.process_query(query)
        return jsonify({'response': response})
    except Exception as e:
        print(f"Query error: {str(e)}")  # Server-side logging
        return jsonify({'error': str(e)}), 500

@app.route('/sample', methods=['POST'])
def use_sample_data():
    """Initialize chatbot with sample data"""
    try:
        # Create sample data
        sample_data = pd.DataFrame({
            'Company': ['Apple', 'Microsoft', 'Tesla'] * 3,
            'Year': [2021, 2021, 2021, 2022, 2022, 2022, 2023, 2023, 2023],
            'Total Revenue': [365817, 168088, 53823, 394328, 198270, 81462, 383285, 211915, 96773],
            'Net Income': [94680, 61271, 5519, 99803, 72738, 12556, 96995, 67718, 14837],
            'Total Assets': [351002, 364840, 62131, 352755, 388588, 82338, 358547, 403162, 112237],
            'Total Liabilities': [287912, 185768, 30590, 290915, 193244, 36477, 287912, 195244, 45293],
            'Cash Flow from Operating Activities': [104038, 76740, 11497, 122151, 89035, 14724, 110543, 81869, 13285]
        })
        
        # Save sample data
        sample_file = os.path.join(app.config['UPLOAD_FOLDER'], 'sample_data.csv')
        sample_data.to_csv(sample_file, index=False)
        
        # Initialize chatbot with sample data
        global chatbot_instance
        chatbot_instance = FinancialChatbot(sample_file, 'csv')
        
        return jsonify({'message': 'Sample data loaded successfully'})
        
    except Exception as e:
        print(f"Sample data error: {str(e)}")  # Server-side logging
        return jsonify({'error': f'Failed to load sample data: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)