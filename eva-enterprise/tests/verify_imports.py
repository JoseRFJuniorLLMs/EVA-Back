import sys
import os

# Add project root to path
sys.path.append("/eva-enterprise")

try:
    print("Verifying imports...")
    from main import app
    print("Successfully imported main.app")
    
    from api import routes_config, routes_idosos, routes_medicamentos, routes_agendamentos, routes_alertas, routes_pagamentos, routes_extras
    print("Successfully imported all routers")
    
    print("Verification Passed!")
except Exception as e:
    print(f"Verification Failed: {e}")
    sys.exit(1)
