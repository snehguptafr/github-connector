# GitHub Connector API

A FastAPI application that connects to GitHub using OAuth 2.0 authentication and provides REST API endpoints to interact with GitHub repositories, issues, and pull requests.

## Features

- ✅ OAuth 2.0 GitHub authentication
- ✅ List user repositories
- ✅ List/create issues
- ✅ List commits
- ✅ Create pull requests
- ✅ Secure JWT-based session management
- ✅ Interactive API documentation

## Setup

### 1. Prerequisites
- Python 3.8+
- pip

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create GitHub OAuth App

1. Go to https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in:
   - **Application name:** GitHub Connector(or any name you prefer)
   - **Homepage URL:** http://localhost:8000
   - **Authorization callback URL:** http://localhost:8000/callback
4. Copy the Client ID and Client Secret

### 5. Create .env File

Create `.env` in project root:
```
GITHUB_CLIENT_ID=your_client_id_here
GITHUB_CLIENT_SECRET=your_client_secret_here
GITHUB_REDIRECT_URI=http://localhost:8000/callback
SECRET_KEY=your_random_secret_key_here
```

### 6. Run the Application
```bash
uvicorn app.main:app --reload
```

The API will be available at: `http://localhost:8000`

## API Documentation

### Interactive Docs
Visit `http://localhost:8000/docs` (Through Swagger UI)

### Endpoints

#### Authentication
- **GET `/login`** - Redirect to GitHub OAuth
- **GET `/callback`** - OAuth callback
- **GET `/logout`** - Logout user

#### User
- **GET `/user`** - Get authenticated user info

#### Repositories
- **GET `/repos`** - List authenticated user's repositories

#### Issues
- **GET `/repos/{owner}/{repo}/issues`** - List issues
- **POST `/repos/{owner}/{repo}/issues`** - Create issue
```json
  {
    "title": "Issue title",
    "body": "Issue description"
  }
```

#### Commits
- **GET `/repos/{owner}/{repo}/commits`** - List commits

#### Pull Requests
- **POST `/repos/{owner}/{repo}/pulls`** - Create pull request
```json
  {
    "title": "Feature title",
    "head": "feature-branch",
    "base": "main",
    "body": "Description"
  }
```

## Example Usage through curl

### 1. Login
Visit `http://localhost:8000/login` on browser first to get the session cookie.

### 2. Get Your Repos
```bash
curl -X GET "http://localhost:8000/repos" \
  -H "Cookie: session=your_session_cookie"
```

### 3. List Issues
```bash
curl -X GET "http://localhost:8000/repos/owner/repo/issues" \
  -H "Cookie: session=your_session_cookie"
```

### 4. Create Issue
```bash
curl -X POST "http://localhost:8000/repos/owner/repo/issues" \
  -H "Cookie: session=your_session_cookie" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Bug: Something broken",
    "body": "Description of the bug"
  }'
```

### 5. Create Pull Request
```bash
curl -X POST "http://localhost:8000/repos/owner/repo/pulls" \
  -H "Cookie: session=your_session_cookie" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Feature: Add new feature",
    "head": "test",
    "base": "main",
    "body": "Description"
  }'
```

## Security

- ✅ OAuth 2.0 authentication
- ✅ JWT-based session management
- ✅ HttpOnly and Secure cookies 
- ✅ Environment variables for secrets

## Error Handling

The API handles:
- **400 Bad Request** - Malformed request
- **401 Unauthorized** - Not authenticated or invalid session
- **404 Not Found** - Resource not found
- **422 Unprocessable Content** - Validation error (missing/invalid fields)
- **429 Too Many Requests** - GitHub API rate limit exceeded
- **500 Server Error** - Internal server error

## Testing

Test all endpoints using the interactive API docs:
1. Start the server
2. Visit `http://localhost:8000/login`
3. Click "Authorize" and login with GitHub
2. Visit `http://localhost:8000/docs` after login
4. Try each endpoint through the interactive docs

## Tech Stack

- **Framework:** FastAPI
- **Authentication:** OAuth 2.0 (GitHub)
- **Session Management:** JWT (JSON Web Tokens)
- **Data Validation:** Pydantic
- **Server:** Uvicorn