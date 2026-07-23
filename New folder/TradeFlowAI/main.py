# main.py
print("[SYSTEM] main.py is loading...") # Immediate check to prove the script is running

import MetaTrader5 as mt5
import config
import threading
import time
from ai_engine import run_ai_analysis
# Importing from 'bot_executor' (singular) to match your filename
from bot_executor import breakout_bot, grid_bot, scalper_bot 

def initialize_broker():
    print("[SYSTEM] Connecting to MetaTrader 5...")
    if not mt5.initialize():
        print(f"[ERROR] MT5 Initialization failed. Error code: {mt5.last_error()}")
        return False
        
    # Attempt login using credentials in config.py
    login_success = mt5.login(
        login=config.LOGIN, 
        password=config.PASSWORD, 
        server=config.SERVER
    )
    
    if not login_success:
        print(f"[ERROR] Failed to login to account {config.LOGIN}. Error: {mt5.last_error()}")
        mt5.shutdown()
        return False
        
    print(f"[SUCCESS] Connected to MT5 Account: {config.LOGIN}")
    return True

def main():
    print("[SYSTEM] Starting TradeFlow AI Master Controller...")
    
    # 1. Start Broker Connection
    if not initialize_broker():
        print("[SYSTEM] Initialization failed. Terminating process.")
        return

    # 2. Define active workers
    workers = [
        threading.Thread(target=run_ai_analysis, name="AI_Engine", daemon=True),
        threading.Thread(target=breakout_bot, name="Breakout_Bot", daemon=True),
        threading.Thread(target=grid_bot, name="Grid_Bot", daemon=True),
        threading.Thread(target=scalper_bot, name="Scalper_Bot", daemon=True),
    ]

    # 3. Spin up all workers concurrently
    for worker in workers:
        worker.start()
        print(f"[SYSTEM] Thread started: {worker.name}")

    # 4. Global Keep-Alive & Emergency Control Loop
    try:
        while True:
            account_info = mt5.account_info()
            if account_info is not None:
                equity = account_info.equity
                balance = account_info.balance
                drawdown_pct = ((equity - balance) / balance) * 100
                
                # Check for critical drawdown threshold trigger
                if drawdown_pct <= config.state.daily_drawdown_limit:
                    print(f"[CRITICAL] Drawdown limit hit ({drawdown_pct:.2%}). Activating killswitch!")
                    with config.state.lock:
                        config.state.system_active = False
                    break
                    
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[SYSTEM] Shutting down systems manually...")
        
    finally:
        # Clear connections
        with config.state.lock:
            config.state.system_active = False
        mt5.shutdown()
        print("[SYSTEM] All processes closed safely.")

# THIS IS THE CRITICAL EXECUTION ENTRY POINT
if __name__ == "__main__":
    print("[SYSTEM] __main__ block triggered. Invoking main()...")
    main()