# Security Testing for El Jefe Dashboard

Run comprehensive security validation tests to identify vulnerabilities and ensure robust security controls.

```bash
python3 tests/run_tests.py --test-type security
```

**Individual Security Tests:**
```bash
# Authentication and authorization testing
pytest tests/test_dashboard_functionality.py::TestAuthenticationSecurity -v

# XSS protection validation
pytest tests/test_dashboard_functionality.py::test_xss_prevention -v

# SQL injection protection
pytest tests/test_dashboard_functionality.py::test_sql_injection_protection -v

# Input validation and sanitization
pytest tests/test_dashboard_functionality.py::TestDataValidation -v
```

**Security Test Coverage:**
- **Authentication Validation**: Login/logout flows, session management, token validation
- **XSS Prevention**: Script injection protection in chat, forms, and file uploads
- **SQL Injection Protection**: Database query sanitization and parameter binding
- **Path Traversal Prevention**: File system access controls and directory traversal
- **Input Validation**: Data sanitization, type checking, and length validation
- **Session Security**: Token generation, expiration, and secure handling
- **CORS Configuration**: Cross-origin resource sharing policies
- **Rate Limiting**: Request throttling and DDoS protection

**Security Test Payloads:**
- XSS vectors: `<script>alert('xss')</script>`, `javascript:alert('xss')`
- SQL injection: `'; DROP TABLE users; --`, `1' OR '1'='1`
- Path traversal: `../../../etc/passwd`, `..\\..\\..\\windows\\system32`

**Vulnerability Scenarios:**
- Authentication bypass attempts
- Privilege escalation testing
- Data injection and manipulation
- File upload security validation
- API endpoint protection testing

**Security Headers Validation:**
- Content Security Policy (CSP)
- X-Frame-Options
- X-Content-Type-Options
- Strict-Transport-Security
- Referrer-Policy

Requirements:
- Dashboard running on localhost:8080
- Full testing framework installed
- No destructive payloads (read-only security testing)

Expected duration: 2-3 minutes for complete security validation suite.

Use for security validation before deployments and after significant code changes.