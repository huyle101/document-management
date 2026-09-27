import http.client
import json
import os
import socketserver
import sys
import time
import uuid
import webbrowser
from pathlib import Path
from typing import BinaryIO

from werkzeug.serving import ThreadedWSGIServer

import storage
from app import create_app


class LoopbackServer(ThreadedWSGIServer):
    def server_bind(self) -> None:
        socketserver.TCPServer.server_bind(self)
        self.server_name = "localhost"
        self.server_port = self.server_address[1]


def _try_lock(file: BinaryIO) -> bool:
    file.seek(0, os.SEEK_END)
    if file.tell() == 0:
        file.write(b"\0")
        file.flush()
    file.seek(0)
    try:
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(file.fileno(), msvcrt.LK_NBLCK, 1)  # type: ignore[attr-defined]
        else:
            import fcntl

            fcntl.flock(file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        return False
    return True


def _open_browser(url: str) -> None:
    if os.environ.get("DOCUMENT_MANAGER_NO_BROWSER") != "1":
        webbrowser.open(url)


def _open_running_instance(port_file: Path) -> None:
    for _ in range(40):
        try:
            port = int(port_file.read_text(encoding="ascii"))
            if not 1 <= port <= 65535:
                raise ValueError("Invalid local port")
            url = f"http://127.0.0.1:{port}"
            connection = http.client.HTTPConnection("127.0.0.1", port, timeout=0.3)
            try:
                connection.request("GET", "/__instance")
                response = connection.getresponse()
                identity = json.loads(response.read()) if response.status == 200 else {}
            finally:
                connection.close()
            if identity.get("application") == "KhoVanBan":
                _open_browser(url)
                return
        except (OSError, ValueError, http.client.HTTPException):
            time.sleep(0.1)
    raise RuntimeError("Ứng dụng đang khởi động. Hãy thử mở lại sau ít giây.")


def run() -> None:
    data_dir = storage.default_data_dir()
    data_dir.parent.mkdir(parents=True, exist_ok=True)
    lock_path = data_dir.with_name(f"{data_dir.name}.lock")
    port_path = data_dir.with_name(f"{data_dir.name}.port")

    with lock_path.open("a+b") as lock_file:
        if not _try_lock(lock_file):
            _open_running_instance(port_path)
            return
        app = create_app(data_dir)
        server = LoopbackServer("127.0.0.1", 0, app)
        app.config["SHUTDOWN_CALLBACK"] = server.shutdown
        temporary_port = port_path.with_name(f"{port_path.name}.{uuid.uuid4().hex}.tmp")
        temporary_port.write_text(str(server.server_port), encoding="ascii")
        os.replace(temporary_port, port_path)
        try:
            _open_browser(f"http://127.0.0.1:{server.server_port}")
            server.serve_forever()
        finally:
            server.server_close()
            port_path.unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        run()
    except Exception as error:
        if sys.platform == "win32":
            import ctypes

            ctypes.windll.user32.MessageBoxW(0, str(error), "Kho văn bản", 0x10)
        else:
            raise
