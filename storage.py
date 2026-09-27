import os
import shutil
import sqlite3
import sys
import tempfile
import threading
import unicodedata
import uuid
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from werkzeug.datastructures import FileStorage

DB_NAME = "documents.sqlite3"
FIELDS = ("title", "number", "kind", "issue_date", "issuer", "summary")
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".jpg", ".jpeg", ".png"}
DATA_LOCK = threading.RLock()


def default_data_dir() -> Path:
    override = os.environ.get("DOCUMENT_MANAGER_DATA_DIR")
    if override:
        return Path(override).expanduser()
    if sys.platform == "win32":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        root = Path.home() / "Library" / "Application Support"
    else:
        root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return root / "KhoVanBan"


def connect(data_dir: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(data_dir / DB_NAME)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize(data_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    with closing(connect(data_dir)) as connection, connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL DEFAULT '',
                number TEXT NOT NULL DEFAULT '',
                kind TEXT NOT NULL DEFAULT '',
                issue_date TEXT NOT NULL DEFAULT '',
                issuer TEXT NOT NULL DEFAULT '',
                summary TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )"""
        )
        connection.execute(
            """CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY,
                document_id INTEGER NOT NULL REFERENCES documents(id),
                original_name TEXT NOT NULL,
                stored_name TEXT NOT NULL UNIQUE,
                byte_size INTEGER NOT NULL
            )"""
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS attachments_document_id ON attachments(document_id)"
        )


def list_documents(data_dir: Path) -> list[dict]:
    with closing(connect(data_dir)) as connection:
        rows = connection.execute(
            """SELECT documents.*,
               (SELECT COUNT(*) FROM attachments WHERE document_id = documents.id)
               AS attachment_count
               FROM documents ORDER BY created_at DESC, id DESC"""
        ).fetchall()
    return [dict(row) for row in rows]


def search_documents(data_dir: Path, query: str) -> list[dict]:
    documents = list_documents(data_dir)
    needle = normalize_for_search(query.strip())
    if not needle:
        return documents
    return [document for document in documents if needle in normalize_for_search(document["title"])]


def normalize_for_search(value: str) -> str:
    folded = value.casefold().replace("đ", "d")
    return "".join(
        character
        for character in unicodedata.normalize("NFD", folded)
        if unicodedata.category(character) != "Mn"
    )


def get_document(data_dir: Path, document_id: int) -> dict | None:
    with closing(connect(data_dir)) as connection:
        row = connection.execute(
            "SELECT * FROM documents WHERE id = ?", (document_id,)
        ).fetchone()
    return dict(row) if row is not None else None


def list_attachments(data_dir: Path, document_id: int) -> list[dict]:
    with closing(connect(data_dir)) as connection:
        rows = connection.execute(
            "SELECT * FROM attachments WHERE document_id = ? ORDER BY id", (document_id,)
        ).fetchall()
    return [dict(row) for row in rows]


def get_attachment(data_dir: Path, attachment_id: int) -> dict | None:
    with closing(connect(data_dir)) as connection:
        row = connection.execute(
            "SELECT * FROM attachments WHERE id = ?", (attachment_id,)
        ).fetchone()
    return dict(row) if row is not None else None


def save_document(
    data_dir: Path,
    values: dict[str, str],
    uploads: list[FileStorage],
    document_id: int | None = None,
) -> int:
    with DATA_LOCK:
        return _save_document(data_dir, values, uploads, document_id)


def _save_document(
    data_dir: Path,
    values: dict[str, str],
    uploads: list[FileStorage],
    document_id: int | None = None,
) -> int:
    files_dir = data_dir / "files"
    chosen = [item for item in uploads if item.filename]
    if chosen:
        files_dir.mkdir(exist_ok=True)
    moved: list[Path] = []
    with tempfile.TemporaryDirectory(dir=data_dir) as temporary:
        staged: list[tuple[str, str, Path, int]] = []
        for upload in chosen:
            original_name = (upload.filename or "").replace("\\", "/").rsplit("/", 1)[-1].strip()
            if not original_name or Path(original_name).suffix.lower() not in ALLOWED_EXTENSIONS:
                raise ValueError(f"Tệp không được hỗ trợ: {original_name or 'không có tên'}")
            stored_name = uuid.uuid4().hex
            stage_path = Path(temporary) / stored_name
            with stage_path.open("wb") as output:
                shutil.copyfileobj(upload.stream, output)
                output.flush()
                os.fsync(output.fileno())
            staged.append((original_name, stored_name, stage_path, stage_path.stat().st_size))

        now = datetime.now(timezone.utc).isoformat()
        try:
            with closing(connect(data_dir)) as connection, connection:
                if document_id is None:
                    cursor = connection.execute(
                        """INSERT INTO documents
                           (title, number, kind, issue_date, issuer, summary, created_at, updated_at)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        tuple(values[field] for field in FIELDS) + (now, now),
                    )
                    assert cursor.lastrowid is not None
                    document_id = cursor.lastrowid
                else:
                    connection.execute(
                        """UPDATE documents
                           SET title = ?, number = ?, kind = ?, issue_date = ?,
                               issuer = ?, summary = ?, updated_at = ? WHERE id = ?""",
                        tuple(values[field] for field in FIELDS) + (now, document_id),
                    )
                for original_name, stored_name, stage_path, byte_size in staged:
                    destination = files_dir / stored_name
                    os.replace(stage_path, destination)
                    moved.append(destination)
                    connection.execute(
                        """INSERT INTO attachments
                           (document_id, original_name, stored_name, byte_size)
                           VALUES (?, ?, ?, ?)""",
                        (document_id, original_name, stored_name, byte_size),
                    )
        except Exception:
            for destination in moved:
                destination.unlink(missing_ok=True)
            raise
    assert document_id is not None
    return document_id
