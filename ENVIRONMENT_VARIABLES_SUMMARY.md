# Environment Variables Summary

## Rwanda NCSA Compliance Auditor v3.0.0

### Quick Answer: Environment Variables Needed

**SHORT ANSWER: NONE required! (1 optional)**

The system is designed to work **completely out-of-the-box** without any environment variables.

---

## Optional Environment Variable (Only 1)

### OPENAI_API_KEY (Optional)

**Used by:**
- ENGINE 2 (Document Processing) - Port 8002
- ENGINE 5 (Report Generation) - Port 8003
- ENGINE 6 (Web UI Backend) - Port 8006

**Purpose:**
- Enables LLM-powered features (GPT-4)
- Document control extraction with AI
- Professional report narrative generation

**What happens if NOT set:**
- ✅ System works perfectly fine!
- ✅ ENGINE 2 uses mock document processing (still extracts controls)
- ✅ ENGINE 5 uses mock report generation (still creates PDF reports)
- ✅ All other engines work normally

**How to set (if you want to):**

```bash
# Method 1: Create .env file in project root
cp .env.example .env
echo "OPENAI_API_KEY=sk-your-key-here" >> .env

# Method 2: Export in terminal
export OPENAI_API_KEY="sk-your-key-here"

# Method 3: Don't set it - system works without it!
```

---

## Auto-Configured Variables (NO ACTION NEEDED)

These are automatically set in `docker-compose.yml`:

### Database & Cache
- `POSTGRES_URL` - Auto-configured for all engines that need it
- `POSTGRES_DB` - Set to `compliance_db`
- `POSTGRES_USER` - Set to `compliance_user`
- `POSTGRES_PASSWORD` - Set to `compliance_pass`
- `REDIS_URL` - Auto-configured

### Inter-Engine Communication
- `ENGINE3_URL` - Points to `http://xgboost-api:8000` (internal Docker network)
- `ENGINE4_URL` - Points to `http://decision-engine:8001` (internal Docker network)

**These are set automatically by Docker Compose internal networking - you don't need to set them!**

---

## Summary by Engine

| Engine | Requires Env Vars? | Optional Vars |
|--------|-------------------|---------------|
| ENGINE 1 (Log Collector) | ❌ No | None |
| ENGINE 2 (Document Processor) | ❌ No | OPENAI_API_KEY |
| ENGINE 3 (XGBoost) | ❌ No | None |
| ENGINE 4 (Decision) | ❌ No | None |
| ENGINE 5 (Report Generator) | ❌ No | OPENAI_API_KEY |
| ENGINE 6 (Web UI) | ❌ No | OPENAI_API_KEY |
| PostgreSQL | ❌ No | None (auto-configured) |
| Redis | ❌ No | None (auto-configured) |

---

## For Your Use Case (Document Upload Testing)

Since you want to test document upload from the UI:

**Option A: With OpenAI API Key (Recommended if you have one)**
```bash
# Create .env file
echo "OPENAI_API_KEY=sk-your-actual-key" > .env

# Result: ENGINE 2 will use GPT-4 to intelligently extract controls from your PDF
```

**Option B: Without OpenAI API Key (Works perfectly fine!)**
```bash
# Do nothing - just start the system

# Result: ENGINE 2 will use mock mode to extract controls from your PDF
# Mock mode is still functional and will show realistic control extraction
```

---

## Verification

After starting the system, verify OpenAI integration status:

```bash
# Check ENGINE 2 status
curl http://localhost:8002/health | jq

# Look for: "llm_enabled": true (if API key set) or false (if not set)

# Check ENGINE 5 status
curl http://localhost:8003/health | jq

# Look for: "llm_enabled": true (if API key set) or false (if not set)
```

---

## Recommendation for Testing

**For your document upload testing, I recommend:**

1. **Start without OpenAI API key first**
   - This proves the system works independently
   - You can upload and process documents immediately
   - Mock mode is fully functional

2. **Optionally add API key later**
   - If you want to see GPT-4 enhanced extraction
   - Stop containers: `docker-compose down`
   - Add API key to `.env` file
   - Restart: `docker-compose up -d`

---

## Complete Startup Command (No Env Vars Needed!)

```bash
# Navigate to project
cd "/Users/moiseiradukunda/Documents/CMU/RESEARCH PROJECT/model-engine"

# Build (one time)
docker-compose build

# Start all services
docker-compose up -d

# That's it! No environment variables required!
```

---

## Bottom Line

✅ **REQUIRED ENVIRONMENT VARIABLES: 0**
✅ **OPTIONAL ENVIRONMENT VARIABLES: 1 (OPENAI_API_KEY)**
✅ **SYSTEM WORKS WITHOUT ANY ENV VARS: YES**
✅ **DOCUMENT UPLOAD WORKS WITHOUT ENV VARS: YES**

**You can start testing immediately without setting any environment variables!**

