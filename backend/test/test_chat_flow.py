# backend/test/test_chat_flow.py

import json

import requests

BASE_URL = "http://localhost:8000/api"

def test_chat_flow():
    # Start conversation
    response = requests.post(f"{BASE_URL}/chat/message", json={
        "message": "Hi, I'd like to track my investments"
    })
    data = response.json()
    session_id = data["session_id"]
    print(f"Session started: {session_id}")
    print(f"Bot: {data['message']}\n")

    # Test conversations
    test_messages = [
        "I have 50 shares of Tesla",
        "I also own 2 Bitcoin",
        "My house is worth $500k with a $300k mortgage from Chase",
        "I have $25000 in my Bank of America savings",
        "That's everything"
    ]

    for msg in test_messages:
        print(f"User: {msg}")
        response = requests.post(f"{BASE_URL}/chat/message", json={
            "message": msg,
            "session_id": session_id
        })
        data = response.json()
        print(f"Bot: {data['message']}")
        print(f"Show form: {data.get('show_form', False)}")
        print(f"Assets count: {data.get('portfolio_summary', {}).get('assets', 0)}\n")

        if data.get('show_form'):
            print("Form data:", json.dumps(data.get('form_data'), indent=2))

    # Get current portfolio
    response = requests.get(f"{BASE_URL}/chat/session/{session_id}/portfolio")
    portfolio_data = response.json()
    print(f"\nFinal portfolio: {json.dumps(portfolio_data, indent=2)}")

    # Submit for analysis
    print("\nSubmitting for analysis...")
    response = requests.post(f"{BASE_URL}/chat/submit-portfolio", json={
        "session_id": session_id,
        "portfolio": portfolio_data["portfolio"],
        "analyze_immediately": True
    })
    result = response.json()

    if result.get("success"):
        print("Analysis completed!")
        if "analysis" in result:
            print(f"Recommendations: {result['analysis']['recommendations']}")

if __name__ == "__main__":
    test_chat_flow()
