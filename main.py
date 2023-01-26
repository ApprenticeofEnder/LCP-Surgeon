import zipfile
import io

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi import UploadFile

from lcp_surgeon.lcp_processor import process_lcp

app = FastAPI()

@app.post("/api/lcp/processor")
async def upload_lcp(lcp_file: UploadFile):
    new_lcp_bytes = process_lcp(lcp_file)
    package = io.BytesIO()
    with zipfile.ZipFile(package, 'w') as package_file:
        package_file.writestr(f'{lcp_file.filename}.bak', lcp_file.file.read())
        package_file.writestr(lcp_file.filename, new_lcp_bytes)
    response = StreamingResponse(iter([package.getvalue()]),
                            media_type="application/zip")
    new_filename = f"{lcp_file.filename.replace('.lcp', '')}-cleaned.zip"
    response.headers["Content-Disposition"] = f"attachment; filename={new_filename}"
    return response

# Place After All Other Routes
app.mount('', StaticFiles(directory="client/public/", html=True), name="static")