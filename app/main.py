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

@app.get("/api/report/{report_id}")
def get_report(report_id: str):
    try:
        row = cursor.execute(
            "SELECT data, expires_at FROM reports WHERE id = ?",
            (report_id,)
        ).fetchone()
    except Exception as e:
        raise HTTPException(500, f"Database query error: {str(e)}")

    if not row:
        raise HTTPException(404, "Report ID not found")

    try:
        data_json = json.loads(row[0])
    except Exception as e:
        raise HTTPException(500, f"Corrupt report data: {str(e)}")

    expires_at = row[1]
    now_ms = int(time.time() * 1000)

    if expires_at is None:
        # safe default behavior
        pass
    elif now_ms > expires_at:
        raise HTTPException(410, "Report expired")

    return {
        "report_id": report_id,
        "data": data_json,
        "expires_at": expires_at
    }

