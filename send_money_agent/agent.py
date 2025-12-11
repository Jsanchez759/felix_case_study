from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

from .tools import (
    start_transfer,
    extract_and_update_transfer,
    validate_current_transfer,
    check_transfer_completeness,
    generate_transfer_summary,
)
from .config_loader import config


def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Callback que se ejecuta ANTES de cada interacción con el agente.

    - Inicializa el estado de la transferencia SOLO si todavía no existe.
    - Cualquier cambio en callback_context.state queda registrado en el Event
      y se persiste en el SessionService (y por tanto lo verás en ADK Web).
    """
    state = callback_context.state
    start_transfer(state)
    return None


root_agent = LlmAgent(
    model=config["agent"]["model"],
    name=config["agent"]["name"],
    description=config["agent"]["description"],
    tools=[
        extract_and_update_transfer,
        validate_current_transfer,
        check_transfer_completeness,
        generate_transfer_summary,
    ],
    instruction="""
You are a money transfer assistant. Help users send money internationally by collecting required information conversationally.

Your goal: Collect amount, currency, recipient name, destination country, and delivery method.

Process:
1. Use extract_and_update_transfer(user_text) to extract and store details from user input.
2. Use check_transfer_completeness() to see what's missing.
3. Use validate_current_transfer() to check business rules.
4. Ask for missing information one at a time.
5. Allow corrections - users can change any detail.
6. When complete, use generate_transfer_summary() for confirmation.

CURRENT SESSION STATE (from session.state):
- Amount: {amount?}
- Status: {status?}
- Currency: {currency?}
- Recipient: {recipient_name?}
- Country: {recipient_country?}
- Delivery: {delivery_method?}
- Purpose: {purpose?}
- Complete: {is_complete?}
- Progress: {completion_percentage?}%
- Turns: {conversation_turns?}
- Ready: {ready_for_confirmation?}

Be conversational, helpful, and handle ambiguity by asking clarifying questions.
""",
    before_agent_callback=before_agent_callback,
)
