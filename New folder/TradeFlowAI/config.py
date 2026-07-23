# config.py
import threading

# --- Broker Credentials ---
LOGIN = 201997328  # Replace with your MT5 account number
PASSWORD = "#Riss070167"
SERVER = "Deriv-Demo"

# --- Thread-Safe Global Trading State ---
class SystemState:
    def __init__(self):
        self.lock = threading.Lock()
        
        # Operational parameters controlled by the AI Engine
        self.market_regime = "ranging"       # Options: trending_up, trending_down, ranging, volatile_pause
        self.risk_multiplier = 1.0           # Scale down lot sizes if risk increases (e.g., 0.5)
        self.allowed_bots = ["grid", "scalper"]  # Active bots allowed to trade
        
        # Security overrides
        self.system_active = True            # Master switch
        self.daily_drawdown_limit = -5.0     # Max percent drawdown allowed (-5%)

state = SystemState()