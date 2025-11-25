#!/usr/bin/env python3
"""
Test script for the new logging system
"""

import asyncio
import hashlib
import aiohttp
import json
from datetime import datetime

async def test_logging_system():
    """Test the logging system by making authenticated requests."""

    # Login to get session token
    password = "Bermalberist-55"
    auth_token = hashlib.sha256(password.encode()).hexdigest()[:16]

    base_url = "http://localhost:8080"

    async with aiohttp.ClientSession() as session:
        print("🧪 Testing Dashboard Logging System")
        print("=" * 40)

        # Test 1: Login
        print("1. Testing authentication...")
        async with session.post(f"{base_url}/login", data={"password": password}) as resp:
            if resp.status == 200:
                print("✅ Login successful")
                cookies = resp.cookies
            else:
                print(f"❌ Login failed: {resp.status}")
                return

        # Test 2: Get debug info
        print("\n2. Testing debug info endpoint...")
        async with session.get(f"{base_url}/api/debug/info", cookies=cookies) as resp:
            if resp.status == 200:
                debug_data = await resp.json()
                print("✅ Debug info retrieved")
                print(f"   - Dashboard running: {debug_data['dashboard_state']['dashboard_running']}")
                print(f"   - Total logs in memory: {debug_data['dashboard_state']['total_logs']}")
                print(f"   - Log file path: {debug_data['log_file_path']}")
            else:
                print(f"❌ Debug info failed: {resp.status}")

        # Test 3: Get logs
        print("\n3. Testing logs endpoint...")
        async with session.get(f"{base_url}/api/logs?limit=10", cookies=cookies) as resp:
            if resp.status == 200:
                logs_data = await resp.json()
                print("✅ Logs retrieved")
                print(f"   - Total logs: {logs_data['summary']['total_logs']}")
                print(f"   - Recent errors: {logs_data['summary']['recent_errors']}")
                print(f"   - Level counts: {logs_data['summary']['level_counts']}")
                print(f"   - Category counts: {logs_data['summary']['category_counts']}")

                # Show recent logs
                if logs_data['logs']:
                    print(f"\n   Recent log entries:")
                    for i, log in enumerate(logs_data['logs'][:3]):
                        timestamp = datetime.fromisoformat(log['timestamp']).strftime('%H:%M:%S')
                        print(f"   {i+1}. [{timestamp}] {log['level']} [{log['category']}] {log['message']}")
            else:
                print(f"❌ Logs endpoint failed: {resp.status}")
                error_text = await resp.text()
                print(f"   Error: {error_text}")

        # Test 4: Export logs
        print("\n4. Testing logs export...")
        async with session.get(f"{base_url}/api/logs/export?format=json&include_details=false", cookies=cookies) as resp:
            if resp.status == 200:
                export_data = await resp.text()
                export_json = json.loads(export_data)
                print("✅ Logs export successful")
                print(f"   - Export timestamp: {export_json['export_timestamp']}")
                print(f"   - Total logs exported: {export_json['total_logs']}")
                print(f"   - Dashboard version: {export_json['dashboard_version']}")
            else:
                print(f"❌ Logs export failed: {resp.status}")

        print("\n🎉 Logging system test completed!")
        print("\n📊 Access the logs dashboard at:")
        print(f"   - Local: http://localhost:8080/logs")
        print(f"   - Network: http://192.168.18.181:8080/logs")
        print(f"   - Password: {password}")

if __name__ == "__main__":
    asyncio.run(test_logging_system())