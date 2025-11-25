# Available Claude Code Slash Commands

The following custom slash commands are now available for El Jefe dashboard testing:

## 🧪 Testing Commands

### `/test-validation`
**Purpose**: Quick validation of testing framework setup
**Usage**: `/test-validation`
**What it does**: Runs basic setup validation tests to ensure the testing framework is working correctly
**Requirements**: None (can run without dashboard running)

### `/test-all`
**Purpose**: Run complete testing suite
**Usage**: `/test-all`
**What it does**: Runs unit tests, integration tests, E2E tests, performance tests, and security validation
**Requirements**: Dashboard running on localhost:8080
**Duration**: 5-10 minutes

### `/test-unit`
**Purpose**: Run unit tests only
**Usage**: `/test-unit`
**What it does**: Validates API endpoints, authentication, workflow detection, data validation, and error handling
**Requirements**: Dashboard running on localhost:8080
**Duration**: 1-2 minutes

### `/test-e2e`
**Purpose**: Run end-to-end browser tests
**Usage**: `/test-e2e`
**Options**: Can specify browser (`--browser chromium/firefox/webkit`)
**What it does**: Complete user workflows, cross-browser compatibility, responsive design, accessibility compliance
**Requirements**: Dashboard running on localhost:8080, Playwright browsers installed
**Duration**: 3-5 minutes per browser

### `/test-performance`
**Purpose**: Run load and performance testing
**Usage**: `/test-performance`
**What it does**: Simulates concurrent users, measures response times, validates performance under load
**Requirements**: Dashboard running on localhost:8080, Locust installed
**Duration**: 1+ minutes (configurable)

### `/test-security`
**Purpose**: Run security validation tests
**Usage**: `/test-security`
**What it does**: Tests authentication, XSS protection, SQL injection prevention, input validation, session security
**Requirements**: Dashboard running on localhost:8080
**Duration**: 2-3 minutes

## 🚀 Quick Start Commands

```bash
# Validate testing setup
/test-validation

# Quick health check
/test-unit

# Full validation before deployment
/test-all

# Performance monitoring
/test-performance

# Security audit
/test-security
```

## 📋 Prerequisites

**Before running most tests, ensure:**
1. Dashboard is running: `python3 monitoring_dashboard.py`
2. Dashboard accessible on: http://localhost:8080
3. All dependencies installed: `pip install -r requirements.txt`
4. Testing tools installed: `pip install pytest playwright locust`

## 🎯 Test Coverage Summary

- **Functionality**: API endpoints, workflows, chat interface, file uploads
- **Compatibility**: Cross-browser (Chrome, Firefox, Safari), mobile responsive
- **Performance**: Load testing, response times, concurrent users
- **Security**: Authentication, XSS/SQL injection protection, input validation
- **Accessibility**: WCAG 2.1 AA compliance, keyboard navigation
- **User Experience**: Complete workflows, error handling, real-time updates

## 📊 Test Results

All tests generate comprehensive reports including:
- **HTML reports** with detailed results and screenshots
- **JSON reports** for automated processing
- **Performance metrics** and benchmarks
- **Security findings** and recommendations
- **Coverage analysis** and gaps identification

## 🔧 Customization

Each test command can be customized:
- Modify test parameters in `tests/test_config.json`
- Adjust performance thresholds
- Add custom test scenarios
- Configure browser options
- Set up custom user simulation patterns

## 📞 Support

For any issues with the testing commands:
1. Check dashboard status: `curl -s -o /dev/null -w "%{http_code}" http://localhost:8080`
2. Verify dependencies: `pip list | grep -E "(pytest|playwright|locust)"`
3. Review test logs for specific error details
4. Check `tests/README.md` for detailed documentation

---

**All slash commands are properly formatted and ready to use with Claude Code!**