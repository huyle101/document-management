import hashlib
import hmac
import json
import os
import re
import shutil
import sqlite3
import tempfile
import uuid
import zipfile
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

import backup
import storage

STORED_NAME = re.compile(r"[0-9a-f]{32}")
SHA256 = re.compile(r"[0-9a-f]{64}")


def recover_if_needed(data_dir: Path) -> None:
    if data_dir.exists() or not data_dir.parent.exists():
        return
    previous = sorted(data_dir.parent.glob(f"{data_dir.name}.previous-*"), reverse=True)
    if previous:
        os.replace(previous[0], data_dir)


def _validate_entry(entry: object, expected_name: str) -> dict:
    if not isinstance(entry, dict):
        raise TypeError("Thông tin gói sao lưu không hợp lệ.")
    if entry.get("archive_name") != expected_name:
        raise ValueError("Tên tệp trong gói sao lưu không hợp lệ.")
    if type(entry.get("size")) is not int or entry["size"] < 0:
        raise ValueError("Dung lượng trong gói sao lưu không hợp lệ.")
    if not isinstance(entry.get("sha256"), str) or not SHA256.fullmatch(entry["sha256"]):
        raise ValueError("Mã kiểm tra gói sao lưu không hợp lệ.")
    return entry


def _copy_verified(archive: zipfile.ZipFile, entry: dict, destination: Path) -> None:
    info = archive.getinfo(entry["archive_name"])
    if info.file_size != entry["size"]:
        raise ValueError("Dung lượng tệp trong gói sao lưu không khớp.")
    digest = hashlib.sha256()
    size = 0
    with archive.open(info) as source, destination.open("wb") as target:
        while chunk := source.read(1024 * 1024):
            target.write(chunk)
            digest.update(chunk)
            size += len(chunk)
        target.flush()
        os.fsync(target.fileno())
    if size != entry["size"] or not hmac.compare_digest(digest.hexdigest(), entry["sha256"]):
        raise ValueError("Nội dung gói sao lưu bị hỏng hoặc đã thay đổi.")


def _extract_verified(package_path: Path, stage_dir: Path) -> None:
    with zipfile.ZipFile(package_path) as archive:
        try:
            manifest_info = archive.getinfo("manifest.json")
        except KeyError as exc:
            raise ValueError("Gói sao lưu thiếu thông tin kiểm tra.") from exc
        if manifest_info.file_size > 20 * 1024 * 1024:
            raise ValueError("Thông tin gói sao lưu quá lớn.")
        manifest = json.loads(archive.read(manifest_info))
        if not isinstance(manifest, dict) or type(manifest.get("format_version")) is not int:
            raise ValueError("Gói sao lưu không hợp lệ.")
        if manifest["format_version"] != backup.FORMAT_VERSION:
            raise ValueError("Phiên bản gói sao lưu chưa được hỗ trợ.")
        database_entry = _validate_entry(manifest.get("database"), storage.DB_NAME)
        files = manifest.get("files")
        if not isinstance(files, list):
            raise TypeError("Danh sách tệp trong gói sao lưu không hợp lệ.")

        expected = {"manifest.json", storage.DB_NAME}
        names = set()
        for item in files:
            if not isinstance(item, dict):
                raise TypeError("Thông tin tệp trong gói sao lưu không hợp lệ.")
            archive_name = item.get("archive_name")
            if not isinstance(archive_name, str) or not archive_name.startswith("files/"):
                raise ValueError("Đường dẫn tệp trong gói sao lưu không hợp lệ.")
            stored_name = archive_name.removeprefix("files/")
            if not STORED_NAME.fullmatch(stored_name):
                raise ValueError("Tên tệp trong gói sao lưu không hợp lệ.")
            _validate_entry(item, archive_name)
            if not isinstance(item.get("original_name"), str):
                raise TypeError("Tên gốc trong gói sao lưu không hợp lệ.")
            names.add(archive_name)
            expected.add(archive_name)
        if len(names) != len(files) or set(archive.namelist()) != expected:
            raise ValueError("Gói sao lưu thiếu tệp hoặc chứa tệp ngoài danh sách.")
        if len(archive.namelist()) != len(expected):
            raise ValueError("Gói sao lưu có tệp trùng tên.")

        files_dir = stage_dir / "files"
        files_dir.mkdir()
        _copy_verified(archive, database_entry, stage_dir / storage.DB_NAME)
        for item in files:
            stored_name = item["archive_name"].removeprefix("files/")
            _copy_verified(archive, item, files_dir / stored_name)

    database_path = stage_dir / storage.DB_NAME
    with closing(sqlite3.connect(database_path)) as connection:
        if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("Cơ sở dữ liệu trong gói sao lưu bị hỏng.")
        if connection.execute("PRAGMA foreign_key_check").fetchone() is not None:
            raise ValueError("Quan hệ dữ liệu trong gói sao lưu bị hỏng.")
        connection.execute("SELECT COUNT(*) FROM documents").fetchone()
        rows = connection.execute(
            "SELECT original_name, stored_name, byte_size FROM attachments"
        ).fetchall()
    expected_files = sorted(
        (
            item["original_name"],
            item["archive_name"].removeprefix("files/"),
            item["size"],
        )
        for item in files
    )
    if sorted(rows) != expected_files:
        raise ValueError("Danh sách tệp và cơ sở dữ liệu không khớp.")


def _promote_stage(stage_dir: Path, data_dir: Path) -> None:
    os.replace(stage_dir, data_dir)


def restore_backup(data_dir: Path, package_path: Path) -> Path:
    with storage.DATA_LOCK, tempfile.TemporaryDirectory(
        prefix=f"{data_dir.name}.restore-", dir=data_dir.parent
    ) as temporary:
        stage_dir = Path(temporary) / "stage"
        stage_dir.mkdir()
        _extract_verified(package_path, stage_dir)

        safety_dir = data_dir.parent / "KhoVanBan-safety"
        safety_dir.mkdir(exist_ok=True)
        safety_backup = backup.create_backup(data_dir, safety_dir)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        previous = data_dir.with_name(f"{data_dir.name}.previous-{stamp}-{uuid.uuid4().hex[:6]}")
        os.replace(data_dir, previous)
        try:
            _promote_stage(stage_dir, data_dir)
        except Exception:
            os.replace(previous, data_dir)
            raise
        try:
            shutil.rmtree(previous)
        except OSError:
            pass
        return safety_backup
