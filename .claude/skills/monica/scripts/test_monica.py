import importlib.util
import io, json, os, tempfile, unittest
from contextlib import redirect_stderr
from importlib.machinery import SourceFileLoader
from pathlib import Path

_path = str(Path(__file__).parent / "monica")
_spec = importlib.util.spec_from_file_location("monica", _path, loader=SourceFileLoader("monica", _path))
monica = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(monica)

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

class InputValidationTest(unittest.TestCase):
    def test_parse_json_arg_invalid_json_fails_cleanly(self):
        buf = io.StringIO()
        with redirect_stderr(buf):
            with self.assertRaises(SystemExit) as cm:
                monica.parse_json_arg("{not valid json")
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("invalid JSON in --json argument", buf.getvalue())

    def test_parse_json_arg_valid_json_passes_through(self):
        self.assertEqual(monica.parse_json_arg('{"a": 1}'), {"a": 1})

    def test_expand_birthdate_invalid_date_fails_cleanly(self):
        buf = io.StringIO()
        with redirect_stderr(buf):
            with self.assertRaises(SystemExit) as cm:
                monica.expand_birthdate({"first_name": "A", "birthdate": "not-a-date"})
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("invalid birthdate", buf.getvalue())

    def test_parse_tag_list_strips_and_drops_empty(self):
        self.assertEqual(monica.parse_tag_list("a, b ,, c "), ["a", "b", "c"])

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
            "gender": "Woman", "gender_type": None, "description": None,
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
        # ContactResource exposes only the gender NAME, never gender_id;
        # the mapping leaves gender_id out entirely (resolution happens in the command layer).
        self.assertNotIn("gender_id", p)

    def test_resolve_gender_id(self):
        genders = [{"id": 1, "name": "Man", "type": "M"},
                   {"id": 2, "name": "Woman", "type": "F"},
                   {"id": 3, "name": "Rather not say", "type": "O"}]
        self.assertEqual(monica.resolve_gender_id(genders, "Woman"), 2)
        self.assertEqual(monica.resolve_gender_id(genders, "woman"), 2)   # case-insensitive
        self.assertIsNone(monica.resolve_gender_id(genders, "Nonexistent"))
        self.assertIsNone(monica.resolve_gender_id(genders, None))

    GENDERS = [{"id": 1, "name": "Man"}, {"id": 2, "name": "Woman"}]

    def _current(self):  # minimal gendered ContactResource shape
        return {"id": 7, "first_name": "Ann", "last_name": "Lee", "nickname": None,
                "gender": "Woman", "description": None, "is_dead": False,
                "information": {"dates": {"birthdate": {"date": None},
                                          "deceased_date": {"date": None}}}}

    def test_build_update_body_gender_omitted_resolves(self):
        body = monica.build_update_body(self._current(), {"nickname": "Zed"},
                                        lambda: self.GENDERS)
        self.assertEqual(body["gender_id"], 2)
        self.assertEqual(body["nickname"], "Zed")

    def test_build_update_body_explicit_gender_respected(self):
        def boom():  # explicit gender_id must not trigger a genders fetch
            raise AssertionError("genders fetched despite explicit gender_id")
        body = monica.build_update_body(self._current(), {"gender_id": 1}, boom)
        self.assertEqual(body["gender_id"], 1)

    def test_build_update_body_explicit_null_gender_respected(self):
        def boom():
            raise AssertionError("genders fetched despite explicit null gender_id")
        body = monica.build_update_body(self._current(), {"gender_id": None}, boom)
        self.assertIsNone(body["gender_id"])   # clear-intent passes through untouched

    def test_build_update_body_gender_resolve_miss_warns(self):
        buf = io.StringIO()
        with redirect_stderr(buf):
            body = monica.build_update_body(self._current(), {},
                                            lambda: [{"id": 1, "name": "Man"}])
        self.assertIsNone(body["gender_id"])
        self.assertIn("could not resolve gender", buf.getvalue())

class RefCacheTest(unittest.TestCase):
    CFG = {"MONICA_API_URL": "https://crm.example:8443/api", "MONICA_API_TOKEN": "t"}
    FIXTURE = [{"id": 1, "name": "Man"}, {"id": 2, "name": "Woman"}]

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._orig_cache_dir = monica.CACHE_DIR
        self._orig_paginate = monica.paginate
        monica.CACHE_DIR = Path(self._tmpdir.name)
        self.calls = []
        def fake_paginate(cfg, path, params=None):
            self.calls.append(path)
            return list(self.FIXTURE)
        monica.paginate = fake_paginate

    def tearDown(self):
        monica.CACHE_DIR = self._orig_cache_dir
        monica.paginate = self._orig_paginate
        self._tmpdir.cleanup()

    def _cache_file(self, kind):
        return Path(self._tmpdir.name) / ("crm.example_8443-%s.json" % kind)

    def test_first_call_fetches_and_writes_cache(self):
        items = monica.ref_lookup(self.CFG, "genders")
        self.assertEqual(items, self.FIXTURE)
        self.assertEqual(self.calls, ["genders"])
        self.assertTrue(self._cache_file("genders").exists())
        self.assertEqual(json.loads(self._cache_file("genders").read_text()), self.FIXTURE)

    def test_second_call_reads_cache_without_fetching(self):
        monica.ref_lookup(self.CFG, "genders")
        def boom(cfg, path, params=None):
            raise AssertionError("paginate called despite valid cache")
        monica.paginate = boom
        self.assertEqual(monica.ref_lookup(self.CFG, "genders"), self.FIXTURE)

    def test_corrupt_cache_falls_back_and_repairs(self):
        self._cache_file("genders").write_text("not json")
        items = monica.ref_lookup(self.CFG, "genders")
        self.assertEqual(items, self.FIXTURE)                       # no traceback, refetched
        self.assertEqual(self.calls, ["genders"])
        self.assertEqual(json.loads(self._cache_file("genders").read_text()),
                         self.FIXTURE)                              # cache repaired

    def test_refresh_bypasses_valid_cache(self):
        monica.ref_lookup(self.CFG, "genders")
        monica.ref_lookup(self.CFG, "genders", refresh=True)
        self.assertEqual(self.calls, ["genders", "genders"])        # fetched twice

if __name__ == "__main__":
    unittest.main()
