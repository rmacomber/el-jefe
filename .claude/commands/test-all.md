# Full Test Suite for El Jefe Dashboard

Run the complete testing suite including unit tests, integration tests, end-to-end tests, performance tests, and security validation.

```bash
python3 tests/run_tests.py --test-type all
```

This command:
- Automatically starts the dashboard if not running
- Runs unit tests for API endpoints and functionality
- Executes integration tests for workflow systems
- Performs end-to-end browser automation tests
- Conducts security validation and penetration testing
- Generates comprehensive test reports

Requirements:
- Python 3.11+ with all testing dependencies
- Dashboard accessible on localhost:8080
- Sufficient system resources for comprehensive testing

Test Coverage:
- API endpoints and authentication
- Workflow assignment and execution
- Chat interface and file uploads
- Cross-browser compatibility
- Mobile responsive design
- Performance and load testing
- Security validation (XSS, SQL injection)
- Accessibility compliance (WCAG 2.1 AA)

Expected duration: 5-10 minutes for full suite completion.