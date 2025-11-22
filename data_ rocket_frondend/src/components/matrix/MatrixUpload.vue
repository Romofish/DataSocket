<template>
  <div class="rounded-2xl p-4 shadow border border-cyan-100 bg-white">
    <div v-if="store.loading" class="h-1 w-full bg-cyan-50 rounded overflow-hidden mb-3">
      <div class="h-full w-1/2 animate-pulse bg-cyan-300/60"></div>
    </div>
    <!-- Vertical step flow -->
    <div class="space-y-5">
      <!-- Step 1: ALS upload -->
      <div>
        <h3 class="text-sm font-medium text-[#0EA5E9] mb-2">Step 1 — Upload ALS</h3>
        <div class="flex items-center gap-3">
          <label class="btn-upload-pink cursor-pointer">
            <input type="file" accept=".xlsx" class="hidden" @change="onAls">
            <i data-lucide="upload" class="w-4 h-4 mr-2"></i>
            Choose a file
          </label>
          <span class="text-xs text-gray-600 truncate max-w-[16rem]" v-if="store.alsFileName">{{ store.alsFileName }}</span>
          <span class="text-xs text-gray-400" v-else>No file chosen</span>
        </div>
      </div>

      <!-- Step 2: Discover matrices (shown only after file selected) -->
      <div v-if="store.alsFile">
        <h3 class="text-sm font-medium text-[#0EA5E9] mb-2">Step 2 — Discover Matrices</h3>
        <button class="btn-primary" :disabled="store.loading" @click="store.discoverMatrices">Discover Matrices</button>
      </div>

      <!-- Step 3: Select matrix (only after discovery) -->
      <div v-if="store.alsFile && store.availableMatrices.length">
        <h3 class="text-sm font-medium text-[#0EA5E9] mb-2">Step 3 — Select Matrix</h3>
        <select v-model="store.selectedMatrixOID" class="select-pink w-full max-w-md">
          <option disabled value="">— Select a matrix —</option>
          <option v-for="m in store.availableMatrices" :key="m.matrixOID" :value="m.matrixOID">
            {{ m.matrixOID }} (sheet: {{ m.sheet }})
          </option>
        </select>
        <div class="mt-1 text-xs text-gray-500">Default preference: MASTERDASHBOARD</div>
      </div>

      <!-- Step 4: Extract matrix (only after a matrix is selected) -->
      <div v-if="store.alsFile && store.availableMatrices.length && store.selectedMatrixOID">
        <h3 class="text-sm font-medium text-[#0EA5E9] mb-2">Step 4 — Extract Matrix</h3>
        <button class="btn-primary" :disabled="store.loading" @click="store.extractMatrix">Extract Matrix</button>
        <p class="text-xs text-gray-500 mt-2">CSV columns: FolderName, FolderOID, FormName, FormOID</p>
        <div v-if="store.result?.meta" class="mt-3 text-xs text-gray-600">
          <div>Chosen matrixOID: <span class="font-mono">{{ store.result.meta.matrixOID }}</span></div>
          <div>Worksheet: <span class="font-mono">{{ store.result.meta.sheet }}</span></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useMatrixStore } from '../../stores/matrix'
const store = useMatrixStore()

function onAls(e: Event){
  const input = e.target as HTMLInputElement
  const file = input.files?.[0] ?? null
  store.setALS(file)
}
</script>

<style scoped>
.btn-primary { @apply px-4 py-2 rounded-xl shadow bg-[#0EA5E9] text-white hover:shadow-lg hover:shadow-cyan-200/60 focus:ring-2 focus:ring-cyan-300 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed; }
.btn-secondary { @apply px-4 py-2 rounded-xl shadow border border-cyan-100 bg-white text-cyan-700 hover:bg-cyan-50 focus:ring-2 focus:ring-cyan-200 disabled:opacity-50 disabled:cursor-not-allowed; }
.btn-chip { @apply px-3 py-1.5 rounded-lg text-sm border border-cyan-100 hover:bg-cyan-50 disabled:opacity-50; }
.select-pink { @apply w-full rounded-xl border border-cyan-100 p-2 text-sm outline-none focus:ring-2 focus:ring-cyan-200 bg-white; }
.btn-upload-pink { @apply inline-flex items-center px-4 py-2 rounded-full border border-pink-300 text-pink-600 bg-white hover:bg-pink-50 shadow-sm focus:ring-2 focus:ring-pink-200; }
</style>
