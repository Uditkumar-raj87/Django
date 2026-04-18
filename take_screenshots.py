import asyncio
from playwright.async_api import async_playwright
import time

async def take_screenshots():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # 1. Take screenshot of admin site
            print("Taking screenshot of admin site...")
            await page.goto("http://localhost:8000/admin/")
            
            # Login
            await page.fill('input[name="username"]', 'admin')
            await page.fill('input[name="password"]', 'admin123')
            await page.click('input[type="submit"]')
            
            # Wait for navigation
            await page.wait_for_url("http://localhost:8000/admin/")
            await page.wait_for_timeout(1000)
            
            # Take screenshot of admin site
            await page.screenshot(path="/workspaces/Django/03-admin-site.png", full_page=True)
            print("✓ Admin site screenshot saved: 03-admin-site.png")
            
            # 2. Go to course details page
            print("\nAccessing course details page...")
            await page.goto("http://localhost:8000/course/1/", wait_until="networkidle")
            await page.wait_for_timeout(1000)
            
            # Take screenshot of course details
            await page.screenshot(path="/workspaces/Django/course-details.png", full_page=True)
            print("✓ Course details screenshot saved: course-details.png")
            
            # 3. Submit exam with correct answers
            print("\nSubmitting exam...")
            # Select all correct answers
            await page.click('input[value="2"]')  # Question 1 - correct choice
            await page.wait_for_timeout(500)
            await page.click('input[value="6"]')  # Question 2 - correct choice (List)
            await page.wait_for_timeout(500)
            await page.click('input[value="9"]')  # Question 3 - correct choice (8)
            await page.wait_for_timeout(500)
            
            # Submit the form
            await page.click('button[type="submit"]')
            
            # Wait for results page
            await page.wait_for_url("http://localhost:8000/result/**", timeout=10000)
            await page.wait_for_timeout(2000)
            
            # Take screenshot of exam results
            await page.screenshot(path="/workspaces/Django/07-final.png", full_page=True)
            print("✓ Exam results screenshot saved: 07-final.png")
            
            print("\n✅ All screenshots captured successfully!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

# Run the async function
asyncio.run(take_screenshots())
