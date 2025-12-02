# API Documentation

## Authentication

### Register User

**POST** `/api/v1/auth/register`

Request body:

```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string"
}
```

Response:

```json
{
  "id": 1,
  "username": "string",
  "email": "user@example.com",
  "created_at": "2023-01-01T00:00:00"
}
```

### Login

**POST** `/api/v1/auth/login`

Request body (form data):

```
username: string
password: string
```

Response:

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### Get Current User

**GET** `/api/v1/auth/me`

Headers:

```
Authorization: Bearer <access_token>
```

Response:

```json
{
  "id": 1,
  "username": "string",
  "email": "user@example.com",
  "created_at": "2023-01-01T00:00:00"
}
```

## Users

### Get Users

**GET** `/api/v1/users/`

Query parameters:

- `skip`: int (default: 0)
- `limit`: int (default: 100)

Response:

```json
[
  {
    "id": 1,
    "username": "string",
    "email": "user@example.com",
    "created_at": "2023-01-01T00:00:00"
  }
]
```

### Get User by ID

**GET** `/api/v1/users/{user_id}`

Response:

```json
{
  "id": 1,
  "username": "string",
  "email": "user@example.com",
  "created_at": "2023-01-01T00:00:00"
}
```

### Create User

**POST** `/api/v1/users/`

Request body:

```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string"
}
```

Response:

```json
{
  "id": 1,
  "username": "string",
  "email": "user@example.com",
  "created_at": "2023-01-01T00:00:00"
}
```

### Update User

**PUT** `/api/v1/users/{user_id}`

Request body:

```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string"
}
```

Response:

```json
{
  "id": 1,
  "username": "string",
  "email": "user@example.com",
  "created_at": "2023-01-01T00:00:00"
}
```

### Delete User

**DELETE** `/api/v1/users/{user_id}`

Response:

```json
{
  "message": "User deleted successfully"
}
```

## Social Features

### Follow a User

**POST** `/api/v1/social/follow/{user_id}`

Headers:

```
Authorization: Bearer <access_token>
```

Response:

```json
{
  "follower_id": 1,
  "followee_id": 2,
  "is_active": true,
  "created_at": "2023-01-01T00:00:00"
}
```

### Unfollow a User

**DELETE** `/api/v1/social/follow/{user_id}`

Headers:

```
Authorization: Bearer <access_token>
```

Response:

```json
{
  "follower_id": 1,
  "followee_id": 2,
  "is_active": false,
  "created_at": "2023-01-01T00:00:00"
}
```

### Get Followers

**GET** `/api/v1/social/followers/{user_id}`

Query parameters:

- `skip`: int (default: 0)
- `limit`: int (default: 100, max: 1000)

Response:

```json
[
  {
    "id": 1,
    "follower_id": 2,
    "followee_id": 1,
    "is_active": true,
    "created_at": "2023-01-01T00:00:00",
    "follower": {
      "id": 2,
      "username": "user2",
      "avatar_url": "https://example.com/avatar.jpg"
    }
  }
]
```

### Get Following

**GET** `/api/v1/social/following/{user_id}`

Query parameters:

- `skip`: int (default: 0)
- `limit`: int (default: 100, max: 1000)

Response:

```json
[
  {
    "id": 1,
    "follower_id": 1,
    "followee_id": 2,
    "is_active": true,
    "created_at": "2023-01-01T00:00:00",
    "followee": {
      "id": 2,
      "username": "user2",
      "avatar_url": "https://example.com/avatar.jpg"
    }
  }
]
```

### Check Follow Status

**GET** `/api/v1/social/is-following/{user_id}`

Headers:

```
Authorization: Bearer <access_token>
```

Response:

```json
{
  "is_following": true
}
```

### Get Follow Statistics

**GET** `/api/v1/social/follow-stats/{user_id}`

Response:

```json
{
  "followers_count": 42,
  "following_count": 38
}
```

### Get User Profile with Social Info

**GET** `/api/v1/social/profile/{user_id}`

Headers:

```
Authorization: Bearer <access_token>  # Optional
```

Response:

```json
{
  "id": 1,
  "username": "user1",
  "email": "user1@example.com",
  "bio": "Hello, I'm a developer!",
  "avatar_url": "https://example.com/avatar.jpg",
  "website": "https://mywebsite.com",
  "location": "New York, NY",
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00",
  "is_active": true,
  "followers_count": 42,
  "following_count": 38,
  "posts_count": 15,
  "is_following": true
}
```

## Notifications

### Get Notifications

**GET** `/api/v1/social/notifications`

Headers:

```
Authorization: Bearer <access_token>
```

Query parameters:

- `skip`: int (default: 0)
- `limit`: int (default: 50, max: 200)
- `unread_only`: boolean (default: false)

Response:

```json
[
  {
    "id": 1,
    "user_id": 1,
    "actor_id": 2,
    "notification_type": "new_follower",
    "title": "New Follower",
    "message": "user2 started following you",
    "entity_type": "user",
    "entity_id": 2,
    "is_read": false,
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00",
    "actor_username": "user2",
    "actor_avatar_url": "https://example.com/avatar.jpg"
  }
]
```

### Mark Notification as Read

**PUT** `/api/v1/social/notifications/{notification_id}/read`

Headers:

```
Authorization: Bearer <access_token>
```

Response:

```json
{
  "id": 1,
  "user_id": 1,
  "actor_id": 2,
  "notification_type": "new_follower",
  "title": "New Follower",
  "message": "user2 started following you",
  "entity_type": "user",
  "entity_id": 2,
  "is_read": true,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

### Mark All Notifications as Read

**PUT** `/api/v1/social/notifications/read-all`

Headers:

```
Authorization: Bearer <access_token>
```

Response:

```json
{
  "updated_count": 5
}
```

## Health Check

### Health Status

**GET** `/health`

Response:

```json
{
  "status": "healthy"
}
