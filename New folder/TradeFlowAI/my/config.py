# config.py
import threading

# --- Broker Credentials ---
LOGIN = 201997328 
PASSWORD = "#Riss070167"
SERVER = "Deriv-Demo"

# --- Market Target Settings ---
TARGET_SYMBOLS = ["Volatility 75 Index" ,"Volatility 10 Index", "Volatility 100 Index"]          # Change this to the exact Volatility asset name in your MT5
SWING_PERIOD = 3                   
ATR_PERIOD = 14                    

# --- Thread-Safe Global Trading State ---
class SystemState:
    def __init__(self):
        self.lock = threading.Lock()
        self.market_regime = "ranging"
        self.risk_multiplier = 1.0
        self.allowed_bots = ["grid", "scalper"]
        
        # Security overrides
        self.system_active = True
        self.daily_drawdown_limit = -5.0


# --- Risk Management Settings ---
RISK_PER_TRADE_PCT = 0.01  # Represents 1% risk per trade layout
state = SystemState()