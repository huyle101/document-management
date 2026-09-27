import hashlib
import json
import tempfile
import unittest
import zipfile
from io import BytesIO
from pathlib import Path

import storage
from app import create_app


class BackupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.data_dir = self.root / "data"
        self.backup_dir = self.root / "usb"
        self.backup_dir.mkdir()
        self.client = create_app(self.data_dir).test_client()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_backup_contains_database_and_all_file_bytes(self) -> None:
        self.client.post(
            "/documents",
            data={
                "title": "Nghị định",
                "attachments": [
                    (BytesIO(b"pdf one"), "một.pdf"),
                    (BytesIO(b"pdf two"), "hai.pdf"),
                ],
            },
            content_type="multipart/form-data",
        )
        response = self.client.post("/backup", data={"destination": str(self.backup_dir)})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Đã tạo bản sao lưu", response.text)

        archive_path = next(self.backup_dir.glob("*.zip"))
        with zipfile.ZipFile(archive_path) as archive:
            manifest = json.loads(archive.read("manifest.json"))
            self.assertEqual(manifest["format_version"], 1)
            self.assertEqual(len(manifest["files"]), 2)
            for entry in [manifest["database"], *manifest["files"]]:
                content = archive.read(entry["archive_name"])
                self.assertEqual(len(content), entry["size"])
                self.assertEqual(hashlib.sha256(content).hexdigest(), entry["sha256"])
            self.assertEqual(
                {archive.read(item["archive_name"]) for item in manifest["files"]},
                {b"pdf one", b"pdf two"},
            )

    def test_missing_file_cannot_produce_successful_backup(self) -> None:
        self.client.post(
            "/documents",
            data={"attachments": (BytesIO(b"file"), "x.pdf")},
            content_type="multipart/form-data",
        )
        attachment = storage.get_attachment(self.data_dir, 1)
        assert attachment is not None
        (self.data_dir / "files" / attachment["stored_name"]).unlink()

        response = self.client.post("/backup", data={"destination": str(self.backup_dir)})
        self.assertIn("Thiếu tệp đã lưu", response.text)
        self.assertEqual(list(self.backup_dir.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
