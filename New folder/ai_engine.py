# ai_engine.py
import MetaTrader5 as mt5
import pandas as pd
import pandas_ta_classic as ta 
import config
import time

def calculate_market_regime(symbol="EURUSD"):
    # Fetch latest 100 bars on M15 timeframe
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 100)
    if rates is None or len(rates) == 0:
        return "ranging", 1.0, ["grid"] # Conservative fallback
        
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    # Calculate indicators using pandas-ta
    df.ta.adx(append=True)     # Average Directional Index (Trend Strength)
    df.ta.rsi(append=True)     # Relative Strength Index (Overbought/Oversold)
    df.ta.atr(append=True)     # Average True Range (Volatility)
    
    # Extract latest values
    latest_adx = df['ADX_14'].iloc[-1]
    latest_rsi = df['RSI_14'].iloc[-1]
    latest_atr = df['AT_14'].iloc[-1] if 'AT_14' in df.columns else df.ta.atr().iloc[-1]

    # Analysis logic determining bot states:
    # 1. Strong Trend (ADX > 25): Breakout / Scalper bots run. Turn off Grid to avoid dangerous drawdowns.
    # 2. Quiet Range (ADX < 20): Grid / Scalper bots run. Turn off Breakout.
    # 3. Extreme Volatility (ATR spiked): Safety lock on. Close/pause activity.
    
    if latest_atr > (df.ta.atr().mean() * 1.8): # Volatility spike detection
        return "volatile_pause", 0.2, ["scalper"] 
    elif latest_adx > 25:
        # Determine trend direction
        trend_dir = "trending_up" if latest_rsi > 50 else "trending_down"
        return trend_dir, 1.0, ["breakout", "scalper"]
    else:
        return "ranging", 0.8, ["grid", "scalper"]

def run_ai_analysis():
    print("AI Analysis Engine active...")
    while config.state.system_active:
        try:
            regime, risk, active_bots = calculate_market_regime("EURUSD")
            
            # Safely write updates to shared memory
            with config.state.lock:
                config.state.market_regime = regime
                config.state.risk_multiplier = risk
                config.state.allowed_bots = active_bots
                
            print(f"[AI] Regime calculated: {regime.upper()} | Risk Scale: {risk} | Bots Active: {active_bots}")
        except Exception as e:
            print(f"AI Engine analysis error: {e}")
            
        time.sleep(60) # Run analysis on a 60-second loop