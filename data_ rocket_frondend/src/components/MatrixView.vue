<!-- src/components/MatrixView.vue -->
<template>
    <div class="matrix-container">
      <!-- 矩阵选择下拉框 -->
      <div class="matrix-selector">
        <label for="matrixSelect">Matrix:</label>
        <select id="matrixSelect" v-model="selectedMatrixName">
          <option v-for="m in matrixSheets" :key="m.sheetName" :value="m.sheetName">
            {{ m.sheetName }}
          </option>
        </select>
        <!-- 切换显示模式 -->
        <div class="display-toggle">
          <button :class="{ active: displayMode === 'name' }" @click="displayMode = 'name'">Name</button>
          <button :class="{ active: displayMode === 'oid' }" @click="displayMode = 'oid'">OID</button>
        </div>
      </div>
  
      <!-- 矩阵表格 -->
      <div class="matrix-table-wrapper" v-if="selectedMatrix">
        <table class="matrix-table">
          <thead>
            <tr>
              <th></th>
              <th v-for="folderOid in selectedMatrix.folderOids" :key="folderOid">
                {{ displayMode === 'name' ? getFolderName(folderOid) : folderOid }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="entry in selectedMatrix.matrixEntries" :key="entry.formOid">
              <th>{{ displayMode === 'name' ? getFormName(entry.formOid) : entry.formOid }}</th>
              <td v-for="folderOid in selectedMatrix.folderOids" :key="folderOid">
                <span v-if="entry.includedFolders.includes(folderOid)">X</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, watch } from 'vue';
  import { useAlsStore } from '@/stores/alsStore';
  
  const alsStore = useAlsStore();
  const matrixSheets = computed(() => alsStore.sheets.matrixSheets || []);
  const selectedMatrixName = ref('');
  const displayMode = ref('name');
  
  // 当解析出来的矩阵列表变化时，自动选中第一个
  watch(matrixSheets, (val) => {
    if (val && val.length && !selectedMatrixName.value) {
      selectedMatrixName.value = val[0].sheetName;
    }
  });
  
  // 查找当前选中的矩阵对象
  const selectedMatrix = computed(() =>
    matrixSheets.value.find((m) => m.sheetName === selectedMatrixName.value)
  );
  
  // 根据 OID 获取 Folder 名称
  const getFolderName = (oid) => {
    const folders = alsStore.sheets.folders || [];
    const found = folders.find((f) => String(f.OID) === String(oid));
    return found ? found.FolderName || oid : oid;
  };
  
  // 根据 OID 获取 Form 名称
  const getFormName = (oid) => {
    const forms = alsStore.sheets.forms || [];
    const found = forms.find((f) => String(f.OID) === String(oid));
    return found ? found.DraftFormName || oid : oid;
  };
  </script>
  
  <style scoped>
  .matrix-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
  .matrix-selector {
    display: flex;
    gap: 20px;
    align-items: center;
  }
  .matrix-selector select {
    background-color: var(--background-interactive);
    border: 1px solid var(--border-interactive);
    color: var(--text-primary);
    padding: 8px 12px;
    border-radius: 5px;
  }
  .display-toggle button {
    background-color: var(--background-interactive);
    border: 1px solid var(--border-interactive);
    color: var(--text-secondary);
    padding: 8px 12px;
    cursor: pointer;
    border-radius: 5px;
    transition: all 0.2s;
  }
  .display-toggle button.active {
    background-color: var(--text-accent);
    color: var(--text-inverted);
    font-weight: bold;
    border-color: var(--text-accent);
  }
  .matrix-table-wrapper {
    overflow-x: auto;
  }
  .matrix-table {
    border-collapse: collapse;
    width: 100%;
  }
  .matrix-table th,
  .matrix-table td {
    border: 1px solid var(--border-primary);
    padding: 8px;
    text-align: center;
  }
  .matrix-table th {
    background-color: var(--background-secondary);
  }
  </style>
  