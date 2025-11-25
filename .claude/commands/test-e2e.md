# End-to-End Browser Testing for El Jefe Dashboard

Run comprehensive cross-browser end-to-end tests using Playwright to validate complete user workflows and browser compatibility.

```bash
pytest tests/test_end_to_end.py -v --browser chromium
```

**Browser Options:**
```bash
# Chrome/Chromium testing
pytest tests/test_end_to_end.py --browser chromium

# Firefox testing
pytest tests/test_end_to_end.py --browser firefox

# Safari/WebKit testing
pytest tests/test_end_to_end.py --browser webkit

# All browsers (sequential)
pytest tests/test_end_to_end.py --browser chromium --browser firefox --browser webkit
```

**Additional Options:**
```bash
# Run tests with visible browser (headed mode)
pytest tests/test_end_to_end.py --headed

# Generate HTML report
pytest tests/test_end_to_end.py --html=report.html

# Run specific test class
pytest tests/test_end_to_end.py::TestDashboardE2E -v
```

**Test Coverage:**
- Full user workflows from login to task completion
- Cross-browser compatibility (Chrome, Firefox, Safari)
- Responsive design validation (mobile, tablet, desktop)
- Accessibility compliance (WCAG 2.1 AA standards)
- Performance metrics (page load times, rendering speed)
- Real-time update functionality
- Error handling and user feedback
- Form validation and submission

**User Workflow Scenarios:**
- Authentication and dashboard navigation
- Chat interface and workflow assignment
- File upload and management
- Analytics and charts interaction
- Multi-dashboard version switching
- Mobile touch interactions

**Performance Validation:**
- Page load time < 3 seconds
- Chart rendering < 2 seconds
- Interactive elements < 500ms response

Requirements:
- Dashboard running on localhost:8080
- Playwright browsers installed (`playwright install`)
- Sufficient system resources for browser automation

Expected duration: 3-5 minutes per browser for complete E2E suite.