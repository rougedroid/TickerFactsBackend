import json
import signal
import sys
import time
from sqlalchemy.engine.url import make_url 

import httpx
import psycopg2
from psycopg2.extras import execute_values


SEC_USER_AGENT = "Bhavan bhavan@tutamail.com"
DATABASE_URL="postgresql+asyncpg://tradingview:chartsarestupid@localhost:5432/traderview"
STATE_FILE = "company_import_state.json"
BATCH_SIZE = 100

STOP = False


def handle_signal(signum, frame):
    global STOP
    print("\nStopping gracefully...")
    STOP = True


signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)


class CompanyImporter:

    COMPANY_LIST_URL = "https://www.sec.gov/files/company_tickers.json"

    COMPANY_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

    DUMMY_ACCESSION = "COMPANY_PROFILE"

    def __init__(self):

        self.client = httpx.Client(
            headers={"User-Agent": SEC_USER_AGENT},
            timeout=60,
        )

        url = make_url(DATABASE_URL)
        self.conn = psycopg2.connect(
            host=url.host,
            port=url.port,
            dbname=url.database,
            user=url.username,
            password=url.password,
        )

        self.cursor = self.conn.cursor()

        self.state = self.load_state()

    def load_state(self):

        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except FileNotFoundError:

            return {"index": 0}

    def save_state(self):

        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f)

    def download_company_list(self):

        print("Downloading company list...")

        response = self.client.get(self.COMPANY_LIST_URL)

        response.raise_for_status()

        companies = response.json()

        return list(companies.values())

    def insert_company(self, company):

        cik = str(company["cik_str"]).zfill(10)

        self.cursor.execute(
            """
            INSERT INTO companies
            (
                id,
                ticker,
                cik,
                name
            )
            VALUES
            (
                gen_random_uuid(),
                %s,
                %s,
                %s
            )
            ON CONFLICT (cik)
            DO UPDATE SET
                ticker = EXCLUDED.ticker,
                name = EXCLUDED.name,
                updated_at = NOW()
            """,
            (
                company["ticker"],
                cik,
                company["title"],
            ),
        )

        return cik

    def insert_metric(
        self,
        cik,
        metric_name,
        category,
        value,
        unit=None,
    ):

        accession = f"{self.DUMMY_ACCESSION}:{cik}"

        if isinstance(value, bool):

            numeric = None
            text = None
            boolean = value

        elif isinstance(value, (int, float)):

            numeric = float(value)
            text = None
            boolean = None

        else:

            numeric = None
            text = str(value)
            boolean = None

        self.cursor.execute(
            """
            INSERT INTO metrics
            (
                id,
                accession_number,
                metric_name,
                metric_category,
                numeric_value,
                text_value,
                boolean_value,
                unit
            )
            VALUES
            (
                gen_random_uuid(),
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            ON CONFLICT DO NOTHING
            """,
            (
                accession,
                metric_name,
                category,
                numeric,
                text,
                boolean,
                unit,
            ),
        )

    def import_company_facts(self, cik):

        response = self.client.get(self.COMPANY_FACTS_URL.format(cik=cik))

        if response.status_code == 404:
            return

        response.raise_for_status()

        data = response.json()

        facts = data.get("facts", {})

        for taxonomy, taxonomy_data in facts.items():

            for metric_name, metric in taxonomy_data.items():

                units = metric.get("units", {})

                for unit_name, values in units.items():

                    if not values:
                        continue

                    latest = values[-1]

                    value = latest.get("val")

                    if value is None:
                        continue

                    self.insert_metric(
                        cik=cik,
                        metric_name=metric_name,
                        category=taxonomy,
                        value=value,
                        unit=unit_name,
                    )

    def run(self):

        companies = self.download_company_list()

        start = self.state["index"]

        total = len(companies)

        print(f"Starting from {start}/{total}")

        try:

            for i in range(start, total):

                if STOP:
                    break

                company = companies[i]

                cik = self.insert_company(company)

                try:

                    self.import_company_facts(cik)

                except Exception as e:

                    print(f"Failed {company['ticker']} : {e}")
                    print(company)

                self.state["index"] = i + 1

                if (i + 1) % BATCH_SIZE == 0:

                    self.conn.commit()
                    self.save_state()

                    print(f"Committed batch ending at {i+1}/{total}")

                    time.sleep(0.2)

            self.conn.commit()
            self.save_state()

        finally:

            self.conn.commit()
            self.save_state()

            self.cursor.close()
            self.conn.close()
            self.client.close()

            print("State saved.")


if __name__ == "__main__":

    CompanyImporter().run()
