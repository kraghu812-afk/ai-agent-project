# Raghu AI Agent v2.0

A beginner-friendly Python API project demonstrating user registration, secure password hashing, JWT login, and a protected AI Agent endpoint.

## Features

- Register users with a username and password
- Hash passwords using Argon2 (passwords are never stored in plain text)
- Log in and receive a signed JWT access token
- Protect user and agent endpoints with token verification
- Expire access tokens after 30 minutes
- Store user records in a local SQLite database
- Interactive API documentation at `/docs`

## Project files

| File | Purpose |
|---|---|
| `main.py` | FastAPI application, registration, login, JWT validation, protected routes |
| `agent.py` | Original beginner command-line agent |
| `requirements.txt` | Python dependencies |
| `.env.example` | Safe template for local environment settings |
| `.gitignore` | Prevents local secrets and database files from being committed |

## Step 1 — Install Python

Use Python 3.10 or newer. Check your installation:

```bash
python --version
```

## Step 2 — Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

## Step 3 — Install packages

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Step 4 — Create your local secret file

Copy `.env.example` to a new file named `.env`. Do not upload `.env` to GitHub.

Generate a strong random key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the generated value into your local `.env` file:

```env
JWT_SECRET_KEY=paste_your_generated_random_value_here
```

The value above is a placeholder example, not a usable secret. Keep your real key private. If it is exposed, generate a new one; existing tokens signed with the old key will stop working.

## Step 5 — Start the API

```bash
uvicorn main:app --reload
```

Open:

- API welcome page: http://127.0.0.1:8000/
- Interactive API docs: http://127.0.0.1:8000/docs

## Step 6 — Register a user

In `/docs`, open **POST /auth/register**, select **Try it out**, and submit:

```json
{
  "username": "raghu",
  "password": "ChooseAUniquePassword123!"
}
```

Use your own strong password. This is sample input; do not reuse it as a real password.

The server hashes the password with Argon2 before storing it in `users.db`.

## Step 7 — Log in and get a JWT

Open **POST /auth/token**. Enter the same username and password in the form fields. The response contains:

- `access_token`: the signed JWT
- `token_type`: `bearer`
- `expires_in`: token lifetime in seconds (1800 seconds = 30 minutes)

Treat the access token like a password. Do not paste it into GitHub, screenshots, public chats, or source code.

## Step 8 — Call a protected endpoint

In the Swagger page, click **Authorize** and enter the username and password when prompted, or provide the returned bearer token as:

```text
Bearer YOUR_ACCESS_TOKEN
```

Then try:

- **GET /users/me** — returns the identity associated with the valid token
- **POST /agent/chat** — calls the protected agent endpoint

Example chat request:

```json
{
  "message": "hello"
}
```

Without a valid token, these protected endpoints return HTTP 401.

## How JWT authentication works

1. Registration receives a password over the API and hashes it with Argon2.
2. Only the password hash is stored in SQLite.
3. Login verifies the submitted password against that hash.
4. If verification succeeds, the server signs a JWT containing the username (`sub`), issue time (`iat`), and expiry (`exp`).
5. The client sends the token in the HTTP Authorization header using the Bearer scheme.
6. FastAPI's `OAuth2PasswordBearer` extracts the token. PyJWT verifies its signature and expiry.
7. The API checks that the user still exists, then allows the protected request.

## Credential and token safety

- Never commit `.env`, real passwords, access tokens, or private keys.
- `.env.example` contains only a placeholder.
- Passwords are hashed with Argon2; they are not encrypted or stored in plain text.
- JWTs are signed, not encrypted. Their payload can be decoded by anyone holding the token, so do not put passwords or sensitive personal data inside them.
- Use HTTPS in production so credentials and bearer tokens are encrypted in transit.
- Keep tokens short-lived. This starter project uses 30-minute access tokens.
- This project does not implement refresh tokens, server-side logout/revocation, email verification, login rate limiting, or account recovery. Add these before using it for a public production service.
- SQLite is suitable for learning and small local projects. Consider PostgreSQL for a deployed multi-user service.
- Do not expose the development server directly to the public internet.

## Common errors

**JWT_SECRET_KEY is missing**

Create a local `.env` file and set a random `JWT_SECRET_KEY` as shown in Step 4.

**Form data requires "python-multipart"**

Run:

```bash
pip install -r requirements.txt
```

**401 Unauthorized**

Log in again and use the latest access token. Tokens expire after 30 minutes.

**Port 8000 is already in use**

Run:

```bash
uvicorn main:app --reload --port 8001
```

## Original command-line agent

The original beginner command-line program remains available:

```bash
python agent.py
```

## Author

Raghu Kompelli
