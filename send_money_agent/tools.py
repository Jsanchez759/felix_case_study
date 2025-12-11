import re
from typing import Dict, Any

from google.adk.tools.tool_context import ToolContext
from .config_loader import config


def start_transfer(state: Dict[str, Any]) -> None:
    """
    Start a new transfer by initializing the session state.

    Solo inicializa si no existe el estado previo.
    Se llama desde before_agent_callback, así que se ejecuta en cada turno,
    pero NO pisa valores si 'status' ya existe.
    """
    if "status" not in state:
        state["amount"] = 0.0
        state["status"] = "started"
        state["currency"] = ""
        state["recipient_name"] = ""
        state["recipient_country"] = ""
        state["delivery_method"] = ""
        state["purpose"] = ""
        state["is_complete"] = False
        state["completion_percentage"] = 0.0
        state["conversation_turns"] = 0
        state["ready_for_confirmation"] = False


def extract_and_update_transfer(
    tool_context: ToolContext,
    user_text: str,
) -> Dict[str, Any]:
    """
    Extract transfer details from user input and update session state.

    IMPORTANTE:
    - Modificamos tool_context.state directamente.
    - ADK registra el delta en EventActions.state_delta y lo persiste en session.state.

    Args:
        tool_context: ToolContext que trae el session.state actual.
        user_text: Texto libre del usuario.

    Returns:
        dict: Resumen de campos extraídos y estado actual.
    """
    state = tool_context.state
    text = user_text.lower()
    extracted: Dict[str, Any] = {}

    # Extract amount (ej: 100, 1,000.50, $200)
    amount_match = re.search(r"\$?(\d+(?:,\d{3})*(?:\.\d{2})?)", user_text)
    if amount_match:
        try:
            amount = float(amount_match.group(1).replace(",", ""))
            extracted["amount"] = amount
            state["amount"] = amount
        except ValueError:
            pass

    # Extract currency
    currencies = {c.lower(): c for c in config["supported_currencies"]}
    for curr_lower, curr_upper in currencies.items():
        if curr_lower in text or (curr_lower == "usd" and "$" in user_text):
            extracted["currency"] = curr_upper
            state["currency"] = curr_upper
            break

    # Extract country
    countries = {c.lower(): c for c in config["supported_countries"]}
    for country_lower, country_proper in countries.items():
        if country_lower in text:
            extracted["recipient_country"] = country_proper
            state["recipient_country"] = country_proper
            break

    # Extract delivery method (muy simplificado)
    if any(word in text for word in ["bank", "transfer", "account"]):
        extracted["delivery_method"] = "bank_transfer"
        state["delivery_method"] = "bank_transfer"
    elif any(word in text for word in ["cash", "pickup"]):
        extracted["delivery_method"] = "cash_pickup"
        state["delivery_method"] = "cash_pickup"
    elif any(word in text for word in ["mobile", "wallet"]):
        extracted["delivery_method"] = "mobile_wallet"
        state["delivery_method"] = "mobile_wallet"
    elif any(word in text for word in ["home", "delivery"]):
        extracted["delivery_method"] = "home_delivery"
        state["delivery_method"] = "home_delivery"

    # Extract recipient name (muy heurístico)
    name_match = re.search(
        r"(?:to|for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        user_text,
        re.IGNORECASE,
    )
    if name_match:
        name = name_match.group(1).title()
        extracted["recipient_name"] = name
        state["recipient_name"] = name

    # Update conversation count
    state["conversation_turns"] = state.get("conversation_turns", 0) + 1

    return {
        "status": "success",
        "extracted_fields": list(extracted.keys()),
        "extracted_info": extracted,
        "current_state_summary": {
            "amount": state.get("amount"),
            "currency": state.get("currency"),
            "recipient": state.get("recipient_name"),
            "country": state.get("recipient_country"),
            "delivery": state.get("delivery_method"),
        },
    }


def validate_current_transfer(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Validate current transfer details in session state.

    Args:
        tool_context: ToolContext con session.state.

    Returns:
        dict: Resultado de validación (is_valid + lista de errores).
    """
    state = tool_context.state
    errors = []

    # Validate amount
    amount = state.get("amount")
    if amount:
        min_amt = config["transfer_limits"]["min_amount"]
        max_amt = config["transfer_limits"]["max_amount"]
        if amount < min_amt or amount > max_amt:
            errors.append(f"Amount must be between ${min_amt} and ${max_amt:,.0f}")

    # Validate currency
    currency = state.get("currency")
    if currency and currency not in config["supported_currencies"]:
        errors.append(
            "Unsupported currency. Supported: "
            + ", ".join(config["supported_currencies"])
        )

    # Validate country
    country = state.get("recipient_country")
    if country and country not in config["supported_countries"]:
        errors.append(
            "Unsupported country. Supported: "
            + ", ".join(config["supported_countries"])
        )

    # Validate delivery method
    method = state.get("delivery_method")
    if method and method not in config["delivery_methods"]:
        errors.append(
            "Unsupported delivery method. Supported: "
            + ", ".join(config["delivery_methods"])
        )

    return {
        "status": "success" if not errors else "error",
        "is_valid": len(errors) == 0,
        "errors": errors,
    }


def check_transfer_completeness(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Check what transfer information is missing from session state.

    Args:
        tool_context: ToolContext con session.state.

    Returns:
        dict: Estado de completitud (missing_fields, completion_percentage, etc.).
    """
    state = tool_context.state
    required = [
        "amount",
        "currency",
        "recipient_name",
        "recipient_country",
        "delivery_method",
    ]
    missing = [field for field in required if not state.get(field)]

    is_complete = len(missing) == 0
    completion_pct = ((len(required) - len(missing)) / len(required)) * 100

    state["is_complete"] = is_complete
    state["completion_percentage"] = completion_pct
    state["missing_fields"] = missing

    return {
        "status": "success",
        "is_complete": is_complete,
        "missing_fields": missing,
        "completion_percentage": completion_pct,
        "collected_fields": {
            "amount": state.get("amount"),
            "currency": state.get("currency"),
            "recipient_name": state.get("recipient_name"),
            "recipient_country": state.get("recipient_country"),
            "delivery_method": state.get("delivery_method"),
        },
    }


def generate_transfer_summary(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Generate transfer summary from session state.

    Args:
        tool_context: ToolContext con session.state.

    Returns:
        dict: Resumen de la transferencia o error si faltan campos.
    """
    state = tool_context.state
    required = [
        "amount",
        "currency",
        "recipient_name",
        "recipient_country",
        "delivery_method",
    ]
    missing = [field for field in required if not state.get(field)]

    if missing:
        return {
            "status": "error",
            "error_message": f"Cannot generate summary. Missing: {', '.join(missing)}",
        }

    summary = f"""💰 Amount: {state['currency']} {state['amount']:,.2f}
👤 Recipient: {state['recipient_name']}
🌍 Destination: {state['recipient_country']}
📦 Delivery: {state['delivery_method'].replace('_', ' ').title()}
{f"📝 Purpose: {state['purpose']}" if state.get('purpose') else ''}

✅ Ready to send!"""

    state["ready_for_confirmation"] = True

    return {
        "status": "success",
        "summary": summary,
        "transfer_details": {
            "amount": state["amount"],
            "currency": state["currency"],
            "recipient_name": state["recipient_name"],
            "recipient_country": state["recipient_country"],
            "delivery_method": state["delivery_method"],
            "purpose": state.get("purpose", ""),
        },
    }
