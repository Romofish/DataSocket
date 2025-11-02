<template>
  <div class="rounded-2xl p-4 shadow border border-pink-100" v-if="store.result">
    <div class="flex items-center justify-between mb-3">
      <h2 class="text-xl font-semibold text-[#FF66A1]">Folder Filter</h2>
      <div class="flex items-center gap-2">
        <button @click="store.selectAll" class="btn-chip">Select all</button>
        <button @click="store.clearAll" class="btn-chip">Clear all</button>
        <button @click="store.saveSelection" class="btn-chip">Save selection</button>
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
      <button class="btn-pink-outline" @click="store.exportMatrixCsv">Export CSV</button>
    </div>

    <div class="grid gap-3">
      <div v-for="f in store.visibleFolders" :key="f.folderOID" class="rounded-xl border border-pink-200 p-3">
        <div class="flex items-center justify-between">
          <div>
            <div class="font-medium">{{ f.folderOID }}</div>
            <div class="text-xs text-gray-500" v-if="f.folderName">{{ f.folderName }}</div>
          </div>
          <span class="text-xs px-2 py-1 rounded-full bg-pink-50 border border-pink-200">{{ f.forms.length }} forms</span>
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
.btn-pink-outline { @apply px-4 py-2 rounded-xl shadow border border-pink-200 hover:bg-pink-50 disabled:opacity-50; }
.btn-chip { @apply px-3 py-1.5 rounded-lg text-sm border border-pink-200 hover:bg-pink-50 disabled:opacity-50; }
</style>

