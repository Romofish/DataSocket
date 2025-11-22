<template>
  <div class="p-6 ts-gradient-bg min-h-[calc(100vh-60px)]">
    <!-- Header -->
    <header class="mb-4">
      <div class="text-center relative">
        <h1 class="text-2xl font-semibold text-[#0EA5E9]">Matrix Review</h1>
        <div class="flex items-center justify-center mt-1 text-sm text-gray-500">
          <span>Upload ALS, discover matrices, filter folders, and compare with SSD.</span>
          <span class="ml-2 relative group">
            <i data-lucide="circle-help" class="w-4 h-4 text-cyan-500 cursor-pointer"></i>
            <!-- Hover guide -->
            <div class="opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto transition absolute left-1/2 -translate-x-1/2 mt-2 z-20 w-[320px] p-3 rounded-2xl border border-cyan-100 bg-white shadow">
              <h3 class="text-sm font-medium text-cyan-700 mb-1">操作顺序指南</h3>
              <ol class="text-xs text-gray-600 list-decimal pl-4 space-y-1">
                <li>上传 ALS → 发现并选择 Matrix</li>
                <li>提取 Matrix → 自动跳转到 Folders & Export</li>
                <li>筛选 Folder 并导出 CSV</li>
                <li>Compare SSD：粘贴或上传 SSD，预览→对比→导出结果</li>
              </ol>
            </div>
          </span>
        </div>
      </div>
    </header>

    <!-- Tabs (Figma-like) -->
    <nav class="flex items-center justify-center gap-2 mb-4">
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
import { ref, watch, onMounted } from 'vue'
import MatrixUpload from '../components/matrix/MatrixUpload.vue'
import MatrixFolders from '../components/matrix/MatrixFolders.vue'
import MatrixCompare from '../components/matrix/MatrixCompare.vue'
import { useMatrixStore } from '../stores/matrix'
const store = useMatrixStore()
const active = ref(0)
function tabClass(idx: number){
  const base = 'px-4 py-2 rounded-full text-sm border transition flex items-center'
  const on = 'bg-[#0EA5E9] text-white border-cyan-300 shadow'
  const off = 'bg-white text-cyan-700 border-cyan-100 disabled:opacity-50 hover:bg-cyan-50'
  return idx===active.value ? `${base} ${on}` : `${base} ${off}`
}
onMounted(() => { if ((window as any).lucide) (window as any).lucide.createIcons?.() })
// Auto-jump to Folders tab after successful extract
watch(() => store.result, (v) => { if (v && (v.folders?.length || 0) > 0) active.value = 1 })
</script>

<style scoped>
/* Page background: very light cool gradient */
.ts-gradient-bg { background: linear-gradient(180deg, rgba(240,249,255,0.8) 0%, rgba(255,255,255,1) 100%); }
</style>
