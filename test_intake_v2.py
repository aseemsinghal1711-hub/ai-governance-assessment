"""
Test the v2 intake agent in the terminal, with evidence-attaching capability.

Suggested test flow:
1. Describe an AI system
2. When asked about AI policy, say YES and provide path: sample_ai_policy.txt
3. When asked about bias testing, say YES and provide path: sample_bias_results.xlsx
4. Other questions, answer naturally

Type 'profile' to see current state including evidence.
Type 'quit' to exit and see final profile.
"""
from intake_agent_v2 import build_intake_agent_v2, ProfileStateV2
from langchain_core.messages import HumanMessage

profile = ProfileStateV2()
agent = build_intake_agent_v2(profile)

messages = []

print("=" * 70)
print("AI Governance Intake Agent v2 - Terminal Test (with evidence)")
print("=" * 70)
print("Type 'profile' at any time to see current state.")
print("Type 'quit' to exit.")
print()
print("Sample evidence files available in this folder:")
print("  - sample_ai_policy.txt          (an AI policy)")
print("  - sample_bias_results.xlsx      (bias testing results)")
print("  - sample_ai_inventory.csv       (AI system inventory)")
print("  - sample_scanned_methodology.pdf (a scanned methodology doc)")
print("=" * 70)

# Let the agent speak first
initial_response = agent.invoke({
    "messages": [HumanMessage(content="Hi, I'm ready to start.")]
})
agent_message = initial_response["messages"][-1].content
print(f"\nAgent: {agent_message}\n")
messages = initial_response["messages"]

while True:
    user_input = input("You: ").strip()
    
    if not user_input:
        continue
    
    if user_input.lower() == "quit":
        break
    
    if user_input.lower() == "profile":
        print("\n--- Current Profile State ---")
        state = profile.to_dict()
        print("Fields:")
        for k, v in state["fields"].items():
            print(f"  {k}: {v}")
        print(f"\nEvidence attachments ({len(state['evidence'])}):")
        for e in state["evidence"]:
            print(f"  - {e['field_name']}: {e['filename']} "
                  f"({e['file_type']}, {len(e['extracted_text'])} chars)")
        completeness = profile.get_completeness()
        print(f"\nCompleteness: {completeness['completed']}/{completeness['total_required']}")
        if completeness["claimed_no_evidence"]:
            print(f"Claimed no evidence: {', '.join(completeness['claimed_no_evidence'])}")
        print()
        continue
    
    messages.append(HumanMessage(content=user_input))
    result = agent.invoke({"messages": messages})
    messages = result["messages"]
    
    agent_message = messages[-1].content
    print(f"\nAgent: {agent_message}\n")
    
    if "INTAKE COMPLETE" in agent_message:
        print("=" * 70)
        print("Final profile:")
        print("=" * 70)
        state = profile.to_dict()
        for k, v in state["fields"].items():
            print(f"  {k}: {v}")
        print(f"\nEvidence attachments: {len(state['evidence'])}")
        for e in state["evidence"]:
            print(f"  - {e['field_name']}: {e['filename']}")
        break