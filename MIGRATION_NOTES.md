Matrix Review – Migration Notes

Scope
- Implemented SSD upload compare endpoint in backend and wired the existing Vue Matrix view/components to use it when an SSD file is uploaded. Pasted SSD JSON/CSV is still handled client‑side.
- Kept changes restricted to matrix-related files.

Backend
- New endpoint: POST /ssd/compare
  - Form-data fields: `als_file` (xlsx), `ssd_file` (json/csv/xlsx), optional query `matrix_oid`.
  - Parses SSD to a map { FolderOID: [FormOID,…] } and calls the existing ALS extractor with `ssd_matrix`.
  - Response: `{ status, meta, counts, diff: { missing_in_db, extra_in_db }, missingInDB, extraInDB }`.
- Files: backend/app/api/routes_ssd.py, backend/app/main.py (router included).

Frontend
- New route view with tabs:
  - data_ rocket_frondend/src/views/MatrixReview.vue
- New Pinia store:
  - data_ rocket_frondend/src/stores/matrix.ts
- New split components (Figma-style, Tailwind preserved):
  - data_ rocket_frondend/src/components/matrix/MatrixUpload.vue
  - data_ rocket_frondend/src/components/matrix/MatrixFolders.vue
  - data_ rocket_frondend/src/components/matrix/MatrixCompare.vue
- Router updated to point `/matrix` to `MatrixReview.vue`.
- SSD compare UX per requirements:
  - Upload path does not paste content into the textbox.
  - Preview must be explicitly triggered; shows 10 lines per page with pagination.
  - Pasted JSON/CSV still supported; client-side compare used when no file is uploaded.
  - Export results button outputs `Type,FolderOID,FormOID`.

Notes / Next steps (if desired)
- Optional refactor into dedicated modules per Figma spec:
  - Components: MatrixUpload.vue, MatrixFolders.vue, MatrixCompare.vue under `src/components/matrix/`.
  - Store: `src/stores/matrix.ts` for shared state (alsFile, discovered matrices, folders, selected folders, differences).
  - Router view for Matrix with 3-tabs structure (Upload & Matrix / Folders & Export / Compare SSD) using the existing Tailwind styles.
  - Presently the features live in the existing MatrixView components to minimize scope.

Env
- Uses existing `VITE_API_BASE` for API base URL.
