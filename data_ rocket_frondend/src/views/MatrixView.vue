<!-- Only the CHANGED/NEW parts are shown; replace your current component with this full file if easier -->

<template>
  <div class="p-6">
    <!-- Header -->
    <header class="mb-4">
      <h1 class="text-2xl font-semibold text-[#FF66A1]">ALS Matrix • Folder → Forms</h1>
      <p class="text-sm text-gray-500">
        Upload ALS, backend discovers Matrices (MASTERDASHBOARD preferred), pick one, expand (no “X”), filter by folder, compare with SSD, and export CSV.
      </p>
    </header>

    <section class="grid gap-4">
      <!-- Upload + Matrix Picker + SSD + Actions -->
      <div class="rounded-2xl p-4 shadow border border-pink-100">
        <div class="grid lg:grid-cols-3 gap-4">
          <!-- File input (custom-styled) -->
          <div>
            <label class="block text-sm font-medium mb-2 text-[#FF66A1]">ALS Excel (.xlsx)</label>
            <div class="flex items-center gap-3">
              <label class="btn-pink-outline cursor-pointer">
                <input
                  ref="fileEl"
                  type="file"
                  accept=".xlsx"
                  class="hidden"
                  @change="onUpload"
                />
                Choose a file
              </label>
              <span class="text-xs text-gray-600 truncate max-w-[16rem]" v-if="alsFileName">{{ alsFileName }}</span>
              <span class="text-xs text-gray-400" v-else>No file chosen</span>
            </div>

            <!-- Matrix picker: now ALWAYS visible once a file is chosen -->
            <div v-if="alsFile" class="mt-3">
              <div class="flex items-center justify-between">
                <label class="block text-sm font-medium text-[#FF66A1]">Select Matrix</label>
                <button
                  :disabled="loading || !alsFile"
                  @click="discover"
                  class="btn-chip"
                  title="Re-scan matrices from this ALS"
                >
                  {{ loading && discoverPhase ? "Discovering..." : "Discover Matrices" }}
                </button>
              </div>

              <div v-if="availableMatrices.length > 0" class="mt-2">
                <select v-model="selectedMatrixOID" class="select-pink">
                  <option v-for="m in availableMatrices" :key="m.matrixOID" :value="m.matrixOID">
                    {{ m.matrixOID }} (sheet: {{ m.sheet }})
                  </option>
                </select>
                <p class="text-xs text-gray-500 mt-1">
                  Default preference: MASTERDASHBOARD → Matrix
                </p>
              </div>

              <div v-else class="mt-2 text-xs text-gray-500">
                No matrices discovered yet. Click <span class="font-medium">Discover Matrices</span>.
              </div>
            </div>
          </div>

          <!-- SSD input -->
          <div>
            <label class="block text-sm font-medium mb-2 text-[#FF66A1]">Optional SSD JSON</label>
            <textarea
              v-model="ssdJson"
              rows="6"
              placeholder='{"SVISIT01":["AE","CM"]}'
              class="w-full rounded-xl border border-pink-200 p-3 text-sm outline-none focus:ring-2 focus:ring-pink-300"
            ></textarea>
          </div>

          <!-- Actions -->
          <div>
            <label class="block text-sm font-medium mb-2 text-[#FF66A1]">Actions</label>
            <div class="flex flex-wrap gap-2">
              <button :disabled="loading || !alsFile"
                      @click="submit"
                      class="btn-pink-solid">
                {{ loading && !discoverPhase ? "Processing..." : "Extract Matrix" }}
              </button>

              <button :disabled="!result" @click="exportCsv" class="btn-pink-outline">
                Export CSV
              </button>
            </div>
            <p class="text-xs text-gray-500 mt-2">
              CSV columns: FolderName, FolderOID, FormName, FormOID
            </p>

            <!-- Chosen meta -->
            <div v-if="result?.meta" class="mt-3 text-xs text-gray-600">
              <div>Chosen matrixOID: <span class="font-mono">{{ result.meta.matrixOID }}</span></div>
              <div>Worksheet: <span class="font-mono">{{ result.meta.sheet }}</span></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div v-if="result" class="rounded-2xl p-4 shadow border border-pink-100">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-xl font-semibold text-[#FF66A1]">Folder Filter</h2>
          <div class="flex items-center gap-2">
            <button @click="selectAll" class="btn-chip">Select all</button>
            <button @click="clearAll" class="btn-chip">Clear all</button>
            <button @click="saveSelection" class="btn-chip">Save selection</button>
            <label class="ml-2 inline-flex items-center gap-2 text-sm">
              <input type="checkbox" v-model="autoRemember" />
              Auto-remember
            </label>
          </div>
        </div>

        <!-- Folder chips -->
        <div class="flex flex-wrap gap-2">
          <label v-for="f in allFolders" :key="'chip-'+f.folderOID"
                 class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border cursor-pointer"
                 :class="selectedFolders.has(f.folderOID) ? 'bg-pink-50 border-pink-300' : 'border-pink-200 hover:bg-pink-50'">
            <input type="checkbox"
                   :value="f.folderOID"
                   :checked="selectedFolders.has(f.folderOID)"
                   @change="toggleFolder(f.folderOID)" />
            <span class="text-sm">
              <span class="font-mono">{{ f.folderOID }}</span>
              <span v-if="f.folderName" class="text-gray-500"> — {{ f.folderName }}</span>
            </span>
          </label>
        </div>
      </div>

      <!-- Expanded Matrix -->
      <div v-if="result" class="rounded-2xl p-4 shadow border border-pink-100">
        <h2 class="text-xl font-semibold text-[#FF66A1] mb-3">Expanded Matrix (Filtered)</h2>

        <div v-if="visibleFolders.length === 0" class="text-sm text-gray-500">
          No folders selected.
        </div>

        <div class="grid gap-3">
          <div v-for="f in visibleFolders" :key="f.folderOID"
               class="rounded-xl border border-pink-200 p-3">
            <div class="flex items-center justify-between">
              <div>
                <div class="font-medium">{{ f.folderOID }}</div>
                <div class="text-xs text-gray-500" v-if="f.folderName">{{ f.folderName }}</div>
              </div>
              <span class="text-xs px-2 py-1 rounded-full bg-pink-50 border border-pink-200">
                {{ f.forms.length }} forms
              </span>
            </div>

            <ul class="mt-2 pl-4 list-disc">
              <li v-for="fm in f.forms" :key="fm.formOID" class="text-sm">
                <span class="font-mono">{{ fm.formOID }}</span>
                <span v-if="fm.formName" class="text-gray-600"> — {{ fm.formName }}</span>
                <span v-else class="text-gray-400"> — (no name)</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Diff -->
      <div v-if="result && result.diff" class="rounded-2xl p-4 shadow border border-pink-100">
        <h2 class="text-xl font-semibold text-[#FF66A1] mb-3">SSD vs ALS Differences</h2>
        <div class="grid md:grid-cols-2 gap-4">
          <div class="rounded-xl border border-pink-200 p-3">
            <h3 class="font-medium text-pink-600 mb-2">Missing in DB (should exist)</h3>
            <div v-if="isEmpty(result.diff.missing_in_db)" class="text-sm text-gray-500">None</div>
            <div v-else class="space-y-2">
              <div v-for="(forms, foid) in result.diff.missing_in_db" :key="'miss-'+foid">
                <div class="font-mono text-sm">{{ foid }}</div>
                <div class="text-xs text-gray-600">{{ forms.join(', ') }}</div>
              </div>
            </div>
          </div>
          <div class="rounded-xl border border-pink-200 p-3">
            <h3 class="font-medium text-pink-600 mb-2">Extra in DB (not in SSD)</h3>
            <div v-if="isEmpty(result.diff.extra_in_db)" class="text-sm text-gray-500">None</div>
            <div v-else class="space-y-2">
              <div v-for="(forms, foid) in result.diff.extra_in_db" :key="'extra-'+foid">
                <div class="font-mono text-sm">{{ foid }}</div>
                <div class="text-xs text-gray-600">{{ forms.join(', ') }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue"

const fileEl = ref<HTMLInputElement | null>(null)
const alsFile = ref<File | null>(null)
const alsFileName = ref<string>("")
const ssdJson = ref<string>("")
const result = ref<any | null>(null)
const loading = ref(false)
const discoverPhase = ref(false)

/** Matrix discovery */
type MatrixItem = { matrixOID: string; sheet: string }
const availableMatrices = ref<MatrixItem[]>([])
const selectedMatrixOID = ref<string | null>(null)

/** Folder selection (filter) */
const selectedFolders = ref<Set<string>>(new Set())
const autoRemember = ref<boolean>(true)

/** On file choose: store + AUTO-DISCOVER matrices */
function onUpload(e: Event) {
  const input = e.target as HTMLInputElement
  alsFile.value = input.files?.[0] ?? null
  alsFileName.value = alsFile.value?.name ?? ""
  result.value = null
  availableMatrices.value = []
  selectedMatrixOID.value = null
  if (alsFile.value) {
    // auto-discover to make the selector appear without extra clicks
    setTimeout(() => discover(), 0)
  }
}

/** Helpers */
function isEmpty(obj: any) {
  return !obj || Object.keys(obj).length === 0
}

/** Load/Save selection to localStorage */
const LS_KEY = "als-matrix-folder-selection"

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
    for (const oid of (parsed.selected || [])) {
      if (folderOIDs.has(oid)) validSet.add(oid)
    }
    if (validSet.size) selectedFolders.value = validSet
  } catch {}
}

