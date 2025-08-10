from playwright.sync_api import sync_playwright

def extract_biodata(usn, dob):
    url = "https://www.webprosindia.com/Gokaraju/Academics/StudentProfile.aspx?scrid=17"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set True to run in headless mode
        context = browser.new_context()
        page = context.new_page()

        # Go to login page
        page.goto("https://www.webprosindia.com/Gokaraju/")
        page.wait_for_timeout(2000)

        # Fill student login
        page.fill("#txtStudentID", usn)
        page.fill("#txtPassword", dob)
        page.click("#btnStudent")

        # Wait for redirect
        page.wait_for_load_state("networkidle")
        page.goto(url)
        page.wait_for_timeout(3000)

        # Scrape biodata table
        table = page.locator("table").nth(2)  # 3rd table usually has biodata
        rows = table.locator("tr")

        print("\nStudent Biodata:\n------------------")
        for i in range(rows.count()):
            cols = rows.nth(i).locator("td")
            if cols.count() >= 2:
                key = cols.nth(0).inner_text().strip().replace(":", "")
                value = cols.nth(1).inner_text().strip()
                print(f"{key}: {value}")

        browser.close()

# Example usage
usn = "25245a0538"     # Replace with your ID
dob = "03112006"    # Replace with your DOB (format: dd/mm/yyyy)
extract_biodata(usn, dob)
