# run_analysis.py
import pandas as pd
import numpy as np
from analyzer import VolatilityEntryEngine

def simulate_live_market_feed():
    """Generates a realistic Volatility Index price array for system scanning."""
    np.random.seed(101)
    time_index = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='M15')
    
    # Simulating a market expansion to test the breakthrough trigger logic
    base_prices = 3500 + np.cumsum(np.random.normal(5, 20, 100))
    # Forces a major breakout on the final bar to trip the entry engine
    base_prices[-1] = base_prices.max() + 75 
    
    df = pd.DataFrame({
        'open': base_prices - np.random.normal(0, 5, 100),
        'high': base_prices + np.abs(np.random.normal(15, 5, 100)),
        'low': base_prices - np.abs(np.random.normal(15, 5, 100)),
        'close': base_prices,
    }, index=time_index)
    return df

def execute_analysis_cycle():
    # 1. Fetch current historical data block
    market_dataframe = simulate_live_market_feed()
    
    # 2. Run analysis mechanics
    engine = VolatilityEntryEngine(swing_period=3, atr_period=14)
    alert = engine.scan_for_entries(market_dataframe)
    
    # 3. Print out clean entry specifications
    print("\n==================================================")
    print("      TRADEAPA VOLATILITY ENTRY ENGINE ALERTS      ")
    print("==================================================")
    
    if alert['status'] == 'ENTRY_TRIGGERED':
        print(f"[🔥] SIGNAL ACQUIRED: {alert['direction']}")
        print(f" -> Execute Entry At: {alert['entry_price']}")
        print(f" -> Protective Stop : {alert['stop_loss']}")
        print(f" -> Take Profit 1   : {alert['take_profit_1']}")
        print(f" -> Take Profit 2   : {alert['take_profit_2']}")
    else:
        print(f"[🔎] STATUS: {alert['status']}")
        print(f" -> Message: {alert['message']}")
        
    print("==================================================\n")

if __name__ == "__main__":
    execute_analysis_cycle()