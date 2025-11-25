# El Jefe Dashboard Testing Suite

Comprehensive testing framework for the El Jefe monitoring dashboard, including unit tests, integration tests, end-to-end tests, performance tests, and security validation.

## 🧪 Test Types

### Unit Tests (`test_dashboard_functionality.py`)
- **API endpoint testing** - Validate all REST endpoints
- **Authentication testing** - Verify security and access control
- **Data validation** - Test input validation and sanitization
- **Error handling** - Verify graceful error responses
- **Workflow detection logic** - Test automated workflow assignment

### Integration Tests (`test_functionality_validation.py`)
- **Full workflow lifecycle** - Complete workflow assignment to completion
- **Chat workflow integration** - Message-to-workflow automation
- **Component integration** - Dashboard navigation and data flow
- **Security pipeline validation** - Three-stage security verification

### End-to-End Tests (`test_end_to_end.py`)
- **Full user workflows** - Complete user journeys from login to task completion
- **Cross-browser compatibility** - Chrome, Firefox, Safari testing
- **Responsive design** - Mobile, tablet, desktop validation
- **Accessibility compliance** - WCAG 2.1 AA testing
- **Performance validation** - Load times and rendering performance

### Performance Tests (`locustfile.py`)
- **Load testing** - Simulate concurrent user load
- **Stress testing** - System limits and breaking points
- **User behavior simulation** - Realistic interaction patterns
- **Performance monitoring** - Response times and resource usage

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-flask selenium playwright locust
playwright install
```

### 2. Start the Dashboard
```bash
python monitoring_dashboard.py
```

### 3. Run All Tests
```bash
python tests/run_tests.py
```

### 4. Run Specific Test Types
```bash
# Unit tests only
python tests/run_tests.py --test-type unit

# End-to-end tests only
python tests/run_tests.py --test-type e2e

# Performance tests only
python tests/run_tests.py --test-type performance
```

## 📊 Test Categories

### Security Testing
- **Authentication validation** - Login/logout flows
- **XSS prevention** - Script injection protection
- **SQL injection protection** - Database security
- **Path traversal prevention** - File system security
- **Session management** - Token validation

### Performance Testing
- **Page load times** - Dashboard initialization
- **API response times** - Backend endpoint performance
- **Chart rendering performance** - Data visualization speed
- **Concurrent user handling** - System scalability
- **Memory usage monitoring** - Resource efficiency

### Usability Testing
- **Keyboard navigation** - Accessibility compliance
- **Screen reader compatibility** - WCAG guidelines
- **Mobile responsiveness** - Touch interface optimization
- **Error message clarity** - User experience validation
- **Workflow intuitiveness** - User journey optimization

## 🛠️ Test Configuration

Configuration is managed through `tests/test_config.json`:

```json
{
  "test_settings": {
    "dashboard_url": "http://localhost:5000",
    "default_timeout": 30000,
    "browser_versions": ["chromium", "firefox", "webkit"]
  },
  "performance_thresholds": {
    "page_load_time": 3000,
    "api_response_time": 1000,
    "concurrent_users": 50
  }
}
```

## 📈 Performance Testing with Locust

### Web Interface
```bash
locust -f tests/locustfile.py --host http://localhost:5000
```
Visit http://localhost:8089 for the web interface.

### Headless Mode
```bash
locust -f tests/locustfile.py --headless --users 100 --spawn-rate 10 --run-time 5m
```

### User Simulation Patterns
- **DashboardUser** (70% of users) - Standard dashboard interactions
- **AdminUser** (20% of users) - Administrative functions
- **MobileUser** (10% of users) - Mobile-optimized interactions

## 🔧 Individual Test Execution

### Pytest Commands
```bash
# Run specific test class
pytest tests/test_dashboard_functionality.py::TestDashboardAPI -v

# Run with coverage
pytest tests/ --cov=monitoring_dashboard --cov-report=html

# Run with performance profiling
pytest tests/ --profile

# Run in parallel
pytest tests/ -n auto
```

### Playwright E2E Testing
```bash
# Run specific browser
pytest tests/test_end_to_end.py --browser chromium

# Run with UI (headed mode)
pytest tests/test_end_to_end.py --headed

