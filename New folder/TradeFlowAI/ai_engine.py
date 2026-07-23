# ai_engine.py
import MetaTrader5 as mt5
import pandas as pd
import pandas_ta_classic as ta
import time
import config

def detect_swings(df):
    """
    Detects peak (highs) and valley (lows) turning points.
    Checks if a candle is higher/lower than the 2 candles before and after it.
    """
    df['swing_high'] = False
    df['swing_low'] = False
    
    # Needs at least 5 candles to check left and right neighbors
    for i in range(2, len(df) - 2):
        # Swing High: highest peak among 5 candles
        if (df['high'].iloc[i] > df['high'].iloc[i-1] and 
            df['high'].iloc[i] > df['high'].iloc[i-2] and
            df['high'].iloc[i] > df['high'].iloc[i+1] and 
            df['high'].iloc[i] > df['high'].iloc[i+2]):
            df.at[df.index[i], 'swing_high'] = True
            
        # Swing Low: lowest valley among 5 candles
        if (df['low'].iloc[i] < df['low'].iloc[i-1] and 
            df['low'].iloc[i] < df['low'].iloc[i-2] and
            df['low'].iloc[i] < df['low'].iloc[i+1] and 
            df['low'].iloc[i] < df['low'].iloc[i+2]):
            df.at[df.index[i], 'swing_low'] = True
            
    return df

def detect_order_blocks(df):
    """
    Identifies Order Blocks (where big institutions left footprints).
    Looks for strong expansion candles after an opposite candle.
    """
    df['bullish_ob'] = None
    df['bearish_ob'] = None
    
    for i in range(1, len(df)):
        body_size = abs(df['close'].iloc[i] - df['open'].iloc[i])
        candle_range = df['high'].iloc[i] - df['low'].iloc[i]
        if candle_range == 0:
            continue
            
        prev_candle_red = df['close'].iloc[i-1] < df['open'].iloc[i-1]
        prev_candle_green = df['close'].iloc[i-1] > df['open'].iloc[i-1]
        
        # Bullish OB: Strong green expansion candle (body takes up 60%+ of range) after a red candle
        if df['close'].iloc[i] > df['open'].iloc[i] and body_size > candle_range * 0.6:
            if prev_candle_red:
                # The red candle's high acts as the Bullish OB level
                df.at[df.index[i], 'bullish_ob'] = df['high'].iloc[i-1]
                
        # Bearish OB: Strong red expansion candle (body takes up 60%+ of range) after a green candle
        if df['close'].iloc[i] < df['open'].iloc[i] and body_size > candle_range * 0.6:
            if prev_candle_green:
                # The green candle's low acts as the Bearish OB level
                df.at[df.index[i], 'bearish_ob'] = df['low'].iloc[i-1]
                
    return df

def detect_head_and_shoulders(df):
    """
    Scans through historical swing highs to detect a Head & Shoulders pattern.
    """
    df['head_and_shoulders'] = False
    swing_high_indices = df[df['swing_high'] == True].index.tolist()
    
    if len(swing_high_indices) >= 3:
        for idx in range(len(swing_high_indices) - 2):
            sh1_idx = swing_high_indices[idx]
            sh2_idx = swing_high_indices[idx+1]
            sh3_idx = swing_high_indices[idx+2]
            
            h1 = df.loc[sh1_idx, 'high']  # Left Shoulder
            h2 = df.loc[sh2_idx, 'high']  # Head
            h3 = df.loc[sh3_idx, 'high']  # Right Shoulder
            
            # Head must be taller than both shoulders
            if h2 > h1 and h2 > h3:
                # Shoulders must be within 15% height difference of each other
                shoulder_diff = abs(h1 - h3) / max(h1, h3) if max(h1, h3) > 0 else 0
                if shoulder_diff < 0.15:
                    df.at[sh3_idx, 'head_and_shoulders'] = True
                    
    return df

def run_ai_analysis():
    """
    The main engine loop. Periodically fetches live candlesticks from MT5,
    detects patterns, determines the market regime, and updates system state.
    """
    # Use Gold (XAUUSD) or fallback to whatever pair is active
    symbol = "XAUUSD" 
    timeframe = mt5.TIMEFRAME_H1 # We'll check the 1-Hour chart for robust structures
    
    print("[AI] Engine is now live and analyzing structures...")
    
    while config.state.system_active:
        try:
            # 1. Grab the last 100 hourly candles from MT5
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 100)
            
            if rates is None or len(rates) == 0:
                print(f"[AI] Error: Could not fetch rates for {symbol}. Will try again...")
                time.sleep(10)
                continue
                
            # Convert structural data to a Pandas DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # 2. Feed the data to our pattern recognizers
            df = detect_swings(df)
            df = detect_order_blocks(df)
            df = detect_head_and_shoulders(df)
            
            # 3. Read the absolute newest results (last candle in DataFrame)
            last_idx = df.index[-1]
            latest_row = df.iloc[-1]
            
            # 4. Check for active indicators and print clear logs
            print(f"\n--- [AI Market Scan | {symbol}] ---")
            
            # Check for swing points
            if latest_row['swing_high']:
                print("[ALERT] Swing High Formed! Potential resistance ceiling reached.")
            elif latest_row['swing_low']:
                print("[ALERT] Swing Low Formed! Potential support floor established.")
                
            # Check for fresh Order Blocks
            if latest_row['bullish_ob'] is not None:
                print(f"[ALERT] BULLISH Order Block detected at price: {latest_row['bullish_ob']} (Heavy Buy Interest)")
            if latest_row['bearish_ob'] is not None:
                print(f"[ALERT] BEARISH Order Block detected at price: {latest_row['bearish_ob']} (Heavy Sell Interest)")
                
            # Check for Head & Shoulders
            if latest_row['head_and_shoulders']:
                print("[ALERT] HEAD & SHOULDERS pattern completed! Major trend reversal imminent.")
                
            # Determine regime
            # (Simple trend assessment using typical moving average logic on rates)
            close_prices = df['close']
            fast_ma = close_prices.rolling(window=10).mean().iloc[-1]
            slow_ma = close_prices.rolling(window=30).mean().iloc[-1]
            
            with config.state.lock:
                if fast_ma > slow_ma:
                    config.state.market_regime = "TRENDING_UP"
                    config.state.allowed_bots = ["breakout", "scalper"]
                elif fast_ma < slow_ma:
                    config.state.market_regime = "TRENDING_DOWN"
                    config.state.allowed_bots = ["breakout", "scalper"]
                else:
                    config.state.market_regime = "RANGING"
                    config.state.allowed_bots = ["grid"]
                    
            print(f"[AI] Calculated Regime: {config.state.market_regime} | Allowed Bots: {config.state.allowed_bots}")
            
        except Exception as e:
            print(f"[AI ERROR] Exception in pattern scanner: {e}")
            
        # Run scan every 10 seconds to keep updates responsive
        time.sleep(10)