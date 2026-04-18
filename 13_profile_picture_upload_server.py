import re
import sqlite3
import mimetypes
from datetime import datetime, timezone
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import FileResponse, HTMLResponse, JSONResponse, Response

PROFILE_PIC_DIR = Path(__file__).resolve().parent / "uploads" / "profile_pictures"
DB_PATH = Path(__file__).resolve().parent / "profile_pictures.db"

# Keep user_id safe for filenames/DB and prevent path traversal.
USER_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")

# Restrict to common image types for profile pictures.
ALLOWED_MIME_TO_EXT = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
}


def _ensure_storage() -> None:
    PROFILE_PIC_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS profile_pictures (
                user_id TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_user_id(user_id: str) -> str:
    user_id = (user_id or "").strip()
    if not user_id:
        # Default "anonymous" bucket when user doesn't provide an id.
        user_id = "anonymous"
    if not USER_ID_RE.match(user_id):
        raise ValueError(
            "Invalid user_id. Use only letters, numbers, '_' or '-' (max 64 chars)."
        )
    return user_id


def _guess_mime_and_ext(filename: str | None, content_type: str | None) -> tuple[str, str]:
    guessed_type = None
    if filename:
        guessed_type = mimetypes.guess_type(filename)[0]

    mime_type = (content_type or guessed_type or "").lower().strip()
    ext = ALLOWED_MIME_TO_EXT.get(mime_type)
    if not ext:
        raise ValueError(
            f"Unsupported image type '{mime_type}'. Allowed: {', '.join(ALLOWED_MIME_TO_EXT)}"
        )
    return mime_type, ext


def _get_conn() -> sqlite3.Connection:
    # sqlite3 is blocking but local + small files are expected here.
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


mcp = FastMCP("ProfilePictureUpload")


@mcp.custom_route("/", methods=["GET"], name="profile-picture-page-root")
async def profile_picture_page(request: Request) -> HTMLResponse:
    # Simple frontend page served by the same HTTP server.
    user_id = request.query_params.get("user_id") or "anonymous"

    html = f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width,initial-scale=1" />
        <title>Profile Picture Upload</title>
        <style>
          body {{ font-family: Arial, sans-serif; padding: 24px; }}
          .card {{ max-width: 560px; padding: 16px; border: 1px solid #ddd; border-radius: 10px; }}
          input[type="text"] {{ width: 240px; padding: 8px; }}
          input[type="file"] {{ display: block; margin-top: 12px; }}
          button {{ margin-top: 12px; padding: 10px 14px; cursor: pointer; }}
          #preview {{ margin-top: 16px; max-width: 180px; display: none; border-radius: 10px; }}
          #status {{ margin-top: 12px; color: #444; white-space: pre-wrap; }}
          .hint {{ color: #666; font-size: 13px; margin-top: 6px; }}
        </style>
      </head>
      <body>
        <div class="card">
          <h2>Upload Profile Picture</h2>
          <p class="hint">Backend API: <code>/api/profile-picture/upload</code></p>

          <form id="uploadForm" action="/api/profile-picture/upload" method="post" enctype="multipart/form-data">
            <label>User ID (optional)</label><br/>
            <input type="text" name="user_id" value="{user_id}" placeholder="anonymous" />

            <input type="file" name="profile_picture" accept="image/*" required />
            <button type="submit">Upload</button>
          </form>

          <div id="status"></div>
          <img id="preview" alt="Profile preview" />
        </div>

        <script>
          const form = document.getElementById('uploadForm');
          const statusEl = document.getElementById('status');
          const previewEl = document.getElementById('preview');

          form.addEventListener('submit', async (e) => {{
            e.preventDefault();
            statusEl.textContent = 'Uploading...';

            const formData = new FormData(form);
            const res = await fetch(form.action, {{
              method: 'POST',
              body: formData,
            }});

            const data = await res.json().catch(() => ({{}}));
            if (!res.ok || !data.ok) {{
              statusEl.textContent = data.error || 'Upload failed.';
              previewEl.style.display = 'none';
              return;
            }}

            previewEl.src = data.image_url + '?t=' + Date.now();
            previewEl.style.display = 'block';
            statusEl.textContent = 'Uploaded successfully for user_id=' + data.user_id;
          }});
        </script>
      </body>
    </html>
    """
    return HTMLResponse(html)


@mcp.custom_route("/profile-picture", methods=["GET"], name="profile-picture-page")
async def profile_picture_page_alias(request: Request) -> HTMLResponse:
    # Same page as '/' (convenience).
    return await profile_picture_page(request)


@mcp.custom_route("/api/profile-picture/upload", methods=["POST"], name="profile-picture-upload-api")
async def upload_profile_picture(request: Request) -> Response:
    _ensure_storage()
    _ensure_db()

    try:
        form = await request.form()
        user_id_raw = form.get("user_id")  # might be None
        user_id = _validate_user_id(str(user_id_raw) if user_id_raw is not None else "")

        upload = form.get("profile_picture")
        if upload is None:
            return JSONResponse(
                {"ok": False, "error": "Missing file field 'profile_picture'."},
                status_code=400,
            )

        # Starlette gives UploadFile objects for multipart files.
        filename = getattr(upload, "filename", None)
        content_type = getattr(upload, "content_type", None)
        mime_type, ext = _guess_mime_and_ext(filename=filename, content_type=content_type)

        data = await upload.read()
        if not data:
            return JSONResponse({"ok": False, "error": "Uploaded file is empty."}, status_code=400)

        # Optional sanity limit (2MB). Increase if you want.
        max_bytes = 2 * 1024 * 1024
        if len(data) > max_bytes:
            return JSONResponse(
                {"ok": False, "error": f"File too large (max {max_bytes // (1024 * 1024)}MB)."},
                status_code=413,
            )

        final_path = PROFILE_PIC_DIR / f"{user_id}{ext}"

        conn = _get_conn()
        try:
            with conn:
                row = conn.execute(
                    "SELECT file_path FROM profile_pictures WHERE user_id = ?",
                    (user_id,),
                ).fetchone()

                # Delete old file if one exists.
                if row and row["file_path"]:
                    old_path = Path(row["file_path"])
                    if old_path.exists():
                        old_path.unlink(missing_ok=True)

                conn.execute(
                    """
                    INSERT INTO profile_pictures (user_id, file_path, updated_at)
                    VALUES (?, ?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                        file_path=excluded.file_path,
                        updated_at=excluded.updated_at
                    """,
                    (user_id, str(final_path), _now_iso()),
                )

            # Write file after DB update to reduce orphan records on rare IO failures.
            final_path.write_bytes(data)
        finally:
            conn.close()

        return JSONResponse(
            {
                "ok": True,
                "user_id": user_id,
                "image_url": f"/api/profile-picture/{user_id}",
                "content_type": mime_type,
            }
        )
    except ValueError as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"ok": False, "error": f"Unexpected error: {e}"}, status_code=500)


@mcp.custom_route("/api/profile-picture/{user_id}", methods=["GET"], name="profile-picture-get-api")
async def get_profile_picture(request: Request) -> Response:
    _ensure_storage()
    _ensure_db()

    user_id = request.path_params.get("user_id") or ""
    try:
        user_id = _validate_user_id(str(user_id))
    except ValueError:
        return JSONResponse({"ok": False, "error": "Invalid user_id."}, status_code=400)

    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT file_path FROM profile_pictures WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()

    if not row or not row["file_path"]:
        return JSONResponse({"ok": False, "error": "Profile picture not found."}, status_code=404)

    img_path = Path(row["file_path"])
    if not img_path.exists():
        return JSONResponse({"ok": False, "error": "Profile picture file missing."}, status_code=404)

    guessed_type = mimetypes.guess_type(img_path.name)[0] or "application/octet-stream"
    return FileResponse(
        img_path,
        media_type=guessed_type,
    )


if __name__ == "__main__":
    # Run an HTTP server so the browser can load the frontend page + upload endpoint.
    # Visit: http://127.0.0.1:8000/profile-picture
    mcp.run(transport="http", host="127.0.0.1", port=8000, show_banner=False)