# Generate HTML report
pytest tests/test_end_to_end.py --html=report.html
```

## 📋 Test Reports

### Automated Report Generation
After running tests, you'll get:
- **HTML report** - Visual test results with screenshots
- **JSON report** - Machine-readable test data
- **Performance metrics** - Response times and resource usage
- **Coverage report** - Code coverage analysis

### Custom Reporting
```bash
# Generate combined report
python tests/run_tests.py --report-only

# Custom report location
TEST_RESULTS_DIR=custom_reports python tests/run_tests.py
```

## 🔍 Test Data and Fixtures

### Sample Data (`conftest.py`)
- **Workflow data** - Sample workflows for testing
- **Analytics data** - Mock analytics responses
- **Chat data** - Sample conversation histories
- **Authentication data** - Test user credentials

### Mock Services
- **Agent responses** - Mock agent availability and capabilities
- **WebSocket connections** - Simulated real-time updates
- **File uploads** - Mock file handling
- **External APIs** - Mock external service integration

## 🚨 Security Test Payloads

### XSS Protection Tests
```javascript
<script>alert('xss')</script>
javascript:alert('xss')
onmouseover=alert('xss')
';alert('xss');//
```

### SQL Injection Tests
```sql
'; DROP TABLE users; --
1' OR '1'='1
UNION SELECT * FROM users
```

### Path Traversal Tests
```
../../../etc/passwd
..\\..\\..\\windows\\system32
....//....//....//etc/passwd
```

## 📱 Mobile Testing

### Responsive Breakpoints
- **Mobile**: 375x667 (iPhone)
- **Tablet**: 768x1024 (iPad)
- **Desktop**: 1920x1080 (Full HD)

### Mobile-Specific Tests
- Touch gesture handling
- Viewport scaling
- Mobile menu functionality
- Performance on slower connections

## 🔧 CI/CD Integration

### GitHub Actions Example
```yaml
name: Dashboard Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio playwright
          playwright install chromium
      - name: Run tests
        run: python tests/run_tests.py --test-type unit,integration
```

### Docker Testing
```dockerfile
FROM python:3.11
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN playwright install chromium
CMD ["python", "tests/run_tests.py"]
```

## 🐛 Troubleshooting

### Common Issues

**Dashboard not starting**
```bash
# Check if port 5000 is available
lsof -i :5000
# Kill existing processes
kill -9 <PID>
```

**Playwright browsers not found**
```bash
# Reinstall browsers
playwright install --force
```

**Tests timing out**
```bash
# Increase timeout in test_config.json
"default_timeout": 60000
```

**Authentication failures**
```bash
# Check dashboard password
grep -n "eljefe_admin" monitoring_dashboard.py
```

### Debug Mode
```bash
# Run tests with debug output
pytest tests/ -v -s --tb=long

# Run dashboard in debug mode
python monitoring_dashboard.py --debug
```

## 📚 Advanced Usage

### Custom Test Scenarios
Create custom tests by extending existing test classes:

```python
class CustomDashboardTests(TestDashboardFunctionality):
    def test_custom_workflow(self):
        # Custom test implementation
        pass
```

### Performance Baselines
Establish performance baselines and track improvements:

```bash
# Run baseline tests
python tests/run_tests.py --test-type performance

# Compare with previous results
python tests/compare_performance.py baseline.json current.json
```

### Continuous Monitoring
Set up continuous monitoring for performance regression:

```bash
# Run monitoring tests hourly
0 * * * * cd /path/to/dashboard && python tests/run_tests.py --test-type performance
```

## 🎯 Best Practices

1. **Test Isolation** - Each test should be independent
2. **Data Cleanup** - Clean up test data after each test
3. **Mock External Dependencies** - Avoid real external service calls
4. **Performance Budgets** - Set and monitor performance thresholds
5. **Regular Maintenance** - Keep tests updated with feature changes

## 🤝 Contributing

When adding new tests:
1. Follow existing test patterns and naming conventions
2. Update documentation for new test scenarios
3. Ensure tests are deterministic and reliable
4. Add appropriate fixtures for test data
5. Include both positive and negative test cases

## 📞 Support

For testing issues:
1. Check troubleshooting section above
2. Review test logs for specific error details
3. Verify dashboard is running and accessible
4. Ensure all dependencies are installed correctly
5. Check network connectivity for integration tests