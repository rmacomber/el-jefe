#!/usr/bin/env python3
"""
Dashboard Testing with Authentication Support

Tests the enhanced dashboard functionality with proper authentication handling.
"""

import asyncio
import aiohttp
import json
import time
import base64
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from monitoring_dashboard import MonitoringDashboard


class AuthenticatedDashboardTester:
    """Test suite for dashboard with authentication"""

    def __init__(self):
        self.base_url = "http://localhost:8082"
        self.ws_url = "ws://localhost:8082/ws"
        self.dashboard = None
        self.test_results = []
        self.password = "Bermalberist-55"  # Same password as main dashboard
        self.auth_token = None

    async def start_test_dashboard(self):
        """Start dashboard in test mode on port 8082 with known password"""
        try:
            self.dashboard = MonitoringDashboard(
                host="localhost",
                port=8082,
                password=self.password
            )
            self.dashboard_runner = await self.dashboard.start()
            print(f"✅ Test dashboard started on {self.base_url}")

            # Generate auth token
            import hashlib
            self.auth_token = hashlib.sha256(self.password.encode()).hexdigest()
            print(f"✅ Authentication token generated")

            return True
        except Exception as e:
            print(f"❌ Failed to start test dashboard: {e}")
            return False

    def get_auth_headers(self):
        """Get authentication headers"""
        credentials = base64.b64encode(f"admin:{self.password}".encode()).decode()
        return {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json"
        }

    async def test_authenticated_access(self):
        """Test authenticated access to dashboard"""
        print("\n🔐 Testing Authenticated Access")
        print("-" * 30)

        try:
            async with aiohttp.ClientSession() as session:
                # Test login
                login_data = {
                    "username": "admin",
                    "password": self.password
                }

                async with session.post(
                    f"{self.base_url}/login",
                    json=login_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("  ✅ Login successful")
                        return True
                    else:
                        print(f"  ❌ Login failed: {response.status}")
                        return False

        except Exception as e:
            print(f"  ❌ Auth test failed: {e}")
            return False

    async def test_enhanced_api_endpoints(self):
        """Test enhanced API endpoints with authentication"""
        print("\n🔗 Testing Enhanced API Endpoints")
        print("-" * 30)

        try:
            auth_headers = self.get_auth_headers()
            async with aiohttp.ClientSession(headers=auth_headers) as session:
                endpoints_to_test = [
                    {
                        "method": "GET",
                        "url": f"{self.base_url}/api/status",
                        "description": "System status"
                    },
                    {
                        "method": "GET",
                        "url": f"{self.base_url}/api/agents",
                        "description": "Agents list"
                    },
                    {
                        "method": "GET",
                        "url": f"{self.base_url}/api/workflows",
                        "description": "Workflows list"
                    },
                    {
                        "method": "GET",
                        "url": f"{self.base_url}/api/chat/sessions",
                        "description": "Chat sessions"
                    },
                    {
                        "method": "GET",
                        "url": f"{self.base_url}/api/scheduled-workflows",
                        "description": "Scheduled workflows"
                    }
                ]

                endpoint_results = []

                for endpoint in endpoints_to_test:
                    start_time = time.time()

                    if endpoint["method"] == "GET":
                        async with session.get(endpoint["url"]) as response:
                            end_time = time.time()
                            response_time = end_time - start_time

                            success = response.status == 200
                            endpoint_results.append({
                                "endpoint": endpoint["description"],
                                "success": success,
                                "status_code": response.status,
                                "response_time_ms": response_time * 1000
                            })

                            status = "✅" if success else "❌"
                            print(f"  {status} {endpoint['description']}: {response.status} ({response_time*1000:.1f}ms)")

                success_rate = sum(1 for r in endpoint_results if r["success"]) / len(endpoint_results) * 100
                print(f"  📊 API Endpoint Success Rate: {success_rate:.1f}%")

                self.test_results.append({
                    "test": "Enhanced API Endpoints",
                    "success": success_rate > 80,
                    "endpoints_tested": len(endpoint_results),
                    "successful_endpoints": sum(1 for r in endpoint_results if r["success"]),
                    "success_rate": success_rate
                })

        except Exception as e:
            print(f"  ❌ API endpoints test failed: {e}")
            self.test_results.append({
                "test": "Enhanced API Endpoints",
                "success": False,
                "error": str(e)
            })

    async def test_workflow_operations(self):
        """Test workflow operations with authentication"""
        print("\n⚙️ Testing Workflow Operations")
        print("-" * 30)

        try:
            auth_headers = self.get_auth_headers()
            async with aiohttp.ClientSession(headers=auth_headers) as session:
                # Test workflow assignment
                workflow_data = {
                    "workflow_id": "feature-development",
                    "parameters": {"feature": "test functionality", "priority": "medium"},
                    "priority": "medium",
                    "session_id": "test_session"
                }

                start_time = time.time()

                async with session.post(
                    f"{self.base_url}/api/workflows/start",
                    json=workflow_data
                ) as response:
                    end_time = time.time()
                    response_time = end_time - start_time

                    if response.status == 200:
                        result = await response.json()
                        print(f"  ✅ Workflow assignment successful: {result.get('session_id', 'N/A')}")

                        # Wait a moment for workflow processing
                        await asyncio.sleep(2)

                        # Check workflow status
                        async with session.get(f"{self.base_url}/api/workflows") as status_response:
                            if status_response.status == 200:
                                workflows_data = await status_response.json()
                                active_workflows = len(workflows_data)
                                print(f"  ✅ Active workflows: {active_workflows}")

                        self.test_results.append({
                            "test": "Workflow Operations",
                            "success": True,
                            "assignment_time_ms": response_time * 1000,
                            "active_workflows": active_workflows if 'active_workflows' in locals() else 0
                        })

                    else:
                        print(f"  ❌ Workflow assignment failed: {response.status}")
                        self.test_results.append({
                            "test": "Workflow Operations",
                            "success": False,
                            "status_code": response.status
                        })

        except Exception as e:
            print(f"  ❌ Workflow operations test failed: {e}")
            self.test_results.append({
                "test": "Workflow Operations",
                "success": False,
                "error": str(e)
            })

    async def test_file_upload(self):
        """Test file upload functionality"""
        print("\n📁 Testing File Upload")
        print("-" * 20)

        try:
            auth_headers = self.get_auth_headers()
            async with aiohttp.ClientSession(headers=auth_headers) as session:
                # Test file upload
                test_content = "def test_function():\n    return 'Hello, World!'"
                content_b64 = base64.b64encode(test_content.encode()).decode()

                upload_data = {
                    "filename": "test_file.py",
                    "content": content_b64,
                    "file_type": "text/x-python",
                    "session_id": "test_upload_session"
                }

                start_time = time.time()

                async with session.post(
                    f"{self.base_url}/api/upload",
                    json=upload_data
                ) as response:
                    end_time = time.time()
                    upload_time = end_time - start_time

                    if response.status == 200:
                        result = await response.json()
                        file_size = result.get("file_size", 0)
                        print(f"  ✅ File upload successful: {file_size} bytes")

                        self.test_results.append({
                            "test": "File Upload",
                            "success": True,
                            "upload_time_ms": upload_time * 1000,
                            "file_size": file_size
                        })

                    else:
                        print(f"  ❌ File upload failed: {response.status}")
                        self.test_results.append({
                            "test": "File Upload",
                            "success": False,
                            "status_code": response.status
                        })

        except Exception as e:
            print(f"  ❌ File upload test failed: {e}")
            self.test_results.append({
                "test": "File Upload",
                "success": False,
                "error": str(e)
            })

    async def test_dashboard_access(self):
        """Test dashboard page access"""
        print("\n🌐 Testing Dashboard Access")
        print("-" * 25)

        try:
            auth_headers = self.get_auth_headers()
            async with aiohttp.ClientSession(headers=auth_headers) as session:
                dashboard_urls = [
                    ("/", "Default dashboard"),
                    ("/dashboard/simple", "Simple dashboard"),
                    ("/dashboard/enhanced", "Enhanced dashboard"),
                    ("/dashboard/charts", "Charts dashboard"),
                    ("/dashboard/advanced", "Advanced dashboard"),
                    ("/dashboard/nav", "Navigation page")
                ]

                access_results = []

                for url, description in dashboard_urls:
                    full_url = f"{self.base_url}{url}"
                    start_time = time.time()

                    async with session.get(full_url) as response:
                        end_time = time.time()
                        load_time = end_time - start_time

                        success = response.status == 200
                        content_type = response.headers.get('content-type', '')

                        access_results.append({
                            "url": url,
                            "description": description,
                            "success": success,
                            "status_code": response.status,
                            "content_type": content_type,
                            "load_time_ms": load_time * 1000
                        })

                        status = "✅" if success else "❌"
                        print(f"  {status} {description}: {response.status} ({load_time*1000:.1f}ms)")

                success_rate = sum(1 for r in access_results if r["success"]) / len(access_results) * 100
                print(f"  📊 Dashboard Access Success Rate: {success_rate:.1f}%")

                self.test_results.append({
                    "test": "Dashboard Access",
                    "success": success_rate > 80,
                    "urls_tested": len(dashboard_urls),
                    "successful_urls": sum(1 for r in access_results if r["success"]),
                    "success_rate": success_rate
                })

        except Exception as e:
            print(f"  ❌ Dashboard access test failed: {e}")
            self.test_results.append({
                "test": "Dashboard Access",
                "success": False,
                "error": str(e)
            })

    async def run_all_tests(self):
        """Run complete test suite with authentication"""
        print("🧪 Starting Dashboard Tests with Authentication")
        print("=" * 50)

        try:
            # Start dashboard
            if not await self.start_test_dashboard():
                return False

            # Wait for dashboard to initialize
            await asyncio.sleep(3)

            # Run tests
            await self.test_authenticated_access()
            await self.test_enhanced_api_endpoints()
            await self.test_workflow_operations()
            await self.test_file_upload()
            await self.test_dashboard_access()

            # Generate test report
            await self.generate_test_report()

            return True

        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            return False

        finally:
            await self.cleanup()

    async def generate_test_report(self):
        """Generate test report"""
        print("\n" + "=" * 50)
        print("📋 DASHBOARD TEST REPORT")
        print("=" * 50)

        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r.get("success", False))
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0

        print(f"\n📊 Overall Results:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Successful: {successful_tests}")
        print(f"  Success Rate: {success_rate:.1f}%")

        print(f"\n📋 Test Results:")
        for result in self.test_results:
            test_name = result.get("test", "Unknown")
            success = result.get("success", False)
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} {test_name}")

        if success_rate >= 80:
            print(f"\n✅ Dashboard functionality is working well!")
        elif success_rate >= 60:
            print(f"\n⚠️ Dashboard functionality is partially working.")
        else:
            print(f"\n❌ Dashboard functionality needs significant improvements.")

        # Save report
        report_data = {
            "test_run": datetime.now().isoformat(),
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": success_rate,
            "test_results": self.test_results
        }

        report_file = f"test_report_dashboard_auth_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"\n📄 Report saved to: {report_file}")

    async def cleanup(self):
        """Clean up test resources"""
        try:
            if self.dashboard_runner:
                await self.dashboard_runner.cleanup()
                print("🧹 Test dashboard cleaned up")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")


async def main():
    """Main test runner"""
    tester = AuthenticatedDashboardTester()
    success = await tester.run_all_tests()

    if success:
        print("\n✅ Dashboard tests completed successfully!")
        return 0
    else:
        print("\n❌ Dashboard tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)