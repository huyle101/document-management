import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from app import create_app


class DocumentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temp_dir.name)
        self.client = create_app(self.data_dir).test_client()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_empty_fields_and_edit_survive_reopen(self) -> None:
        response = self.client.post("/documents", data={})
        self.assertEqual(response.status_code, 303)
        self.assertIn("Chưa đặt tên", self.client.get("/").text)

        response = self.client.post(
            "/documents/1/edit",
            data={"title": "Nghị định", "issuer": "Đơn vị", "issue_date": "2026-09-25"},
        )
        self.assertEqual(response.status_code, 303)
        reopened = create_app(self.data_dir).test_client().get("/").text
        self.assertIn("Nghị định", reopened)
        self.assertIn("Đơn vị", reopened)
        self.assertIn("25/09/2026", reopened)

    def test_invalid_date_preserves_entered_text(self) -> None:
        response = self.client.post(
            "/documents", data={"title": "Giữ lại", "issue_date": "2026-02-31"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Giữ lại", response.text)
        self.assertIn("Ngày ban hành không hợp lệ", response.text)
        self.assertNotIn("Giữ lại", self.client.get("/").text)

    def test_multiple_same_named_files_survive_source_removal(self) -> None:
        first = self.data_dir / "source-one" / "quyết định.pdf"
        second = self.data_dir / "source-two" / "quyết định.pdf"
        first.parent.mkdir()
        second.parent.mkdir()
        first.write_bytes(b"first file")
        second.write_bytes(b"second file")
        with first.open("rb") as first_stream, second.open("rb") as second_stream:
            response = self.client.post(
                "/documents",
                data={
                    "title": "Hồ sơ",
                    "attachments": [
                        (first_stream, first.name),
                        (second_stream, second.name),
                    ],
                },
                content_type="multipart/form-data",
            )
        self.assertEqual(response.status_code, 303)
        first.unlink()
        second.unlink()

        index = self.client.get("/").text
        self.assertIn("2 tệp", index)
        edit_page = self.client.get("/documents/1/edit").text
        self.assertEqual(edit_page.count("quyết định.pdf"), 2)
        first_download = self.client.get("/files/1")
        second_download = self.client.get("/files/2")
        self.assertEqual(first_download.data, b"first file")
        self.assertEqual(second_download.data, b"second file")
        first_download.close()
        second_download.close()

    def test_bad_attachment_does_not_save_record(self) -> None:
        response = self.client.post(
            "/documents",
            data={"title": "Không lưu", "attachments": (BytesIO(b"hello"), "notes.txt")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Không lưu", response.text)
        self.assertIn("Tệp không được hỗ trợ", response.text)
        self.assertNotIn("Không lưu", self.client.get("/").text)

    def test_copy_failure_does_not_leave_successful_record(self) -> None:
        with patch("storage.shutil.copyfileobj", side_effect=OSError("disk full")):
            response = self.client.post(
                "/documents",
                data={"title": "Chưa lưu", "attachments": (BytesIO(b"file"), "a.pdf")},
                content_type="multipart/form-data",
            )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Chưa lưu", response.text)
        self.assertNotIn("Chưa lưu", self.client.get("/").text)

    def test_search_finds_vietnamese_title_without_accents(self) -> None:
        self.client.post("/documents", data={"title": "Nghị định về đơn vị"})
        self.client.post("/documents", data={"title": "Thông báo khác"})

        results = self.client.get("/?q=NGHI+DINH").text
        self.assertIn("Nghị định về đơn vị", results)
        self.assertNotIn("Thông báo khác", results)
        self.assertIn("Nghị định về đơn vị", self.client.get("/?q=don+vi").text)
        self.assertIn("Thông báo khác", self.client.get("/?q=").text)

    def test_search_result_opens_detail_and_correct_file(self) -> None:
        self.client.post(
            "/documents",
            data={"title": "Nghị định", "attachments": (BytesIO(b"content"), "tệp.pdf")},
            content_type="multipart/form-data",
        )
        results = self.client.get("/?q=nghi+dinh").text
        self.assertIn('href="/documents/1"', results)
        detail = self.client.get("/documents/1").text
        self.assertIn("tệp.pdf", detail)
        self.assertIn('href="/files/1"', detail)


if __name__ == "__main__":
    unittest.main()
