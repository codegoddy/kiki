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

## Health Check

### Health Status

**GET** `/health`

Response:

```json
{
  "status": "healthy"
}
