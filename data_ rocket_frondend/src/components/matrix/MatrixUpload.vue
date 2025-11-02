<template>
  <div class="rounded-2xl p-4 shadow border border-pink-100">
    <div class="grid lg:grid-cols-3 gap-4">
      <!-- ALS Upload -->
      <div>
        <label class="block text-sm font-medium mb-2 text-[#FF66A1]">ALS Excel (.xlsx)</label>
        <div class="flex items-center gap-3">
          <label class="btn-pink-outline cursor-pointer">
            <input type="file" accept=".xlsx" class="hidden" @change="onAls">
            Choose a file
          </label>
          <span class="text-xs text-gray-600 truncate max-w-[16rem]" v-if="store.alsFileName">{{ store.alsFileName }}</span>
          <span class="text-xs text-gray-400" v-else>No file chosen</span>
        </div>

        <!-- Matrix picker -->
        <div v-if="store.alsFile" class="mt-3">
          <div class="flex items-center justify-between">
            <label class="block text-sm font-medium text-[#FF66A1]">Select Matrix</label>
            <button :disabled="store.loading || !store.alsFile" @click="store.discoverMatrices" class="btn-chip">Discover Matrices</button>
          </div>
          <div v-if="store.availableMatrices.length" class="mt-2">
            <select v-model="store.selectedMatrixOID" class="select-pink">
              <option v-for="m in store.availableMatrices" :key="m.matrixOID" :value="m.matrixOID">{{ m.matrixOID }} (sheet: {{ m.sheet }})</option>
            </select>
            <p class="text-xs text-gray-500 mt-1">Default preference: MASTERDASHBOARD</p>
          </div>
          <div v-else class="mt-2 text-xs text-gray-500">No matrices discovered yet. Click Discover Matrices.</div>
        </div>
      </div>

      <!-- Spacer column (matches Figma layout) -->
      <div></div>

      <!-- Actions / Meta -->
      <div>
        <label class="block text-sm font-medium mb-2 text-[#FF66A1]">Actions</label>
        <div class="flex flex-wrap gap-2">
          <button :disabled="store.loading || !store.alsFile" @click="store.extractMatrix" class="btn-pink-solid">Extract Matrix</button>
        </div>
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
.btn-pink-solid { @apply px-4 py-2 rounded-xl shadow bg-[#FF66A1] text-white hover:opacity-90 disabled:opacity-50; }
.btn-pink-outline { @apply px-4 py-2 rounded-xl shadow border border-pink-200 hover:bg-pink-50 disabled:opacity-50; }
.btn-chip { @apply px-3 py-1.5 rounded-lg text-sm border border-pink-200 hover:bg-pink-50 disabled:opacity-50; }
.select-pink { @apply w-full rounded-xl border border-pink-200 p-2 text-sm outline-none focus:ring-2 focus:ring-pink-300 bg-white; }
</style>

