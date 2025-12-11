from send_money_agent.agent import send_money_agent

def main():
    """Demo the Send Money Agent with Session State"""
    print("🏦 Send Money Agent - Session State Demo")
    print("==========================================\n")
    
    print("This agent uses ADK session state to track transfer details.")
    print("Each tool updates the session state automatically.\n")
    
    # Demo inputs showing session state management
    demo_inputs = [
        "I want to send money",
        "$500 USD to Maria Garcia in Mexico", 
        "Cash pickup please",
        "Actually, change the amount to $750",
        "Yes, proceed"
    ]
    
    print("Agent: Hi! I can help you send money internationally. What would you like to do?\n")
    
    for user_input in demo_inputs:
        print(f"User: {user_input}")
        
        # Agent uses session state via ToolContext
        try:
            response = send_money_agent.process(user_input)
            print(f"Agent: {response}\n")
        except Exception as e:
            print(f"Agent: I encountered an issue: {e}\n")
    
    print("✅ Demo complete! Session state managed all transfer details.")

if __name__ == "__main__":
    main()