/** Discover matrices (backend) */
async function discover() {
  if (!alsFile.value) return
  loading.value = true
  discoverPhase.value = true
  try {
    const fd = new FormData()
    fd.append("als_file", alsFile.value)
    const res = await fetch(import.meta.env.VITE_API_BASE + "/als/matrices", {
      method: "POST",
      body: fd
    })
    if (!res.ok) throw new Error(await res.text())
    const data = await res.json()
    availableMatrices.value = data.availableMatrices || []
    // Preferred default is MASTERDASHBOARD; fall back to first item
    const preferred = "MASTERDASHBOARD"
    const hasPreferred = availableMatrices.value.find(m => m.matrixOID.toLowerCase() === preferred.toLowerCase())
    selectedMatrixOID.value = (hasPreferred?.matrixOID) || (availableMatrices.value[0]?.matrixOID) || null
  } catch (err) {
    alert("Discovery failed: " + err)
  } finally {
    loading.value = false
    discoverPhase.value = false
  }
}

/** Extract/parse ALS with selected matrix_oid */
async function submit() {
  if (!alsFile.value) return
  // guard: ensure matrix chosen if list exists
  if (availableMatrices.value.length > 0 && !selectedMatrixOID.value) {
    alert("Please select a Matrix to proceed.")
    return
  }
  loading.value = true
  discoverPhase.value = false
  try {
    const fd = new FormData()
    fd.append("als_file", alsFile.value)
    if (ssdJson.value.trim()) {
      fd.append("ssd_folder_forms", new Blob([ssdJson.value], { type: "application/json" }))
    }
    const q = selectedMatrixOID.value ? ("?matrix_oid=" + encodeURIComponent(selectedMatrixOID.value)) : ""
    const res = await fetch(import.meta.env.VITE_API_BASE + "/als/matrix" + q, {
      method: "POST",
      body: fd
    })
    if (!res.ok) throw new Error(await res.text())
    result.value = await res.json()

    // If backend returns meta.availableMatrices, keep it for the selector (extra safety)
    if (result.value?.meta?.availableMatrices?.length) {
      availableMatrices.value = result.value.meta.availableMatrices
      if (!selectedMatrixOID.value) {
        selectedMatrixOID.value = result.value.meta.matrixOID || null
      }
    }

    // Initialize folder selection
    const all = result.value?.folders?.map((f: any) => f.folderOID) ?? []
    selectedFolders.value = new Set(all)

    if (autoRemember.value) {
      setTimeout(() => restoreSelection(), 0)
    }
  } catch (err) {
    alert("Upload/parse failed: " + err)
  } finally {
    loading.value = false
  }
}

