# bot_executor.py
import MetaTrader5 as mt5
import config
import time

def breakout_bot():
    print("[BOT] Breakout Bot Loop Started...")
    magic_number = 1111
    while config.state.system_active:
        with config.state.lock:
            allowed = "breakout" in config.state.allowed_bots
            risk_scale = config.state.risk_multiplier
            
        if allowed:
            # Your breakout strategy rules go here
            pass
        time.sleep(1.0) 

def grid_bot():
    print("[BOT] Grid Bot Loop Started...")
    magic_number = 2222
    while config.state.system_active:
        with config.state.lock:
            allowed = "grid" in config.state.allowed_bots
            risk_scale = config.state.risk_multiplier
            
        if allowed:
            # Your grid strategy rules go here
            pass
        time.sleep(2.0) 

def scalper_bot():
    print("[BOT] Scalper Bot Loop Started...")
    magic_number = 3333
    while config.state.system_active:
        with config.state.lock:
            allowed = "scalper" in config.state.allowed_bots
            risk_scale = config.state.risk_multiplier
            
        if allowed:
            # Your scalper strategy rules go here
            pass
        time.sleep(0.1)