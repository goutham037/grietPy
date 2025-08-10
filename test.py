import asyncio
from playwright.async_api import async_playwright

# === Credentials ===
USERNAME = "25245a0538"
PASSWORD = "03112006"  # format: DDMMYYYY

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set True to hide browser
        page = await browser.new_page()
        
        # Open the portal
        await page.goto("https://www.webprosindia.com/Gokaraju/StudentMaster.aspx", timeout=60000)

        # Fill in login fields
        await page.fill("#txtId2", USERNAME)
        await page.fill("#txtPwd2", PASSWORD)

        # Click the login button (image)
        await page.click("#imgBtn2")
        await page.wait_for_timeout(3000)

        # Get full page HTML
        html_content = await page.content()

        # Check login success
        if "logout" in html_content.lower() or "student profile" in html_content.lower():
            print("✅ Login successful! Saving HTML...")

            # Save to file
            with open("login_success.html", "w", encoding="utf-8") as f:
                f.write(html_content)

            print("📄 Saved HTML to 'login_success.html'")
            print("\n===== HTML Preview Start =====\n")
            print(html_content[:3000])  # Print first 3000 characters
            print("\n===== HTML Preview End =====")

        else:
            print("❌ Login failed or could not verify. HTML below:")
            print(html_content)

        await browser.close()

# Run the async script
asyncio.run(run())
