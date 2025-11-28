import pytest

def test_create_comment(client):
    # Create user and post first
    user_data = {"username": "testuser2", "email": "test2@example.com", "password": "password"}
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 200
    user = response.json()

    post_data = {"title": "Test Post", "content": "This is a test post", "author_id": user["id"]}
    response = client.post("/api/v1/posts/", json=post_data)
    assert response.status_code == 200
    post = response.json()

    comment_data = {"content": "This is a test comment", "post_id": post["id"], "author_id": user["id"]}
    response = client.post("/api/v1/comments/", json=comment_data)
    assert response.status_code == 200
    comment = response.json()
    assert comment["content"] == "This is a test comment"
    assert comment["post_id"] == post["id"]
    assert comment["author_id"] == user["id"]

def test_get_comments(client):
    response = client.get("/api/v1/comments/")
    assert response.status_code == 200
    comments = response.json()
    assert isinstance(comments, list)

def test_get_comment(client):
    response = client.get("/api/v1/comments/1")
    if response.status_code == 200:
        comment = response.json()
        assert "content" in comment
    else:
        assert response.status_code == 404

def test_get_comments_by_post(client):
    response = client.get("/api/v1/posts/1/comments/")
    assert response.status_code == 200
    comments = response.json()
    assert isinstance(comments, list)

def test_update_comment(client):
    update_data = {"content": "Updated comment"}
    response = client.put("/api/v1/comments/1", json=update_data)
    if response.status_code == 200:
        comment = response.json()
        assert comment["content"] == "Updated comment"
    else:
        assert response.status_code == 404

def test_delete_comment(client):
    response = client.delete("/api/v1/comments/1")
    if response.status_code == 200:
        assert response.json() == {"message": "Comment deleted successfully"}
    else:
        assert response.status_code == 404