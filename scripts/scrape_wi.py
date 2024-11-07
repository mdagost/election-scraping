import pandas as pd
from playwright.sync_api import sync_playwright


def scrape_2016(debug=False):
    all_counties = []
    all_fips = []
    all_rep_pcts = []
    all_rep_votes = []
    all_dem_pcts = []
    all_dem_votes = []

    with sync_playwright() as playwright:
        chromium = playwright.chromium
        browser = chromium.launch(headless=True)
        
        # Create a context with a realistic user agent
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        page.set_viewport_size({"width": 1920, "height": 8000})

        RESULTS_2016 = "https://www.politico.com/2016-election/results/map/president/wisconsin/"

        page.goto(RESULTS_2016)
        page.wait_for_timeout(2000)

        # Scroll to bottom of page to ensure all content is loaded
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)  # Wait for any dynamic content to load after scrolling

        counties = page.query_selector_all('article.results-group')
        if debug:
            print(f"Found {len(counties)} counties")
            
        for county in counties:
            county_name = county.get_attribute('id')
            county_fips = county.get_attribute('data-fips')

            if not county_name:
                continue

            county_name = county_name.replace('county', '')
            all_counties.append(county_name)
            all_fips.append(county_fips)
            
            if debug:
                print(f"County: {county_name}, FIPS: {county_fips}")
            
            vote_data = county.query_selector('.results-data')
            if vote_data:
                table = vote_data.query_selector('.results-table')
                if table:
                    republican_row = table.query_selector('.type-republican')
                    if republican_row:
                        rep_pct = float(republican_row.query_selector('.results-percentage').text_content().replace("%", ""))
                        rep_votes = int(republican_row.query_selector('.results-popular').text_content().replace(",", ""))
                        if rep_pct and rep_votes:
                            if debug:
                                print(f"Republican percentage: {rep_pct}")
                                print(f"Republican votes: {rep_votes}")
                            all_rep_pcts.append(rep_pct)
                            all_rep_votes.append(rep_votes)

                    democratic_row = table.query_selector('.type-democrat')
                    if democratic_row:
                        dem_pct = float(democratic_row.query_selector('.results-percentage').text_content().replace("%", ""))
                        dem_votes = int(democratic_row.query_selector('.results-popular').text_content().replace(",", ""))
                        if dem_pct and dem_votes:
                            if debug:
                                print(f"Democratic percentage: {dem_pct}")
                                print(f"Democratic votes: {dem_votes}")
                            all_dem_pcts.append(dem_pct)
                            all_dem_votes.append(dem_votes)

        data = pd.DataFrame({
            'county': all_counties,
            'fips': all_fips,
            'rep_pct': all_rep_pcts,
            'rep_votes': all_rep_votes,
            'dem_pct': all_dem_pcts,
            'dem_votes': all_dem_votes
        })

        return data


def scrape_2020(debug=False):
    all_counties = []
    all_rep_pcts = []
    all_rep_votes = []
    all_dem_pcts = []
    all_dem_votes = []

    with sync_playwright() as playwright:
        chromium = playwright.chromium
        browser = chromium.launch(headless=False)
        
        # Create a context with a realistic user agent
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        page.set_viewport_size({"width": 1920, "height": 8000})

        RESULTS_2020 = "https://www.politico.com/2020-election/results/wisconsin/"

        page.goto(RESULTS_2020, timeout=120000)

        # Scroll to bottom of page to ensure all content is loaded
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)  # Wait for any dynamic content to load after scrolling

        # Click the "See all 72 counties" button to expand all counties
        show_all_button = page.get_by_text("See all 72 counties")
        show_all_button.click()
        
        # Wait a moment for counties to load after expanding
        page.wait_for_timeout(1000)

        county_rows = page.query_selector_all('.county-row')
        
        if debug:
            print(f"Found {len(county_rows)} county rows")

        for row in county_rows:
            # Extract county name
            county_name_cell = row.query_selector('.county-name')
            county_name = county_name_cell.inner_text().strip().replace(" County", "") if county_name_cell else None
            all_counties.append(county_name)
            
            # Extract Democratic votes and percentage
            dem_votes_cell = row.query_selector('.votes-cell.dem')
            dem_votes = int(dem_votes_cell.inner_text().strip().replace(",", "")) if dem_votes_cell else None
            all_dem_votes.append(dem_votes)

            dem_pct_cell = row.query_selector('.percent-cell')
            dem_pct = float(dem_pct_cell.inner_text().strip().replace("%", "")) if dem_pct_cell else None
            all_dem_pcts.append(dem_pct)
            # Extract Republican votes and percentage
            rep_votes_cell = row.query_selector('.votes-cell.gop')
            rep_votes = int(rep_votes_cell.inner_text().strip().replace(",", "")) if rep_votes_cell else None
            all_rep_votes.append(rep_votes)
            rep_pct_cell = row.query_selector_all('.percent-cell')[1]
            rep_pct = float(rep_pct_cell.inner_text().strip().replace("%", "")) if rep_pct_cell else None
            all_rep_pcts.append(rep_pct)

            if debug:
                print(f"County: {county_name}, Dem Votes: {dem_votes}, Dem %: {dem_pct}, Rep Votes: {rep_votes}, Rep %: {rep_pct}")

        data = pd.DataFrame({
            'county': all_counties,
            'rep_pct': all_rep_pcts,
            'rep_votes': all_rep_votes,
            'dem_pct': all_dem_pcts,
            'dem_votes': all_dem_votes
        })

        return data


