# backend/tests/test_posts.py

def test_create_post(client, random_user):
    payload = {
        "content": "This is a test post from pytest.",
        "image": "https://example.com/image.png"
    }
    response = client.post("/api/v1/posts/", json=payload, headers=random_user["headers"])
    assert response.status_code == 200
    assert response.json()["success"] is True
    # Save the post ID for the next test? 
    # In pytest, it's often better to just create a new one or return data.
    assert "id" in response.json()

def test_get_feed(client, random_user):
    # Ensure there is at least one post (created above)
    response = client.get("/api/v1/posts/", headers=random_user["headers"])
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Check structure
    first_post = data[0]
    assert "content" in first_post
    assert "author" in first_post
    assert "username" in first_post["author"]

def test_like_post(client, random_user):
    # 1. Create a post
    create_res = client.post("/api/v1/posts/", json={"content": "Like me"}, headers=random_user["headers"])
    post_id = create_res.json()["id"]

    # 2. Like it
    like_res = client.post(f"/api/v1/posts/{post_id}/like", headers=random_user["headers"])
    assert like_res.status_code == 200
    assert like_res.json()["liked"] is True

    # 3. Unlike it (Toggle)
    unlike_res = client.post(f"/api/v1/posts/{post_id}/like", headers=random_user["headers"])
    assert unlike_res.status_code == 200
    assert unlike_res.json()["liked"] is False