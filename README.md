# FinBERT Market Volatility Analyzer

## 📌 Project Overview
This repository contains a quantitative research pipeline designed to measure the immediate impact of financial news on stock market volatility. Built for an AP Research study on Generative AI's market impact, this tool processes news headlines, assigns sentiment scores using a Financial Large Language Model (FinBERT), and correlates them with intraday price movements of the **Invesco QQQ Trust (QQQ)**.

## 🚀 Features
* **Sentiment Analysis:** Uses `ProsusAI/finbert` (via Hugging Face Transformers) to generate domain-specific sentiment scores (-1.0 to +1.0) for financial headlines.
* **Market Data Retrieval:** Connects to the **Alpaca Data API** (IEX Feed) to fetch minute-level historical bar data.
* **Volatility Metrics:** Calculates multiple volatility windows (1-min, 5-min, 30-min, 60-min, and Daily) to distinguish between HFT (High-Frequency Trading) reactions and longer-term market digestion.
* **Network Resilience:** Includes custom SSL context handling to function securely within restricted network environments (e.g., enterprise or school firewalls).

## 📂 Project Structure
```text
├── scripts/
│   ├── main.py              # Entry point for the analysis pipeline
│   ├── backend/             # Core logic modules
│   │   ├── config.py        # API keys, global settings, and SSL patching
│   │   ├── market.py        # Alpaca API connection & volatility calculations
│   │   ├── sentiment.py     # FinBERT model loader & inference engine
│   │   ├── pipeline.py      # Orchestrator combining data & models
│   │   └── utils.py         # Data cleaning & type conversion helpers
│   └── data/
│       ├── articles.xlsx    # Input: Raw headlines & timestamps
│       └── results.xlsx     # Output: Final dataset with sentiment & volatility


🛠️ Installation & Setup
1. Prerequisites
Python 3.9+

An Alpaca Markets Account (Free "Paper" Tier is sufficient)

2. Install Dependencies
This project relies on PyTorch for the LLM and the Alpaca SDK for market data.

Bash
pip install -r requirements.txt
3. Configuration
Open backend/config.py and add your Alpaca API credentials:

Python
ALPACA_API_KEY = "YOUR_KEY_HERE"
ALPACA_SECRET_KEY = "YOUR_SECRET_HERE"
ALPACA_BASE_URL = "[https://paper-api.alpaca.markets](https://paper-api.alpaca.markets)"
📊 Usage
Place your Excel file containing headlines in the data/ folder (named articles.xlsx).

Run the main analysis script:

Bash
python scripts/main.py
The script will:

Load the FinBERT model.

Score every headline.

Fetch historical price data for the exact minute each article was published.

Calculate volatility and save the result to final_research_results.xlsx.

📚 Methodology Note
This tool uses a 60-minute look-ahead window from the time of publication to determine market reaction. Volatility is calculated as (High - Low) / Open, and Sentiment is derived from the softmax probabilities of Positive vs. Negative tokens in the FinBERT model.
