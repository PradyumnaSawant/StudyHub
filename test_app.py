from fastapi.testclient import TestClient
from run import app

client = TestClient(app)

def test_landing_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "StudyHub" in response.text
    assert "Verified Materials" in response.text

def test_login_and_dashboard():
    # Login as student
    response = client.post(
        "/login",
        data={"email": "kamonmi@student.edu", "password": "student123"},
        follow_redirects=False
    )
    assert response.status_code == 302
    assert "access_token" in response.cookies

    # Access dashboard with cookie
    dash_res = client.get("/dashboard", cookies=response.cookies)
    assert dash_res.status_code == 200
    assert "Kamonmi" in dash_res.text
    assert "Computer Science" in dash_res.text or "CSE" in dash_res.text

def test_resources_search_and_filter():
    response = client.get("/resources")
    assert response.status_code == 200
    assert "Engineering Resource Catalog" in response.text

    # HTMX Search
    htmx_res = client.get("/resources?query=Graph", headers={"HX-Request": "true"})
    assert htmx_res.status_code == 200
    assert "Graph Algorithms" in htmx_res.text

def test_resource_detail_and_ai_summary():
    # View detail
    detail_res = client.get("/resources/1")
    assert detail_res.status_code == 200
    assert "Graph Algorithms" in detail_res.text

    # Trigger AI summary endpoint
    ai_res = client.post("/resources/1/ai-summary")
    assert ai_res.status_code == 200
    assert "AI Fast-Track Study Breakdown" in ai_res.text or "AI Study Summary" in ai_res.text

def test_verifier_access():
    # Login as verifier
    v_login = client.post(
        "/login",
        data={"email": "faculty.verifier@studyhub.edu", "password": "verifier123"},
        follow_redirects=False
    )
    assert v_login.status_code == 302
    
    # Access Verification Hub
    v_hub = client.get("/verification", cookies=v_login.cookies)
    assert v_hub.status_code == 200
    assert "Faculty Verification Hub" in v_hub.text

def test_admin_access():
    # Login as admin
    a_login = client.post(
        "/login",
        data={"email": "admin@studyhub.edu", "password": "admin123"},
        follow_redirects=False
    )
    assert a_login.status_code == 302

    # Access Admin Panel
    admin_res = client.get("/admin", cookies=a_login.cookies)
    assert admin_res.status_code == 200
    assert "System Administration Control" in admin_res.text

def test_json_api():
    res = client.get("/api/resources")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0

    subj_res = client.get("/api/subjects")
    assert subj_res.status_code == 200
    subjs = subj_res.json()
    assert len(subjs) >= 8

if __name__ == "__main__":
    print("[INFO] Running StudyHub Test Suite...")
    test_landing_page()
    test_login_and_dashboard()
    test_resources_search_and_filter()
    test_resource_detail_and_ai_summary()
    test_verifier_access()
    test_admin_access()
    test_json_api()
    print("[SUCCESS] All 7 Core Test Suites Passed Perfectly!")
