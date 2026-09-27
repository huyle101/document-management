import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.parse
import urllib.request
from pathlib import Path
from unittest.mock import patch

from app import create_app
from launcher import LoopbackServer

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class LauncherTests(unittest.TestCase):
    def test_local_server_does_not_wait_for_reverse_dns(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, patch(
            "socket.getfqdn", side_effect=AssertionError("reverse DNS called")
        ):
            server = LoopbackServer("127.0.0.1", 0, create_app(Path(temporary) / "data"))
            server.server_close()

    def test_start_second_click_and_quit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            environment = os.environ.copy()
            environment["DOCUMENT_MANAGER_DATA_DIR"] = str(root / "data")
            environment["DOCUMENT_MANAGER_NO_BROWSER"] = "1"
            port_file = root / "data.port"
            process = subprocess.Popen(
                [sys.executable, "launcher.py"],
                cwd=PROJECT_ROOT,
                env=environment,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            try:
                for _ in range(100):
                    if port_file.is_file():
                        break
                    if process.poll() is not None:
                        self.fail(f"Launcher exited early: {process.stderr.read()!r}")
                    time.sleep(0.05)
                self.assertTrue(port_file.is_file())
                url = f"http://127.0.0.1:{int(port_file.read_text())}"
                with urllib.request.urlopen(url, timeout=2) as response:
                    page = response.read().decode("utf-8")
                self.assertIn("Văn bản của bạn", page)

                second = subprocess.run(
                    [sys.executable, "launcher.py"],
                    cwd=PROJECT_ROOT,
                    env=environment,
                    check=False,
                    capture_output=True,
                    timeout=5,
                )
                self.assertEqual(second.returncode, 0, second.stderr.decode())
                self.assertIsNone(process.poll())

                token_match = re.search(r'name="quit_token" value="([^"]+)"', page)
                assert token_match is not None
                request = urllib.request.Request(
                    f"{url}/quit",
                    data=urllib.parse.urlencode({"quit_token": token_match.group(1)}).encode(),
                    method="POST",
                )
                with urllib.request.urlopen(request, timeout=2) as response:
                    self.assertIn("Ứng dụng đã đóng", response.read().decode("utf-8"))
                self.assertEqual(process.wait(timeout=5), 0)
                self.assertFalse(port_file.exists())
            finally:
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=5)
                if process.stderr:
                    process.stderr.close()


if __name__ == "__main__":
    unittest.main()
