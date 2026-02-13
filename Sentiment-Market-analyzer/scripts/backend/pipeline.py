import pandas as pd
import numpy as np
from scipy.stats import pearsonr

from .config import TICKER, MODEL_NAME
from .utils import combine_date_time, format_for_excel
from .sentiment import SentimentEngine
from .market import MarketEngine

class ResearchPipeline:
    def __init__(self):
        self.sentiment_engine = SentimentEngine(MODEL_NAME)
        self.market_engine = MarketEngine(TICKER)

    def _calculate_accuracy(self, df):
        """Checks accuracy based on the 60-minute trend (more stable)."""
        acc_list = []
        for _, row in df.iterrows():
            sent = row.get('Sentiment_Score', 0)
            # We use the 60-minute move for accuracy checking
            move = row.get('Price_Chg_60m_%', 0)
            
            if (sent > 0.05 and move > 0): acc_list.append(1)
            elif (sent < -0.05 and move < 0): acc_list.append(1)
            elif (sent > 0.05 and move < 0): acc_list.append(0)
            elif (sent < -0.05 and move > 0): acc_list.append(0)
            else: acc_list.append(None)
        return acc_list

    def run(self, input_file, output_file):
        print(f"--- STARTING MULTI-TIMEFRAME PIPELINE ({TICKER}) ---")
        
        # 1. LOAD
        try:
            df = pd.read_excel(input_file)
            print(f"Loaded {len(df)} articles.")
        except Exception as e:
            print(f"ERROR: Could not load {input_file}\n{e}")
            return

        # 2. SENTIMENT
        print("Step 1/3: Analyzing Sentiment...")
        df['Sentiment_Score'] = [self.sentiment_engine.get_score(txt) for txt in df['Headline']]

        # 3. MARKET DATA
        print("Step 2/3: Fetching Data (5m, 30m, 60m, Daily)...")
        market_data_list = []
        total = len(df)
        
        for idx, row in df.iterrows():
            if idx % 10 == 0: print(f"Processing {idx}/{total}...", end='\r')
            
            dt = combine_date_time(row.get('Date'), row.get('Time'))
            # Default: 8 zeros for 4 timeframes x 2 metrics
            metrics = [0.0] * 8 
            
            if dt:
                bars = self.market_engine.fetch_data(dt)
                if bars:
                    metrics = self.market_engine.calculate_metrics(bars)
            
            market_data_list.append(metrics)
        
        # Unpack results into DataFrame columns
        market_arr = np.array(market_data_list)
        
        # 5 Minute
        df['Vol_5m_%'] = market_arr[:, 0]
        df['Price_Chg_5m_%'] = market_arr[:, 1]
        
        # 30 Minute
        df['Vol_30m_%'] = market_arr[:, 2]
        df['Price_Chg_30m_%'] = market_arr[:, 3]
        
        # 60 Minute
        df['Vol_60m_%'] = market_arr[:, 4]
        df['Price_Chg_60m_%'] = market_arr[:, 5]
        
        # End of Day
        df['Vol_Day_%'] = market_arr[:, 6]
        df['Price_Chg_Day_%'] = market_arr[:, 7]

        # 4. STATS & SAVE
        print("\nStep 3/3: Finalizing...")
        df['AI_Correct'] = self._calculate_accuracy(df)
        
        # Quick Correlation Check (Sentiment vs 60m Price)
        valid = df[df['Vol_60m_%'] > 0]
        if len(valid) > 1:
            r, p = pearsonr(valid['Sentiment_Score'], valid['Price_Chg_60m_%'])
            print(f"\nCorrelation (Sentiment vs 60m Price): r={r:.4f} (p={p:.4f})")
            
        # Save
        df = format_for_excel(df)
        df.to_excel(output_file, index=False)
        print(f"Saved: {output_file}")