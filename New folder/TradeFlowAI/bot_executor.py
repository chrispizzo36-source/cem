# executor.py
import MetaTrader5 as mt5
import time
import config
from trading_utils import send_market_order

# Set default trading symbol (e.g., Gold)
SYMBOL = "XAUUSD"

def breakout_bot():
    print("[BOT] Breakout Bot Loop Started...")
    magic_number = 1111
    
    while config.state.system_active:
        with config.state.lock:
            allowed = "breakout" in config.state.allowed_bots
            regime = config.state.market_regime
            
        if allowed:
            # --- 1. BULLISH BREAKOUT (TRENDING UP) ---
            if regime == "TRENDING_UP":
                print("[BREAKOUT] Spotting strong upward momentum. Preparing BUY order...")
                tick = mt5.symbol_info_tick(SYMBOL)
                if tick:
                    buy_price = tick.ask
                    stop_loss = buy_price - 10.0
                    take_profit = buy_price + 20.0
                    
                    send_market_order(
                        symbol=SYMBOL,
                        order_type=mt5.ORDER_TYPE_BUY,
                        volume=0.01,
                        magic_number=magic_number,
                        stop_loss=stop_loss,
                        take_profit=take_profit
                    )
                    time.sleep(300) # Cooldown to avoid double-trading
                    
            # --- 2. BEARISH BREAKOUT (TRENDING DOWN) ---
            elif regime == "TRENDING_DOWN":
                print("[BREAKOUT] Spotting strong downward momentum. Preparing SELL order...")
                tick = mt5.symbol_info_tick(SYMBOL)
                if tick:
                    sell_price = tick.bid
                    # For a sell: Stop Loss is ABOVE entry, Take Profit is BELOW entry
                    stop_loss = sell_price + 10.0
                    take_profit = sell_price - 20.0
                    
                    send_market_order(
                        symbol=SYMBOL,
                        order_type=mt5.ORDER_TYPE_SELL,
                        volume=0.01,
                        magic_number=magic_number,
                        stop_loss=stop_loss,
                        take_profit=take_profit
                    )
                    time.sleep(300) # Cooldown to avoid double-trading
                    
        time.sleep(1.0)

def grid_bot():
    print("[BOT] Grid Bot Loop Started...")
    magic_number = 2222
    
    while config.state.system_active:
        with config.state.lock:
            allowed = "grid" in config.state.allowed_bots
            regime = config.state.market_regime
            
        if allowed:
            # 2. Grid Strategy Logic (Ranging Markets)
            # When the market is bouncing sideways, we buy low and sell high
            if regime == "RANGING":
                print("[GRID] Market is flat. Placing range-bound grid levels...")
                # (Grid logic will call buy-limit / sell-limit orders here)
                pass
                
        time.sleep(2.0) 

def scalper_bot():
    print("[BOT] Scalper Bot Loop Started...")
    magic_number = 3333
    
    while config.state.system_active:
        with config.state.lock:
            allowed = "scalper" in config.state.allowed_bots
            
        if allowed:
            # 3. Scalper Strategy Logic (High Frequency)
            # Looks for immediate, micro-swing reversals
            pass
            
        time.sleep(0.1)