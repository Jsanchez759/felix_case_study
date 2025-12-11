# Send Money Agent – Google ADK Implementation

A conversational AI agent built with **Google ADK** that guides users through the process of sending money internationally by collecting transfer details naturally.  
The agent extracts key information, validates business rules, tracks progress across the session, and generates a complete transfer summary.

## ✨ Features

- **Conversational Extraction**: Identifies amount, currency, country, delivery method, and recipient name from free-form user input.
- **Progressive Data Gathering**: Detects missing fields and asks targeted follow-up questions.
- **Business Rule Validation**: Ensures input matches configured limits, allowed currencies, countries, and delivery methods.
- **Stateful Conversations**: Stores transfer state in ADK’s session storage across multiple turns.
- **Corrections Supported**: Users can update any detail at any point.
- **Readable Summaries**: Generates a clean confirmation summary when complete.
- **Production-Ready Tools**: Clear separation between LLM behavior and deterministic Python logic.

## 📁 Project Structure

send_money_agent/
├── agent.py # Main ADK agent with LLM instructions and callbacks
├── tools.py # Extraction, validation, completeness checks, summary generation
├── config_loader.py # Loads config.yaml into memory
└── config.yaml # Business rules (countries, currencies, limits, methods)

## 🧠 Key Components

### 1. **Transfer State (ADK Session State)**  
The agent maintains a persistent state across turns including:

- `amount`
- `currency`
- `recipient_name`
- `recipient_country`
- `delivery_method`
- `purpose`
- `status`
- `is_complete`
- `completion_percentage`
- `conversation_turns`
- `ready_for_confirmation`

Tools update this state directly through `tool_context.state`.

---

### 2. **Extraction Logic (`extract_and_update_transfer`)**
- Parses free-form text using regex and keyword matching.
- Updates state with any detected fields.
- Increments conversation turn count.
- Returns structured extraction results for the LLM to interpret.

Extracts:

- Numeric amounts (`500`, `$1,000.50`, etc.)
- Currencies by keyword or symbol
- Countries from config list
- Delivery methods (`bank_transfer`, `cash_pickup`, `mobile_wallet`, `home_delivery`)
- Recipient names (`"to Maria Lopez"`)

### 3. **Validation (`validate_current_transfer`)**
Checks each populated field against rules in `config.yaml`:

- Amount within `min_amount` and `max_amount`
- Supported currency
- Allowed country
- Delivery method permitted

Returns:
- `is_valid: true/false`
- `errors: [...]`

### 4. **Completeness (`check_transfer_completeness`)**
Determines if the required fields are present:

- amount  
- currency  
- recipient_name  
- recipient_country  
- delivery_method  

Also writes to state:

- `is_complete`
- `completion_percentage`
- `missing_fields`

---

### 5. **Summary Generation (`generate_transfer_summary`)**
Creates a user-friendly summary:
💰 Amount: USD 500.00
👤 Recipient: Maria Garcia
🌍 Destination: Mexico
📦 Delivery: Cash Pickup
📝 Purpose: (optional)


Updates state:

- `ready_for_confirmation = True`

## 🌍 Supported Features (Configured via YAML)

- **Countries**: From `supported_countries`
- **Currencies**: From `supported_currencies`
- **Delivery Methods**: From `delivery_methods`
- **Amount Limits**: From `transfer_limits.min_amount` and `.max_amount`

All values are easily modifiable without touching code.


## 🧩 Design Principles

- **LLM handles conversation**
Prompts drive the dialogue; no logic is hidden inside the model.

- **Python tools handle business logic**
Extraction, validation, and state updates are deterministic and testable.

- **State belongs to ADK**
Tools mutate tool_context.state, and ADK persists deltas automatically.

- **Separation of concerns**

LLM = natural language

Tools = logic

Config = rules

- **Extensibility**
New fields, new countries, or new delivery methods require minimal changes.