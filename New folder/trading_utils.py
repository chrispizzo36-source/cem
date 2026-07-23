# trading_utils.py
import MetaTrader5 as mt5

def send_market_order(symbol, order_type, volume, magic_number, stop_loss=0.0, take_profit=0.0):
    """
    Sends a market buy or sell order to MetaTrader 5.
    
    Parameters:
      - symbol (str): The asset to trade, e.g., "XAUUSD"
      - order_type (int): mt5.ORDER_TYPE_BUY or mt5.ORDER_TYPE_SELL
      - volume (float): The lot size, e.g., 0.01 or 0.1
      - magic_number (int): Unique identifier for the bot sending the order
      - stop_loss (float): Price for the emergency exit (safety net)
      - take_profit (float): Price target to collect profits
    """
    # 1. Fetch current price tick (Bid/Ask)
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print(f"[TRADE ERROR] Could not get tick info for {symbol}. Order rejected.")
        return None
        
    # Buy at the Ask price; Sell at the Bid price
    price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid

    # 2. Build the MT5 order structure
    request = {
        "action": mt5.TRADE_ACTION_DEAL,      # Immediate execution
        "symbol": symbol,
        "volume": float(volume),
        "type": order_type,
        "price": float(price),
        "sl": float(stop_loss) if stop_loss > 0 else 0.0,
        "tp": float(take_profit) if take_profit > 0 else 0.0,
        "deviation": 10,                      # Maximum allowed slippage (in points)
        "magic": int(magic_number),           # Ties the trade to a specific bot
        "comment": f"TradeFlowAI Bot {magic_number}",
        "type_time": mt5.ORDER_TIME_GTC,       # Good 'Til Cancelled
        "type_filling": mt5.ORDER_FILLING_IOC, # Immediate Or Cancel
    }

    # 3. Send the order request to the MT5 terminal
    result = mt5.order_send(request)
    
    # 4. Handle and print the result
    if result is None:
        print(f"[TRADE ERROR] Order failed entirely. No response from MT5.")
        return None
        
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"[TRADE ERROR] Order rejected for Magic {magic_number}. Code: {result.retcode} | Reason: {result.comment}")
    else:
        print(f"[TRADE SUCCESS] Trade opened successfully! Ticket: {result.order} | Price: {result.price} | SL: {result.sl} | TP: {result.tp}")
        
    return result