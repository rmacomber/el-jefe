#!/usr/bin/env python3
"""
Dashboard Launcher for El Jefe

Simple utility to launch the monitoring dashboard from within the El Jefe system.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def launch_dashboard():
    """Launch the monitoring dashboard."""
    try:
        # Import the dashboard module
        from monitoring_dashboard import MonitoringDashboard

        # Create and start the dashboard
        dashboard = MonitoringDashboard()

        print("🚀 Starting El Jefe Monitoring Dashboard...")
        print("📊 Dashboard will be available at: http://localhost:8080")

        # Use asyncio to start the dashboard
        async def start_dashboard_async():
            runner = await dashboard.start()
            print("✅ Dashboard started successfully!")
            print("💻 Open http://localhost:8080 in your browser to view")
            print("⏹️ Press Ctrl+C to stop the dashboard")

            try:
                # Keep running until interrupted
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n⏹️ Stopping monitoring dashboard...")
                await dashboard.stop()
                await runner.cleanup()
                print("✅ Dashboard stopped successfully")

        # Run the dashboard
        asyncio.run(start_dashboard_async())

    except ImportError as e:
        print(f"❌ Dashboard dependencies not found: {e}")
        print("💡 Install with: pip install websockets aiohttp-cors")
        return False
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        return False

    return True


if __name__ == "__main__":
    launch_dashboard()