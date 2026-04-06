"""
Seed database with comprehensive Indian mutual funds, stocks, and more PMS/AIF.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.database import SessionLocal, init_db
from backend.db.models import FundData

MUTUAL_FUNDS = [
    # Large Cap MF
    {"fund_name":"SBI Bluechip Fund","fund_house":"SBI MF","category":"MF_LargeCap","strategy":"Large Cap","aum":45000,"min_investment":0.005,"returns_1y":18.5,"returns_3y":15.2,"returns_5y":14.8,"max_drawdown":12,"sharpe_ratio":1.1,"benchmark":"Nifty 100","benchmark_returns_1y":16.0,"alpha_1y":2.5,"fund_manager":"Saurabh Pant"},
    {"fund_name":"Mirae Asset Large Cap Fund","fund_house":"Mirae Asset MF","category":"MF_LargeCap","strategy":"Large Cap","aum":38000,"min_investment":0.005,"returns_1y":20.1,"returns_3y":16.5,"returns_5y":15.9,"max_drawdown":11,"sharpe_ratio":1.2,"benchmark":"Nifty 100","benchmark_returns_1y":16.0,"alpha_1y":4.1,"fund_manager":"Gaurav Misra"},
    {"fund_name":"ICICI Pru Bluechip Fund","fund_house":"ICICI Pru MF","category":"MF_LargeCap","strategy":"Large Cap","aum":52000,"min_investment":0.005,"returns_1y":19.2,"returns_3y":15.8,"returns_5y":15.1,"max_drawdown":10.5,"sharpe_ratio":1.15,"benchmark":"Nifty 100","benchmark_returns_1y":16.0,"alpha_1y":3.2,"fund_manager":"Anish Tawakley"},
    {"fund_name":"Axis Bluechip Fund","fund_house":"Axis MF","category":"MF_LargeCap","strategy":"Large Cap","aum":35000,"min_investment":0.005,"returns_1y":16.8,"returns_3y":13.5,"returns_5y":14.2,"max_drawdown":13,"sharpe_ratio":0.95,"benchmark":"Nifty 50","benchmark_returns_1y":15.5,"alpha_1y":1.3,"fund_manager":"Shreyash Devalkar"},
    {"fund_name":"Kotak Bluechip Fund","fund_house":"Kotak MF","category":"MF_LargeCap","strategy":"Large Cap","aum":28000,"min_investment":0.005,"returns_1y":17.5,"returns_3y":14.8,"returns_5y":14.5,"max_drawdown":11.5,"sharpe_ratio":1.05,"benchmark":"Nifty 100","benchmark_returns_1y":16.0,"alpha_1y":1.5,"fund_manager":"Harsha Upadhyaya"},
    {"fund_name":"HDFC Top 100 Fund","fund_house":"HDFC MF","category":"MF_LargeCap","strategy":"Large Cap","aum":30000,"min_investment":0.005,"returns_1y":21.5,"returns_3y":17.2,"returns_5y":14.8,"max_drawdown":12.5,"sharpe_ratio":1.18,"benchmark":"Nifty 100","benchmark_returns_1y":16.0,"alpha_1y":5.5,"fund_manager":"Rahul Baijal"},
    {"fund_name":"Nippon India Large Cap Fund","fund_house":"Nippon MF","category":"MF_LargeCap","strategy":"Large Cap","aum":22000,"min_investment":0.005,"returns_1y":22.8,"returns_3y":18.1,"returns_5y":15.5,"max_drawdown":13,"sharpe_ratio":1.25,"benchmark":"Nifty 100","benchmark_returns_1y":16.0,"alpha_1y":6.8,"fund_manager":"Sailesh Raj Bhan"},
    # Mid Cap MF
    {"fund_name":"HDFC Mid-Cap Opportunities Fund","fund_house":"HDFC MF","category":"MF_MidCap","strategy":"Mid Cap","aum":62000,"min_investment":0.005,"returns_1y":32.5,"returns_3y":25.8,"returns_5y":22.1,"max_drawdown":18,"sharpe_ratio":1.35,"benchmark":"Nifty Midcap 150","benchmark_returns_1y":28.0,"alpha_1y":4.5,"fund_manager":"Chirag Setalvad"},
    {"fund_name":"Kotak Emerging Equity Fund","fund_house":"Kotak MF","category":"MF_MidCap","strategy":"Mid Cap","aum":42000,"min_investment":0.005,"returns_1y":30.2,"returns_3y":24.5,"returns_5y":21.8,"max_drawdown":17,"sharpe_ratio":1.3,"benchmark":"Nifty Midcap 150","benchmark_returns_1y":28.0,"alpha_1y":2.2,"fund_manager":"Pankaj Tibrewal"},
    {"fund_name":"Motilal Oswal Midcap Fund","fund_house":"Motilal Oswal MF","category":"MF_MidCap","strategy":"Mid Cap","aum":18000,"min_investment":0.005,"returns_1y":45.2,"returns_3y":32.1,"returns_5y":25.5,"max_drawdown":20,"sharpe_ratio":1.55,"benchmark":"Nifty Midcap 150","benchmark_returns_1y":28.0,"alpha_1y":17.2,"fund_manager":"Niket Shah"},
    {"fund_name":"Axis Midcap Fund","fund_house":"Axis MF","category":"MF_MidCap","strategy":"Mid Cap","aum":25000,"min_investment":0.005,"returns_1y":28.5,"returns_3y":22.1,"returns_5y":20.8,"max_drawdown":15,"sharpe_ratio":1.28,"benchmark":"Nifty Midcap 150","benchmark_returns_1y":28.0,"alpha_1y":0.5,"fund_manager":"Shreyash Devalkar"},
    {"fund_name":"SBI Magnum Midcap Fund","fund_house":"SBI MF","category":"MF_MidCap","strategy":"Mid Cap","aum":20000,"min_investment":0.005,"returns_1y":29.8,"returns_3y":23.5,"returns_5y":21.2,"max_drawdown":16.5,"sharpe_ratio":1.32,"benchmark":"Nifty Midcap 150","benchmark_returns_1y":28.0,"alpha_1y":1.8,"fund_manager":"Bhavin Vithlani"},
    # Small Cap MF
    {"fund_name":"Nippon India Small Cap Fund","fund_house":"Nippon MF","category":"MF_SmallCap","strategy":"Small Cap","aum":48000,"min_investment":0.005,"returns_1y":38.5,"returns_3y":30.2,"returns_5y":28.5,"max_drawdown":22,"sharpe_ratio":1.42,"benchmark":"Nifty Small Cap 250","benchmark_returns_1y":32.0,"alpha_1y":6.5,"fund_manager":"Samir Rachh"},
    {"fund_name":"Quant Small Cap Fund","fund_house":"Quant MF","category":"MF_SmallCap","strategy":"Small Cap","aum":22000,"min_investment":0.005,"returns_1y":42.8,"returns_3y":35.5,"returns_5y":32.1,"max_drawdown":25,"sharpe_ratio":1.48,"benchmark":"Nifty Small Cap 250","benchmark_returns_1y":32.0,"alpha_1y":10.8,"fund_manager":"Sandeep Tandon"},
    {"fund_name":"SBI Small Cap Fund","fund_house":"SBI MF","category":"MF_SmallCap","strategy":"Small Cap","aum":28000,"min_investment":0.005,"returns_1y":35.2,"returns_3y":28.8,"returns_5y":26.5,"max_drawdown":20,"sharpe_ratio":1.38,"benchmark":"Nifty Small Cap 250","benchmark_returns_1y":32.0,"alpha_1y":3.2,"fund_manager":"R Srinivasan"},
    {"fund_name":"HDFC Small Cap Fund","fund_house":"HDFC MF","category":"MF_SmallCap","strategy":"Small Cap","aum":30000,"min_investment":0.005,"returns_1y":36.8,"returns_3y":29.5,"returns_5y":27.2,"max_drawdown":21,"sharpe_ratio":1.4,"benchmark":"Nifty Small Cap 250","benchmark_returns_1y":32.0,"alpha_1y":4.8,"fund_manager":"Chirag Setalvad"},
    {"fund_name":"Axis Small Cap Fund","fund_house":"Axis MF","category":"MF_SmallCap","strategy":"Small Cap","aum":20000,"min_investment":0.005,"returns_1y":33.5,"returns_3y":27.2,"returns_5y":25.8,"max_drawdown":19,"sharpe_ratio":1.35,"benchmark":"Nifty Small Cap 250","benchmark_returns_1y":32.0,"alpha_1y":1.5,"fund_manager":"Anupam Tiwari"},
    # Flexi Cap MF
    {"fund_name":"Parag Parikh Flexi Cap Fund","fund_house":"PPFAS MF","category":"MF_FlexiCap","strategy":"Flexi Cap","aum":55000,"min_investment":0.005,"returns_1y":24.5,"returns_3y":20.8,"returns_5y":19.5,"max_drawdown":14,"sharpe_ratio":1.3,"benchmark":"Nifty 500","benchmark_returns_1y":18.0,"alpha_1y":6.5,"fund_manager":"Rajeev Thakkar"},
    {"fund_name":"HDFC Flexi Cap Fund","fund_house":"HDFC MF","category":"MF_FlexiCap","strategy":"Flexi Cap","aum":48000,"min_investment":0.005,"returns_1y":22.8,"returns_3y":19.5,"returns_5y":17.8,"max_drawdown":15,"sharpe_ratio":1.22,"benchmark":"Nifty 500","benchmark_returns_1y":18.0,"alpha_1y":4.8,"fund_manager":"Roshi Jain"},
    {"fund_name":"Quant Flexi Cap Fund","fund_house":"Quant MF","category":"MF_FlexiCap","strategy":"Flexi Cap","aum":8000,"min_investment":0.005,"returns_1y":35.5,"returns_3y":28.2,"returns_5y":25.8,"max_drawdown":18,"sharpe_ratio":1.45,"benchmark":"Nifty 500","benchmark_returns_1y":18.0,"alpha_1y":17.5,"fund_manager":"Sandeep Tandon"},
    {"fund_name":"JM Flexi Cap Fund","fund_house":"JM Financial MF","category":"MF_FlexiCap","strategy":"Flexi Cap","aum":4500,"min_investment":0.005,"returns_1y":38.2,"returns_3y":30.5,"returns_5y":22.8,"max_drawdown":20,"sharpe_ratio":1.5,"benchmark":"Nifty 500","benchmark_returns_1y":18.0,"alpha_1y":20.2,"fund_manager":"Satish Ramanathan"},
    # Multi Cap MF
    {"fund_name":"Quant Active Fund","fund_house":"Quant MF","category":"MF_MultiCap","strategy":"Multi Cap","aum":10000,"min_investment":0.005,"returns_1y":40.2,"returns_3y":32.5,"returns_5y":28.8,"max_drawdown":22,"sharpe_ratio":1.48,"benchmark":"Nifty 500","benchmark_returns_1y":18.0,"alpha_1y":22.2,"fund_manager":"Sandeep Tandon"},
    {"fund_name":"Nippon India Multi Cap Fund","fund_house":"Nippon MF","category":"MF_MultiCap","strategy":"Multi Cap","aum":35000,"min_investment":0.005,"returns_1y":32.5,"returns_3y":26.8,"returns_5y":22.5,"max_drawdown":18,"sharpe_ratio":1.38,"benchmark":"Nifty 500","benchmark_returns_1y":18.0,"alpha_1y":14.5,"fund_manager":"Sailesh Raj Bhan"},
    {"fund_name":"ICICI Pru Multicap Fund","fund_house":"ICICI Pru MF","category":"MF_MultiCap","strategy":"Multi Cap","aum":12000,"min_investment":0.005,"returns_1y":28.8,"returns_3y":22.5,"returns_5y":19.8,"max_drawdown":16,"sharpe_ratio":1.28,"benchmark":"Nifty 500","benchmark_returns_1y":18.0,"alpha_1y":10.8,"fund_manager":"Anish Tawakley"},
    # ELSS / Tax Saving
    {"fund_name":"Quant ELSS Tax Saver Fund","fund_house":"Quant MF","category":"MF_ELSS","strategy":"ELSS","aum":9000,"min_investment":0.005,"returns_1y":38.5,"returns_3y":30.2,"returns_5y":27.5,"max_drawdown":20,"sharpe_ratio":1.45,"benchmark":"Nifty 500","benchmark_returns_1y":18.0,"alpha_1y":20.5,"fund_manager":"Sandeep Tandon"},
    {"fund_name":"Mirae Asset ELSS Tax Saver","fund_house":"Mirae Asset MF","category":"MF_ELSS","strategy":"ELSS","aum":22000,"min_investment":0.005,"returns_1y":25.2,"returns_3y":20.8,"returns_5y":18.5,"max_drawdown":14,"sharpe_ratio":1.25,"benchmark":"Nifty 500","benchmark_returns_1y":18.0,"alpha_1y":7.2,"fund_manager":"Gaurav Misra"},
    {"fund_name":"SBI Long Term Equity Fund","fund_house":"SBI MF","category":"MF_ELSS","strategy":"ELSS","aum":18000,"min_investment":0.005,"returns_1y":22.8,"returns_3y":18.5,"returns_5y":16.8,"max_drawdown":13,"sharpe_ratio":1.15,"benchmark":"Nifty 500","benchmark_returns_1y":18.0,"alpha_1y":4.8,"fund_manager":"Dinesh Balachandran"},
    # Debt Funds
    {"fund_name":"HDFC Corporate Bond Fund","fund_house":"HDFC MF","category":"MF_Debt","strategy":"Corporate Bond","aum":30000,"min_investment":0.005,"returns_1y":7.8,"returns_3y":6.5,"returns_5y":7.2,"max_drawdown":2,"sharpe_ratio":0.8,"benchmark":"CRISIL Corp Bond","benchmark_returns_1y":7.0,"alpha_1y":0.8,"fund_manager":"Anupam Joshi"},
    {"fund_name":"ICICI Pru Corporate Bond Fund","fund_house":"ICICI Pru MF","category":"MF_Debt","strategy":"Corporate Bond","aum":28000,"min_investment":0.005,"returns_1y":7.5,"returns_3y":6.2,"returns_5y":7.0,"max_drawdown":1.8,"sharpe_ratio":0.78,"benchmark":"CRISIL Corp Bond","benchmark_returns_1y":7.0,"alpha_1y":0.5,"fund_manager":"Manish Banthia"},
    {"fund_name":"SBI Magnum Medium Duration Fund","fund_house":"SBI MF","category":"MF_Debt","strategy":"Medium Duration","aum":12000,"min_investment":0.005,"returns_1y":8.2,"returns_3y":7.0,"returns_5y":7.5,"max_drawdown":3,"sharpe_ratio":0.85,"benchmark":"CRISIL Medium Term","benchmark_returns_1y":7.5,"alpha_1y":0.7,"fund_manager":"Rajeev Radhakrishnan"},
    {"fund_name":"Kotak Dynamic Bond Fund","fund_house":"Kotak MF","category":"MF_Debt","strategy":"Dynamic Bond","aum":8000,"min_investment":0.005,"returns_1y":8.5,"returns_3y":7.2,"returns_5y":7.8,"max_drawdown":3.5,"sharpe_ratio":0.88,"benchmark":"CRISIL Composite Bond","benchmark_returns_1y":7.2,"alpha_1y":1.3,"fund_manager":"Abhishek Bisen"},
    # Index Funds
    {"fund_name":"UTI Nifty 50 Index Fund","fund_house":"UTI MF","category":"MF_Index","strategy":"Index - Nifty 50","aum":18000,"min_investment":0.005,"returns_1y":15.5,"returns_3y":14.8,"returns_5y":14.2,"max_drawdown":12,"sharpe_ratio":1.0,"benchmark":"Nifty 50","benchmark_returns_1y":15.5,"alpha_1y":0.0,"fund_manager":"Sharwan Goyal"},
    {"fund_name":"HDFC Index Fund Nifty 50","fund_house":"HDFC MF","category":"MF_Index","strategy":"Index - Nifty 50","aum":15000,"min_investment":0.005,"returns_1y":15.4,"returns_3y":14.7,"returns_5y":14.1,"max_drawdown":12,"sharpe_ratio":0.99,"benchmark":"Nifty 50","benchmark_returns_1y":15.5,"alpha_1y":-0.1,"fund_manager":"Krishan Daga"},
    {"fund_name":"Motilal Oswal Nifty 500 Index Fund","fund_house":"Motilal Oswal MF","category":"MF_Index","strategy":"Index - Nifty 500","aum":5000,"min_investment":0.005,"returns_1y":18.2,"returns_3y":16.5,"returns_5y":15.0,"max_drawdown":14,"sharpe_ratio":1.05,"benchmark":"Nifty 500","benchmark_returns_1y":18.0,"alpha_1y":0.2,"fund_manager":"Swapnil Mayekar"},
    {"fund_name":"Motilal Oswal Nifty Midcap 150 Index Fund","fund_house":"Motilal Oswal MF","category":"MF_Index","strategy":"Index - Midcap 150","aum":4000,"min_investment":0.005,"returns_1y":28.5,"returns_3y":22.8,"returns_5y":20.5,"max_drawdown":18,"sharpe_ratio":1.2,"benchmark":"Nifty Midcap 150","benchmark_returns_1y":28.0,"alpha_1y":0.5,"fund_manager":"Swapnil Mayekar"},
    # Hybrid / Balanced
    {"fund_name":"ICICI Pru Balanced Advantage Fund","fund_house":"ICICI Pru MF","category":"MF_Hybrid","strategy":"Balanced Advantage","aum":58000,"min_investment":0.005,"returns_1y":14.5,"returns_3y":12.8,"returns_5y":12.2,"max_drawdown":8,"sharpe_ratio":1.1,"benchmark":"CRISIL Hybrid 35+65","benchmark_returns_1y":12.0,"alpha_1y":2.5,"fund_manager":"Sankaran Naren"},
    {"fund_name":"HDFC Balanced Advantage Fund","fund_house":"HDFC MF","category":"MF_Hybrid","strategy":"Balanced Advantage","aum":72000,"min_investment":0.005,"returns_1y":18.2,"returns_3y":15.5,"returns_5y":14.8,"max_drawdown":9,"sharpe_ratio":1.2,"benchmark":"CRISIL Hybrid 35+65","benchmark_returns_1y":12.0,"alpha_1y":6.2,"fund_manager":"Gopal Agrawal"},
    {"fund_name":"SBI Equity Hybrid Fund","fund_house":"SBI MF","category":"MF_Hybrid","strategy":"Aggressive Hybrid","aum":65000,"min_investment":0.005,"returns_1y":16.5,"returns_3y":14.2,"returns_5y":13.8,"max_drawdown":10,"sharpe_ratio":1.08,"benchmark":"CRISIL Hybrid 35+65","benchmark_returns_1y":12.0,"alpha_1y":4.5,"fund_manager":"R Srinivasan"},
    # Sectoral / Thematic
    {"fund_name":"ICICI Pru Technology Fund","fund_house":"ICICI Pru MF","category":"MF_Sectoral","strategy":"Technology","aum":12000,"min_investment":0.005,"returns_1y":28.5,"returns_3y":18.2,"returns_5y":22.5,"max_drawdown":25,"sharpe_ratio":1.1,"benchmark":"Nifty IT","benchmark_returns_1y":25.0,"alpha_1y":3.5,"fund_manager":"Vaibhav Dusad"},
    {"fund_name":"SBI Healthcare Opportunities Fund","fund_house":"SBI MF","category":"MF_Sectoral","strategy":"Pharma & Healthcare","aum":8000,"min_investment":0.005,"returns_1y":35.2,"returns_3y":22.5,"returns_5y":18.8,"max_drawdown":15,"sharpe_ratio":1.25,"benchmark":"Nifty Pharma","benchmark_returns_1y":30.0,"alpha_1y":5.2,"fund_manager":"Tanmaya Desai"},
    {"fund_name":"Nippon India Banking & Financial Fund","fund_house":"Nippon MF","category":"MF_Sectoral","strategy":"Banking & Financial","aum":6500,"min_investment":0.005,"returns_1y":22.8,"returns_3y":18.5,"returns_5y":15.2,"max_drawdown":20,"sharpe_ratio":1.05,"benchmark":"Nifty Bank","benchmark_returns_1y":20.0,"alpha_1y":2.8,"fund_manager":"Bhavin Vithlani"},
    {"fund_name":"Quant Infrastructure Fund","fund_house":"Quant MF","category":"MF_Sectoral","strategy":"Infrastructure","aum":3500,"min_investment":0.005,"returns_1y":45.8,"returns_3y":35.2,"returns_5y":28.5,"max_drawdown":22,"sharpe_ratio":1.5,"benchmark":"Nifty Infra","benchmark_returns_1y":30.0,"alpha_1y":15.8,"fund_manager":"Sandeep Tandon"},
    {"fund_name":"Tata Digital India Fund","fund_house":"Tata MF","category":"MF_Sectoral","strategy":"Technology","aum":9000,"min_investment":0.005,"returns_1y":25.2,"returns_3y":16.8,"returns_5y":20.5,"max_drawdown":28,"sharpe_ratio":1.0,"benchmark":"Nifty IT","benchmark_returns_1y":25.0,"alpha_1y":0.2,"fund_manager":"Meeta Shetty"},
    # International
    {"fund_name":"Motilal Oswal Nasdaq 100 FOF","fund_house":"Motilal Oswal MF","category":"MF_International","strategy":"US Large Cap Tech","aum":6000,"min_investment":0.005,"returns_1y":32.5,"returns_3y":15.8,"returns_5y":22.0,"max_drawdown":30,"sharpe_ratio":1.15,"benchmark":"Nasdaq 100","benchmark_returns_1y":30.0,"alpha_1y":2.5,"fund_manager":"Pratik Oswal"},
    {"fund_name":"PGIM India Global Equity Opp Fund","fund_house":"PGIM MF","category":"MF_International","strategy":"Global Equity","aum":3000,"min_investment":0.005,"returns_1y":28.8,"returns_3y":12.5,"returns_5y":18.5,"max_drawdown":28,"sharpe_ratio":1.0,"benchmark":"MSCI World","benchmark_returns_1y":25.0,"alpha_1y":3.8,"fund_manager":"PGIM Jennison"},
]

STOCKS_NIFTY50 = [
    {"fund_name":"Reliance Industries","fund_house":"Reliance","category":"Stock_LargeCap","strategy":"Conglomerate","aum":1850000,"min_investment":0.0,"returns_1y":12.5,"returns_3y":15.8,"returns_5y":18.2,"max_drawdown":20,"sharpe_ratio":0.9,"benchmark":"Nifty 50","benchmark_returns_1y":15.5,"alpha_1y":-3.0,"fund_manager":"Mukesh Ambani"},
    {"fund_name":"TCS","fund_house":"Tata Group","category":"Stock_LargeCap","strategy":"IT Services","aum":1350000,"min_investment":0.0,"returns_1y":18.2,"returns_3y":12.5,"returns_5y":15.8,"max_drawdown":18,"sharpe_ratio":1.0,"benchmark":"Nifty IT","benchmark_returns_1y":25.0,"alpha_1y":-6.8,"fund_manager":"K Krithivasan"},
    {"fund_name":"HDFC Bank","fund_house":"HDFC Group","category":"Stock_LargeCap","strategy":"Private Bank","aum":1200000,"min_investment":0.0,"returns_1y":8.5,"returns_3y":10.2,"returns_5y":12.5,"max_drawdown":15,"sharpe_ratio":0.7,"benchmark":"Nifty Bank","benchmark_returns_1y":20.0,"alpha_1y":-11.5,"fund_manager":"Sashidhar Jagdishan"},
    {"fund_name":"Infosys","fund_house":"Infosys","category":"Stock_LargeCap","strategy":"IT Services","aum":650000,"min_investment":0.0,"returns_1y":22.5,"returns_3y":10.8,"returns_5y":14.2,"max_drawdown":22,"sharpe_ratio":0.95,"benchmark":"Nifty IT","benchmark_returns_1y":25.0,"alpha_1y":-2.5,"fund_manager":"Salil Parekh"},
    {"fund_name":"ICICI Bank","fund_house":"ICICI Group","category":"Stock_LargeCap","strategy":"Private Bank","aum":850000,"min_investment":0.0,"returns_1y":25.8,"returns_3y":22.5,"returns_5y":20.2,"max_drawdown":18,"sharpe_ratio":1.2,"benchmark":"Nifty Bank","benchmark_returns_1y":20.0,"alpha_1y":5.8,"fund_manager":"Sandeep Bakhshi"},
    {"fund_name":"Bharti Airtel","fund_house":"Bharti","category":"Stock_LargeCap","strategy":"Telecom","aum":750000,"min_investment":0.0,"returns_1y":55.2,"returns_3y":42.5,"returns_5y":35.8,"max_drawdown":15,"sharpe_ratio":1.6,"benchmark":"Nifty 50","benchmark_returns_1y":15.5,"alpha_1y":39.7,"fund_manager":"Gopal Vittal"},
    {"fund_name":"State Bank of India","fund_house":"SBI","category":"Stock_LargeCap","strategy":"PSU Bank","aum":680000,"min_investment":0.0,"returns_1y":32.5,"returns_3y":35.2,"returns_5y":28.8,"max_drawdown":25,"sharpe_ratio":1.3,"benchmark":"Nifty Bank","benchmark_returns_1y":20.0,"alpha_1y":12.5,"fund_manager":"C S Setty"},
    {"fund_name":"ITC","fund_house":"ITC","category":"Stock_LargeCap","strategy":"FMCG/Hotels","aum":580000,"min_investment":0.0,"returns_1y":8.2,"returns_3y":28.5,"returns_5y":15.8,"max_drawdown":12,"sharpe_ratio":0.8,"benchmark":"Nifty FMCG","benchmark_returns_1y":10.0,"alpha_1y":-1.8,"fund_manager":"Sanjiv Puri"},
    {"fund_name":"Hindustan Unilever","fund_house":"Unilever","category":"Stock_LargeCap","strategy":"FMCG","aum":550000,"min_investment":0.0,"returns_1y":-5.2,"returns_3y":2.5,"returns_5y":8.8,"max_drawdown":18,"sharpe_ratio":0.3,"benchmark":"Nifty FMCG","benchmark_returns_1y":10.0,"alpha_1y":-15.2,"fund_manager":"Rohit Jawa"},
    {"fund_name":"Kotak Mahindra Bank","fund_house":"Kotak","category":"Stock_LargeCap","strategy":"Private Bank","aum":380000,"min_investment":0.0,"returns_1y":5.8,"returns_3y":8.2,"returns_5y":10.5,"max_drawdown":18,"sharpe_ratio":0.5,"benchmark":"Nifty Bank","benchmark_returns_1y":20.0,"alpha_1y":-14.2,"fund_manager":"Ashok Vaswani"},
    {"fund_name":"Larsen & Toubro","fund_house":"L&T","category":"Stock_LargeCap","strategy":"Infrastructure","aum":520000,"min_investment":0.0,"returns_1y":28.5,"returns_3y":35.8,"returns_5y":25.2,"max_drawdown":20,"sharpe_ratio":1.25,"benchmark":"Nifty 50","benchmark_returns_1y":15.5,"alpha_1y":13.0,"fund_manager":"S N Subrahmanyan"},
    {"fund_name":"Bajaj Finance","fund_house":"Bajaj Group","category":"Stock_LargeCap","strategy":"NBFC","aum":450000,"min_investment":0.0,"returns_1y":15.2,"returns_3y":12.8,"returns_5y":18.5,"max_drawdown":30,"sharpe_ratio":0.85,"benchmark":"Nifty Financial","benchmark_returns_1y":18.0,"alpha_1y":-2.8,"fund_manager":"Rajeev Jain"},
    {"fund_name":"Asian Paints","fund_house":"Asian Paints","category":"Stock_LargeCap","strategy":"Consumer","aum":280000,"min_investment":0.0,"returns_1y":-12.5,"returns_3y":-2.8,"returns_5y":5.2,"max_drawdown":28,"sharpe_ratio":0.1,"benchmark":"Nifty 50","benchmark_returns_1y":15.5,"alpha_1y":-28.0,"fund_manager":"Amit Syngle"},
    {"fund_name":"Maruti Suzuki","fund_house":"Suzuki","category":"Stock_LargeCap","strategy":"Auto","aum":380000,"min_investment":0.0,"returns_1y":18.5,"returns_3y":22.8,"returns_5y":12.5,"max_drawdown":22,"sharpe_ratio":1.0,"benchmark":"Nifty Auto","benchmark_returns_1y":25.0,"alpha_1y":-6.5,"fund_manager":"Hisashi Takeuchi"},
    {"fund_name":"Sun Pharma","fund_house":"Sun Pharma","category":"Stock_LargeCap","strategy":"Pharma","aum":420000,"min_investment":0.0,"returns_1y":42.5,"returns_3y":35.2,"returns_5y":22.8,"max_drawdown":15,"sharpe_ratio":1.5,"benchmark":"Nifty Pharma","benchmark_returns_1y":30.0,"alpha_1y":12.5,"fund_manager":"Dilip Shanghvi"},
    {"fund_name":"Titan Company","fund_house":"Tata Group","category":"Stock_LargeCap","strategy":"Consumer/Jewellery","aum":320000,"min_investment":0.0,"returns_1y":5.8,"returns_3y":15.2,"returns_5y":22.5,"max_drawdown":25,"sharpe_ratio":0.6,"benchmark":"Nifty 50","benchmark_returns_1y":15.5,"alpha_1y":-9.7,"fund_manager":"C K Venkataraman"},
    {"fund_name":"Wipro","fund_house":"Wipro","category":"Stock_LargeCap","strategy":"IT Services","aum":280000,"min_investment":0.0,"returns_1y":25.8,"returns_3y":5.2,"returns_5y":10.5,"max_drawdown":30,"sharpe_ratio":0.8,"benchmark":"Nifty IT","benchmark_returns_1y":25.0,"alpha_1y":0.8,"fund_manager":"Srini Pallia"},
    {"fund_name":"Tata Motors","fund_house":"Tata Group","category":"Stock_LargeCap","strategy":"Auto","aum":350000,"min_investment":0.0,"returns_1y":45.2,"returns_3y":80.5,"returns_5y":42.8,"max_drawdown":30,"sharpe_ratio":1.4,"benchmark":"Nifty Auto","benchmark_returns_1y":25.0,"alpha_1y":20.2,"fund_manager":"N Chandrasekaran"},
    {"fund_name":"Adani Enterprises","fund_house":"Adani Group","category":"Stock_LargeCap","strategy":"Conglomerate","aum":380000,"min_investment":0.0,"returns_1y":-8.5,"returns_3y":25.2,"returns_5y":55.8,"max_drawdown":65,"sharpe_ratio":0.5,"benchmark":"Nifty 50","benchmark_returns_1y":15.5,"alpha_1y":-24.0,"fund_manager":"Gautam Adani"},
    {"fund_name":"HCL Technologies","fund_house":"HCL","category":"Stock_LargeCap","strategy":"IT Services","aum":420000,"min_investment":0.0,"returns_1y":20.5,"returns_3y":15.8,"returns_5y":18.2,"max_drawdown":18,"sharpe_ratio":1.05,"benchmark":"Nifty IT","benchmark_returns_1y":25.0,"alpha_1y":-4.5,"fund_manager":"C Vijayakumar"},
]

def seed():
    init_db()
    session = SessionLocal()
    added = 0
    skipped = 0

    all_funds = MUTUAL_FUNDS + STOCKS_NIFTY50

    for f in all_funds:
        exists = session.query(FundData).filter(FundData.fund_name == f["fund_name"]).first()
        if exists:
            skipped += 1
            continue
        fund = FundData(
            fund_name=f["fund_name"],
            fund_house=f["fund_house"],
            category=f["category"],
            strategy=f["strategy"],
            aum=f["aum"],
            min_investment=f.get("min_investment", 0),
            returns_1y=f.get("returns_1y"),
            returns_3y=f.get("returns_3y"),
            returns_5y=f.get("returns_5y"),
            max_drawdown=f.get("max_drawdown"),
            sharpe_ratio=f.get("sharpe_ratio"),
            benchmark=f.get("benchmark"),
            benchmark_returns_1y=f.get("benchmark_returns_1y"),
            alpha_1y=f.get("alpha_1y"),
            fund_manager=f.get("fund_manager"),
        )
        session.add(fund)
        added += 1

    session.commit()
    total = session.query(FundData).count()
    session.close()
    print(f"Added: {added} | Skipped: {skipped} | Total in DB: {total}")

if __name__ == "__main__":
    seed()
