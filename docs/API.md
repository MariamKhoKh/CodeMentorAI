# CodeMentorAI API Documentation

## Overview

The CodeMentorAI API is a RESTful service for managing coding problems, user authentication, code submissions, AI-powered analysis, and personalized recommendations. All endpoints return JSON. Most require authentication via JWT.

Base URL: `/api/`

---

## Authentication

### Register
**POST** `/auth/register`

Registers a new user.

**Request Body:**
```json
{
	"email": "user@example.com",
	"username": "string",
	"password": "string"
}
```
**Response:**
```json
{
	"email": "user@example.com",
	"username": "string",
	"id": 0,
	"is_active": true,
	"created_at": "2025-12-25T18:51:43.925Z"
}
```

### Login (Form)
**POST** `/auth/login`

OAuth2 compatible. Use `username` for email.

**Request Body:** `application/x-www-form-urlencoded`
- `username`: string (email)
- `password`: string

**Response:**
```json
{
	"access_token": "string",
	"token_type": "bearer"
}
```

### Login (JSON)
**POST** `/auth/login/json`

Alternative login with JSON body.

**Request Body:**
```json
{
	"email": "user@example.com",
	"password": "string"
}
```
**Response:** (same as above)

### Get Current User
**GET** `/auth/me`

Returns current authenticated user info.

**Response:**
```json
{
	"email": "user@example.com",
	"username": "string",
	"id": 0,
	"is_active": true,
	"created_at": "2025-12-25T18:51:43.935Z"
}
```

---

## Problems

### Create Problem
**POST** `/problems/`

**Request Body:**
```json
{
	"title": "string",
	"slug": "string",
	"description": "string",
	"difficulty": "easy",
	"constraints": {},
	"tags": ["string"],
	"test_cases": [
		{"input": {}, "expected_output": "string", "is_hidden": false, "explanation": "string"}
	],
	"optimal_patterns": {
		"time_complexity": "string",
		"space_complexity": "string",
		"key_patterns": ["string"],
		"key_data_structures": ["string"]
	},
	"starter_code": {},
	"reference_solution": {}
}
```
**Response:** (201)
```json
{
	...request fields...,
	"id": 0,
	"created_at": "2025-12-25T18:51:43.903Z",
	"updated_at": "2025-12-25T18:51:43.903Z"
}
```

### List Problems
**GET** `/problems/`

**Query Params:**
- `skip`: int (default 0)
- `limit`: int (default 50, max 100)
- `difficulty`: string (optional)
- `tag`: string (optional)

**Response:**
```json
[
	{"id": 0, "title": "string", "slug": "string", "description": "string", "difficulty": "easy", "tags": ["string"], "created_at": "2025-12-25T18:51:43.907Z"}
]
```

### Get Problem Stats
**GET** `/problems/stats`

**Response:**
```json
{
	"total_problems": 0,
	"by_difficulty": {"easy": 0, "medium": 0, "hard": 0},
	"by_tags": {"arrays": 0, "math": 0}
}
```

### Get Problem
**GET** `/problems/{problem_id}`

**Response:** (see Create Problem response)

### Update Problem
**PUT** `/problems/{problem_id}`

**Request Body:** (same as Create Problem, minus slug)

**Response:** (200, see Create Problem response)

### Delete Problem
**DELETE** `/problems/{problem_id}`

**Response:** (204, empty string)

### Get Problem By Slug
**GET** `/problems/slug/{slug}`

**Response:** (see Create Problem response)

---

## Submissions

### Submit Code
**POST** `/submissions/`

**Request Body:**
```json
{
	"problem_id": 0,
	"code": "string",
	"language": "python"
}
```
**Response:**
```json
{
	"id": 0,
	"user_id": 0,
	"problem_id": 0,
	"code": "string",
	"language": "python",
	"status": "pending",
	"test_results": [
		{"test_case_id": 0, "status": "passed", "runtime_ms": 0, "memory_kb": 0, "input": "string", "expected_output": "string", "actual_output": "string", "error_message": "string", "is_hidden": false}
	],
	"all_tests_passed": true,
	"total_tests": 0,
	"passed_tests": 0,
	"runtime_ms": 0,
	"memory_kb": 0,
	"error_message": "string",
	"created_at": "2025-12-25T18:51:43.938Z"
}
```

### List Submissions
**GET** `/submissions/`

**Query Params:**
- `problem_id`: int (optional)
- `skip`: int (default 0)
- `limit`: int (default 20, max 100)

**Response:**
```json
[
	{"id": 0, "problem_id": 0, "language": "python", "status": "pending", "all_tests_passed": true, "passed_tests": 0, "total_tests": 0, "created_at": "2025-12-25T18:51:43.942Z"}
]
```

### Get My Submissions
**GET** `/submissions/me`

**Query Params:**
- `skip`: int (default 0)
- `limit`: int (default 20, max 100)

**Response:** (same as List Submissions)

### Get Submission
**GET** `/submissions/{submission_id}`

**Response:** (see Submit Code response)

---

## Analysis

### Get Analysis
**GET** `/analysis/{submission_id}`

**Response:**
```json
{
	"id": 0,
	"submission_id": 0,
	"ast_features": {},
	"estimated_time_complexity": "string",
	"estimated_space_complexity": "string",
	"optimal_time_complexity": "string",
	"optimal_space_complexity": "string",
	"complexity_match": 0,
	"error_category": "INEFFICIENT_ALGORITHM",
	"error_confidence": 0,
	"feedback_text": "string",
	"improvement_suggestions": ["string"],
	"created_at": "2025-12-25T18:51:43.952Z"
}
```

---

## Recommendations

### Generate AI Problem
**POST** `/recommendations/ai-problem`

**Response:** (see Create Problem response)

### Get Recommendations
**GET** `/recommendations/`

**Response:**
```json
[
	{"problem_id": 0, "problem_title": "string", "reason": "string", "confidence_score": 0}
]
```

### Update Weaknesses
**POST** `/recommendations/update-weaknesses`

**Response:**
```json
"string"
```

### Get Weaknesses
**GET** `/recommendations/weaknesses`

**Response:**
```json
"string"
```

---

## Default & Health

### Root
**GET** `/`

### Health Check
**GET** `/health`

**Response:**
```json
"string"
```

---

## Error Handling

All errors return a JSON object:
```json
{
	"detail": [
		{"loc": ["string", 0], "msg": "string", "type": "string"}
	]
}
```
Common codes: 400, 401, 403, 404, 422, 500
