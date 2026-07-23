# analyzer.py
import pandas as pd
import numpy as np

class VolatilityEntryEngine:
    """Analyzes market structure and isolates precise entry setups for Volatility Markets."""
    def __init__(self, swing_period: int = 4, atr_period: int = 14):
        self.p = swing_period
        self.atr_period = atr_period

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Locates technical swing points and processes an ATR baseline."""
        df = df.copy()
        
        # 1. Calculate ATR for dynamic buffer scaling
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift(1))
        low_close = np.abs(df['low'] - df['close'].shift(1))
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = tr.rolling(window=self.atr_period).mean()

        # 2. Map structural Swing Highs and Swing Lows
        df['swing_high'] = np.nan
        df['swing_low'] = np.nan
        
        for i in range(self.p, len(df) - self.p):
            current_high = df['high'].iloc[i]
            current_low = df['low'].iloc[i]
            
            if current_high == df['high'].iloc[i - self.p : i + self.p + 1].max():
                df.iloc[i, df.columns.get_loc('swing_high')] = current_high
            if current_low == df['low'].iloc[i - self.p : i + self.p + 1].min():
                df.iloc[i, df.columns.get_loc('swing_low')] = current_low
                
        # Forward-fill structural zones to keep track of the most recent valid anchors
        df['last_structural_high'] = df['swing_high'].ffill()
        df['last_structural_low'] = df['swing_low'].ffill()
        return df

    def scan_for_entries(self, df: pd.DataFrame) -> dict:
        """Scans the market geometry matrix and isolates concrete entry conditions."""
        df_analyzed = self.process_data(df)
        
        if len(df_analyzed) < 2:
            return {"status": "INSUFFICIENT_DATA"}
            
        current_bar = df_analyzed.iloc[-1]
        previous_bar = df_analyzed.iloc[-2]
        
        current_price = current_bar['close']
        structure_high = current_bar['last_structural_high']
        structure_low = current_bar['last_structural_low']
        atr = current_bar['atr']
        
        # Prevent math bugs if structural points haven't formed yet
        if pd.isna(structure_high) or pd.isna(structure_low) or pd.isna(atr):
            return {"status": "SCANNING", "message": "Building historical structural baselines..."}

        # Calculate standard Fibonacci levels inside the current trading leg
        trading_leg_range = structure_high - structure_low
        fib_618 = structure_high - (trading_leg_range * 0.618)
        fib_786 = structure_high - (trading_leg_range * 0.786)

        # --- SETUP 1: BULLISH STRUCTURE SHIFT (Reversal / Extension Entry) ---
        # Trigger Condition: Close crosses cleanly over the prior structural peak
        if current_price > structure_high and previous_bar['close'] <= structure_high:
            return {
                "status": "ENTRY_TRIGGERED",
                "direction": "BUY (Bullish Structure Shift)",
                "entry_price": round(current_price, 2),
                "stop_loss": round(structure_low - (atr * 0.5), 2),  # Anchored below structure with an ATR pad
                "take_profit_1": round(current_price + (trading_leg_range * 1.0), 2),
                "take_profit_2": round(current_price + (trading_leg_range * 2.0), 2)
            }

        # --- SETUP 2: DISCOUNT RETRACEMENT ENTRY (Fibonacci Confluence) ---
        # Trigger Condition: Price pulls back deep into the golden pocket zone while overall structure holds
        if current_price <= fib_618 and current_price >= fib_786 and previous_bar['close'] > fib_618:
            return {
                "status": "ENTRY_TRIGGERED",
                "direction": "BUY (Deep Discount Pullback)",
                "entry_price": round(current_price, 2),
                "stop_loss": round(structure_low - (atr * 0.2), 2),
                "take_profit_1": round(structure_high, 2),
                "take_profit_2": round(structure_high + (trading_leg_range * 0.5), 2)
            }

        # --- SETUP 3: BEARISH STRUCTURE SHIFT (Short Entry) ---
        # Trigger Condition: Close cracks cleanly below the prior structural floor
        if current_price < structure_low and previous_bar['close'] >= structure_low:
            return {
                "status": "ENTRY_TRIGGERED",
                "direction": "SELL (Bearish Structure Shift)",
                "entry_price": round(current_price, 2),
                "stop_loss": round(structure_high + (atr * 0.5), 2), # Anchored above structural ceiling
                "take_profit_1": round(current_price - (trading_leg_range * 1.0), 2),
                "take_profit_2": round(current_price - (trading_leg_range * 2.0), 2)
            }

        return {
            "status": "SCANNING",
            "message": f"Market structural boundaries holding. Range: {structure_low:.2f} - {structure_high:.2f}. Monitoring..."
        }