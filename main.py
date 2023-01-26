from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi import UploadFile
from lcp_surgeon.lcp_processor import process_lcp

app = FastAPI()

@app.post("/api/lcp/processor")
async def upload_lcp(uploaded_file: UploadFile):
    pass

# Place After All Other Routes
app.mount('', StaticFiles(directory="client/public/", html=True), name="static")