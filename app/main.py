import json, time, uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .db import conn, cursor
from .analysis import analyze_handle

app = FastAPI()

EXPIRY_HOURS = 24

class AnalyzeRequest(BaseModel):
    handle: str
    requested_by: str | None = None

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    report_id = uuid.uuid4().hex
    now = int(time.time() * 1000)
    expires = now + EXPIRY_HOURS * 3600 * 1000

    data = analyze_handle(req.handle)

    cursor.execute(
        "INSERT INTO reports VALUES (?, ?, ?, ?, ?)",
        (report_id, req.handle, json.dumps(data), now, expires)
    )
    conn.commit()

    return {
        "url": f"https://404nerds.app/r/{report_id}",
        "expires_at": expires
    }

@app.get("/report/{report_id}")
def get_report(report_id: str):
    row = cursor.execute(
        "SELECT data, expires_at FROM reports WHERE id = ?",
        (report_id,)
    ).fetchone()

    if not row:
        raise HTTPException(404, "Not found")

    if int(time.time() * 1000) > row[1]:
        raise HTTPException(410, "Report expired")

    return json.loads(row[0])
