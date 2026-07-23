import time
import pandas as pd
import MetaTrader5 as mt5
import config  # Ensure RISK_PER_TRADE_PCT = 0.01 is defined here
from analyzer import VolatilityEntryEngine

def initialize_mt5_with_config():
    """Initializes the connection to the MetaTrader 5 terminal."""
    if not mt5.initialize():
        print(f"MT5 Initialization failed. Error code: {mt5.last_error()}")
        quit()
    
    # Authenticate using config file credentials
    login = int(config.LOGIN) if hasattr(config, 'LOGIN') else int(config.ACCOUNT)
    password = str(config.PASSWORD)
    server = str(config.SERVER)
    
    if mt5.login(login, password=password, server=server):
        print(f"Successfully authenticated Account #{login} on server: {server}")
    else:
        print(f"Authentication failed! Error code: {mt5.last_error()}")
        quit()

def fetch_live_data(symbol, timeframe, num_candles=50):
    """Pulls historical data array for a specific timeframe securely."""
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_candles)
    if rates is None or len(rates) == 0:
        print(f"Data pull failed for {symbol} on timeframe {timeframe}. Error: {mt5.last_error()}")
        return None
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    return df

def has_open_positions(symbol):
    """Checks if there are any active positions currently open for the asset."""
    positions = mt5.positions_get(symbol=symbol)
    if positions is None:
        return False
    return len(positions) > 0

def calculate_lot_size(symbol, entry_price, stop_loss):
    """Computes risk-adjusted lot sizing dynamically using account balance metrics."""
    account_info = mt5.account_info()
    if account_info is None:
        return 0.1  # Safe minimum fallback lot size
        
    balance = account_info.balance
    risk_pct = getattr(config, 'RISK_PER_TRADE_PCT', 0.01)
    risk_amount = balance * risk_pct
    
    price_distance = abs(float(entry_price) - float(stop_loss))
    if price_distance == 0:
        return 0.1
        
    # Standard technical lot calculation structure
    calculated_lot = risk_amount / price_distance
    
    # Normalize step parameters to prevent broker sizing rejects
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is not None:
        min_lot = symbol_info.volume_min
        max_lot = symbol_info.volume_max
        return max(min(calculated_lot, max_lot), min_lot)
        
    return round(calculated_lot, 2)

def execute_market_order(symbol, direction, entry_price, stop_loss, take_profit):
    """Constructs and routes the formal two-step execution request directly to the broker."""
    if has_open_positions(symbol):
        print(f"[{symbol}] Entry signal detected, but a position is already open. Skipping.")
        return

    order_type = mt5.ORDER_TYPE_BUY if direction == "BUY" else mt5.ORDER_TYPE_SELL
    tick_info = mt5.symbol_info_tick(symbol)
    if tick_info is None:
        print(f"❌ Failed to fetch current live ticks for {symbol}.")
        return
        
    price = tick_info.ask if direction == "BUY" else tick_info.bid
    lot = calculate_lot_size(symbol, entry_price, stop_loss)

    # STEP 1: Route clean entry execution order to bypass market execution filters
    trade_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(lot),
        "type": order_type,
        "price": float(price),
        "deviation": 20,
        "magic": 991122,
        "comment": "TradeFlow AI Sniper",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    print(f"Sending entry execution request: {direction} {lot:.2f} lots on {symbol}...")
    result = mt5.order_send(trade_request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"❌ Order Execution Failed! Error payload: {result.comment} (Code: {result.retcode})")
        return
        
    print(f"🚀 [TRADE OPENED] Ticket ID: {result.order}. Attaching bracket protections...")
    
    # Allow broker server latency processing synchronization
    time.sleep(0.2) 

    # STEP 2: Modify the open live deal to tightly clamp SL and TP parameters
    modify_request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "position": result.order,
        "symbol": symbol,
        "sl": float(stop_loss),
        "tp": float(take_profit)
    }
    
    modify_result = mt5.order_send(modify_request)
    if modify_result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"⚠️ Warning: Failed to anchor SL/TP brackets! Error: {modify_result.comment}")
    else:
        print(f"🛡️ [PROTECTION SECURED] SL locked at {stop_loss} | TP locked at {take_profit}")

def run_system():
    """Core continuum execution engine loop scanning multi-timeframe arrays."""
    initialize_mt5_with_config()
    
    engine = VolatilityEntryEngine(
        swing_period=config.SWING_PERIOD, 
        atr_period=config.ATR_PERIOD
    )
    
    print(f"Monitoring MTF Continuum (H4 -> H1 -> M15 -> M1) on: {config.TARGET_SYMBOLS}...")
    
    try:
        while True:
            for symbol in config.TARGET_SYMBOLS:
                mt5.symbol_select(symbol, True)
                
                # Fetch multi-timeframe framework data arrays
                df_h4  = fetch_live_data(symbol, mt5.TIMEFRAME_H4, num_candles=50)
                df_h1  = fetch_live_data(symbol, mt5.TIMEFRAME_H1, num_candles=50)
                df_m15 = fetch_live_data(symbol, mt5.TIMEFRAME_M15, num_candles=50)
                df_m1  = fetch_live_data(symbol, mt5.TIMEFRAME_M1, num_candles=100)
                
                if all(df is not None for df in [df_h4, df_h1, df_m15, df_m1]):
                    
                    # Process mathematical models safely
                    h4_analysis  = engine.scan_for_entries(df_h4)
                    h1_analysis  = engine.scan_for_entries(df_h1)
                    m15_analysis = engine.scan_for_entries(df_m15)
                    m1_alert     = engine.scan_for_entries(df_m1)
                    
                    # Extract positions using fallbacks to avoid any KeyError crashes
                    h4_status = h4_analysis.get('status', 'Scanning')
                    h1_status = h1_analysis.get('status', 'Scanning')
                    m15_status = m15_analysis.get('status', 'Scanning')
                    
                    print(f"[{symbol}] H4 Flow: {h4_status} | H1 Flow: {h1_status} | M1: Monitoring structural zones...")
                    
                    # Execution filter matrix
                    if m1_alert.get('status') == 'ENTRY_TRIGGERED':
                        m1_direction = m1_alert.get('direction')
                        
                        # ANTI-WHIPSAW FILTER: Ensure M1 execution matches immediate M15 and H1 structural trends
                        if m1_direction == h1_status and m1_direction == m15_status:
                            print(f"\n[🔥 TRIPLE-CONCURRENCE sniper entry triggered | {symbol}] {m1_direction}")
                            
                            execute_market_order(
                                symbol=symbol,
                                direction=m1_direction,
                                entry_price=m1_alert.get('entry_price'),
                                stop_loss=m1_alert.get('stop_loss'),
                                take_profit=m1_alert.get('take_profit_1')
                            )
                        else:
                            print(f"❌ [{symbol}] M1 entry filtered out: Out of alignment with intermediate H1 ({h1_status}) or M15 ({m15_status}) horizons.")
            
            # Use tight interval constraints for granular execution tracking
            print("--- Cycle complete. Sleeping for 15 seconds ---")
            time.sleep(15)
            
    except KeyboardInterrupt:
        print("\nShutting down MT5 bridge safely.")
        mt5.shutdown()

if __name__ == "__main__":
    run_system()