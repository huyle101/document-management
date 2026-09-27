import re
import shutil
import sqlite3
import tempfile
import unittest
import zipfile
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import backup
import restore
from app import create_app


class RestoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.data_dir = self.root / "data"
        self.backup_dir = self.root / "usb"
        self.backup_dir.mkdir()
        self.client = create_app(self.data_dir).test_client()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def make_backup(self) -> Path:
        self.client.post(
            "/documents",
            data={"title": "Nghị định", "attachments": (BytesIO(b"original"), "bản.pdf")},
            content_type="multipart/form-data",
        )
        return backup.create_backup(self.data_dir, self.backup_dir)

    def test_restore_replaces_data_and_saves_previous_version(self) -> None:
        package = self.make_backup()
        self.client.post("/documents", data={"title": "Văn bản mới"})

        safety_package = restore.restore_backup(self.data_dir, package)
        current = create_app(self.data_dir).test_client()
        listing = current.get("/").text
        self.assertIn("Nghị định", listing)
        self.assertNotIn("Văn bản mới", listing)
        download = current.get("/files/1")
        self.assertEqual(download.data, b"original")
        download.close()

        self.assertTrue(safety_package.is_file())
        with zipfile.ZipFile(safety_package) as archive:
            old_db = self.root / "old.sqlite3"
            old_db.write_bytes(archive.read("documents.sqlite3"))
        with sqlite3.connect(old_db) as connection:
            titles = {row[0] for row in connection.execute("SELECT title FROM documents")}
        self.assertEqual(titles, {"Nghị định", "Văn bản mới"})

    def test_missing_file_in_backup_leaves_current_data_untouched(self) -> None:
        package = self.make_backup()
        self.client.post("/documents", data={"title": "Giữ nguyên"})
        broken = self.root / "broken.zip"
        with zipfile.ZipFile(package) as source, zipfile.ZipFile(broken, "w") as target:
            for name in source.namelist():
                if not name.startswith("files/"):
                    target.writestr(name, source.read(name))

        with self.assertRaises(ValueError):
            restore.restore_backup(self.data_dir, broken)
        self.assertIn("Giữ nguyên", self.client.get("/").text)
        self.assertFalse((self.root / "KhoVanBan-safety").exists())

    def test_changed_file_content_fails_checksum_before_replacement(self) -> None:
        package = self.make_backup()
        damaged = self.root / "damaged.zip"
        with zipfile.ZipFile(package) as source, zipfile.ZipFile(damaged, "w") as target:
            for name in source.namelist():
                content = source.read(name)
                if name.startswith("files/"):
                    content = b"tampered"
                target.writestr(name, content)

        with self.assertRaises(ValueError):
            restore.restore_backup(self.data_dir, damaged)
        self.assertIn("Nghị định", self.client.get("/").text)

    def test_restore_form_rejects_missing_token(self) -> None:
        package = self.make_backup()
        response = self.client.post(
            "/restore",
            data={"confirm": "yes", "package": (BytesIO(package.read_bytes()), "backup.zip")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 403)

    def test_reopen_recovers_data_if_switch_was_interrupted(self) -> None:
        self.client.post("/documents", data={"title": "Còn dữ liệu"})
        previous = self.root / "data.previous-20260925000000-abcdef"
        shutil.move(self.data_dir, previous)

        reopened = create_app(self.data_dir).test_client()
        self.assertIn("Còn dữ liệu", reopened.get("/").text)
        self.assertFalse(previous.exists())

    def test_failed_switch_restores_previous_data(self) -> None:
        package = self.make_backup()
        self.client.post("/documents", data={"title": "Giữ bản mới"})
        with patch("restore._promote_stage", side_effect=OSError("cannot move")), self.assertRaises(OSError):
            restore.restore_backup(self.data_dir, package)
        listing = create_app(self.data_dir).test_client().get("/").text
        self.assertIn("Giữ bản mới", listing)
        self.assertIn("Nghị định", listing)

    def test_restore_form_accepts_valid_backup_after_confirmation(self) -> None:
        package = self.make_backup()
        self.client.post("/documents", data={"title": "Được thay"})
        page = self.client.get("/restore").text
        token_match = re.search(r'name="restore_token" value="([^"]+)"', page)
        assert token_match is not None
        response = self.client.post(
            "/restore",
            data={
                "restore_token": token_match.group(1),
                "confirm": "yes",
                "package": (BytesIO(package.read_bytes()), "backup.zip"),
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Đã khôi phục dữ liệu", response.text)
        self.assertNotIn("Được thay", self.client.get("/").text)


if __name__ == "__main__":
    unittest.main()
