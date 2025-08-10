import asyncio
import csv
import json
from playwright.async_api import async_playwright

# === Credentials ===
USERNAME = "25245a0538"
PASSWORD = "03112006"  # format: DDMMYYYY

# === URLs ===
LOGIN_URL = "https://www.webprosindia.com/Gokaraju/StudentMaster.aspx"
ATTENDANCE_URL = "https://www.webprosindia.com/Gokaraju/Academics/StudentAttendance.aspx?scrid=3&showtype=SA"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
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
            print("Could not find or select 'Till Now' radio button:", e)

        try:
            await page.click('input[id="btnShow"]')
        except Exception as e:
            print("Could not find or click 'Submit' button:", e)

        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)

        # Step 5: Get and print attendance page HTML
        attendance_html = await page.content()

        print("\n===== Attendance Page HTML Preview =====\n")
        print(attendance_html[:3000])  # Just the start for readability
        print("\n===== End Preview =====\n")

        # Save raw HTML
        with open("attendance_paage.html", "w", encoding="utf-8") as f:
            f.write(attendance_html)

        print("Saved attendance page HTML to 'attendance_page.html'")

        # Step 6: Scrape attendance table
        try:
            rows = await page.query_selector_all("table#tblAttendance tr")
            data = []
            headers = []

            for i, row in enumerate(rows):
                cols = await row.query_selector_all("th, td")
                texts = [await col.inner_text() for col in cols]

                if i == 0:
                    headers = texts
                else:
                    data.append(dict(zip(headers, texts)))

            # Save CSV
            with open("attendance_data.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data)

            # Save JSON
            with open("attendance_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            print("Attendance data saved to:")
            print(" - attendance_data.csv")
            print(" - attendance_data.json")

        except Exception as e:
            print("Failed to extract attendance table:", e)

        # Do not close browser if you want to inspect
        await page.wait_for_timeout(60000)  # Keep open for 60 seconds

# Run the async script
asyncio.run(run())
