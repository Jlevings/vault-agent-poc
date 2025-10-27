from fastapi.testclient import TestClient

from app.main import app


def test_chat_endpoint_returns_stub_response(monkeypatch):
    client = TestClient(app)
    monkeypatch.setattr(
        "app.main.agent.handle_prompt",
        lambda message: {
            "answer": "Example answer",
            "products": [],
            "keywords": ["example"],
        },
    )

    response = client.post("/api/v1/chat", json={"message": "Need automation"})
    assert response.status_code == 200
    data = response.json()

    assert "answer" in data
    assert isinstance(data["products"], list)
    assert isinstance(data["keywords"], list)
