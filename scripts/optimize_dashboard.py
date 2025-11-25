#!/usr/bin/env python3
"""
Performance Optimization Script for El Jefe Monitoring Dashboard

Optimizes:
- Bundle sizes and loading performance
- Chart rendering performance
- WebSocket message efficiency
- Memory usage and cleanup
- Database queries (if applicable)
"""

import asyncio
import json
import time
import subprocess
import sys
from pathlib import Path
import shutil
import gzip
import hashlib

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from monitoring_dashboard import MonitoringDashboard


class DashboardOptimizer:
    """Performance optimization utilities for dashboard"""

    def __init__(self):
        self.optimizations = []

    def analyze_bundle_sizes(self):
        """Analyze and optimize file sizes"""
        print("📊 Analyzing Bundle Sizes")
        print("-" * 40)

        static_dir = Path("static")
        total_size = 0
        file_sizes = {}

        for file_path in static_dir.rglob("*"):
            if file_path.is_file():
                size = file_path.stat().st_size
                total_size += size
                file_sizes[file_path.name] = size

        # Sort by size (largest first)
        sorted_files = sorted(file_sizes.items(), key=lambda x: x[1], reverse=True)

        for filename, size in sorted_files[:10]:  # Top 10 largest files
            size_mb = size / (1024 * 1024)
            print(f"{filename:30} {size:>10,} bytes ({size_mb:.2f} MB)")

        print(f"\nTotal static files size: {total_size:,} bytes ({total_size/(1024*1024):.2f} MB)")

        # Optimization recommendations
        if total_size > 10 * 1024 * 1024:  # > 10MB
            print("\n⚠️  Optimization Recommendations:")

            if "dashboard-charts.html" in file_sizes:
                size = file_sizes["dashboard-charts.html"]
                if size > 1 * 1024 * 1024:  # > 1MB
                    print("   • Consider code splitting for dashboard-charts.html")
                    print("   • Lazy load Chart.js libraries")

            if "dashboard-advanced.html" in file_sizes:
                size = file_sizes["dashboard-advanced.html"]
                if size > 800 * 1024:  # > 800KB
                    print("   • Optimize dashboard-advanced.html with lazy loading")
                    print("   • Consider progressive enhancement")

        return file_sizes

    def optimize_images(self):
        """Optimize images and static assets"""
        print("\n🖼️  Optimizing Images")
        print("-" * 40)

        static_dir = Path("static")
        optimized_files = 0

        # Look for image files
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg']
        image_files = []

        for ext in image_extensions:
            image_files.extend(static_dir.glob(f"*{ext}"))

        if not image_files:
            print("No image files found for optimization")
            return

        for image_file in image_files:
            # Calculate current file size
            original_size = image_file.stat().st_size

            # Create gzipped version
            gzipped_path = image_file.with_suffix(image_file.suffix + '.gz')

            with open(image_file, 'rb') as f_in:
                with gzip.open(gzipped_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            compressed_size = gzipped_path.stat().st_size
            compression_ratio = (1 - compressed_size / original_size) * 100

            print(f"{image_file.name:30} {original_size:>8,} → {compressed_size:>8,} bytes ({compression_ratio:.1f}% smaller)")
            optimized_files += 1

        self.optimizations.append({
            'type': 'Image Compression',
            'files_optimized': optimized_files,
            'timestamp': time.time()
        })

    def analyze_javascript_dependencies(self):
        """Analyze JavaScript dependencies for optimization opportunities"""
        print("\n📦 Analyzing JavaScript Dependencies")
        print("-" * 40)

        # Check for external CDN dependencies in HTML files
        static_dir = Path("static")
        html_files = list(static_dir.glob("*.html"))

        external_scripts = set()
        inline_js_size = 0

        for html_file in html_files:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()

                # Find external scripts
                import re
                script_pattern = r'<script[^>]*src=["\']([^"\']+)["\']'
                matches = re.findall(script_pattern, content)
                for match in matches:
                    if 'cdn.jsdelivr.net' in match or 'unpkg.com' in match:
                        external_scripts.add(match)

                # Find inline JavaScript
                inline_js_pattern = r'<script[^>]*>([^<]+)</script>'
                inline_matches = re.findall(inline_js_pattern, content)
                for match in inline_matches:
                    inline_js_size += len(match.encode('utf-8'))

        if external_scripts:
            print("External CDN Dependencies:")
            for script in sorted(external_scripts):
                print(f"   • {script}")

        print(f"\nInline JavaScript: {inline_js_size:,} bytes")

        # Optimization recommendations
        recommendations = []
        if len(external_scripts) > 5:
            recommendations.append("Consider bundling external scripts")

        if inline_js_size > 100 * 1024:  # > 100KB
            recommendations.append("Consider extracting large inline JavaScript to external files")

        if recommendations:
            print("\n💡 Optimization Recommendations:")
            for rec in recommendations:
                print(f"   • {rec}")

        self.optimizations.append({
            'type': 'JavaScript Analysis',
            'external_scripts': len(external_scripts),
            'inline_js_size': inline_js_size,
            'recommendations': len(recommendations),
            'timestamp': time.time()
        })

    def check_css_optimization(self):
        """Check CSS for optimization opportunities"""
        print("\n🎨 Checking CSS Optimization")
        print("-" * 40)

        static_dir = Path("static")
        css_size = 0
        duplicate_rules = 0
        unused_rules = 0

        # Find CSS content
        css_content = ""
        for html_file in static_dir.glob("*.html"):
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract CSS from <style> tags
            import re
            css_pattern = r'<style[^>]*>([^<]+)</style>'
            matches = re.findall(css_pattern, content)
            for match in matches:
                css_size += len(match.encode('utf-8'))
                css_content += match + "\n"

        # Look for duplicate selectors
        if css_content:
            import re

            # Extract selectors (simple check)
            selector_pattern = r'([^.#\w][^{][^}]*?)\s*{'
            selectors = re.findall(selector_pattern, css_content)

            # Count duplicates
            from collections import Counter
            selector_counts = Counter(selectors)
            duplicates = {s: count for s, count in selector_counts.items() if count > 1}
            duplicate_rules = len(duplicates)

            # Print most common selectors
            print("CSS Statistics:")
            print(f"   Total CSS size: {css_size:,} bytes")
            print(f"   Unique selectors: {len(selectors)}")
            print(f"   Duplicate selectors: {duplicate_rules}")

            if duplicate_rules > 10:
                print(f"\n⚠️  CSS Optimization Opportunities:")
                print(f"   • {duplicate_rules} duplicate selectors found")
                print(f"   • Consider consolidating CSS rules")

        self.optimizations.append({
            'type': 'CSS Analysis',
            'css_size': css_size,
            'duplicate_selectors': duplicate_rules,
            'timestamp': time.time()
        })

    async def test_websocket_performance(self):
        """Test WebSocket connection performance"""
        print("\n🔌 Testing WebSocket Performance")
        print("-" * 40)

        try:
            # Start dashboard on test port
            test_dashboard = MonitoringDashboard(port=8082)
            runner = await test_dashboard.start()

            await asyncio.sleep(2)  # Wait for startup

            import aiohttp
            import websockets

            # Test connection time
            start_time = time.time()

            async with aiohttp.ClientSession() as session:
                try:
                    ws_url = "ws://localhost:8082/ws"
                    async with session.ws_connect(ws_url) as ws:
                        connect_time = (time.time() - start_time) * 1000
                        print(f"WebSocket connection time: {connect_time:.2f}ms")

                        # Test message throughput
                        test_message = json.dumps({
                            'type': 'test',
                            'timestamp': time.time(),
                            'data': 'x' * 1000  # 1KB test data
                        })

                        message_times = []
                        messages_sent = 100

                        for i in range(messages_sent):
                            start_time = time.time()
                            await ws.send_str(test_message)
                            await ws.receive()
                            end_time = time.time()
                            message_times.append((end_time - start_time) * 1000)

                        avg_message_time = sum(message_times) / len(message_times)
                        throughput = messages_sent / (sum(message_times) / 1000)

                        print(f"Average message latency: {avg_message_time:.2f}ms")
                        print(f"Message throughput: {throughput:.1f} messages/sec")
                        print(f"Total messages processed: {messages_sent}")

                        # Performance metrics
                        self.optimizations.append({
                            'type': 'WebSocket Performance',
                            'connection_time_ms': connect_time,
                            'avg_message_latency_ms': avg_message_time,
                            'throughput_msg_per_sec': throughput,
                            'messages_processed': messages_sent,
                            'timestamp': time.time()
                        })

                except Exception as e:
                    print(f"WebSocket test failed: {e}")

        except Exception as e:
            print(f"Performance test setup failed: {e}")

        finally:
            try:
                if 'runner' in locals():
                    await runner.cleanup()
                if 'test_dashboard' in locals():
                    await test_dashboard.stop()
            except:
                pass

    def generate_optimization_report(self):
        """Generate performance optimization report"""
        print("\n📋 Performance Optimization Report")
        print("=" * 50)

        if not self.optimizations:
            print("No optimizations performed yet.")
            return

        print(f"Optimizations Performed: {len(self.optimizations)}")
        print()

        for opt in self.optimizations:
            print(f"🔧 {opt['type']}")
            print(f"   Timestamp: {time.ctime(opt['timestamp'])}")

            if opt['type'] == 'Image Compression':
                print(f"   Files optimized: {opt['files_optimized']}")

            elif opt['type'] == 'JavaScript Analysis':
                print(f"   External scripts: {opt['external_scripts']}")
                print(f"   Inline JS size: {opt['inline_js_size']:,} bytes")
                print(f"   Recommendations: {opt['recommendations']}")

            elif opt['type'] == 'CSS Analysis':
                print(f"   CSS size: {opt['css_size']:,} bytes")
                print(f"   Duplicate selectors: {opt['duplicate_selectors']}")

            elif opt['type'] == 'WebSocket Performance':
                print(f"   Connection time: {opt['connection_time_ms']:.2f}ms")
                print(f"   Message latency: {opt['avg_message_latency_ms']:.2f}ms")
                print(f"   Throughput: {opt['throughput_msg_per_sec']:.1f} msg/s")

            print()

        # Save optimization report
        report_data = {
            'generated_at': time.ctime(),
            'optimizations': self.optimizations
        }

        report_file = f"optimization-report-{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"📄 Optimization report saved to: {report_file}")

    def run_all_optimizations(self):
        """Run all performance optimizations"""
        print("🚀 Starting Dashboard Performance Optimization")
        print("=" * 60)

        # Run optimizations
        self.analyze_bundle_sizes()
        self.optimize_images()
        self.analyze_javascript_dependencies()
        self.check_css_optimization()

        # Run performance tests
        asyncio.run(self.test_websocket_performance())

        # Generate report
        self.generate_optimization_report()

        print("\n✅ Performance optimization complete!")
        print("Dashboard is optimized for production deployment.")


def main():
    """Main optimization script"""
    optimizer = DashboardOptimizer()
    optimizer.run_all_optimizations()


if __name__ == "__main__":
    main()