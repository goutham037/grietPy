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

        # Step 1: Login
        await page.goto(LOGIN_URL, timeout=60000)
        await page.fill("#txtId2", USERNAME)
        await page.fill("#txtPwd2", PASSWORD)
        await page.click("#imgBtn2")
        await page.wait_for_timeout(3000)

        # Step 2: Navigate to attendance page
        await page.goto(ATTENDANCE_URL)
        await page.wait_for_load_state("networkidle")

        try:
            await page.check('input[id="radTillNow"]')
            await page.click('input[id="btnShow"]')
        except Exception as e:
            print("Error selecting 'Till Now' or clicking Show:", e)

        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)

        # Step 3: Extract attendance table using known class
        try:
            # Locate the specific table with attendance using its unique class
            rows = await page.query_selector_all('table.cellBorder tr')
            data = []
            headers = ["Sl.No.", "Subject", "Held", "Attend", "%"]

            for row in rows:
                cols = await row.query_selector_all("td")
                if len(cols) == 5:  # Attendance rows have exactly 5 columns
                    values = [await col.inner_text() for col in cols]
                    data.append(dict(zip(headers, values)))

            # Filter out any non-data rows like TOTAL etc.
            data = [row for row in data if row["Sl.No."].isdigit()]

            # Save to CSV
            with open("attendance_data.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data)

            # Save to JSON
            with open("attendance_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            print("Attendance saved to:")
            print(" - attendance_data.csv")
            print(" - attendance_data.json")

        except Exception as e:
            print("Failed to extract attendance table:", e)

        # Optional: keep browser open to view
        await page.wait_for_timeout(60000)

asyncio.run(run())
