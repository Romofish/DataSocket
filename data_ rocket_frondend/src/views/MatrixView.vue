<template>
  <div class="p-6">
    <!-- Header -->
    <header class="mb-4">
      <h1 class="text-2xl font-semibold text-[#FF66A1]">ALS Matrix • Folder → Forms</h1>
      <p class="text-sm text-gray-500">
        Upload ALS, expand Matrix (no “X”), filter by folder, compare with SSD, and export CSV.
      </p>
    </header>

    <section class="grid gap-4">
      <!-- Upload + SSD -->
      <div class="rounded-2xl p-4 shadow border border-pink-100">
        <label class="block text-sm font-medium mb-2 text-[#FF66A1]">ALS Excel (.xlsx)</label>
        <input type="file" accept=".xlsx" @change="onUpload" class="block" />

        <div class="mt-3 grid md:grid-cols-2 gap-3">
          <div>
            <label class="block text-sm font-medium mb-2 text-[#FF66A1]">Optional SSD JSON</label>
            <textarea v-model="ssdJson" rows="5" placeholder='{"SVISIT01":["AE","CM"]}'
                      class="w-full rounded-xl border border-pink-200 p-3 text-sm outline-none focus:ring-2 focus:ring-pink-300"></textarea>
          </div>
          <div class="flex flex-col">
            <label class="block text-sm font-medium mb-2 text-[#FF66A1]">Actions</label>
            <div class="flex flex-wrap gap-2">
              <button :disabled="loading" @click="submit"
                      class="px-4 py-2 rounded-xl shadow bg-[#FF66A1] text-white hover:opacity-90 disabled:opacity-50">
                {{ loading ? "Processing..." : "Extract Matrix" }}
              </button>
              <button :disabled="!result" @click="exportCsv"
                      class="px-4 py-2 rounded-xl shadow border border-pink-200 hover:bg-pink-50">
                Export CSV
              </button>
            </div>
            <p class="text-xs text-gray-500 mt-2">
              CSV columns: FolderName, FolderOID, formname, FormOID
            </p>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div v-if="result" class="rounded-2xl p-4 shadow border border-pink-100">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-xl font-semibold text-[#FF66A1]">Folder Filter</h2>
          <div class="flex items-center gap-2">
            <button @click="selectAll" class="px-3 py-1.5 rounded-lg text-sm border border-pink-200 hover:bg-pink-50">Select all</button>
            <button @click="clearAll" class="px-3 py-1.5 rounded-lg text-sm border border-pink-200 hover:bg-pink-50">Clear all</button>
            <button @click="saveSelection" class="px-3 py-1.5 rounded-lg text-sm border border-pink-200 hover:bg-pink-50">Save selection</button>
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
                <!-- (1) Show FormName along with FormOID -->
                <span class="font-mono">{{ fm.formOID }}</span>
                <span v-if="fm.formname" class="text-gray-600"> — {{ fm.formname }}</span>
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

const fileRef = ref<File | null>(null)
const ssdJson = ref<string>("")
const result = ref<any | null>(null)
const loading = ref(false)

/** Folder selection (filter) */
const selectedFolders = ref<Set<string>>(new Set())
const autoRemember = ref<boolean>(true)

function onUpload(e: Event) {
  const input = e.target as HTMLInputElement
  fileRef.value = input.files?.[0] ?? null
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
    // Only restore folders that still exist in current result
    const folderOIDs = new Set(allFolders.value.map(f => f.folderOID))
    for (const oid of (parsed.selected || [])) {
      if (folderOIDs.has(oid)) validSet.add(oid)
    }
    if (validSet.size) selectedFolders.value = validSet
  } catch {}
}

/** Fetch/parse ALS */
async function submit() {
  if (!fileRef.value) return
  loading.value = true
  try {
    const fd = new FormData()
    fd.append("als_file", fileRef.value)
    if (ssdJson.value.trim()) {
      fd.append("ssd_folder_forms", new Blob([ssdJson.value], { type: "application/json" }))
    }
    const res = await fetch(import.meta.env.VITE_API_BASE + "/als/matrix", {
      method: "POST",
      body: fd
    })
    if (!res.ok) throw new Error(await res.text())
    result.value = await res.json()

    // Initialize selection to all folders on fresh load
    const all = result.value?.folders?.map((f: any) => f.folderOID) ?? []
    selectedFolders.value = new Set(all)

    // Auto-restore prior selection (if enabled and matches current data)
    if (autoRemember.value) {
      // Wait one tick to compute allFolders
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

/** CSV Export: FolderName, FolderOID, FormName, FormOID (one form per row) */
function exportCsv() {
  if (!result.value) return
  const rows: string[] = []
  const header = ["FolderName","FolderOID","FormName","FormOID"]
  rows.push(header.join(","))

  const folders = visibleFolders.value // export only visible folders
  for (const f of folders) {
    const folderName = (f.folderName ?? "").toString().replaceAll('"','""')
    const folderOID  = (f.folderOID  ?? "").toString().replaceAll('"','""')
    for (const fm of (f.forms ?? [])) {
      const formname = (fm.formname ?? "").toString().replaceAll('"','""')
      const formOID  = (fm.formOID  ?? "").toString().replaceAll('"','""')
      // Wrap in quotes to be safe with commas
      rows.push([`"${folderName}"`,`"${folderOID}"`,`"${formname}"`,`"${formOID}"`].join(","))
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
/* Tech-Soft Pink accents kept lightweight; Tailwind handles most styling */
</style>
