import re
from typing import Optional

def extract_amount(text: str) -> Optional[float]:
    """Extract amount from text"""
    match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', text)
    if match:
        try:
            return float(match.group(1).replace(',', ''))
        except ValueError:
            pass
    return None

def format_currency(amount: float, currency: str) -> str:
    """Format currency for display"""
    symbols = {"USD": "$", "EUR": "€", "GBP": "£"}
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"

def validate_amount(amount: float) -> bool:
    """Validate transfer amount"""
    return isinstance(amount, (int, float)) and 0 < amount <= 10000