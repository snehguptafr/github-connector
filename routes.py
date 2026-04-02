from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from utils import get_access_token, get_session, end_session, SESSION_LIFE
import httpx
import os
from dotenv import load_dotenv

from models.models import PRCreate, IssueCreate

load_dotenv()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")

router = APIRouter()

@router.get("/")
async def root():
    return {
        "message": "GitHub Connector API",
        "endpoints": {
            "login": "/login - GitHub login",
            "callback": "/callback - OAuth callback",
            "user": "/user - get user info",
            "repos": "/repos - list user repos",
            "issues": "/repos/{owner}/{repo}/issues - list issues",
            "create_issue": "/repos/{owner}/{repo}/issues - create issue",
            "commits": "/repos/{owner}/{repo}/commits - list commits",
            "create_pr": "/repos/{owner}/{repo}/pulls - create pull request",
            "logout": "/logout - logout"
        }
    }

@router.get("/login")
async def login():
    return RedirectResponse(
        url=f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&redirect_uri={GITHUB_REDIRECT_URI}&scope=user repo"
    )

@router.get("/callback")
async def callback(code: str = None, error: str = None):
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    if not code:
        raise HTTPException(status_code=400, detail="No code provided in callback")
    
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": GITHUB_REDIRECT_URI
            },
            headers={"Accept": "application/json"}
        )
        
        token_data = token_res.json()
        if "error" in token_data:
            raise HTTPException(status_code=400, detail=f"Token exchange error: {token_data.get('error_description', token_data['error'])}")
        
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token received from GitHub")
        
        user_res = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {access_token}"}
        )
        user_data = user_res.json()
        
        session_token = get_session(access_token, user_data)
        
        response = RedirectResponse(url="/user")
        response.set_cookie(
            key="session",
            value=session_token,
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=SESSION_LIFE
        )
        return response

@router.get("/user")
async def get_user(request: Request):
    access_token = get_access_token(request)
    async with httpx.AsyncClient() as client:
        user_res = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        if user_res.status_code != 200:
            raise HTTPException(status_code=user_res.status_code, detail=f"GitHub API error: {user_res.text}")
        return user_res.json()

@router.get("/repos")
async def list_repos(request: Request):
    access_token = get_access_token(request)
    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://api.github.com/user/repos",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=f"GitHub API error: {res.text}")
        return res.json()

@router.get("/repos/{owner}/{repo}/issues")
async def list_issues(request: Request, owner: str, repo: str):
    access_token = get_access_token(request)
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/issues",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=f"GitHub API error: {res.text}")
        return res.json()

@router.post("/repos/{owner}/{repo}/issues")
async def create_issue(request: Request, owner: str, repo: str, issue_data: IssueCreate):
    access_token = get_access_token(request)
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"https://api.github.com/repos/{owner}/{repo}/issues",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.v3+json"
            },
            json={"title": issue_data.title, "body": issue_data.body}
        )
        if res.status_code != 201:
            raise HTTPException(status_code=res.status_code, detail=f"GitHub API error: {res.text}")
        return res.json()

@router.get("/repos/{owner}/{repo}/commits")
async def list_commits(request: Request, owner: str, repo: str):
    access_token = get_access_token(request)
    async with httpx.AsyncClient() as client:
        commits_res = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/commits",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        if commits_res.status_code != 200:
            raise HTTPException(status_code=commits_res.status_code, detail=f"GitHub API error: {commits_res.text}")
        return commits_res.json()

@router.post("/repos/{owner}/{repo}/pulls")
async def create_pull_request(request: Request, owner: str, repo: str, pr_data: PRCreate):
    access_token = get_access_token(request)
    async with httpx.AsyncClient() as client:
        pr_res = await client.post(
            f"https://api.github.com/repos/{owner}/{repo}/pulls",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.v3+json"
            },
            json={
                "title": pr_data.title,
                "head": pr_data.head,
                "base": pr_data.base,
                "body": pr_data.body
            }
        )
        if pr_res.status_code != 201:
            raise HTTPException(status_code=pr_res.status_code, detail=f"GitHub API error: {pr_res.text}")
        return pr_res.json()

@router.get("/logout")
async def logout(request: Request):
    end_session(request.cookies.get("session"))
    response = RedirectResponse(url="/")
    response.delete_cookie(key="session")
    return response