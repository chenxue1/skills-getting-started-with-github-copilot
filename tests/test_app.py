import copy

from fastapi.testclient import TestClient

from src import app as myapp


client = TestClient(myapp.app)


def setup_function():
    # snapshot activities and restore per-test to avoid cross-test state
    global _original_activities
    _original_activities = copy.deepcopy(myapp.activities)


def teardown_function():
    myapp.activities = copy.deepcopy(_original_activities)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # basic sanity checks
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "pytest-user@example.com"

    # ensure email not already present
    assert email not in myapp.activities[activity]["participants"]

    # Signup should succeed
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert email in myapp.activities[activity]["participants"]

    # Duplicate signup should fail
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 400

    # Unregister should succeed
    resp3 = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp3.status_code == 200
    assert email not in myapp.activities[activity]["participants"]

    # Unregistering again should return 404
    resp4 = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp4.status_code == 404


def test_invalid_activity():
    resp = client.post("/activities/NotExist/signup?email=someone@example.com")
    assert resp.status_code == 404
