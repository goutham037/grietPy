import json
import csv
from pathlib import Path
from playwright.async_api import async_playwright

# ─── Configuration ─────────────────────────────────────────────────────────────

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LOGIN_URL      = "https://www.webprosindia.com/Gokaraju/StudentMaster.aspx"
ATTENDANCE_URL = "https://www.webprosindia.com/Gokaraju/Academics/StudentAttendance.aspx?scrid=3&showtype=SA"
LIBRARY_URL    = "https://www.webprosindia.com/gokaraju/Library/studentsbooks.aspx?scrid=14"
PROFILE_URL    = "https://www.webprosindia.com/Gokaraju/Academics/StudentProfile.aspx?scrid=17"

# ─── Shared Login Helper ────────────────────────────────────────────────────────

async def login_and_get_page(playwright, username: str, password: str):
    browser = await playwright.chromium.launch(headless=True)
    page    = await browser.new_page()
    await page.goto(LOGIN_URL)
    await page.fill("#txtId2", username)
    await page.fill("#txtPwd2", password)
    await page.click("#imgBtn2")
    await page.wait_for_timeout(3000)
    return browser, page

# ─── Attendance Scraper ─────────────────────────────────────────────────────────

async def fetch_attendance(username: str, password: str):
    async with async_playwright() as pw:
        browser, page = await login_and_get_page(pw, username, password)
        await page.goto(ATTENDANCE_URL)
        await page.wait_for_load_state("networkidle")

        # click “Till Now” if available
        try:
            await page.check('input[id="radTillNow"]')
            await page.click('input[id="btnShow"]')
        except:
            pass
        await page.wait_for_timeout(2000)

        rows   = await page.query_selector_all('table.cellBorder tr')
        headers= ["Sl.No.", "Subject", "Held", "Attend", "%"]
        data   = []
        for row in rows:
            cols = await row.query_selector_all("td")
            if len(cols) == 5:
                vals = [await c.inner_text() for c in cols]
                if vals[0].isdigit():
                    data.append(dict(zip(headers, vals)))

        await browser.close()

        # save
        with open(OUTPUT_DIR / "attendance_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        with open(OUTPUT_DIR / "attendance_data.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

        return data

# ─── Library Scraper ────────────────────────────────────────────────────────────

async def fetch_library_books(username: str, password: str):
    async with async_playwright() as pw:
        browser, page = await login_and_get_page(pw, username, password)
        await page.goto(LIBRARY_URL)
        await page.wait_for_timeout(2000)

        rows   = await page.query_selector_all("table#tblbooks tr")
        headers= ["Sl.No", "Acc.No", "Title", "Author", "Issue Date", "Due Date", "Fine Days", "Fine Amount"]
        data   = []
        for row in rows:
            cols = await row.query_selector_all("td")
            if len(cols) == 8:
                vals = [await c.inner_text() for c in cols]
                if vals[0].isdigit():
                    data.append(dict(zip(headers, vals)))

        await browser.close()

        # save
        with open(OUTPUT_DIR / "library_books.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        with open(OUTPUT_DIR / "library_books.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

        return data

# ─── Bio-Data & Education Scraper ───────────────────────────────────────────────

async def fetch_bio_data(username: str, password: str):
    async with async_playwright() as pw:
        browser, page = await login_and_get_page(pw, username, password)

        # navigate & expand
        await page.goto(PROFILE_URL)
        await page.wait_for_timeout(2000)
        await page.click("text=BIO-DATA")
        await page.wait_for_selector("#divProfile_BioData", state="visible")

        # parse personal bio (table 0)
        tables = page.locator("#divProfile_BioData > table")
        bio    = {}
        rows0  = tables.nth(0).locator("tr")
        for i in range(await rows0.count()):
            cells = rows0.nth(i).locator("td")
            cnt   = await cells.count()
            if cnt == 2:
                k = (await cells.nth(0).inner_text()).strip().rstrip(":")
                v = (await cells.nth(1).inner_text()).strip()
                if k and v:
                    bio[k] = v
            elif cnt >= 6:
                k1 = (await cells.nth(0).inner_text()).strip().rstrip(":")
                v1 = (await cells.nth(2).inner_text()).strip()
                k2 = (await cells.nth(3).inner_text()).strip().rstrip(":")
                v2 = (await cells.nth(5).inner_text()).strip()
                if k1 and v1: bio[k1] = v1
                if k2 and v2: bio[k2] = v2

        # parse education details (nested table in table 1)
        inner = tables.nth(1).locator("table")
        rows1 = inner.locator("tr")
        edu   = {
            "School (SSC)": {"Board":"", "HallTicketNo":"", "YearOfPass":"", "Institute":"", "MaxMarks":"", "Obtained":"", "GradeLetter":"", "GradePoints":""},
            "Intermediate": {"Board":"", "HallTicketNo":"", "YearOfPass":"", "Institute":"", "MaxMarks":"", "Obtained":"", "GradeLetter":"", "GradePoints":""},
            "Diploma":      {"Board":"", "HallTicketNo":"", "YearOfPass":"", "Institute":"", "MaxMarks":"", "Obtained":"", "GradeLetter":"", "GradePoints":""},
        }
        for i in range(1, await rows1.count()):
            cells = rows1.nth(i).locator("td")
            if await cells.count() < 7:
                continue
            qual = (await cells.nth(0).inner_text()).strip().lower()
            if not qual:
                continue

            # map to key
            key = None
            if qual in ("ssc", "s.s.c"):        key = "School (SSC)"
            elif qual in ("inter", "intermediate"): key = "Intermediate"
            elif qual == "diploma":             key = "Diploma"
            if not key:
                continue

            # read values
            B  = (await cells.nth(1).inner_text()).strip()
            H  = (await cells.nth(2).inner_text()).strip()
            Y  = (await cells.nth(3).inner_text()).strip()
            I  = (await cells.nth(4).inner_text()).strip()
            Mx = (await cells.nth(5).inner_text()).strip()
            Ob = (await cells.nth(6).inner_text()).strip()
            GL = (await cells.nth(7).inner_text()).strip() if await cells.count()>7 else ""
            GP = (await cells.nth(8).inner_text()).strip() if await cells.count()>8 else ""

            # update if any real data
            if any([B,H,Y,I,Mx,Ob,GL,GP]):
                edu[key] = {
                    "Board":        B,
                    "HallTicketNo": H,
                    "YearOfPass":   Y,
                    "Institute":    I,
                    "MaxMarks":     Mx,
                    "Obtained":     Ob,
                    "GradeLetter":  GL,
                    "GradePoints":  GP
                }

        await browser.close()

        # save outputs
        result = {"BioData": bio, "Education": edu}
        with open(OUTPUT_DIR / "bio_data.json", "w", encoding="utf-8") as jf:
            json.dump(result, jf, indent=4, ensure_ascii=False)
        with open(OUTPUT_DIR / "bio_data.csv", "w", newline="", encoding="utf-8") as cf:
            writer = csv.writer(cf)
            writer.writerow(["Section","Subsection","Field","Value"])
            for f, v in bio.items():
                writer.writerow(["BioData","",f,v])
            for sec, details in edu.items():
                for fld, val in details.items():
                    writer.writerow(["Education", sec, fld, val])

        return result
