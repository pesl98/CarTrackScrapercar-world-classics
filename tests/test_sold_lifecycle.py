"""Unit tests for sold-marking, re-list reactivation, and incomplete-scrape safety."""

import os
import tempfile
import unittest
from unittest.mock import patch

from database import Database, INCOMPLETE_SCRAPE_RATIO, SOLD_GRACE_DAYS
from multi_dealer_scraper import BaseDealerScraper, MultiDealerScraper


DEALER = "CarWorldClassics"


def _car_payload(autotrack_id, price=25000, make="Porsche", model="911"):
    return {
        "autotrack_id": autotrack_id,
        "dealer_name": DEALER,
        "make": make,
        "model": model,
        "year": 1989,
        "mileage": 80000,
        "fuel_type": "Petrol",
        "description": f"{make} {model}",
        "image_url": "",
        "source_url": "",
        "price": price,
    }


class StubDealerScraper(BaseDealerScraper):
    """Returns canned listings without hitting the network."""

    def __init__(self, listings):
        super().__init__(DEALER, "https://example.com")
        self.listings = listings

    def get_inventory_url(self, page=1):
        if page == 1:
            return "https://example.com/aanbod"
        return f"https://example.com/aanbod?page={page}"

    def find_car_elements(self, soup):
        return []

    def extract_car_data(self, element):
        return None

    def scrape_page(self, url):
        if "page=" in url:
            return []
        return list(self.listings)


class SoldLifecycleTestCase(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.db = Database(self.db_path)
        self.db.init_db()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def _add_car(self, autotrack_id, price=25000):
        return self.db.add_car(_car_payload(autotrack_id, price=price))

    def _age_last_seen(self, car_id, days):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE cars SET last_seen = datetime('now', ?) WHERE id = ?",
            (f"-{days} days", car_id),
        )
        conn.commit()
        conn.close()

    def _mark_sold(self, car_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE cars
            SET is_sold = TRUE, sold_date = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (car_id,),
        )
        conn.commit()
        conn.close()

    def test_disappeared_past_grace_is_marked_sold(self):
        kept_id = self._add_car("kept-1")
        gone_id = self._add_car("gone-1")
        self._age_last_seen(kept_id, SOLD_GRACE_DAYS + 1)
        self._age_last_seen(gone_id, SOLD_GRACE_DAYS + 1)

        self.db.mark_cars_as_sold(["kept-1"], DEALER)

        kept = self.db.get_car_by_id(kept_id)
        gone = self.db.get_car_by_id(gone_id)
        self.assertFalse(kept["is_sold"])
        self.assertTrue(gone["is_sold"])
        self.assertIsNotNone(gone["sold_date"])

    def test_disappeared_within_grace_stays_active(self):
        gone_id = self._add_car("gone-recent")
        self._age_last_seen(gone_id, 1)

        self.db.mark_cars_as_sold(["someone-else"], DEALER)

        gone = self.db.get_car_by_id(gone_id)
        self.assertFalse(gone["is_sold"])
        self.assertIsNone(gone["sold_date"])

    def test_sold_car_reappears_becomes_active(self):
        car_id = self._add_car("relist-1")
        self._mark_sold(car_id)

        sold = self.db.get_car_by_id(car_id)
        self.assertTrue(sold["is_sold"])
        self.assertIsNotNone(sold["sold_date"])

        reactivated = self.db.touch_car_seen(car_id)
        self.assertTrue(reactivated)

        live = self.db.get_car_by_id(car_id)
        self.assertFalse(live["is_sold"])
        self.assertIsNone(live["sold_date"])
        self.assertIsNotNone(live["last_seen"])

    def test_incomplete_scrape_does_not_mass_mark_sold(self):
        ids = []
        for i in range(10):
            car_id = self._add_car(f"fleet-{i}")
            self._age_last_seen(car_id, SOLD_GRACE_DAYS + 1)
            ids.append(car_id)

        # 2 of 10 listings is 20%, well under the 70% coverage threshold
        self.assertTrue(self.db.should_skip_sold_marking(2, DEALER))

        scraper = MultiDealerScraper(self.db)
        stub = StubDealerScraper([_car_payload("fleet-0"), _car_payload("fleet-1")])
        scraper.scrape_dealer(stub)

        for car_id in ids:
            car = self.db.get_car_by_id(car_id)
            self.assertFalse(car["is_sold"], f"car {car_id} should stay active")

    def test_zero_listings_skips_sold_marking(self):
        car_id = self._add_car("only-one")
        self._age_last_seen(car_id, SOLD_GRACE_DAYS + 1)

        self.assertTrue(self.db.should_skip_sold_marking(0, DEALER))
        self.assertGreater(INCOMPLETE_SCRAPE_RATIO, 0)

        scraper = MultiDealerScraper(self.db)
        stub = StubDealerScraper([])
        with patch.object(stub, "scrape_page", return_value=[]):
            scraper.scrape_dealer(stub)

        car = self.db.get_car_by_id(car_id)
        self.assertFalse(car["is_sold"])

    def test_scrape_reactivates_sold_car_when_seen_again(self):
        car_id = self._add_car("seen-again", price=40000)
        self._mark_sold(car_id)

        scraper = MultiDealerScraper(self.db)
        listings = [_car_payload("seen-again", price=40000)]
        stub = StubDealerScraper(listings)
        scraper.scrape_dealer(stub)

        live = self.db.get_car_by_id(car_id)
        self.assertFalse(live["is_sold"])
        self.assertIsNone(live["sold_date"])


if __name__ == "__main__":
    unittest.main()
