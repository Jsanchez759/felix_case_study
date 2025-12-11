import yaml
import os
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        # Fallback configuration if YAML file not found
        return {
            'agent': {
                'name': 'send_money_agent',
                'model': 'gemini-2.5-flash',
                'description': 'Money transfer agent for collecting transfer details'
            },
            'transfer_limits': {
                'min_amount': 1.0,
                'max_amount': 10000.0
            },
            'supported_countries': ['USA', 'Mexico', 'Canada', 'UK', 'Spain', 'France', 'Germany', 'Italy', 'Brazil', 'Argentina', 'Colombia'],
            'supported_currencies': ['USD', 'EUR', 'GBP', 'MXN', 'CAD', 'BRL', 'ARS', 'COP'],
            'delivery_methods': ['bank_transfer', 'cash_pickup', 'mobile_wallet', 'home_delivery']
        }

# Global config instance
config = load_config()