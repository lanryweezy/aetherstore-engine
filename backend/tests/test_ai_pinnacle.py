import pytest
from fastapi.testclient import TestClient

def test_health_check(test_client: TestClient):
    response = test_client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_system_telemetry(test_client: TestClient):
    response = test_client.get("/api/ai/system-telemetry")
    assert response.status_code == 200
    data = response.json()
    assert "maverick" in data
    assert "sapiens" in data
    assert "dtc" in data

def test_stylist_chat(test_client: TestClient):
    payload = {"message": "Hello Maverick", "user_id": "test_user"}
    response = test_client.post("/api/ai/stylist-chat", json=payload)
    assert response.status_code == 200
    assert "reply" in response.json()

def test_trend_momentum(test_client: TestClient):
    response = test_client.get("/api/intelligence/trend-momentum")
    assert response.status_code == 200
    assert "trending" in response.json()

def test_predict_popularity(test_client: TestClient):
    payload = {"category": "tops", "id": "test_prod"}
    response = test_client.post("/api/intelligence/predict-popularity", json=payload)
    assert response.status_code == 200
    assert "predicted_likes" in response.json()

def test_match_outfit(test_client: TestClient):
    payload = {"top_ids": ["top1"], "bottom_ids": ["bottom1"]}
    response = test_client.post("/api/intelligence/match-outfit", json=payload)
    assert response.status_code == 200
    assert "compatibility_score" in response.json()

def test_generate_locomotion(test_client: TestClient):
    response = test_client.post("/api/ai/generate-locomotion?user_id=test&style=catwalk")
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_analyze_movement_context(test_client: TestClient):
    response = test_client.post("/api/ai/analyze-movement-context?video_stream_id=test_stream")
    assert response.status_code == 200
    assert "detected_action" in response.json()

def test_translate_fashion(test_client: TestClient):
    response = test_client.post("/api/ai/translate-fashion?text=silk dress&target_lang=fr")
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_social_group_analysis(test_client: TestClient):
    payload = ["user1", "user2"]
    response = test_client.post("/api/ai/social/analyze-group?session_id=test_session", json=payload)
    assert response.status_code == 200
    assert "collective_vibe" in response.json()
