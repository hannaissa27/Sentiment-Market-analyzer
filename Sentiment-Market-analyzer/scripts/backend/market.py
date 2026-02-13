import pandas as pd
import requests
import time
from .config import ALPACA_API_KEY, ALPACA_SECRET_KEY
from .utils import force_float

class MarketEngine:
    def __init__(self, ticker):
        self.ticker = ticker
        # We use the raw URL that we KNOW works from diagnostic.py
        self.base_url = "https://data.alpaca.markets/v2/stocks/bars"
        
        self.headers = {
            "APCA-API-KEY-ID": ALPACA_API_KEY,
            "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY,
            "accept": "application/json"
        }

    def fetch_data(self, utc_datetime):
        """
        Fetches market data using RAW REQUESTS (Bypassing the library).
        This mimics diagnostic.py exactly.
        """
        try:
            if not utc_datetime: return None
            
            # 1. Format Time strictly as UTC String (Z-format)
            # This matches the diagnostic format: "2024-02-05T14:30:00Z"
            start_str = utc_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            print(f"[DEBUG] Raw Fetch: {start_str}...", end=" ")
            
            # 2. Build Parameters (Force IEX)
            params = {
                "symbols": self.ticker,
                "timeframe": "1Min",
                "start": start_str,
                "limit": 400, # Get ~1 day of minutes
                "feed": "iex" # STRICTLY FORCE 'IEX'
            }
            
            # 3. Send Request (verify=False for SSL Bypass)
            response = requests.get(
                self.base_url, 
                headers=self.headers, 
                params=params, 
                verify=False
            )
            
            if response.status_code != 200:
                print(f"FAILED (Status {response.status_code})")
                return None
                
            # 4. Parse JSON Response
            data = response.json()
            bars = data.get('bars', {}).get(self.ticker, [])
            
            if not bars:
                print("EMPTY (No IEX data found)")
                return None
                
            print(f"SUCCESS! ({len(bars)} bars)")
            
            # 5. Convert Raw Dicts to Objects (to match old logic)
            # We create a simple class so the rest of your code doesn't break
            class BarObj:
                def __init__(self, b):
                    self.high = b['h']
                    self.low = b['l']
                    self.open = b['o']
                    self.close = b['c']
            
            return [BarObj(b) for b in bars]

        except Exception as e:
            print(f"ERROR: {e}")
            return None

    def calculate_metrics(self, bars_list):
        """
        Calculates Volatility & Price Change.
        """
        if not bars_list or len(bars_list) < 5:
            return [0.0] * 8

        # Windows: 5m, 30m, 60m, Day
        windows = [5, 30, 60, len(bars_list)] 
        results = []
        base_open = bars_list[0].open
        
        for w in windows:
            limit = min(w, len(bars_list))
            slice_data = bars_list[:limit]
            
            if not slice_data:
                results.extend([0.0, 0.0])
                continue

            try:
                high_val = max([b.high for b in slice_data])
                low_val = min([b.low for b in slice_data])
                close_val = slice_data[-1].close
                
                vol = ((high_val - low_val) / base_open) * 100.0
                chg = ((close_val - base_open) / base_open) * 100.0
                
                results.extend([force_float(vol), force_float(chg)])
            except:
                results.extend([0.0, 0.0])
                
        return results