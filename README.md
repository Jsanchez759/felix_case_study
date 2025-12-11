# Send Money Agent - Production Grade Implementation

A conversational AI agent built with Google ADK that helps users send money internationally by collecting transfer details through natural conversation.

## Features

- **Natural Language Processing**: Extracts transfer information from conversational input
- **Step-by-Step Guidance**: Asks for missing information one piece at a time
- **Validation**: Validates all transfer details against business rules
- **Corrections**: Allows users to update or correct information
- **State Management**: Maintains conversation state across multiple turns
- **Production Ready**: Clean architecture with proper error handling

## Architecture

```
send_money_agent/
├── agent.py          # Main agent with LLM integration
├── tools.py          # ADK tools for validation and summaries
├── config.py         # Configuration constants
├── config.yaml       # YAML configuration
├── utils.py          # Utility functions
└── exceptions.py     # Custom exceptions
```

## Key Components

### 1. TransferDetails Model
- Tracks all transfer information (amount, currency, recipient, etc.)
- Provides completion status and missing field detection
- Generates human-readable summaries

### 2. TransferProcessor
- Extracts information from natural language input using regex
- Validates extracted data against business rules
- Handles corrections and updates

### 3. SendMoneyState
- Manages conversation state
- Processes user input and generates appropriate responses
- Integrates with the LLM for natural conversation flow

### 4. ADK Tools
- `TransferValidationTool`: Validates complete transfer details
- `TransferSummaryTool`: Generates formatted summaries

## Supported Features

- **Countries**: USA, Mexico, Canada, UK, Spain, France, Germany, Italy, Brazil, Argentina, Colombia
- **Currencies**: USD, EUR, GBP, MXN, CAD, BRL, ARS, COP
- **Delivery Methods**: Bank transfer, Cash pickup, Mobile wallet, Home delivery
- **Amount Limits**: $1 - $10,000 USD

## Usage

```python
from send_money_agent.agent import send_money_agent, SendMoneyState

# Initialize state
state = SendMoneyState()

# Process user input
response = state.process_input("I want to send $500 to Maria in Mexico")
print(response)  # "Got it! $500. Which country are you sending to?"

# Continue conversation
response = state.process_input("Cash pickup please")
print(response)  # Shows complete transfer summary
```

## Example Conversation

```
User: I want to send money
Agent: How much would you like to send?

User: $500 USD to Maria Garcia in Mexico
Agent: Got it! $500 in USD to Maria Garcia to Mexico. How should they receive it?

User: Cash pickup
Agent: Perfect! Here's your transfer summary:
💰 Amount: USD 500.00
👤 Recipient: Maria Garcia
🌍 Destination: Mexico
📦 Delivery: Cash Pickup

Ready to send!
```

## Design Principles

1. **LLM Handles Conversation**: The LLM manages natural language understanding and response generation
2. **Code Handles Logic**: Business rules, validation, and state management in code
3. **Minimal Complexity**: Simple, focused implementation without over-engineering
4. **Production Ready**: Proper error handling, validation, and clean architecture
5. **Extensible**: Easy to add new countries, currencies, or delivery methods

## Running the Demo

```bash
python main.py
```

This will run a demonstration showing the agent collecting transfer details through a simulated conversation.