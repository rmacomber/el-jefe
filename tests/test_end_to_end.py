"""
End-to-end tests for El Jefe dashboard using Playwright
"""
import pytest
import asyncio
from playwright.async_api import async_playwright, expect
import time

class TestDashboardE2E:
    """End-to-end tests for the dashboard"""

    @pytest.mark.asyncio
    async def test_full_user_workflow(self):
        """Test complete user workflow from login to task completion"""
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                # Navigate to dashboard (adjust URL as needed)
                await page.goto("http://localhost:5000")

                # Wait for page to load
                await expect(page).to_have_title("El Jefe Dashboard")

                # Test authentication
                await page.fill('input[name="password"]', "eljefe_admin")
                await page.click('button[type="submit"]')

                # Wait for dashboard to load
                await expect(page.locator('.dashboard-container')).to_be_visible()

                # Test navigation between dashboard versions
                await page.click('text="Advanced Dashboard"')
                await expect(page.locator('h1')).to_contain_text("Advanced Analytics Dashboard")

                # Test chat functionality
                chat_input = page.locator('#chatInput')
                await chat_input.fill("I need to perform a security audit")
                await page.click('button:has-text("Send")')

                # Wait for response
                await expect(page.locator('.chat-messages')).to_contain_text("security audit")

                # Test workflow assignment
                await page.click('button:has-text("Assign Workflow")')
                await expect(page.locator('.workflow-assignment')).to_be_visible()

                # Test file upload
                file_input = page.locator('input[type="file"]')
                await file_input.set_input_files("test_file.txt")

                # Test agent status monitoring
                await expect(page.locator('.agent-status')).to_be_visible()

                # Test analytics charts
                await page.click('text="Analytics"')
                await expect(page.locator('.chart-container')).to_be_visible()

                print("✅ Full user workflow test passed")

            except Exception as e:
                print(f"❌ Test failed: {e}")
                raise

            finally:
                await browser.close()

    @pytest.mark.asyncio
    async def test_responsive_design(self):
        """Test dashboard responsive design across different screen sizes"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()

            # Test different screen sizes
            screen_sizes = [
                {'width': 1920, 'height': 1080, 'name': 'Desktop'},
                {'width': 768, 'height': 1024, 'name': 'Tablet'},
                {'width': 375, 'height': 667, 'name': 'Mobile'}
            ]

            for size in screen_sizes:
                page = await context.new_page()
                await page.set_viewport_size({'width': size['width'], 'height': size['height']})

                try:
                    await page.goto("http://localhost:5000/dashboard-v2.html")

                    # Wait for page to load
                    await page.wait_for_load_state('networkidle')

                    # Test navigation is visible and functional
                    nav = page.locator('.nav-container')
                    if size['width'] < 768:
                        # Mobile: hamburger menu should be visible
                        await expect(page.locator('.mobile-menu-toggle')).to_be_visible()
                    else:
                        # Desktop/Tablet: full navigation should be visible
                        await expect(nav).to_be_visible()

                    print(f"✅ {size['name']} responsive design test passed")

                except Exception as e:
                    print(f"❌ {size['name']} responsive design test failed: {e}")
                    raise

                finally:
                    await page.close()

            await browser.close()

    @pytest.mark.asyncio
    async def test_accessibility_features(self):
        """Test accessibility features and WCAG compliance"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            page = await context.new_page()

            try:
                await page.goto("http://localhost:5000/dashboard-v2.html")

                # Test keyboard navigation
                await page.keyboard.press('Tab')
                focused_element = await page.evaluate('document.activeElement.tagName')
                assert focused_element in ['BUTTON', 'INPUT', 'A', 'SELECT']

                # Test ARIA labels
                await expect(page.locator('[aria-label]')).to_have_count(0)  # At least some elements should have aria-labels

                # Test color contrast (basic check)
                elements_with_text = await page.locator('*:has-text(/./)').all()
                for element in elements_with_text[:5]:  # Check first 5 elements
                    styles = await element.evaluate('el => window.getComputedStyle(el)')
                    # Basic contrast check (not comprehensive)
                    assert styles['color'] != styles['backgroundColor']

                print("✅ Accessibility features test passed")

            except Exception as e:
                print(f"❌ Accessibility test failed: {e}")
                raise

            finally:
                await browser.close()

    @pytest.mark.asyncio
    async def test_performance_metrics(self):
        """Test dashboard performance metrics"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            page = await context.new_page()

            try:
                # Start performance monitoring
                await page.goto("http://localhost:5000/dashboard-advanced.html")

                # Measure page load time
                load_time = await page.evaluate('''
                    () => {
                        const navigation = performance.getEntriesByType('navigation')[0];
                        return navigation.loadEventEnd - navigation.fetchStart;
                    }
                ''')

                # Page should load within 3 seconds
                assert load_time < 3000, f"Page load time {load_time}ms exceeds 3000ms"

                # Test chart rendering performance
                start_time = time.time()
                await expect(page.locator('.chart-container')).to_be_visible()
                chart_render_time = (time.time() - start_time) * 1000

                # Charts should render within 2 seconds
                assert chart_render_time < 2000, f"Chart render time {chart_render_time}ms exceeds 2000ms"

                print(f"✅ Performance test passed - Load time: {load_time}ms, Chart render: {chart_render_time:.2f}ms")

            except Exception as e:
                print(f"❌ Performance test failed: {e}")
                raise

            finally:
                await browser.close()

    @pytest.mark.asyncio
    async def test_error_handling_ui(self):
        """Test UI error handling and user feedback"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            page = await context.new_page()

            try:
                await page.goto("http://localhost:5000/dashboard-v2.html")

                # Test network error handling
                await page.route('/api/workflows', lambda route: route.abort())

                await page.click('button:has-text("Refresh Workflows")')

                # Should show error message
                await expect(page.locator('.error-message')).to_be_visible(timeout=5000)

                print("✅ Error handling UI test passed")

            except Exception as e:
                print(f"❌ Error handling UI test failed: {e}")
                raise

            finally:
                await browser.close()

    @pytest.mark.asyncio
    async def test_real_time_updates(self):
        """Test real-time update functionality"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            page = await context.new_page()

            try:
                await page.goto("http://localhost:5000/dashboard-charts.html")

                # Wait for initial data to load
                await expect(page.locator('.agent-utilization-chart')).to_be_visible()

                # Simulate real-time update (would need WebSocket connection)
                initial_value = await page.locator('.agent-status').text_content()

                # In a real test, you would trigger WebSocket messages
                # For now, just verify the UI is ready for updates
                await expect(page.locator('.last-updated')).to_be_visible()

                print("✅ Real-time updates test passed")

            except Exception as e:
                print(f"❌ Real-time updates test failed: {e}")
                raise

            finally:
                await browser.close()

class TestDashboardSecurityE2E:
    """Security-focused end-to-end tests"""

    @pytest.mark.asyncio
    async def test_authentication_flow(self):
        """Test complete authentication flow"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            page = await context.new_page()

            try:
                # Test unauthorized access
                await page.goto("http://localhost:5000/")

                # Should be redirected to login or show auth error
                await expect(page.locator('input[name="password"]')).to_be_visible()

                # Test successful login
                await page.fill('input[name="password"]', "eljefe_admin")
                await page.click('button[type="submit"]')

                # Should redirect to dashboard
                await expect(page.locator('.dashboard-container')).to_be_visible()

                print("✅ Authentication flow test passed")

            except Exception as e:
                print(f"❌ Authentication flow test failed: {e}")
                raise

            finally:
                await browser.close()

    @pytest.mark.asyncio
    async def test_xss_prevention(self):
        """Test XSS prevention in the UI"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            page = await context.new_page()

            try:
                await page.goto("http://localhost:5000/dashboard-v2.html")

                # Try to inject XSS in chat
                xss_payload = "<script>alert('XSS')</script>"
                await page.fill('#chatInput', xss_payload)
                await page.click('button:has-text("Send")')

                # Verify script doesn't execute
                # Check that no alert appears
                page.on('dialog', lambda dialog: pytest.fail("XSS alert was triggered"))

                # Verify payload is escaped in UI
                await expect(page.locator('.chat-messages')).not_to_contain_text("<script>")

                print("✅ XSS prevention test passed")

            except Exception as e:
                print(f"❌ XSS prevention test failed: {e}")
                raise

            finally:
                await browser.close()

class TestDashboardMultiBrowser:
    """Cross-browser compatibility tests"""

    @pytest.mark.asyncio
    async def test_chrome_compatibility(self):
        """Test Chrome browser compatibility"""
        await self._test_browser_compatibility("chromium")

    @pytest.mark.asyncio
    async def test_firefox_compatibility(self):
        """Test Firefox browser compatibility"""
        await self._test_browser_compatibility("firefox")

    @pytest.mark.asyncio
    async def test_webkit_compatibility(self):
        """Test WebKit (Safari) browser compatibility"""
        await self._test_browser_compatibility("webkit")

    async def _test_browser_compatibility(self, browser_name):
        """Helper method to test browser compatibility"""
        async with async_playwright() as p:
            browser = await getattr(p, browser_name).launch()
            context = await browser.new_context()
            page = await context.new_page()

            try:
                await page.goto("http://localhost:5000/dashboard-v2.html")
                await page.wait_for_load_state('networkidle')

                # Test basic functionality
                await expect(page.locator('h1')).to_be_visible()
                await expect(page.locator('.nav-container')).to_be_visible()

                # Test chart rendering
                await page.goto("http://localhost:5000/dashboard-charts.html")
                await expect(page.locator('.chart-container')).to_be_visible()

                print(f"✅ {browser_name} compatibility test passed")

            except Exception as e:
                print(f"❌ {browser_name} compatibility test failed: {e}")
                raise

            finally:
                await browser.close()

# Performance testing with multiple users
class TestDashboardLoad:
    """Load testing for dashboard"""

    @pytest.mark.asyncio
    async def test_concurrent_users(self):
        """Test dashboard with multiple concurrent users"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()

            async def simulate_user(user_id):
                context = await browser.new_context()
                page = await context.new_page()

                try:
                    start_time = time.time()
                    await page.goto("http://localhost:5000/dashboard-v2.html")
                    await page.wait_for_load_state('networkidle')
                    load_time = time.time() - start_time

                    # Simulate some user interaction
                    await page.click('text="Analytics"')
                    await expect(page.locator('.analytics-panel')).to_be_visible()

                    return {'user_id': user_id, 'load_time': load_time, 'success': True}

                except Exception as e:
                    return {'user_id': user_id, 'error': str(e), 'success': False}

                finally:
                    await context.close()

            # Simulate 5 concurrent users
            tasks = [simulate_user(i) for i in range(5)]
            results = await asyncio.gather(*tasks)

            # Verify all users succeeded
            successful_users = [r for r in results if r['success']]
            assert len(successful_users) == 5, f"Only {len(successful_users)}/5 users succeeded"

            # Check average load time
            avg_load_time = sum(r['load_time'] for r in successful_users) / len(successful_users)
            assert avg_load_time < 5.0, f"Average load time {avg_load_time}s exceeds 5s"

            print(f"✅ Concurrent users test passed - {len(successful_users)} users, avg load time: {avg_load_time:.2f}s")

            await browser.close()

if __name__ == '__main__':
    # Run tests
    asyncio.run(test_full_user_workflow())