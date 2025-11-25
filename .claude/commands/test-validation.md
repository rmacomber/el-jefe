# Quick Validation for El Jefe Dashboard

Run basic setup validation tests to ensure the testing framework is working correctly.

```bash
pytest tests/test_basic.py -v
```

This command:
- Validates dashboard import and instantiation
- Checks test configuration loading
- Verifies pytest environment setup
- Confirms all testing dependencies are installed

Requirements:
- Dashboard running on localhost:8080 (optional for basic tests)
- pytest and testing dependencies installed

Use this for quick validation after making changes to the testing setup.