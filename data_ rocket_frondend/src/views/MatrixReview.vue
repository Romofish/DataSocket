<template>
  <div class="p-6">
    <!-- Header -->
    <header class="mb-4 flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-[#FF66A1]">Matrix Review</h1>
        <p class="text-sm text-gray-500">Upload ALS, discover Matrices, filter folders, and compare with SSD.</p>
      </div>
      <ThemeToggleButton />
    </header>

    <!-- Tabs (Figma-like) -->
    <nav class="flex items-center gap-2 mb-4">
      <button :class="tabClass(0)" @click="active=0"><i data-lucide="calendar"></i><span class="ml-2">Upload & Matrix</span></button>
      <button :disabled="!store.result" :class="tabClass(1)" @click="store.result && (active=1)"><i data-lucide="folder"></i><span class="ml-2">Folders & Export</span></button>
      <button :disabled="!store.result" :class="tabClass(2)" @click="store.result && (active=2)"><i data-lucide="link"></i><span class="ml-2">Compare SSD</span></button>
    </nav>

    <section class="grid gap-4">
      <MatrixUpload v-if="active===0" />
      <MatrixFolders v-if="active===1" />
      <MatrixCompare v-if="active===2" />
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ThemeToggleButton from '../components/ThemeToggleButton.vue'
import MatrixUpload from '../components/matrix/MatrixUpload.vue'
import MatrixFolders from '../components/matrix/MatrixFolders.vue'
import MatrixCompare from '../components/matrix/MatrixCompare.vue'
import { useMatrixStore } from '../stores/matrix'
const store = useMatrixStore()
const active = ref(0)
function tabClass(idx: number){
  const base = 'px-4 py-2 rounded-full text-sm border transition flex items-center'
  const on = 'bg-[#FF66A1] text-white border-pink-300'
  const off = 'bg-pink-50 text-pink-700 border-pink-200 disabled:opacity-50'
  return idx===active.value ? `${base} ${on}` : `${base} ${off}`
}
onMounted(() => { if ((window as any).lucide) (window as any).lucide.createIcons?.() })
</script>

<style scoped>
</style>

