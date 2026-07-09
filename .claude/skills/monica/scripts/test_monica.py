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

if __name__ == "__main__":
    unittest.main()
