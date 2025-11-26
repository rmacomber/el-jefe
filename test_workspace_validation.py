#!/usr/bin/env python3
"""
Quick validation test for workspace integration
"""
import asyncio
import aiohttp
import json
from pathlib import Path

async def test_workspace_integration():
    """Test that the workspace functionality is properly integrated"""

    # Base URL
    base_url = "http://localhost:8080"

    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True)) as session:
        print("🔍 Testing Workspace Integration")
        print("=" * 50)

        # 1. Test login
        print("\n1. Testing login...")
        login_data = {'password': 'Bermalberist-55'}
        async with session.post(f"{base_url}/login", data=login_data) as resp:
            if resp.status in [200, 302]:  # Both are valid responses
                print("✅ Login processed")
                # Check if we have any cookies set
                cookies = session.cookie_jar.filter_cookies(base_url)
                if cookies:
                    print(f"   Session cookies set: {list(cookies.keys())}")
                else:
                    print("   No cookies set, but continuing...")
            else:
                print(f"❌ Login failed: {resp.status}")
                return False

        # 2. Test main dashboard loads workspace-integrated version
        print("\n2. Testing dashboard serves workspace version...")
        async with session.get(f"{base_url}/") as resp:
            if resp.status == 200:
                content = await resp.text()
                # Check for workspace integration markers
                if 'showView(\'workspaces\')' in content:
                    print("✅ Dashboard serves workspace-integrated version")
                elif 'dashboard-agent-focused.html' in content or '📁 Workspaces' in content:
                    print("✅ Dashboard contains workspace features")
                else:
                    print("⚠️  Dashboard may not be workspace-integrated")
                    print(f"Content length: {len(content)}")
            else:
                print(f"❌ Dashboard load failed: {resp.status}")
                return False

        # 3. Test workspace API endpoint
        print("\n3. Testing workspace API...")
        async with session.get(f"{base_url}/api/workspaces?limit=5") as resp:
            if resp.status == 200:
                data = await resp.json()
                if data.get('success') and 'workspaces' in data:
                    workspaces = data['workspaces']
                    print(f"✅ Workspace API working - found {len(workspaces)} workspaces")
                    if workspaces:
                        print(f"   Example: {workspaces[0].get('name', 'Unknown')}")
                else:
                    print("❌ Workspace API returned invalid response")
            else:
                print(f"❌ Workspace API failed: {resp.status}")

        # 4. Test real agent data API
        print("\n4. Testing real agent data API...")
        async with session.get(f"{base_url}/api/agents/real") as resp:
            if resp.status == 200:
                data = await resp.json()
                if data.get('success'):
                    agents = data.get('agents', [])
                    print(f"✅ Real agent API working - found {len(agents)} agents")
                else:
                    print("⚠️  Real agent API may have issues")
            else:
                print(f"❌ Real agent API failed: {resp.status}")

        print("\n" + "=" * 50)
        print("🎉 Workspace Integration Validation Complete!")
        print("📝 The dashboard should now show:")
        print("   - 📁 Workspaces button in navigation")
        print("   - Toggle between Agents and Workspaces views")
        print("   - Real agent data instead of sample data")
        print("   - Workspace browser with file preview")

        return True

if __name__ == "__main__":
    asyncio.run(test_workspace_integration())