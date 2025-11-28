import pytest

def test_create_post(client):
    # Create a user first
    user_data = {"username": "testuser", "email": "test@example.com", "password": "password"}
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 200
    user = response.json()

    post_data = {"title": "Test Post", "content": "This is a test post", "author_id": user["id"]}
    response = client.post("/api/v1/posts/", json=post_data)
    assert response.status_code == 200
    post = response.json()
    assert post["title"] == "Test Post"
    assert post["content"] == "This is a test post"
    assert post["author_id"] == user["id"]

def test_get_posts(client):
    response = client.get("/api/v1/posts/")
    assert response.status_code == 200
    posts = response.json()
    assert isinstance(posts, list)

def test_get_post(client):
    # Assuming post with id 1 exists from previous test
    response = client.get("/api/v1/posts/1")
    if response.status_code == 200:
        post = response.json()
        assert "title" in post
    else:
        assert response.status_code == 404

def test_update_post(client):
    # Assuming post exists
    update_data = {"title": "Updated Title"}
    response = client.put("/api/v1/posts/1", json=update_data)
    if response.status_code == 200:
        post = response.json()
        assert post["title"] == "Updated Title"
    else:
        assert response.status_code == 404

def test_delete_post(client):
    response = client.delete("/api/v1/posts/1")
    if response.status_code == 200:
        assert response.json() == {"message": "Post deleted successfully"}
    else:
        assert response.status_code == 404