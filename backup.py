import hashlib
import json
import os
import sqlite3
import tempfile
import uuid
import zipfile
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

import storage

FORMAT_VERSION = 1


def _add_file(archive: zipfile.ZipFile, source: Path, archive_name: str) -> dict:
    digest = hashlib.sha256()
    size = 0
    with source.open("rb") as input_file, archive.open(archive_name, "w") as output_file:
        while chunk := input_file.read(1024 * 1024):
            output_file.write(chunk)
            digest.update(chunk)
            size += len(chunk)
    return {"archive_name": archive_name, "sha256": digest.hexdigest(), "size": size}


def create_backup(data_dir: Path, destination_dir: Path) -> Path:
    if not destination_dir.is_absolute() or not destination_dir.is_dir():
        raise ValueError("Hãy nhập đường dẫn đầy đủ đến một thư mục đang tồn tại.")

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    final_path = destination_dir / f"KhoVanBan-{stamp}-{uuid.uuid4().hex[:6]}.zip"
    with tempfile.NamedTemporaryFile(
        prefix="KhoVanBan-", suffix=".partial", dir=destination_dir, delete=False
    ) as temporary_file:
        partial_path = Path(temporary_file.name)

    try:
        with storage.DATA_LOCK, tempfile.TemporaryDirectory(dir=data_dir) as temporary_dir:
            snapshot = Path(temporary_dir) / storage.DB_NAME
            with closing(storage.connect(data_dir)) as source, closing(
                sqlite3.connect(snapshot)
            ) as target:
                source.backup(target)

            with zipfile.ZipFile(partial_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                database_entry = _add_file(archive, snapshot, storage.DB_NAME)
                with closing(sqlite3.connect(snapshot)) as connection:
                    rows = connection.execute(
                        "SELECT original_name, stored_name, byte_size FROM attachments ORDER BY id"
                    ).fetchall()
                file_entries = []
                for original_name, stored_name, byte_size in rows:
                    source_path = data_dir / "files" / stored_name
                    if not source_path.is_file():
                        raise ValueError(f"Thiếu tệp đã lưu: {original_name}")
                    entry = _add_file(archive, source_path, f"files/{stored_name}")
                    if entry["size"] != byte_size:
                        raise ValueError(f"Tệp đã thay đổi dung lượng: {original_name}")
                    entry["original_name"] = original_name
                    file_entries.append(entry)
                manifest = {
                    "format_version": FORMAT_VERSION,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "database": database_entry,
                    "files": file_entries,
                }
                archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False))

            with partial_path.open("r+b") as completed:
                os.fsync(completed.fileno())
            os.replace(partial_path, final_path)
    finally:
        partial_path.unlink(missing_ok=True)
    return final_path
