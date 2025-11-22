<template>
  <div class="rounded-2xl p-4 shadow border border-cyan-100 bg-white" v-if="store.result">
    <h2 class="text-xl font-semibold text-[#0EA5E9] mb-3">Compare with SSD</h2>

    <div class="space-y-5">
      <!-- Step A: paste path -->
      <div>
        <h3 class="text-sm font-medium text-[#0EA5E9] mb-2">Paste SSD JSON/CSV (optional)</h3>
        <textarea v-model="store.ssdText" rows="8" placeholder='{"SVISIT01":["AE","CM"]}' class="w-full rounded-xl border border-cyan-100 p-3 text-sm outline-none focus:ring-2 focus:ring-cyan-200"></textarea>
        <p class="text-xs text-gray-500 mt-1">Upload preview will not copy here; paste is optional.</p>
      </div>

      <!-- Step B: upload path (enabled after ALS extract) -->
      <div>
        <h3 class="text-sm font-medium text-[#0EA5E9] mb-2">Upload SSD File</h3>
        <div class="flex items-center gap-2">
          <label class="btn-primary cursor-pointer">
            <input type="file" accept=".json,.csv,.xlsx" class="hidden" @change="onFile">
            Upload SSD
          </label>
          <span class="text-xs text-gray-600 truncate max-w-[16rem]" v-if="store.ssdFileName">{{ store.ssdFileName }}</span>
          <span class="text-xs text-gray-400" v-else>Supports JSON / CSV / XLSX</span>
          <button v-if="store.ssdFile" class="btn-secondary ml-2" @click="store.previewSSD">Preview</button>
        </div>

        <!-- Preview (10 lines per page) only when explicitly requested -->
        <div v-if="store.ssdPreview.length" class="mt-3 rounded-lg border border-cyan-100">
          <div class="flex items-center justify-between px-3 py-2 text-xs text-gray-600">
            <span>SSD Preview ({{ store.ssdPreview.length }} lines)</span>
            <div class="flex items-center gap-2">
              <button class="btn-chip" @click="store.ssdPage = Math.max(1, store.ssdPage-1)" :disabled="store.ssdPage===1">Prev</button>
              <span>Page {{ store.ssdPage }} / {{ store.ssdTotalPages }}</span>
              <button class="btn-chip" @click="store.ssdPage = Math.min(store.ssdTotalPages, store.ssdPage+1)" :disabled="store.ssdPage===store.ssdTotalPages">Next</button>
            </div>
          </div>
          <pre class="max-h-40 overflow-auto text-xs p-3">{{ store.ssdPreviewSlice.join('\n') }}</pre>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <button class="btn-primary" :disabled="!canCompare" @click="store.compareSSD">Compare</button>
        <button class="btn-secondary" :disabled="!hasDiff" @click="store.exportDiffCsv">Export results</button>
      </div>
    </div>

    <div v-if="hasDiff" class="grid md:grid-cols-2 gap-4 mt-4">
      <div class="rounded-xl border border-cyan-100">
        <div class="p-3 border-b border-cyan-100">
          <h3 class="font-medium text-cyan-700">Missing in DB (should exist)</h3>
        </div>
        <div class="custom-scroll max-h-96 overflow-y-auto p-3">
          <div v-if="isEmpty(store.diff.missing_in_db)" class="text-sm text-gray-500">None</div>
          <div v-else class="space-y-3">
            <div v-for="(forms, foid) in store.diff.missing_in_db" :key="'miss-'+foid" class="">
              <div class="font-mono text-sm">
                {{ foid }}
                <span class="text-gray-500" v-if="folderNamePreferSSD(foid)">— {{ folderNamePreferSSD(foid) }}</span>
              </div>
              <ul class="mt-1 pl-4 list-disc">
                <li v-for="frm in forms" :key="'miss-item-'+foid+'-'+frm" class="text-xs">
                  <span class="font-mono">{{ frm }}</span>
                  <span class="text-gray-600" v-if="formNamePreferSSD(frm)"> — {{ formNamePreferSSD(frm) }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      <div class="rounded-xl border border-cyan-100">
        <div class="p-3 border-b border-cyan-100">
          <h3 class="font-medium text-cyan-700">Extra in DB (not in SSD)</h3>
        </div>
        <div class="custom-scroll max-h-96 overflow-y-auto p-3">
          <div v-if="isEmpty(store.diff.extra_in_db)" class="text-sm text-gray-500">None</div>
          <div v-else class="space-y-3">
            <div v-for="(forms, foid) in store.diff.extra_in_db" :key="'extra-'+foid">
              <div class="font-mono text-sm">
                {{ foid }}
                <span class="text-gray-500" v-if="folderNamePreferALS(foid)">— {{ folderNamePreferALS(foid) }}</span>
              </div>
              <ul class="mt-1 pl-4 list-disc">
                <li v-for="frm in forms" :key="'extra-item-'+foid+'-'+frm" class="text-xs">
                  <span class="font-mono">{{ frm }}</span>
                  <span class="text-gray-600" v-if="formNamePreferALS(frm)"> — {{ formNamePreferALS(frm) }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useMatrixStore } from '../../stores/matrix'
const store = useMatrixStore()
const hasDiff = computed(() => !!store.diff && (!isEmpty(store.diff.missing_in_db) || !isEmpty(store.diff.extra_in_db)))
const canCompare = computed(() => !!store.result && ((store.ssdFile != null) || (store.ssdText.trim().length > 0)))
function isEmpty(obj: any){ return !obj || Object.keys(obj).length === 0 }
function onFile(e: Event){
  const input = e.target as HTMLInputElement
  const file = input.files?.[0] ?? null
  store.ssdFile = file
  store.ssdFileName = file?.name || ''
  // Do not auto-preview or paste into textbox; user must click Preview.
  store.ssdPreview = []
  store.ssdPage = 1
}

// Friendly name resolvers for rendering
const folderNamePreferSSD = (foid: string) => store.ssdFolderNameMap[foid.toUpperCase()] || store.alsFolderNameMap[foid.toUpperCase()] || ''
const formNamePreferSSD   = (frm: string) => store.ssdFormNameMap[frm.toUpperCase()] || store.alsFormNameMap[frm.toUpperCase()] || ''
const folderNamePreferALS = (foid: string) => store.alsFolderNameMap[foid.toUpperCase()] || store.ssdFolderNameMap[foid.toUpperCase()] || ''
const formNamePreferALS   = (frm: string) => store.alsFormNameMap[frm.toUpperCase()] || store.ssdFormNameMap[frm.toUpperCase()] || ''
</script>

<style scoped>
.btn-cyan-solid { @apply px-4 py-2 rounded-xl shadow bg-[#0EA5E9] text-white hover:opacity-90 disabled:opacity-50; }
.btn-cyan-outline { @apply px-4 py-2 rounded-xl shadow border border-cyan-100 hover:bg-cyan-50 disabled:opacity-50; }
.btn-chip { @apply px-3 py-1.5 rounded-lg text-sm border border-cyan-100 hover:bg-cyan-50 disabled:opacity-50; }
/* subtle pretty scrollbar inside cards */
.custom-scroll::-webkit-scrollbar { width: 8px; }
.custom-scroll::-webkit-scrollbar-track { background: #fff0f6; border-radius: 9999px; }
.custom-scroll::-webkit-scrollbar-thumb { background: #7dd3fc; border-radius: 9999px; }
.custom-scroll { scrollbar-width: thin; scrollbar-color: #7dd3fc #ecfeff; }
</style>
