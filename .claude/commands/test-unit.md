# Unit Testing for El Jefe Dashboard

Run comprehensive unit tests to validate individual components, API endpoints, and core functionality.

```bash
python3 tests/run_tests.py --test-type unit
```

**Direct Pytest Execution:**
```bash
# Run all unit tests
pytest tests/test_dashboard_functionality.py -v

# Run specific test classes
pytest tests/test_dashboard_functionality.py::TestDashboardAPI -v
pytest tests/test_dashboard_functionality.py::TestDashboardPages -v
pytest tests/test_dashboard_functionality.py::TestWorkflowDetection -v

# Run specific test methods
pytest tests/test_dashboard_functionality.py::TestDashboardAPI::test_api_workflows_endpoint -v
```

**Unit Test Coverage:**
- **API Endpoint Testing**: All REST endpoints validation
- **Authentication Logic**: Login, token validation, access control
- **Workflow Detection**: Automated workflow assignment algorithms
- **Data Validation**: Input sanitization and type checking
- **Error Handling**: Graceful failure responses and error codes
- **File Upload Logic**: Security validation and processing
- **WebSocket Functionality**: Real-time communication testing
- **Component Integration**: Dashboard navigation and data flow

**Test Categories:**
1. **TestDashboardAPI**: REST API validation
   - Endpoint accessibility and response formats
   - Authentication and authorization
   - Data serialization and validation

2. **TestDashboardPages**: UI component testing
   - Page rendering and navigation
   - Static file serving
   - Template validation

3. **TestWorkflowDetection**: Business logic testing
   - Workflow type detection algorithms
   - Message pattern matching
   - Agent assignment logic

4. **TestFileUploadFunctionality**: File handling testing
   - Upload validation and processing
   - Security checks and sanitization
   - Error handling for invalid files

5. **TestWebSocketFunctionality**: Real-time testing
   - Connection establishment
   - Message handling and routing
   - Connection lifecycle management

**Mocking and Fixtures:**
- Sample workflow, analytics, and chat data
- Authentication headers and tokens
- WebSocket connection simulation
- File upload temporary directories

**Performance Benchmarks:**
- API response times < 1 second
- Database query optimization
- Memory usage validation
- Concurrent request handling

Requirements:
- Dashboard running on localhost:8080 (for integration tests)
- pytest with async support
- All testing dependencies installed

Expected duration: 1-2 minutes for complete unit test suite.

Use for rapid validation during development and CI/CD pipelines.