/** Derived lists */
const allFolders = computed(() => {
  return (result.value?.folders ?? []) as Array<{folderOID: string; folderName?: string; forms: any[]}>
})

const visibleFolders = computed(() => {
  const set = selectedFolders.value
  return allFolders.value.filter(f => set.has(f.folderOID))
})

/** Selection operations */
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

/** CSV Export */
function exportCsv() {
  if (!result.value) return
  const rows: string[] = []
  const header = ["FolderName","FolderOID","FormName","FormOID"]
  rows.push(header.join(","))
  const folders = visibleFolders.value
  for (const f of folders) {
    const folderName = (f.folderName ?? "").toString().replaceAll('"','""')
    const folderOID  = (f.folderOID  ?? "").toString().replaceAll('"','""')
    for (const fm of (f.forms ?? [])) {
      const formName = (fm.formName ?? "").toString().replaceAll('"','""')
      const formOID  = (fm.formOID  ?? "").toString().replaceAll('"','""')
      rows.push([`"${folderName}"`,`"${folderOID}"`,`"${formName}"`,`"${formOID}"`].join(","))
    }
  }
  const blob = new Blob([rows.join("\n")], { type: "text/csv;charset=utf-8" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = "ALS_Matrix_FolderForms.csv"
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

/** Persist auto-remember toggle */
watch(autoRemember, (v) => {
  if (v) saveSelection()
})
</script>

<style scoped>
/* ========= Tech-Soft Pink UI helpers ========= */
.btn-pink-solid {
  @apply px-4 py-2 rounded-xl shadow bg-[#FF66A1] text-white hover:opacity-90 disabled:opacity-50;
}
.btn-pink-outline {
  @apply px-4 py-2 rounded-xl shadow border border-pink-200 hover:bg-pink-50 disabled:opacity-50;
}
.btn-chip {
  @apply px-3 py-1.5 rounded-lg text-sm border border-pink-200 hover:bg-pink-50 disabled:opacity-50;
}
.select-pink {
  @apply w-full rounded-xl border border-pink-200 p-2 text-sm outline-none focus:ring-2 focus:ring-pink-300 bg-white;
}
</style>
