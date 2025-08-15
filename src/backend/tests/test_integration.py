# backend/test/test_integration.py

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_full_chat_flow():
    # Start chat
    response = client.post("/api/chat/message", json={"message": "Hi"})
    assert response.status_code == 200
    data = response.json()
    session_id = data["session_id"]

    # Add assets
    response = client.post(
        "/api/chat/message",
        json={
            "message": "I have 100 AAPL shares and 2 Bitcoin",
            "session_id": session_id,
        },
    )
    assert response.status_code == 200

    # Complete portfolio
    response = client.post(
        "/api/chat/message", json={"message": "That's all", "session_id": session_id}
    )
    data = response.json()
    assert data.get("show_form")

    # Submit portfolio
    response = client.post(
        "/api/chat/submit-portfolio",
        json={
            "session_id": session_id,
            "portfolio": {
                "assets": [
                    {"type": "stock", "ticker": "AAPL", "shares": 100},
                    {"type": "crypto", "symbol": "BTC", "amount": 2},
                ]
            },
            "analyze_immediately": False,  # Skip analysis for test
        },
    )
    assert response.status_code == 200
    assert response.json()["success"]
