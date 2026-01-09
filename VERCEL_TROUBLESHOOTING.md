# Vercel Deployment Troubleshooting

## Common Error: FUNCTION_INVOCATION_FAILED

If you're seeing a 500 error with `FUNCTION_INVOCATION_FAILED`, check the following:

### 1. Check Vercel Function Logs

In Vercel Dashboard:
1. Go to your project
2. Click on "Functions" tab
3. Click on a function invocation
4. Check the logs for specific error messages

### 2. Common Issues and Fixes

#### Issue: Index Files Not Found

**Symptoms:**
- Error: `FileNotFoundError: Index file 'my_notes.index' not found`
- Function logs show path resolution errors

**Fix:**
- Ensure `my_notes.index` and `my_notes_metadata.pkl` are committed to git
- Check file sizes are reasonable (< 50MB total)
- Verify files are in the root directory of your repo

**Verify files are in repo:**
```bash
git ls-files | grep -E "(index|pkl)"
```

#### Issue: Environment Variable Not Set

**Symptoms:**
- Error: `AI_BUILDER_TOKEN environment variable not set`
- Function fails on startup

**Fix:**
1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add: `AI_BUILDER_TOKEN` = `your_token_here`
3. Select all environments (Production, Preview, Development)
4. Redeploy

#### Issue: Import Errors

**Symptoms:**
- Error: `ModuleNotFoundError: No module named 'app'`
- Import errors in function logs

**Fix:**
- Verify `api/index.py` exists and imports correctly
- Check that `app.py` is in the root directory
- Ensure all dependencies are in `requirements.txt`

#### Issue: FAISS Installation Fails

**Symptoms:**
- Build fails with FAISS-related errors
- Import errors for `faiss`

**Fix:**
- Ensure `faiss-cpu` is in `requirements.txt` (not `faiss`)
- Vercel should handle this automatically, but if issues persist:
  ```bash
  # Try adding to requirements.txt:
  faiss-cpu>=1.7.4
  numpy>=1.24.0
  ```

#### Issue: Timeout Errors

**Symptoms:**
- Function times out
- 504 Gateway Timeout errors

**Fix:**
- The `vercel.json` now includes `maxDuration: 30` seconds
- For longer operations, consider:
  - Optimizing index size
  - Using background jobs for indexing
  - Caching results

### 3. Debug Steps

1. **Check Build Logs:**
   - Vercel Dashboard → Deployments → Click on deployment → Build Logs
   - Look for Python installation, dependency installation errors

2. **Check Function Logs:**
   - Vercel Dashboard → Functions → Click on function → Logs
   - Look for runtime errors, import errors, file not found errors

3. **Test Locally:**
   ```bash
   # Install Vercel CLI
   npm i -g vercel
   
   # Run locally
   vercel dev
   
   # Test endpoints
   curl http://localhost:3000/health
   ```

4. **Verify File Structure:**
   ```
   .
   ├── api/
   │   └── index.py       # Must exist
   ├── app.py             # Must exist
   ├── my_notes.index     # Must exist for queries to work
   ├── my_notes_metadata.pkl  # Must exist
   ├── requirements.txt   # Must exist
   └── vercel.json        # Must exist
   ```

### 4. Quick Fixes

#### Rebuild from Scratch

1. Delete the Vercel project
2. Re-import from GitHub
3. Add environment variables
4. Deploy

#### Update Dependencies

```bash
# Locally, update requirements.txt if needed
pip freeze > requirements.txt

# Commit and push
git add requirements.txt
git commit -m "Update dependencies"
git push
```

#### Verify Index Files

```bash
# Check files exist and are reasonable size
ls -lh my_notes.*

# Should show:
# my_notes.index (~150KB)
# my_notes_metadata.pkl (~12KB)
```

### 5. Alternative: Use AI Builder Platform

If Vercel continues to have issues, consider deploying via the AI Builder platform:

1. The platform is optimized for Python/FastAPI apps
2. Automatically handles environment variables
3. Better suited for ML/AI workloads

See `DEPLOYMENT.md` for details.

### 6. Get Help

If issues persist:
1. Check Vercel function logs (most important!)
2. Share error messages from logs
3. Verify all files are committed to git
4. Check environment variables are set correctly

