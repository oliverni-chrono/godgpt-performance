# Deploy Current Project

Deploy the current Git repository using developer-platform MCP.

## Step 1: Check Git Status

```bash
git config --get remote.origin.url
git branch --show-current
git status --porcelain
git log origin/$(git branch --show-current)..HEAD --oneline 2>/dev/null
```

Parse repo as owner/repo from the URL.

### Pre-flight:
- **Uncommitted changes?** → Ask to commit first
- **Unpushed commits?** → Ask to push first, show the commits
- **Clean?** → Continue

## Step 2: Check GitHub Connection

Use `check_github_connection`. If not connected:

1. Use `start_github_device_flow` to get the userCode and deviceCode
2. **Open browser** by running:
   ```bash
   open "https://github.com/login/device"
   ```
3. Display the code prominently to the user like this:
   
   ---
   **GitHub Authorization**
   
   I've opened GitHub in your browser.
   
   Enter this code: **`XXXX-XXXX`**
   
   Then click **Continue** → **Authorize**
   
   ---
   
4. Use `poll_github_device_flow` with the deviceCode until success (poll every 5 seconds)

## Step 3: Find or Create Pipeline

Use `list_pipelines` to find existing pipeline for this repo+branch.

**If exists:** Use it.
**If not:** Create a new pipeline:

1. `detect_repo_type` to get app type (frontend/backend/fullstack)
2. `list_projects` / `create_project`
3. **Analyze code for middleware dependencies:**

   Before asking the user, scan the codebase to detect middleware:
   
   **For Node.js (check package.json dependencies):**
   - `mongodb`, `mongoose`, `@prisma/client` (with mongodb) → suggest MongoDB
   - `redis`, `ioredis`, `@redis/client` → suggest Redis
   - `pg`, `postgres`, `@prisma/client` (with postgresql) → suggest PostgreSQL
   
   **For Python (check requirements.txt or pyproject.toml):**
   - `pymongo`, `motor`, `mongoengine` → suggest MongoDB
   - `redis`, `aioredis` → suggest Redis
   - `psycopg2`, `asyncpg`, `sqlalchemy` → suggest PostgreSQL
   
   **For Go (check go.mod):**
   - `go.mongodb.org/mongo-driver` → suggest MongoDB
   - `github.com/redis/go-redis`, `github.com/go-redis/redis` → suggest Redis
   - `github.com/lib/pq`, `github.com/jackc/pgx` → suggest PostgreSQL
   
   **For .NET/C# (check *.csproj PackageReference or packages.config):**
   - `MongoDB.Driver` → suggest MongoDB
   - `StackExchange.Redis`, `Microsoft.Extensions.Caching.StackExchangeRedis` → suggest Redis
   - `Npgsql`, `Npgsql.EntityFrameworkCore.PostgreSQL` → suggest PostgreSQL

4. **Detect environment variables from .env files:**

   **For Frontend/Fullstack**, read these files (in order of priority):
   - `.env.production` (for production deployments)
   - `.env.development` (for development/staging)
   - `.env.local`
   - `.env`
   
   Look for frontend-specific env vars:
   - `NEXT_PUBLIC_*` (Next.js)
   - `REACT_APP_*` (Create React App)
   - `VITE_*` (Vite)
   - `VUE_APP_*` (Vue CLI)
   
   **Important:** Skip secrets/sensitive values. Only collect variable names and placeholder values.

5. **Ask user about configuration (with detected defaults):**

   Inform user what you detected and confirm:
   
   **For Frontend/Fullstack:**
   - If env vars detected from .env files, show them and ask to confirm
   - If no .env files found: "Do you have any frontend environment variables?"
   
   **For Backend/Fullstack:**
   - "What port does your backend listen on?" (default: 8080)
   - "Do you have any backend environment variables?"
   - If middleware detected: "I detected **MongoDB/Redis** dependencies. Should I provision these?"
   - If not detected: "Do you need a database or cache?"
     - MongoDB → adds `MONGODB_URI` and `MONGODB_DATABASE` (database name = appName)
     - Redis → adds `REDIS_URL`
   
6. `create_pipeline` with:
   - **name** and **appName**: Both use format {repo}-{branch-short}. Keep short and readable.
   - Detected settings from step 1
   - User's env vars in `frontendEnvVars` / `backendEnvVars`
   - Middleware: `["mongodb"]`, `["redis"]`, or `["mongodb", "redis"]`
   - Backend port if not 8080

7. **Show the user the generated URLs** from the response:
   - Frontend URL: https://{appName}.chrono-ai.fun
   - Backend URL: https://{appName}-api.chrono-ai.fun

## Step 4: Deploy

Use `trigger_pipeline_run` with pipelineId.

## Step 5: Monitor

Use `get_run_status` to poll progress. **Poll every 15 seconds** (builds take 2-5 minutes).

Report: stages, success URL, or failure details.

## Important Notes

- **Deployments are manual only.** Use /deploy or trigger_pipeline_run each time you want to deploy new code.
- Automatic deployments on git push are NOT supported.
