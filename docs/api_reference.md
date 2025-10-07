# 🔌 API Reference — AI-Driven Clinical Trial Tool

> Version: v1.0  
> Base URL: `/api/v1`  
> Response Format: `{ code, message, data }`  
> Status Codes:  
> - `code = 0` → Success  
> - `code != 0` → Error

---

## 📦 1. Matrix Extraction

### `POST /api/v1/parse-matrix`
**Description**: Upload an Excel file and parse matrix relationships.  
**Use case**: For small files, synchronous parsing via FastAPI.

| Parameter | Type | Description |
|------------|------|--------------|
| `file` | `File` | Excel file (`.xlsx`) |

**Response Example**
```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "matrixSheets": [
      {
        "sheetName": "Matrix#MASTERDASHBOARD",
        "folderOids": ["Subject", "1100", "1150"],
        "matrixEntries": [
          { "formOid": "PRIMARY001", "includedFolders": ["Subject", "1100"] }
        ]
      }
    ]
  }
}
```

**Errors**
| Code | Message | Description |
|-------|----------|-------------|
| 400 | `file is required` | Missing upload file |
| 500 | `internal error` | FastAPI unavailable or parse error |

---

## 🧮 2. Async Job Management

### `POST /api/v1/jobs`
**Description**: Submit an asynchronous job (e.g., large XLSX or AI processing).

| Parameter | Type | Description |
|------------|------|--------------|
| `s3_key` | `string` | Path to file in S3/MinIO |

**Response Example**
```json
{
  "code": 0,
  "message": "accepted",
  "data": { "job_id": "uuid-1234" }
}
```

---

### `GET /api/v1/jobs/:id`
**Description**: Check job status or retrieve result.

**Response Example**
```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "status": "done",
    "result": { "ok": true, "matrixSheets": [] }
  }
}
```

**Job Status Values**
| Status | Meaning |
|---------|----------|
| `pending` | Waiting for processing |
| `running` | Worker executing task |
| `done` | Completed |
| `error` | Failed or exception occurred |

---

## 🧠 3. Python AI Service Endpoints

### `POST /matrix/extract`
**Description**: Parse matrix data from uploaded XLSX file.  
**Backend Service**: `ai_service/main.py`

**Response**
```json
{
  "ok": true,
  "result": { "matrixSheets": [...] }
}
```

---

### `POST /matrix/extract-by-url`
**Description**: Parse matrix data directly from S3/MinIO object key.  
**Parameter**
```json
{ "s3_key": "CLOU064P12301/input/ALS.xlsx" }
```

---

## 🗃️ 4. Database Schema (PostgreSQL)

```sql
CREATE TABLE jobs (
  id UUID PRIMARY KEY,
  type TEXT NOT NULL,
  status TEXT NOT NULL,
  s3_key TEXT,
  result_url TEXT,
  error_msg TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  created_by TEXT
);
CREATE INDEX idx_jobs_status ON jobs(status);
```

---

## 🔐 5. Error Codes Summary
| Code | Meaning |
|------|----------|
| 0 | Success |
| 400 | Validation or missing params |
| 401 | Unauthorized |
| 404 | Not found |
| 500 | Internal error |

---

## 🚀 6. Future Planned APIs

| API | Description |
|-----|--------------|
| `POST /api/v1/uploads/presign` | Generate presigned URL for direct upload |
| `GET /api/v1/files/:id` | Fetch file metadata |
| `POST /api/v1/qc/run` | Trigger QC rule checks |
| `GET /api/v1/dashboard/stats` | Aggregated job statistics |
