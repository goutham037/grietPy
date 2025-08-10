import asyncio
import json
from playwright.async_api import async_playwright

USERNAME = "25245a0538"
PASSWORD = "03112006"
HEADLESS = False

async def extract_timetable(page):
    print("\nExtracting Timetable...")

    tables = await page.query_selector_all("#tblReport table")
    timetable = []

    for table in tables:
        # grab header row text
        header_cells = await table.query_selector_all("tr:first-child td, tr:first-child th")
        headers = [await cell.inner_text() for cell in header_cells]

        # look for a timetable table by checking for “Day” or “Period” in headers
        if any(h.lower().startswith("day") or "period" in h.lower() for h in headers):
            rows = await table.query_selector_all("tr")
            # normalize our own headers
            std_headers = ["Day","Period 1","Period 2","Period 3","Break","Period 4","Period 5","Period 6","Period 7"]

            for row in rows[1:]:
                cells = await row.query_selector_all("td")
                values = [ (await cell.inner_text()).strip().replace("\xa0","") for cell in cells ]
                # skip invalid
                if len(values) != len(std_headers):
                    continue
                timetable.append(dict(zip(std_headers, values)))
            break

    if timetable:
        with open("timetable.json","w",encoding="utf-8") as f:
            json.dump(timetable, f, indent=2, ensure_ascii=False)
        print(" Saved timetable to 'timetable.json'")
    else:
        print(" No valid timetable found.")
    return timetable

async def extract_faculty_allocation(page):
    print("\n Extracting Faculty Allocation...")

    tables = await page.query_selector_all("#tblReport table")
    faculty = []

    for table in tables:
        header_cells = await table.query_selector_all("tr:first-child td, tr:first-child th")
        headers = [await cell.inner_text() for cell in header_cells]

        # look for the allocation table by matching “Subject Code” or “Name of Faculty”
        if any("subject code" in h.lower() or "faculty" in h.lower() for h in headers):
            rows = await table.query_selector_all("tr")
            for row in rows[1:]:
                cells = await row.query_selector_all("td")
                values = [ (await cell.inner_text()).strip().replace("\xa0","") for cell in cells ]
                if len(values) >= 3:
                    faculty.append({
                        "Subject Code": values[0],
                        "Subject":       values[1],
                        "Faculty Name":  values[2],
                        "Initials":      values[3] if len(values)>3 else ""
                    })
            break

    if faculty:
        with open("faculty_allocation.json","w",encoding="utf-8") as f:
            json.dump(faculty, f, indent=2, ensure_ascii=False)
        print(" Saved faculty allocation to 'faculty_allocation.json'")
    else:
        print(" No valid faculty allocation found.")
    return faculty

async def extract_academic_calendar(page):
    print("\nExtracting academic calendar...")

    # Locate the calendar table
    container = await page.query_selector("#ctl00_CapPlaceHolder_divstudent table.reportTable")
    if not container:
        print("Academic calendar table not found")
        return []

    rows = await container.query_selector_all("tr")
    calendar = []

    # The first row is the header
    header_cells = await rows[0].query_selector_all("td, th")
    headers = [await cell.inner_text() for cell in header_cells]

    # Process data rows
    for row in rows[1:]:
        cells = await row.query_selector_all("td")
        values = [ (await cell.inner_text()).strip() for cell in cells ]
        if len(values) == len(headers):
            entry = dict(zip(headers, values))
            calendar.append(entry)

    # Save to file
    with open("academic_calendar.json", "w", encoding="utf-8") as f:
        json.dump(calendar, f, indent=2, ensure_ascii=False)

    print("Saved academic calendar to 'academic_calendar.json'")
    return calendar


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        page = await browser.new_page()

        print(" Logging in...")
        await page.goto("https://www.webprosindia.com/Gokaraju/StudentMaster.aspx", timeout=60000)
        await page.fill("#txtId2", USERNAME)
        await page.fill("#txtPwd2", PASSWORD)
        await page.click("#imgBtn2")
        await page.wait_for_timeout(3000)

        print(" Navigating to TimeTableReport page...")
        await page.goto("https://www.webprosindia.com/gokaraju/Academics/TimeTableReport.aspx?scrid=18", timeout=60000)
        await page.wait_for_selector("#tblReport")
         
        await extract_timetable(page)
        await extract_faculty_allocation(page)
        await page.goto("https://www.webprosindia.com/gokaraju/Academics/AcademicCalenderReport.aspx?scrid=1", timeout=60000)
        await extract_academic_calendar(page)

        await browser.close()
        print("Done.")
#document (https://www.webprosindia.com/gokaraju/Academics/AcademicCalenderReport.aspx?scrid=1)
if __name__ == "__main__":
    asyncio.run(run())
