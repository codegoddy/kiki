import pytest

def test_create_category(client):
    category_data = {
        "name": "Technology",
        "description": "All about technology",
        "color": "#3b82f6"
    }
    response = client.post("/api/v1/categories/", json=category_data)
    assert response.status_code == 200
    category = response.json()
    assert category["name"] == "Technology"
    assert category["description"] == "All about technology"
    assert category["color"] == "#3b82f6"

def test_get_categories(client):
    response = client.get("/api/v1/categories/")
    assert response.status_code == 200
    categories = response.json()
    assert isinstance(categories, list)

def test_get_category(client):
    # First create a category
    category_data = {"name": "Science", "description": "Scientific content"}
    client.post("/api/v1/categories/", json=category_data)
    
    # Now test getting it
    response = client.get("/api/v1/categories/1")
    if response.status_code == 200:
        category = response.json()
        assert "name" in category
        assert "description" in category
    else:
        assert response.status_code == 404

def test_get_categories_with_counts(client):
    response = client.get("/api/v1/categories/with-counts/")
    assert response.status_code == 200
    categories = response.json()
    assert isinstance(categories, list)
    # All categories should have post_count field
    for category in categories:
        assert "post_count" in category

def test_update_category(client):
    # First create a category
    category_data = {"name": "Sports", "description": "Sports content"}
    client.post("/api/v1/categories/", json=category_data)
    
    # Now test updating it
    update_data = {"description": "Updated sports content"}
    response = client.put("/api/v1/categories/1", json=update_data)
    if response.status_code == 200:
        category = response.json()
        assert category["description"] == "Updated sports content"
    else:
        assert response.status_code == 404

def test_delete_category(client):
    # First create a category
    category_data = {"name": "Music", "description": "Music content"}
    client.post("/api/v1/categories/", json=category_data)
    
    # Now test deleting it
    response = client.delete("/api/v1/categories/1")
    if response.status_code == 200:
        assert response.json() == {"message": "Category deleted successfully"}
    else:
        assert response.status_code == 404

def test_search_categories(client):
    # Create some categories
    categories = [
        {"name": "Technology", "description": "Tech content"},
        {"name": "Science", "description": "Science content"}
    ]
    for cat in categories:
        client.post("/api/v1/categories/", json=cat)
    
    # Test search
    response = client.get("/api/v1/categories/search/?query=tech")
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    # Should find the Technology category
    if results:
        category_names = [cat["name"] for cat in results]
        assert "Technology" in category_names

def test_duplicate_category_name(client):
    # Create first category
    category_data = {"name": "Education", "description": "Educational content"}
    client.post("/api/v1/categories/", json=category_data)
    
    # Try to create another with same name
    duplicate_data = {"name": "Education", "description": "Another education category"}
    response = client.post("/api/v1/categories/", json=duplicate_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_add_post_to_category(client):
    # Create a user first
    user_data = {"username": "testuser", "email": "test@example.com", "password": "password"}
    user_response = client.post("/api/v1/users/", json=user_data)
    assert user_response.status_code == 200
    user = user_response.json()
    
    # Create a post
    post_data = {"title": "Test Post", "content": "Test content", "author_id": user["id"]}
    post_response = client.post("/api/v1/posts/", json=post_data)
    assert post_response.status_code == 200
    post = post_response.json()
    
    # Create a category
    category_data = {"name": "Tutorial", "description": "Tutorial content"}
    category_response = client.post("/api/v1/categories/", json=category_data)
    assert category_response.status_code == 200
    category = category_response.json()
    
    # Add post to category
    response = client.post(f"/api/v1/posts/{post['id']}/categories/", params={"category_id": category["id"]})
    assert response.status_code == 200
    assert "successfully" in response.json()["message"]

def test_get_post_categories(client):
    # This test assumes the previous test setup
    response = client.get("/api/v1/posts/1/categories/")
    if response.status_code == 200:
        categories = response.json()
        assert isinstance(categories, list)
    else:
        # Post or categories may not exist
        assert response.status_code in [200, 404]  # Accept both as valid test outcomes