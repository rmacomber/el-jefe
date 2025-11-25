# Performance Testing for El Jefe Dashboard

Run comprehensive load testing and performance validation using Locust to simulate concurrent users and measure system performance.

```bash
locust -f tests/locustfile.py --headless --users 20 --run-time 60s --host http://localhost:8080
```

This command:
- Simulates 20 concurrent users accessing the dashboard
- Runs load test for 60 seconds
- Measures response times and throughput
- Validates performance under load
- Generates performance metrics and reports

**Custom Parameters:**
- `--users`: Number of concurrent users (default: 20)
- `--run-time`: Test duration (default: 60s)
- `--spawn-rate`: Users spawned per second (default: 5)
- `--host`: Dashboard URL (default: http://localhost:8080)

**Interactive Mode:**
```bash
locust -f tests/locustfile.py --host http://localhost:8080
# Visit http://localhost:8089 for web interface
```

**User Simulation Patterns:**
- DashboardUser (70%): Standard dashboard interactions
- AdminUser (20%): Administrative functions and logs
- MobileUser (10%): Mobile-optimized interactions

**Performance Thresholds:**
- Page load time: < 3 seconds
- API response time: < 1 second
- Chart rendering: < 2 seconds
- Concurrent users: 50+ supported

Requirements:
- Dashboard running on localhost:8080
- Locust installed (`pip install locust`)
- Sufficient system resources for load testing

Use for performance validation before deployments and to monitor system scalability.