import os, tempfile, unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

monica = SourceFileLoader("monica", str(Path(__file__).parent / "monica")).load_module()

class ConfigTest(unittest.TestCase):
    def test_env_file_parsing_and_env_override(self):
        with tempfile.NamedTemporaryFile("w", suffix=".env", delete=False) as f:
            f.write("# comment\nMONICA_API_URL=https://file.example/api\nMONICA_API_TOKEN=filetoken\n")
            path = f.name
        old = dict(os.environ)
        try:
            os.environ.pop("MONICA_API_URL", None)
            os.environ["MONICA_API_TOKEN"] = "envtoken"
            cfg = monica.load_config(Path(path))
            self.assertEqual(cfg["MONICA_API_URL"], "https://file.example/api")  # from file
            self.assertEqual(cfg["MONICA_API_TOKEN"], "envtoken")                # env wins
        finally:
            os.environ.clear(); os.environ.update(old); os.unlink(path)

class PayloadTest(unittest.TestCase):
    def test_expand_birthdate_shorthand(self):
        p = monica.expand_birthdate({"first_name": "A", "birthdate": "1980-03-15"})
        self.assertNotIn("birthdate", p)
        self.assertEqual(
            (p["is_birthdate_known"], p["birthdate_day"], p["birthdate_month"], p["birthdate_year"]),
            (True, 15, 3, 1980))

    def test_contact_to_update_payload_round_trip(self):
        contact = {  # shape of GET /contacts/{id} data (ContactResource)
            "id": 7, "first_name": "Ann", "last_name": "Lee", "nickname": None,
            "gender_type": None, "description": None,
            "information": {
                "dates": {"birthdate": {"date": "1980-03-15T00:00:00Z", "is_age_based": False,
                                        "is_year_unknown": False},
                          "deceased_date": {"date": None, "is_age_based": None, "is_year_unknown": None}},
                "career": {}},
            "is_dead": False,
        }
        p = monica.contact_to_update_payload(contact)
        self.assertEqual(p["first_name"], "Ann")
        self.assertEqual(p["is_birthdate_known"], True)
        self.assertEqual(p["birthdate_year"], 1980)
        self.assertEqual(p["is_deceased_date_known"], False)

if __name__ == "__main__":
    unittest.main()
