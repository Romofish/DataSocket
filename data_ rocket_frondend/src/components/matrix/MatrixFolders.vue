<template>
  <div class="rounded-2xl p-4 shadow border border-cyan-100 bg-white" v-if="store.result">
    <div class="flex items-center justify-between mb-3">
      <h2 class="text-xl font-semibold text-[#0EA5E9]">Folder Filter</h2>
      <div class="flex items-center gap-2">
        <button @click="store.selectAll" class="btn-glass">Select all</button>
        <button @click="store.clearAll" class="btn-glass">Clear all</button>
        <button @click="store.saveSelection" class="btn-glass">Save selection</button>
        <button class="btn-glass" @click="store.exportMatrixCsv">Export CSV</button>
        <label class="ml-2 inline-flex items-center gap-2 text-sm">
          <input type="checkbox" v-model="store.autoRemember" @change="store.saveSelection" />
          Auto-remember
        </label>
      </div>
    </div>

    <div class="flex flex-wrap gap-2 mb-3">
      <label v-for="f in store.allFolders" :key="f.folderOID" class="inline-flex items-center gap-2 text-sm px-3 py-1.5 rounded-full border" :class="store.selectedFolders.has(f.folderOID)?'bg-pink-50 border-pink-300':'border-pink-200'">
        <input type="checkbox" :checked="store.selectedFolders.has(f.folderOID)" @change="store.toggleFolder(f.folderOID)" />
        <span class="font-mono">{{ f.folderOID }}</span>
        <span class="text-gray-500" v-if="f.folderName">— {{ f.folderName }}</span>
      </label>
    </div>

    <div class="flex justify-between items-center mb-2">
      <div class="text-sm text-gray-600">Showing {{ store.visibleFolders.length }} folders</div>
    </div>

    <div class="grid gap-3 custom-scroll max-h-[65vh] overflow-y-auto pr-1">
      <div v-for="f in store.visibleFolders" :key="f.folderOID" class="rounded-xl border border-cyan-100 p-3">
        <div class="flex items-center justify-between">
          <div>
            <div class="font-medium">{{ f.folderOID }}</div>
            <div class="text-xs text-gray-500" v-if="f.folderName">{{ f.folderName }}</div>
          </div>
          <span class="text-xs px-2 py-1 rounded-full bg-cyan-50 border border-cyan-100">{{ f.forms.length }} forms</span>
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
</template>

<script setup lang="ts">
import { useMatrixStore } from '../../stores/matrix'
const store = useMatrixStore()
</script>

<style scoped>
.btn-glass { @apply px-4 py-2 rounded-full border font-semibold text-[#0EA5E9] border-cyan-100 bg-white/70 backdrop-blur-sm shadow-sm hover:shadow-md hover:bg-cyan-50 transition disabled:opacity-50; }
.btn-cyan-outline { @apply px-4 py-2 rounded-xl shadow border border-cyan-100 hover:bg-cyan-50 disabled:opacity-50; }
.btn-chip { @apply px-3 py-1.5 rounded-lg text-sm border border-cyan-100 hover:bg-cyan-50 disabled:opacity-50; }
/* Pretty scrollbar for folder list */
.custom-scroll::-webkit-scrollbar { width: 10px; }
.custom-scroll::-webkit-scrollbar-track { background: #ecfeff; border-radius: 9999px; }
.custom-scroll::-webkit-scrollbar-thumb { background: #7dd3fc; border-radius: 9999px; }
.custom-scroll { scrollbar-width: thin; scrollbar-color: #7dd3fc #ecfeff; }
</style>
