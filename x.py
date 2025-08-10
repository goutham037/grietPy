import json
import csv
from playwright.sync_api import sync_playwright

USERNAME = "25245a0538"
PASSWORD = "03112006"
PROFILE_URL = "https://www.webprosindia.com/Gokaraju/Academics/StudentProfile.aspx?scrid=17"

def scrape_bio_data(username, password):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_context().new_page()

        # 1) Login
        page.goto("https://www.webprosindia.com/Gokaraju")
        page.fill("#txtId2", username)
        page.fill("#txtPwd2", password)
        page.click("#imgBtn2")
        page.wait_for_timeout(3000)

        # 2) Navigate & expand BIO-DATA
        page.goto(PROFILE_URL)
        page.wait_for_timeout(2000)
        page.click("text=BIO-DATA")
        page.wait_for_selector("#divProfile_BioData", state="visible")

        # 3) SCRAPE PERSONAL BIO (the first top‐level <table>)
        bio = {}
        table0 = page.locator("#divProfile_BioData > table").first
        for row in table0.locator("tr").all():
            cells = row.locator("td")
            if cells.count() == 2:
                k = cells.nth(0).inner_text().strip().rstrip(":")
                v = cells.nth(1).inner_text().strip()
                if k and v:
                    bio[k] = v
            elif cells.count() >= 6:
                k1, v1 = cells.nth(0).inner_text().strip().rstrip(":"), cells.nth(2).inner_text().strip()
                k2, v2 = cells.nth(3).inner_text().strip().rstrip(":"), cells.nth(5).inner_text().strip()
                if k1 and v1: bio[k1] = v1
                if k2 and v2: bio[k2] = v2

        # 4) SCRAPE EDUCATION (find the “Education Details” heading, then the very next <tr>’s inner <table>)
        edu = {}
        heading_td = page.locator("#divProfile_BioData td.reportHeading2WithBackground", has_text="Education Details")
        # move to the next sibling <tr>, then find its inner <table>
        inner_table = heading_td.locator("xpath=ancestor::tr/following-sibling::tr[1]//table")
        rows = inner_table.locator("tr").all()

        # skip header row at index 0
        for row in rows[1:]:
            cells = row.locator("td")
            if cells.count() < 7:
                continue
            qual = cells.nth(0).inner_text().strip()
            if not qual:
                continue
            board = cells.nth(1).inner_text().strip()
            htno  = cells.nth(2).inner_text().strip()
            year  = cells.nth(3).inner_text().strip()
            inst  = cells.nth(4).inner_text().strip()
            mx    = cells.nth(5).inner_text().strip()
            obt   = cells.nth(6).inner_text().strip()
            gl    = cells.nth(7).inner_text().strip() if cells.count() > 7 else ""
            gp    = cells.nth(8).inner_text().strip() if cells.count() > 8 else ""

            # only keep real rows (not the all‐empty “Inter” placeholder)
            if any([board, htno, year, inst, mx, obt, gl, gp]):
                edu[qual] = {
                    "Board":        board,
                    "HallTicketNo": htno,
                    "YearOfPass":   year,
                    "Institute":    inst,
                    "MaxMarks":     mx,
                    "Obtained":     obt,
                    "GradeLetter":  gl,
                    "GradePoints":  gp
                }

        browser.close()

        # 5) EXPORT JSON & CSV
        full = {"BioData": bio, "Education": edu}
        with open("student_bio_data.json", "w", encoding="utf-8") as jf:
            json.dump(full, jf, indent=4, ensure_ascii=False)

        with open("student_bio_data.csv", "w", newline="", encoding="utf-8") as cf:
            writer = csv.writer(cf)
            writer.writerow(["Section","Field","Value"])
            for k,v in bio.items():
                writer.writerow(["BioData", k, v])
            for qual, details in edu.items():
                for fld, val in details.items():
                    writer.writerow([qual, fld, val])

        print(" Clean JSON & CSV exported")

if __name__ == "__main__":
    scrape_bio_data(USERNAME, PASSWORD)
