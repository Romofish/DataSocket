<template>
  <div class="rounded-2xl p-4 shadow border border-pink-100" v-if="store.result">
    <h2 class="text-xl font-semibold text-[#FF66A1] mb-3">Compare with SSD</h2>

    <div class="grid lg:grid-cols-2 gap-4">
      <!-- Paste area -->
      <div>
        <label class="block text-sm font-medium mb-2 text-[#FF66A1]">SSD Data (Paste Only)</label>
        <textarea v-model="store.ssdText" rows="10" placeholder='{"SVISIT01":["AE","CM"]}' class="w-full rounded-xl border border-pink-200 p-3 text-sm outline-none focus:ring-2 focus:ring-pink-300"></textarea>
        <p class="text-xs text-gray-500 mt-1">Enter JSON mapping or rows; upload preview will not be copied here.</p>
      </div>

      <!-- Upload + Preview controls -->
      <div>
        <label class="block text-sm font-medium mb-2 text-[#FF66A1]">Upload SSD File</label>
        <div class="flex items-center gap-2">
          <label class="btn-pink-outline cursor-pointer">
            <input type="file" accept=".json,.csv,.xlsx" class="hidden" @change="onFile">
            Upload
          </label>
          <span class="text-xs text-gray-600 truncate max-w-[16rem]" v-if="store.ssdFileName">{{ store.ssdFileName }}</span>
          <span class="text-xs text-gray-400" v-else>Supports JSON / CSV / XLSX</span>
          <button class="btn-chip ml-2" :disabled="!store.ssdFile" @click="store.previewSSD">Preview</button>
        </div>

        <!-- Preview (10 lines per page) shown only after clicking Preview -->
        <div v-if="store.ssdPreview.length" class="mt-3 rounded-lg border border-pink-200">
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
    </div>

    <div class="flex items-center gap-2 mt-4">
      <button class="btn-pink-solid" :disabled="!store.result" @click="store.compareSSD">Compare</button>
      <button class="btn-pink-outline" :disabled="!hasDiff" @click="store.exportDiffCsv">Export results</button>
    </div>

    <div v-if="hasDiff" class="grid md:grid-cols-2 gap-4 mt-4">
      <div class="rounded-xl border border-pink-200">
        <div class="p-3 border-b border-pink-100">
          <h3 class="font-medium text-pink-600">Missing in DB (should exist)</h3>
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
      <div class="rounded-xl border border-pink-200">
        <div class="p-3 border-b border-pink-100">
          <h3 class="font-medium text-pink-600">Extra in DB (not in SSD)</h3>
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
.btn-pink-solid { @apply px-4 py-2 rounded-xl shadow bg-[#FF66A1] text-white hover:opacity-90 disabled:opacity-50; }
.btn-pink-outline { @apply px-4 py-2 rounded-xl shadow border border-pink-200 hover:bg-pink-50 disabled:opacity-50; }
.btn-chip { @apply px-3 py-1.5 rounded-lg text-sm border border-pink-200 hover:bg-pink-50 disabled:opacity-50; }
/* subtle pretty scrollbar inside cards */
.custom-scroll::-webkit-scrollbar { width: 8px; }
.custom-scroll::-webkit-scrollbar-track { background: #fff0f6; border-radius: 9999px; }
.custom-scroll::-webkit-scrollbar-thumb { background: #f9a8d4; border-radius: 9999px; }
.custom-scroll { scrollbar-width: thin; scrollbar-color: #f9a8d4 #fff0f6; }
</style>
