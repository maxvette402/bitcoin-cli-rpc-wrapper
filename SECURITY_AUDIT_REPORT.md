# Security Audit Report
**Date:** 2026-02-12
**Project:** Bitcoin CLI RPC Wrapper
**Auditor:** Claude Code Security Scanner

## 🔴 CRITICAL Issues

### 1. **Insecure .env File Permissions**
- **Severity:** HIGH
- **File:** `.env`
- **Current Permissions:** `644` (readable by all users on the system)
- **Risk:** Any user on the system can read your Bitcoin RPC credentials
- **Fix:**
  ```bash
  chmod 600 .env
  ```
- **Explanation:** The file contains `BITCOIN_RPC_USER` and `BITCOIN_RPC_PASSWORD` which should only be readable by the owner.

## 🟡 MEDIUM Issues

### 2. **Default Credentials in .env File**
- **Severity:** MEDIUM
- **File:** `.env`
- **Issue:** Using default/weak credentials: `bitcoink/bitcoink`
- **Risk:** Predictable credentials make brute-force attacks easier
- **Fix:**
  ```bash
  # Use strong, unique credentials
  BITCOIN_RPC_USER=unique_username_$(date +%s)
  BITCOIN_RPC_PASSWORD=$(openssl rand -base64 32)
  ```

### 3. **SSL Disabled by Default**
- **Severity:** MEDIUM
- **File:** `.env`
- **Issue:** `BITCOIN_RPC_USE_SSL=false`
- **Risk:** Credentials transmitted in plaintext over the network
- **Fix:** Enable SSL for production:
  ```bash
  BITCOIN_RPC_USE_SSL=true
  BITCOIN_RPC_SSL_VERIFY=true
  ```

## ✅ GOOD Security Practices Found

### 1. **Input Validation** ✅
- **File:** `src/commands/validators.py`
- **Implementation:** `sanitize_rpc_param()` validates all user inputs
- **Pattern:** Whitelist approach using regex `^[a-zA-Z0-9\-_./:]+$`
- **Status:** Properly prevents injection attacks

### 2. **.env Properly Gitignored** ✅
- **File:** `.gitignore`
- **Status:** `.env` is in `.gitignore` and NOT committed to repository
- **Verification:** No `.env` history in git log
- **Note:** Only `.env.example` (template) is committed, which is correct

### 3. **No Hardcoded Secrets** ✅
- **Scan Results:** No API keys, private keys, or secrets in source code
- **Test Files:** Only test credentials found in `tests/test_config.py` (safe)
- **Status:** All credentials properly externalized to `.env` file

### 4. **No Shell Command Injection** ✅
- **Scan Results:** No `os.system()`, `subprocess.call()`, or `eval()` calls
- **Status:** No shell command execution vulnerabilities found

### 5. **Secure HTTP Client** ✅
- **File:** `src/rpc_client.py`
- **Implementation:**
  - Uses `requests` library with proper SSL/TLS support
  - Implements retry logic with exponential backoff
  - No direct `requests.get/post` without validation
  - All requests go through RPC client with input validation

### 6. **Docker Secrets Support** ✅
- **File:** `src/config.py`
- **Implementation:** Supports Docker secrets from `/run/secrets/`
- **Priority Order:** env vars > docker secrets > .env file
- **Status:** Production-ready credential management

### 7. **Timeout Protection** ✅
- **File:** `src/rpc_client.py`
- **Implementation:** Default 30s timeout on all HTTP requests
- **Status:** Prevents hanging connections and DoS scenarios

### 8. **Error Transparency** ✅
- **Implementation:** Preserves original Bitcoin Core errors
- **Security Note:** Doesn't leak implementation details beyond Bitcoin Core

## 📋 Recommendations

### Immediate Actions (Critical)
1. **Fix .env permissions:**
   ```bash
   chmod 600 .env
   ```

2. **Change default credentials:**
   ```bash
   # Generate strong credentials
   BITCOIN_RPC_PASSWORD=$(openssl rand -base64 32)
   ```

### Short-term (Medium Priority)
3. **Enable SSL for production:**
   - Update `.env`: `BITCOIN_RPC_USE_SSL=true`
   - Obtain/configure SSL certificates

4. **Add rate limiting:**
   - Consider adding rate limiting to prevent brute-force attacks
   - Can be implemented in nginx proxy or application layer

5. **Security monitoring:**
   - Implement logging of failed authentication attempts
   - Monitor `logs/bitcoin_wrapper.log` for suspicious activity

### Long-term (Best Practices)
6. **Credential rotation:**
   - Rotate RPC credentials regularly (monthly/quarterly)
   - Document rotation procedure

7. **Network segmentation:**
   - Run Bitcoin node on isolated network
   - Use firewall rules to restrict access

8. **Dependency scanning:**
   - Regularly run: `pip-audit` or `safety check`
   - Update dependencies when vulnerabilities are found

9. **Add security headers:**
   - If exposing via web interface, add security headers
   - CSP, X-Frame-Options, etc.

## 🔍 Dependency Vulnerabilities

Run these commands to check for known vulnerabilities:

```bash
# Activate venv first
source venv/bin/activate

# Check Python dependencies
pip-audit

# Or use safety
safety check

# Check for outdated packages
pip list --outdated
```

## 📊 Security Score

| Category | Status | Score |
|----------|--------|-------|
| Secrets Management | ⚠️ Warning | 7/10 |
| Input Validation | ✅ Good | 9/10 |
| Authentication | ⚠️ Warning | 6/10 |
| Network Security | ⚠️ Warning | 6/10 |
| Code Security | ✅ Good | 9/10 |
| **Overall** | ⚠️ **Good** | **7.4/10** |

## 🎯 Quick Fixes

Run these commands to fix critical issues immediately:

```bash
# 1. Fix .env permissions
chmod 600 .env

# 2. Generate strong password (copy this to .env)
echo "New password: $(openssl rand -base64 32)"

# 3. Verify .env is not tracked
git status .env

# 4. Run dependency security check
source venv/bin/activate && pip-audit
```

## ✅ Summary

**Status:** The project follows good security practices overall, with proper input validation and no hardcoded secrets. The main issues are file permissions and default credentials, which are easily fixable.

**Action Items:**
- ❗ Fix .env file permissions immediately
- ❗ Change default credentials
- ⚠️ Enable SSL for production
- ℹ️ Consider implementing rate limiting
- ℹ️ Set up regular dependency scanning

**Risk Level:** LOW (after fixing file permissions)
