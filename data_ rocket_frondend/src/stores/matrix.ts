/*
  useMatrixStore
  Centralized state for Matrix Review: ALS upload, discovery, extraction,
  folder selection, SSD compare (paste or upload with backend), and CSV exports.
*/
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as XLSX from 'xlsx'

export type MatrixItem = { matrixOID: string; sheet: string }
export type DiffMap = Record<string, string[]>

export const useMatrixStore = defineStore('matrix', () => {
  // ALS & Matrix
  const alsFile = ref<File | null>(null)
  const alsFileName = ref('')
  const availableMatrices = ref<MatrixItem[]>([])
  const selectedMatrixOID = ref<string | null>(null)
  const loading = ref(false)
  const result = ref<any | null>(null)

  // Folder selection
  const selectedFolders = ref<Set<string>>(new Set())
  const autoRemember = ref(true)
  const LS_KEY = 'als-matrix-folder-selection'

  // SSD
  const ssdText = ref('')
  const ssdFile = ref<File | null>(null)
  const ssdFileName = ref('')
  const ssdPreview = ref<string[]>([])
  const ssdPage = ref(1)
  const diff = ref<{missing_in_db: DiffMap; extra_in_db: DiffMap}>({ missing_in_db: {}, extra_in_db: {} })
  // Name maps for friendly display
  const alsFolderNameMap = ref<Record<string,string>>({})
  const alsFormNameMap = ref<Record<string,string>>({})
  const ssdFolderNameMap = ref<Record<string,string>>({})
  const ssdFormNameMap = ref<Record<string,string>>({})

  // Derived
  const allFolders = computed(() => (result.value?.folders ?? []) as Array<{folderOID: string; folderName?: string; forms: any[]}>)
  const visibleFolders = computed(() => {
    const set = selectedFolders.value
    return allFolders.value.filter(f => set.has(f.folderOID))
  })
  const ssdTotalPages = computed(() => Math.max(1, Math.ceil(ssdPreview.value.length / 10)))
  const ssdPreviewSlice = computed(() => {
    const start = (ssdPage.value - 1) * 10
    return ssdPreview.value.slice(start, start + 10)
  })

  // Helpers
  function setALS(file: File | null) {
    alsFile.value = file
    alsFileName.value = file?.name || ''
    result.value = null
    availableMatrices.value = []
    selectedMatrixOID.value = null
    selectedFolders.value = new Set()
  }

  async function discoverMatrices() {
    if (!alsFile.value) return
    loading.value = true
    try {
      const fd = new FormData()
      fd.append('als_file', alsFile.value)
      const res = await fetch(import.meta.env.VITE_API_BASE + '/als/matrices', { method: 'POST', body: fd })
      if (!res.ok) throw new Error(await res.text())
      const data = await res.json()
      availableMatrices.value = data.availableMatrices || []
      const preferred = 'MASTERDASHBOARD'
      const hasPreferred = availableMatrices.value.find(m => m.matrixOID.toLowerCase() === preferred.toLowerCase())
      selectedMatrixOID.value = (hasPreferred?.matrixOID) || (availableMatrices.value[0]?.matrixOID) || null
    } finally {
      loading.value = false
    }
  }

  async function extractMatrix() {
    if (!alsFile.value) return
    loading.value = true
    try {
      const fd = new FormData()
      fd.append('als_file', alsFile.value)
      const q = selectedMatrixOID.value ? ('?matrix_oid=' + encodeURIComponent(selectedMatrixOID.value)) : ''
      const res = await fetch(import.meta.env.VITE_API_BASE + '/als/matrix' + q, { method: 'POST', body: fd })
      if (!res.ok) throw new Error(await res.text())
      result.value = await res.json()
      const all = result.value?.folders?.map((f: any) => f.folderOID) ?? []
      selectedFolders.value = new Set(all)
      if (autoRemember.value) restoreSelection()
      // clear previous diff
      diff.value = { missing_in_db: {}, extra_in_db: {} }
      rebuildAlsNameMaps()
    } finally {
      loading.value = false
    }
  }

  function toggleFolder(foid: string) {
    const next = new Set(selectedFolders.value)
    if (next.has(foid)) next.delete(foid); else next.add(foid)
    selectedFolders.value = next
    if (autoRemember.value) saveSelection()
  }
  function selectAll() {
    selectedFolders.value = new Set(allFolders.value.map(f => f.folderOID))
    if (autoRemember.value) saveSelection()
  }
  function clearAll() {
    selectedFolders.value = new Set()
    if (autoRemember.value) saveSelection()
  }

  function saveSelection() {
    const arr = Array.from(selectedFolders.value)
    localStorage.setItem(LS_KEY, JSON.stringify({ selected: arr, auto: autoRemember.value }))
  }
  function restoreSelection() {
    try {
      const raw = localStorage.getItem(LS_KEY)
      if (!raw) return
      const parsed = JSON.parse(raw)
      autoRemember.value = !!parsed.auto
      const validSet = new Set<string>()
      const folderOIDs = new Set(allFolders.value.map(f => f.folderOID))
      for (const oid of (parsed.selected || [])) if (folderOIDs.has(oid)) validSet.add(oid)
      if (validSet.size) selectedFolders.value = validSet
    } catch {}
  }

  // SSD utilities
  function parseCsv(text: string): Array<Record<string, string>> {
    const lines = text.split(/\r?\n/).filter(l => l.trim().length)
    if (!lines.length) return []
    const split = (line: string) => {
      const out: string[] = []
      let cur = ''
      let inQ = false
      for (let i=0;i<line.length;i++){
        const ch = line[i]
        if (ch === '"'){
          if (inQ && line[i+1] === '"'){ cur += '"'; i++; continue }
          inQ = !inQ; continue
        }
        if (ch === ',' && !inQ){ out.push(cur); cur=''; continue }
        cur += ch
      }
      out.push(cur)
      return out
    }
    const headers = split(lines[0]).map(h => h.trim())
    const rows: Array<Record<string,string>> = []
    for (let i=1;i<lines.length;i++){
      const cols = split(lines[i])
      if (cols.every(c => c.trim() === '')) continue
      const obj: Record<string,string> = {}
      headers.forEach((h, idx) => obj[h] = (cols[idx] ?? '').trim())
      rows.push(obj)
    }
    return rows
  }
  function mapFromRows(rows: Array<Record<string,string>>): DiffMap {
    const findKey = (obj: Record<string,string>, opts: string[]) => {
      const keys = Object.keys(obj)
      for (const o of opts){
        const k = keys.find(k => k.trim().toLowerCase() === o.trim().toLowerCase())
        if (k) return k
      }
      return null
    }
    const map: Record<string, Set<string>> = {}
    for (const r of rows){
      const foK = findKey(r, ['FolderOID','Folder OID'])
      const fmK = findKey(r, ['OID','FormOID','Form OID'])
      if (!foK || !fmK) continue
      const fo = (r[foK]||'').trim().toUpperCase(); const fm = (r[fmK]||'').trim().toUpperCase()
      if (!fo || !fm) continue
      if (!map[fo]) map[fo] = new Set()
      map[fo].add(fm)
    }
    const out: DiffMap = {}
    for (const [fo, set] of Object.entries(map)) out[fo] = Array.from(set)
    return out
  }
  function normalizeSsdJson(text: string): DiffMap | null {
    try{
      const parsed = JSON.parse(text)
      if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)){
        const out: DiffMap = {}
        for (const [fo, arr] of Object.entries(parsed as Record<string, any>)){
          if (!Array.isArray(arr)) continue
          out[fo] = Array.from(new Set(arr.map(x => String(x))))
        }
        return out
      }
      if (Array.isArray(parsed)) return mapFromRows(parsed as Array<Record<string,string>>)
    }catch{ return null }
    return null
  }

  function rebuildAlsNameMaps(){
    const fMap: Record<string,string> = {}
    const fmMap: Record<string,string> = {}
    for (const f of (result.value?.folders || [])){
      fMap[String(f.folderOID).toUpperCase()] = f.folderName || ''
      for (const fm of (f.forms || [])){
        fmMap[String(fm.formOID).toUpperCase()] = fm.formName || ''
      }
    }
    alsFolderNameMap.value = fMap
    alsFormNameMap.value = fmMap
  }

  function buildSsdNameMapsFromRows(rows: Array<Record<string,string>>){
    const folderMap: Record<string,string> = {}
    const formMap: Record<string,string> = {}
    const findKey = (o:Record<string,string>, opts:string[])=>opts.find(k=>Object.keys(o).some(x=>x.trim().toLowerCase()===k.trim().toLowerCase()))
    for (const r of rows){
      const foK = findKey(r, ['FolderOID','Folder OID']); const fmK = findKey(r, ['OID','FormOID','Form OID'])
      const fnK = findKey(r, ['FolderName','Folder Name']); const nmK = findKey(r, ['FormName','Form Name'])
      if (foK && fmK){
        const fo = (r[foK]||'').trim().toUpperCase(); const fm = (r[fmK]||'').trim().toUpperCase()
        if (fo) folderMap[fo] = (fnK? r[fnK] : '') || ''
        if (fm) formMap[fm] = (nmK? r[nmK] : '') || ''
      }
    }
    ssdFolderNameMap.value = folderMap
    ssdFormNameMap.value = formMap
  }

  async function previewSSD() {
    if (!ssdFile.value) return
    ssdPreview.value = []
    ssdPage.value = 1
    const ext = ssdFile.value.name.split('.').pop()?.toLowerCase()
    if (ext === 'xlsx'){
      const buf = await ssdFile.value.arrayBuffer()
      const wb = XLSX.read(buf, { type: 'array' })
      const first = wb.SheetNames[0]
      const csv = XLSX.utils.sheet_to_csv(wb.Sheets[first]!)
      ssdPreview.value = csv.split(/\r?\n/).slice(0, 500)
    } else {
      const txt = await ssdFile.value.text()
      ssdPreview.value = txt.split(/\r?\n/).slice(0, 500)
    }
  }

  async function compareSSD() {
    if (!result.value) return
    // Use backend for file upload; text path stays client-side
    if (ssdFile.value){
      const fd = new FormData()
      if (!alsFile.value) return
      fd.append('als_file', alsFile.value)
      fd.append('ssd_file', ssdFile.value)
      const q = selectedMatrixOID.value ? ('?matrix_oid=' + encodeURIComponent(selectedMatrixOID.value)) : ''
      const res = await fetch(import.meta.env.VITE_API_BASE + '/ssd/compare' + q, { method: 'POST', body: fd })
      if (!res.ok) throw new Error(await res.text())
      const data = await res.json()
      diff.value = data.diff || { missing_in_db: {}, extra_in_db: {} }
      // also parse the upload locally to capture names for display
      try{
        const ext = ssdFile.value.name.split('.').pop()?.toLowerCase()
        if (ext === 'xlsx'){
          const buf = await ssdFile.value.arrayBuffer(); const wb = XLSX.read(buf, { type: 'array' })
          const first = wb.SheetNames[0]
          const rows = XLSX.utils.sheet_to_json<Record<string,string>>(wb.Sheets[first]!, { defval: '' })
          buildSsdNameMapsFromRows(rows)
        } else if (ext === 'csv'){
          buildSsdNameMapsFromRows(parseCsv(await ssdFile.value.text()))
        } else if (ext === 'json'){
          const obj = JSON.parse(await ssdFile.value.text())
          if (Array.isArray(obj)) buildSsdNameMapsFromRows(obj)
          else { ssdFolderNameMap.value = {}; ssdFormNameMap.value = {} }
        }
      } catch { ssdFolderNameMap.value = {}; ssdFormNameMap.value = {} }
      return
    }
    // client-side compare using pasted text
    const ssdMap = ssdText.value.trim() ? (normalizeSsdJson(ssdText.value) ?? mapFromRows(parseCsv(ssdText.value))) : null
    if (!ssdMap) return
    const alsMap: Record<string, Set<string>> = {}
    for (const f of (result.value.folders || [])) alsMap[String(f.folderOID).toUpperCase()] = new Set((f.forms||[]).map((x: any) => String(x.formOID).toUpperCase()))
    const missing_in_db: DiffMap = {}
    const extra_in_db: DiffMap = {}
    for (const [fo, forms] of Object.entries(ssdMap)){
      const als = alsMap[fo] || new Set<string>()
      const miss = Array.from(new Set(forms.map(x => x.toUpperCase()))).filter(frm => !als.has(frm)).sort()
      if (miss.length) missing_in_db[fo] = miss
    }
    for (const [fo, alsSet] of Object.entries(alsMap)){
      const ssdSet = new Set((ssdMap[fo] || []).map(x => x.toUpperCase()))
      const extra = Array.from(alsSet).filter(frm => !ssdSet.has(String(frm).toUpperCase())).sort()
      if (extra.length) extra_in_db[fo] = extra
    }
    diff.value = { missing_in_db, extra_in_db }
    // For pasted path, also try to build SSD name maps from text
    try{
      const rows = parseCsv(ssdText.value)
      if (rows.length) buildSsdNameMapsFromRows(rows)
      else { ssdFolderNameMap.value = {}; ssdFormNameMap.value = {} }
    } catch { ssdFolderNameMap.value = {}; ssdFormNameMap.value = {} }
  }

  function exportMatrixCsv() {
    if (!result.value) return
    const rows: string[] = []
    rows.push(['FolderName','FolderOID','FormName','FormOID'].join(','))
    for (const f of visibleFolders.value){
      const folderName = (f.folderName ?? '').toString().replaceAll('"','""')
      const folderOID  = (f.folderOID  ?? '').toString().replaceAll('"','""')
      for (const fm of (f.forms ?? [])){
        const formName = (fm.formName ?? '').toString().replaceAll('"','""')
        const formOID  = (fm.formOID  ?? '').toString().replaceAll('"','""')
        rows.push([`"${folderName}"`,`"${folderOID}"`,`"${formName}"`,`"${formOID}"`].join(','))
      }
    }
    const blob = new Blob([rows.join('\n')], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = 'ALS_Matrix_FolderForms.csv'
    document.body.appendChild(a); a.click(); document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  async function exportDiffCsv(){
    if (!diff.value) return
    const rows: string[] = []
    // Build name maps from ALS
    const alsFolderName = new Map<string,string>(Object.entries(alsFolderNameMap.value))
    const alsFormName = new Map<string,string>(Object.entries(alsFormNameMap.value))
    // Build SSD name maps (attempt from file or pasted text)
    const ssdRows: Array<Record<string,string>> = []
    try{
      if (ssdFile.value){
        const ext = ssdFile.value.name.split('.').pop()?.toLowerCase()
        if (ext === 'xlsx'){
          const buf = await ssdFile.value.arrayBuffer(); const wb = XLSX.read(buf, { type: 'array' })
          const first = wb.SheetNames[0]
          ssdRows.push(...XLSX.utils.sheet_to_json<Record<string,string>>(wb.Sheets[first]!, { defval: '' }))
        } else if (ext === 'csv'){
          ssdRows.push(...parseCsv(await ssdFile.value.text()))
        } else if (ext === 'json'){
          const obj = JSON.parse(await ssdFile.value.text())
          if (Array.isArray(obj)) ssdRows.push(...obj)
        }
      } else if (ssdText.value.trim()){
        const parsed = normalizeSsdJson(ssdText.value)
        if (!parsed){
          // best-effort parse as rows
          ssdRows.push(...parseCsv(ssdText.value))
        }
      }
    } catch {}
    const findKey = (o:Record<string,string>, opts:string[])=>opts.find(k=>Object.keys(o).some(x=>x.trim().toLowerCase()===k.trim().toLowerCase()))
    const ssdFolderName = new Map<string,string>(Object.entries(ssdFolderNameMap.value))
    const ssdFormName = new Map<string,string>(Object.entries(ssdFormNameMap.value))

    // Header per request
    rows.push(['Type','FolderName','FolderOID','FormName','FormOID','Source','Comment'].join(','))
    const emitRows = (type: 'Missing'|'Extra', obj: DiffMap) => {
      for (const [fo, arr] of Object.entries(obj)){
        for (const frm of arr){
          const formUpper = String(frm).toUpperCase()
          const folderName = (type==='Missing' ? (ssdFolderName.get(fo) ?? alsFolderName.get(fo) ?? '') : (alsFolderName.get(fo) ?? ssdFolderName.get(fo) ?? ''))
          const formName   = (type==='Missing' ? (ssdFormName.get(formUpper) ?? alsFormName.get(formUpper) ?? '') : (alsFormName.get(formUpper) ?? ssdFormName.get(formUpper) ?? ''))
          const source = (type==='Missing' ? 'SSD' : 'ALS')
          const comment = (type==='Missing' ? 'Present in SSD only' : 'Present in ALS only')
          rows.push([type, `"${(folderName||'').replaceAll('"','""')}"`, `"${fo}"`, `"${(formName||'').replaceAll('"','""')}"`, `"${formUpper}"`, source, `"${comment}"`].join(','))
        }
      }
    }
    emitRows('Missing', diff.value.missing_in_db || {})
    emitRows('Extra',   diff.value.extra_in_db || {})
    const blob = new Blob([rows.join('\n')], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = 'SSD_Compare_Results_Detailed.csv'
    document.body.appendChild(a); a.click(); document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return {
    // state
    alsFile, alsFileName, availableMatrices, selectedMatrixOID, loading, result,
    selectedFolders, autoRemember, ssdText, ssdFile, ssdFileName, ssdPreview, ssdPage, diff,
    // derived
    allFolders, visibleFolders, ssdTotalPages, ssdPreviewSlice,
    // actions
    setALS, discoverMatrices, extractMatrix,
    toggleFolder, selectAll, clearAll, saveSelection, restoreSelection,
    parseCsv, mapFromRows, normalizeSsdJson, previewSSD, compareSSD,
    exportMatrixCsv, exportDiffCsv,
    // name resolvers for components
    alsFolderNameMap, alsFormNameMap, ssdFolderNameMap, ssdFormNameMap,
  }
})
