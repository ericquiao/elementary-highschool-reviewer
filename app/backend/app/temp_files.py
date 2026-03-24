import os
import tempfile
from typing import Optional

from fastapi import UploadFile


async def save_upload_to_temp(upload: UploadFile) -> str:
    suffix = ""
    if upload.filename and "." in upload.filename:
        suffix = os.path.splitext(upload.filename)[1]

    fd, path = tempfile.mkstemp(prefix="student-reviewer-", suffix=suffix)
    try:
        with os.fdopen(fd, "wb") as temp_file:
            while True:
                chunk = await upload.read(1024 * 1024)
                if not chunk:
                    break
                temp_file.write(chunk)
    finally:
        await upload.close()

    return path


def delete_temp_file(path: Optional[str]) -> None:
    if path and os.path.exists(path):
        os.remove(path)
