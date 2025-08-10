import asyncio
from playwright.async_api import async_playwright

# === Credentials ===
USERNAME = "25245a0538"
PASSWORD = "03112006"  # format: DDMMYYYY

# === URLs ===
LOGIN_URL = "https://www.webprosindia.com/Gokaraju/StudentMaster.aspx"
ATTENDANCE_URL = "https://www.webprosindia.com/Gokaraju/Academics/StudentAttendance.aspx?scrid=3&showtype=SA"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set True to hide browser
        page = await browser.new_page()

        # Step 1: Open login page
        await page.goto(LOGIN_URL, timeout=60000)

        # Step 2: Fill in credentials and submit
        await page.fill("#txtId2", USERNAME)
        await page.fill("#txtPwd2", PASSWORD)
        await page.click("#imgBtn2")
        await page.wait_for_timeout(3000)

        # Step 3: Go to attendance page
        await page.goto(ATTENDANCE_URL)
        await page.wait_for_load_state("networkidle")

        # Step 4: Select "Till Now" radio button and submit
        try:
            await page.check('input[id="radTillNow"]')
        except Exception as e:
            print(" Could not find or select 'Till Now' radio button:", e)

        try:
            await page.click('input[id="btnShow"]')
        except Exception as e:
            print(" Could not find or click 'Submit' button:", e)

        await page.wait_for_load_state("networkidle")

        # Step 5: Get and print attendance page HTML
        attendance_html = await page.content()

        print("\n===== Attendance Page HTML Preview =====\n")
        print(attendance_html[:3000])  # Just the start for readability
        print("\n===== End Preview =====\n")

        # Step 6: Save to file
        with open("attendance_paghe.html", "w", encoding="utf-8") as f:
            f.write(attendance_html)

        print(" Saved attendance page HTML to 'attendance_page.html'")

        

# Run the async script
asyncio.run(run())
