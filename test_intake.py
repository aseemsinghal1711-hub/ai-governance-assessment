"""
Test the intake agent in the terminal.

This simulates a multi-turn conversation. You type, the agent responds,
the profile fills in. Type 'quit' to exit and see the final profile.
"""
from intake_agent import build_intake_agent, ProfileState
from langchain_core.messages import HumanMessage

# Initialize the profile and agent
profile = ProfileState()
agent = build_intake_agent(profile)

# Track conversation history
messages = []

print("=" * 70)
print("AI Governance Intake Agent - Terminal Test")
print("=" * 70)
print("Type your responses. Type 'quit' to exit and see the final profile.")
print("Type 'profile' at any time to see the current profile state.")
print("=" * 70)

# Start the conversation by letting the agent speak first
initial_response = agent.invoke({"messages": [HumanMessage(content="Hi, I'm ready to start.")]})
agent_message = initial_response["messages"][-1].content
print(f"\n🤖 Agent: {agent_message}\n")
messages = initial_response["messages"]

while True:
    user_input = input("👤 You: ").strip()
    
    if not user_input:
        continue
    
    if user_input.lower() == "quit":
        break
    
    if user_input.lower() == "profile":
        print("\n--- Current Profile State ---")
        for k, v in profile.to_dict().items():
            print(f"  {k}: {v}")
        completeness = profile.get_completeness()
        print(f"\n  Completeness: {completeness['completed']}/{completeness['total_required']}")
        if completeness["missing"]:
            print(f"  Missing: {', '.join(completeness['missing'])}")
        print()
        continue
    
    # Add user message to the running conversation
    messages.append(HumanMessage(content=user_input))
    
    # Invoke the agent with the full conversation history
    result = agent.invoke({"messages": messages})
    
    # Update messages with whatever the agent produced
    messages = result["messages"]
    
    # Print the agent's last response
    agent_message = messages[-1].content
    print(f"\n🤖 Agent: {agent_message}\n")
    
    # Check if the agent signaled completion
    if "INTAKE COMPLETE" in agent_message:
        print("=" * 70)
        print("✅ Intake complete! Final profile:")
        print("=" * 70)
        for k, v in profile.to_dict().items():
            print(f"  {k}: {v}")
        break

# Show final profile if we exited via 'quit'
if "INTAKE COMPLETE" not in (agent_message if 'agent_message' in dir() else ""):
    print("\n" + "=" * 70)
    print("Final profile state at exit:")
    print("=" * 70)
    for k, v in profile.to_dict().items():
        print(f"  {k}: {v}")
    completeness = profile.get_completeness()
    print(f"\nCompleteness: {completeness['completed']}/{completeness['total_required']}")