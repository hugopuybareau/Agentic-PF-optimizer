# backend/test/test_chat_agent.py

from backend.app.agents.chat_agent import ChatAgent
from backend.app.models import ChatSession


def test_intent_classification():
    agent = ChatAgent()

    test_cases = [
        ("I have 100 shares of Apple", "add_asset"),
        ("Remove Tesla from my portfolio", "remove_asset"),
        ("Show me my current portfolio", "list_assets"),
        ("That's all my investments", "complete_portfolio"),
        ("Hello", "greeting"),
        ("What is a good PE ratio?", "ask_question")
    ]

    for message, expected_intent in test_cases:
        state = {
            "session": ChatSession(session_id="test"),
            "user_message": message,
            "entities": {},
            "intent": None
        }
        result = agent._classify_intent(state) # type: ignore
        assert result["intent"] == expected_intent

def test_entity_extraction(mock_entity_extraction):
    agent = ChatAgent()

    test_cases = [
        ("I have 100 shares of AAPL", {"type": "stock", "ticker": "AAPL", "shares": 100}),
        ("I own 0.5 Bitcoin", {"type": "crypto", "symbol": "BTC", "amount": 0.5}),
        ("My house at 123 Main St is worth $500k", {"type": "real_estate", "address": "123 Main St", "value": 500000})
    ]

    for message, expected_entities in test_cases:
        state = {
            "session": ChatSession(session_id="test"),
            "user_message": message,
            "intent": "add_asset",
            "entities": {}
        }
        result = agent._extract_entities(state) # type: ignore

        for key, value in expected_entities.items():
            assert key in result["entities"]
            assert result["entities"][key] == value

def test_portfolio_building(mock_entity_extraction):
    agent = ChatAgent()
    session_id = "test-session"

    # Test adding assets
    messages = [
        "I have 100 shares of Apple",
        "I also have 1 Bitcoin",
        "I have $50000 in savings"
    ]

    for msg in messages:
        result = agent.process_message(session_id, msg)
        assert "error" not in result

    # Check portfolio
    portfolio = agent.get_session_portfolio(session_id)
    assert portfolio is not None
    assert len(portfolio.assets) == 3

    # Check asset types
    asset_types = {asset.type for asset in portfolio.assets}
    assert asset_types == {"stock", "crypto", "cash"}