def scrape_2024(debug=False):
    all_counties = []
    all_vote_in = []
    all_rep_pcts = []
    all_rep_votes = []
    all_dem_pcts = []
    all_dem_votes = []

    with sync_playwright() as playwright:
        chromium = playwright.chromium
        browser = chromium.launch(headless=False)
        
        # Create a context with a realistic user agent
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()

        RESULTS_2024 = "https://www.jsonline.com/elections/results/2024-11-05/race/0/wisconsin"

        page.goto(RESULTS_2024, timeout=30000)

        # Scroll to bottom of page to ensure all content is loaded
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)  # Wait for any dynamic content to load after scrolling

        # Find all county headers
        county_headers = page.query_selector_all('h3:has-text("County")')
        
        if debug:
            print(f"Found {len(county_headers)} county headers")
            
        for header in county_headers:
            county_name = header.inner_text().strip().replace(" County", "")
            all_counties.append(county_name)

            # Find the "Est. Vote In" span for this county
            vote_in_span = header.evaluate('''node => {
                const nextElement = node.nextElementSibling;
                const spans = nextElement.querySelectorAll("span");
                for (const span of spans) {
                    if (span.textContent.includes("Est. Vote In")) {
                        return span.textContent;
                    }
                }
                return null;
            }''')
            
            if debug:
                print(f"County: {county_name}")

            if vote_in_span:
                vote_in_text = vote_in_span.strip()
                vote_in_text = float(vote_in_text.replace("% Est. Vote In", ""))
                if debug:
                    print(f"Est. Vote In: {vote_in_text}")
                all_vote_in.append(vote_in_text)

            # Find the table associated with this county
            table = header.evaluate('''node => {
                const grandParentElement = node.parentElement.parentElement;
                const table = grandParentElement.querySelector('table');
                const rows = table.querySelectorAll('tr');
                const data = [];
                // Get first two rows (skip header row if it exists)
                for (let i = 0; i < Math.min(3, rows.length); i++) {
                    const cells = rows[i].querySelectorAll('td');
                    const rowData = [];
                    cells.forEach(cell => rowData.push(cell.textContent.trim()));
                    data.push(rowData);
                }
                return data;
            }''')
            
            for row in table:
                if len(row) == 0:
                    continue
                
                if row[0] == "Donald Trump (R)Trump (R)":
                    rep_pct = float(row[3].replace("%", ""))
                    rep_votes = int(row[2].replace(",", ""))
                elif row[0] == "Kamala Harris (D)Harris (D)":
                    dem_pct = float(row[3].replace("%", ""))
                    dem_votes = int(row[2].replace(",", ""))

            all_rep_pcts.append(rep_pct)
            all_rep_votes.append(rep_votes)
            all_dem_pcts.append(dem_pct)
            all_dem_votes.append(dem_votes)

            if debug:
                print(f"Rep %: {rep_pct}, Rep Votes: {rep_votes}, Dem %: {dem_pct}, Dem Votes: {dem_votes}")

        data = pd.DataFrame({   
            'county': all_counties,
            'vote_in': all_vote_in,
            'rep_pct': all_rep_pcts,
            'rep_votes': all_rep_votes,
            'dem_pct': all_dem_pcts,
            'dem_votes': all_dem_votes
        })

        return data


if __name__ == "__main__":
    data_2016 = scrape_2016(debug=False)
    data_2020 = scrape_2020(debug=False)
    data_2024 = scrape_2024(debug=False)

    # standardize these two county names
    counties_with_spaces = ["Fond du Lac", "Eau Claire", "Green Lake", "St. Croix", "La Crosse"]
    for county in counties_with_spaces:
        data_2016["county"] = data_2016.county.str.replace(county.replace(" ", ""), county)
        data_2020["county"] = data_2020.county.str.replace(county.replace(" ", ""), county)
        data_2024["county"] = data_2024.county.str.replace(county.replace(" ", ""), county)

    data_2016 = data_2016.rename(columns={
        "rep_pct": "rep_pct_2016",
        "rep_votes": "rep_votes_2016",
        "dem_pct": "dem_pct_2016",
        "dem_votes": "dem_votes_2016"
    })

    data_2020 = data_2020.rename(columns={
        "rep_pct": "rep_pct_2020",
        "rep_votes": "rep_votes_2020",
        "dem_pct": "dem_pct_2020",
        "dem_votes": "dem_votes_2020"
    })

    data_2024 = data_2024.rename(columns={
        "rep_pct": "rep_pct_2024",
        "rep_votes": "rep_votes_2024",
        "dem_pct": "dem_pct_2024",
        "dem_votes": "dem_votes_2024"
    })

    data = data_2016.merge(data_2020, on="county").merge(data_2024, on="county")

    data_2016.to_csv("./data/data_2016.csv", index=False)
    data_2020.to_csv("./data/data_2020.csv", index=False)
    data_2024.to_csv("./data/data_2024.csv", index=False)
    data.to_csv("./data/consolidated_data.csv", index=False)