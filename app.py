import secrets
import shutil
import sqlite3
import tempfile
import threading
import zipfile
from datetime import date
from pathlib import Path

from flask import (
    Flask,
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

import backup
import restore
import storage

FIELD_LIMITS = {
    "title": 300,
    "number": 100,
    "kind": 100,
    "issue_date": 10,
    "issuer": 200,
    "summary": 4000,
}


def read_form() -> tuple[dict[str, str], str | None]:
    values = {field: request.form.get(field, "").strip() for field in FIELD_LIMITS}
    for field, limit in FIELD_LIMITS.items():
        if len(values[field]) > limit:
            return values, f"Trường thông tin quá dài (tối đa {limit} ký tự)."
    if values["issue_date"]:
        try:
            date.fromisoformat(values["issue_date"])
        except ValueError:
            return values, "Ngày ban hành không hợp lệ."
    return values, None


def create_app(data_dir: Path | None = None) -> Flask:
    resource_root = Path(__file__).resolve().parent
    app = Flask(
        __name__,
        template_folder=str(resource_root / "templates"),
        static_folder=str(resource_root / "static"),
    )
    app.config["DATA_DIR"] = data_dir or storage.default_data_dir()
    app.config["RESTORE_TOKEN"] = secrets.token_urlsafe(32)
    restore.recover_if_needed(app.config["DATA_DIR"])
    storage.initialize(app.config["DATA_DIR"])

    @app.get("/")
    def index():
        query = request.args.get("q", "").strip()
        documents = storage.search_documents(app.config["DATA_DIR"], query)
        return render_template("index.html", documents=documents, query=query)

    @app.get("/documents/<int:document_id>")
    def document_detail(document_id: int):
        document = storage.get_document(app.config["DATA_DIR"], document_id)
        if document is None:
            abort(404)
        attachments = storage.list_attachments(app.config["DATA_DIR"], document_id)
        return render_template(
            "document_detail.html", document=document, attachments=attachments
        )

    @app.get("/new")
    def new_document():
        return render_template(
            "document_form.html",
            values={},
            error=None,
            heading="Thêm văn bản",
            action=url_for("create_document"),
        )

    @app.post("/documents")
    def create_document():
        values, error = read_form()
        if error:
            return render_template(
                "document_form.html",
                values=values,
                error=error,
                heading="Thêm văn bản",
                action=url_for("create_document"),
            ), 400
        try:
            storage.save_document(
                app.config["DATA_DIR"], values, request.files.getlist("attachments")
            )
        except ValueError as exc:
            error = str(exc)
        except OSError:
            error = "Không lưu được tệp. Kiểm tra dung lượng ổ đĩa rồi thử lại."
        if error:
            return render_template(
                "document_form.html",
                values=values,
                error=error,
                heading="Thêm văn bản",
                action=url_for("create_document"),
            ), 400
        return redirect(url_for("index"), code=303)

    @app.route("/documents/<int:document_id>/edit", methods=["GET", "POST"])
    def edit_document(document_id: int):
        document = storage.get_document(app.config["DATA_DIR"], document_id)
        if document is None:
            abort(404)
        action = url_for("edit_document", document_id=document_id)
        if request.method == "GET":
            return render_template(
                "document_form.html",
                values=document,
                error=None,
                heading="Sửa văn bản",
                action=action,
                attachments=storage.list_attachments(app.config["DATA_DIR"], document_id),
            )
        values, error = read_form()
        if error:
            return render_template(
                "document_form.html",
                values=values,
                error=error,
                heading="Sửa văn bản",
                action=action,
                attachments=storage.list_attachments(app.config["DATA_DIR"], document_id),
            ), 400
        try:
            storage.save_document(
                app.config["DATA_DIR"], values, request.files.getlist("attachments"), document_id
            )
        except ValueError as exc:
            error = str(exc)
        except OSError:
            error = "Không lưu được tệp. Kiểm tra dung lượng ổ đĩa rồi thử lại."
        if error:
            return render_template(
                "document_form.html",
                values=values,
                error=error,
                heading="Sửa văn bản",
                action=action,
                attachments=storage.list_attachments(app.config["DATA_DIR"], document_id),
            ), 400
        return redirect(url_for("index"), code=303)

    @app.get("/files/<int:attachment_id>")
    def download_attachment(attachment_id: int):
        attachment = storage.get_attachment(app.config["DATA_DIR"], attachment_id)
        if attachment is None:
            abort(404)
        path = app.config["DATA_DIR"] / "files" / attachment["stored_name"]
        if not path.is_file():
            abort(404)
        return send_file(path, as_attachment=True, download_name=attachment["original_name"])

    @app.route("/backup", methods=["GET", "POST"])
    def backup_page():
        default_dir = Path.home() / "Documents"
        if not default_dir.is_dir():
            default_dir = Path.home()
        destination = request.form.get("destination", str(default_dir))
        error = None
        result = None
        if request.method == "POST":
            try:
                result = backup.create_backup(
                    app.config["DATA_DIR"], Path(destination).expanduser()
                )
            except ValueError as exc:
                error = str(exc)
            except (OSError, sqlite3.Error, zipfile.BadZipFile):
                error = "Không tạo được bản sao lưu. Kiểm tra thư mục và dung lượng ổ đĩa."
        return render_template(
            "backup.html", destination=destination, error=error, result=result
        )

    @app.route("/restore", methods=["GET", "POST"])
    def restore_page():
        error = None
        safety_backup = None
        if request.method == "POST":
            if request.form.get("restore_token") != app.config["RESTORE_TOKEN"]:
                abort(403)
            if request.form.get("confirm") != "yes":
                error = "Hãy xác nhận việc thay toàn bộ dữ liệu hiện tại."
            elif not (package := request.files.get("package")) or not package.filename:
                error = "Hãy chọn gói sao lưu để khôi phục."
            else:
                with tempfile.TemporaryDirectory(dir=app.config["DATA_DIR"].parent) as temporary:
                    package_path = Path(temporary) / "backup.zip"
                    try:
                        with package_path.open("wb") as output:
                            shutil.copyfileobj(package.stream, output)
                        safety_backup = restore.restore_backup(
                            app.config["DATA_DIR"], package_path
                        )
                    except (ValueError, TypeError, OSError, sqlite3.Error, zipfile.BadZipFile, EOFError, RuntimeError) as exc:
                        error = f"Không thể khôi phục: {exc}"
        return render_template(
            "restore.html",
            error=error,
            safety_backup=safety_backup,
            restore_token=app.config["RESTORE_TOKEN"],
        )

    @app.get("/__instance")
    def instance_identity():
        return jsonify({"application": "KhoVanBan"})

    @app.post("/quit")
    def quit_app():
        if request.form.get("quit_token") != app.config["RESTORE_TOKEN"]:
            abort(403)
        shutdown = app.config.get("SHUTDOWN_CALLBACK")
        if shutdown is None:
            abort(503)
        threading.Thread(target=shutdown, daemon=True).start()
        return render_template("closed.html")

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=8765, debug=False)
