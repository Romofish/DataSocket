<template>
  <div class="als-reader-container">
    <div v-if="!alsStore.isParsed" class="initial-view">
        <div class="content-wrapper">
            <header class="mb-8 text-center">
            <h1 class="text-5xl font-bold header-title">ALS Reader</h1>
            <p class="mt-2 text-lg card-description">Upload, parse and preview your Medidata Rave Architect Loader Sheet</p>
            </header>
            <div class="upload-section">
            <div @click="triggerFileInput" @dragover.prevent @drop.prevent="handleFileDrop" class="upload-box">
                <div class="upload-icon-wrapper"><i data-lucide="upload-cloud" class="w-16 h-16 text-cyan-300"></i></div>
                <h3 class="text-2xl font-semibold header-title">Click here or drag & drop a file to upload</h3>
                <p class="mt-2 card-description">Please select an .xlsx format ALS file</p>
                <input type="file" ref="fileInput" @change="handleFileSelect" class="hidden" accept=".xlsx, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet">
            </div>
            </div>
        </div>
    </div>

    <div v-else class="data-view">
      <aside class="sidebar">
        <div class="sidebar-header">
          <h2 class="text-xl font-bold">Forms</h2>
          <p class="text-sm truncate" :title="alsStore.fileName">{{ alsStore.fileName }}</p>
        </div>
        <nav class="form-list">
          <a v-for="form in alsStore.sheets.forms" :key="form.OID" @click="selectForm(form)"
             :class="{ 'active': selectedForm && selectedForm.OID === form.OID }">
            {{ form.OID }}
          </a>
        </nav>
        <button @click="resetView" class="reset-button" title="Upload a new file">
            <i data-lucide="file-up" class="inline-block w-4 h-4 mr-2"></i>
            Upload New File
        </button>
      </aside>

      <main class="main-content">
        <div class="preview-header">
          <div class="header-info" v-if="!isMatrixMode">
            <h1 v-if="selectedForm" class="text-3xl font-bold">{{ selectedForm.OID }}</h1>
            <h1 v-else class="text-3xl font-bold">Please select a Form</h1>
            <p v-if="selectedForm" class="">{{ fieldsForPreview.length }} fields visible</p>
          </div>
          <div class="header-info" v-else>
            <h1 class="text-3xl font-bold">Matrix Overview</h1>
            <p class="">Folders mapped across matrix tabs</p>
          </div>
          <div class="control-bar">
            <div class="view-mode-toggle">
              <button
                :class="{ active: !isMatrixMode }"
                @click="isMatrixMode = false"
              >
                Fields
              </button>
              <button
                :class="{ active: isMatrixMode }"
                @click="isMatrixMode = true"
              >
                Matrix
              </button>
            </div>
            <div class="controls" v-if="!isMatrixMode">
              <div class="control-group">
                <label for="role-selector">Role</label>
                <select id="role-selector" v-model="selectedRole" class="selector">
                  <option v-for="role in alsStore.getAllRoles" :key="role" :value="role">{{ role }}</option>
                </select>
              </div>
              <div class="control-group">
                <label>Label</label>
                <div class="toggle-group">
                  <button @click="labelMode = 'DraftFieldName'" :class="{active: labelMode === 'DraftFieldName'}">Name</button>
                  <button @click="labelMode = 'SASLabel'" :class="{active: labelMode === 'SASLabel'}">SAS Label</button>
                  <button @click="labelMode = 'Both'" :class="{active: labelMode === 'Both'}">Both</button>
                </div>
              </div>
              <div class="control-group">
                <label>Preview Mode</label>
                <div class="toggle-group">
                  <button @click="previewMode = 'dropdown'" :class="{active: previewMode === 'dropdown'}">Dropdown</button>
                  <button @click="previewMode = 'flat'" :class="{active: previewMode === 'flat'}">Flat</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="isMatrixMode" class="matrix-view-wrapper">
          <div class="p-6 rounded-xl border border-pink-200 bg-pink-50 text-pink-700">
            Matrix overview moved to Matrix Review page. Use route /matrix.
          </div>
        </div>
        
        <template v-else>
          <div v-if="!selectedForm" class="placeholder">
            <i data-lucide="mouse-pointer-square" class="w-24 h-24 mb-4"></i>
            <h2 class="text-2xl font-bold">Please select a Form from the left panel to preview</h2>
          </div>
          
          <div v-else class="form-preview-area">
            <div class="form-fields-container">
              <FormField
                v-for="field in fieldsForPreview"
                :key="field.OID"
                :field="field"
                :label-mode="labelMode"
                :preview-mode="previewMode"
              />
            </div>
          </div>
        </template>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useAlsStore } from '@/stores/alsStore';
import FormField from '@/components/FormField.vue';
// 不再需要导入 ThemeToggleButton

const router = useRouter();
const alsStore = useAlsStore();

const fileInput = ref(null);
const selectedForm = ref(null);
const selectedRole = ref('All');
const labelMode = ref('DraftFieldName');
const previewMode = ref('dropdown');
const isMatrixMode = ref(false);

onMounted(() => {
  lucide.createIcons();
});

watch(selectedForm, async () => {
  selectedRole.value = 'All';
  labelMode.value = 'DraftFieldName';
  previewMode.value = 'dropdown';
  await nextTick();
  lucide.createIcons();
});

watch(isMatrixMode, async () => {
  await nextTick();
  lucide.createIcons();
});

const fieldsForPreview = computed(() => {
  if (!selectedForm.value) return [];
  return alsStore.getFieldsForPreview(selectedForm.value.OID, selectedRole.value);
});

const triggerFileInput = () => fileInput.value.click();
const handleFileSelect = (e) => { if (e.target.files[0]) alsStore.parseFile(e.target.files[0]); };
const handleFileDrop = (e) => { if (e.dataTransfer.files[0]) alsStore.parseFile(e.dataTransfer.files[0]); };
const selectForm = (form) => { selectedForm.value = form; };
const resetView = () => {
  alsStore.reset();
  selectedForm.value = null;
  isMatrixMode.value = false;
};
</script>

<style scoped>
/* 样式与之前版本类似，只是移除了不再需要的 .action-group 和 .back-button */
.als-reader-container { min-height: 100vh; background-color: var(--background-primary); color: var(--text-primary); }
.initial-view { display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 40px; }
.content-wrapper { width: 100%; max-width: 800px; }
.header-title { color: var(--text-primary); }
.card-description { color: var(--text-secondary); }
.upload-section { background-color: var(--background-secondary); border-radius: 20px; padding: 40px; border: 1px solid var(--border-primary); }
.upload-box { border: 2px dashed var(--border-accent); border-radius: 15px; padding: 60px 20px; text-align: center; cursor: pointer; }
.upload-box:hover { background-color: var(--background-interactive-hover); }
.upload-icon-wrapper { display: inline-flex; padding: 20px; border-radius: 50%; background-color: var(--background-interactive); margin-bottom: 20px; }
.data-view { display: flex; height: 100vh; }
.sidebar { width: 280px; background-color: var(--background-secondary); border-right: 1px solid var(--border-primary); display: flex; flex-direction: column; flex-shrink: 0; }
.sidebar-header { padding: 20px; border-bottom: 1px solid var(--border-primary); }
.sidebar-header h2 { color: var(--text-primary); }
.sidebar-header p { color: var(--text-secondary); }
.form-list { flex-grow: 1; overflow-y: auto; }
.form-list a { display: block; padding: 15px 20px; color: var(--text-secondary); text-decoration: none; transition: all 0.2s ease; border-left: 3px solid transparent; cursor: pointer; word-wrap: break-word; }
.form-list a:hover { background-color: var(--background-interactive-hover); color: var(--text-primary); }
.form-list a.active { background-color: var(--background-interactive-hover); color: var(--text-accent); border-left-color: var(--border-accent); font-weight: bold; }
.reset-button { padding: 20px; background-color: #6d28d9; color: white; text-align: center; font-weight: bold; cursor: pointer; transition: background 0.3s; border: none; display: flex; align-items: center; justify-content: center; }
.reset-button:hover { background-color: #8b5cf6; }
.main-content { display: flex; flex-direction: column; flex-grow: 1; overflow-y: auto; }
.preview-header { position: sticky; top: 0; background-color: var(--background-secondary-translucent); backdrop-filter: blur(10px); padding: 20px 40px; border-bottom: 1px solid var(--border-primary); z-index: 10; display: flex; justify-content: space-between; align-items: center; }
.header-info h1 { color: var(--text-primary); }
.header-info p { color: var(--text-secondary); }
.controls { display: flex; flex-wrap: wrap; gap: 20px 30px; align-items: flex-end; }
.control-bar { display: flex; flex-wrap: wrap; gap: 20px; align-items: flex-end; justify-content: space-between; width: 100%; }
.control-group { display: flex; flex-direction: column; gap: 8px; }
.control-group label { font-size: 0.8rem; color: var(--text-secondary); font-weight: bold; text-transform: uppercase; }
.selector { background-color: var(--background-interactive); border: 1px solid var(--border-interactive); color: var(--text-primary); padding: 8px 12px; border-radius: 5px; }
.toggle-group button { background-color: var(--background-interactive); border: 1px solid var(--border-interactive); color: var(--text-secondary); padding: 8px 12px; cursor: pointer; transition: all 0.2s; }
.toggle-group button:first-child { border-radius: 5px 0 0 5px; border-right-width: 0.5px; }
.toggle-group button:last-child { border-radius: 0 5px 5px 0; border-left-width: 0.5px; }
.toggle-group button.active { background-color: var(--text-accent); color: var(--text-inverted); font-weight: bold; border-color: var(--text-accent); }
.placeholder { display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%; text-align: center; padding: 20px; color: var(--text-secondary); }
.form-preview-area { padding: 40px; }
.form-fields-container { display: grid; grid-template-columns: 1fr; gap: 25px; }
.view-mode-toggle { display: flex; gap: 10px; }
.view-mode-toggle button { padding: 6px 12px; border: 1px solid var(--border-interactive); background-color: var(--background-interactive); color: var(--text-secondary); border-radius: 4px; cursor: pointer; transition: background-color 0.2s ease, color 0.2s ease, border-color 0.2s ease; }
.view-mode-toggle button.active { background-color: var(--text-accent); color: var(--text-inverted); font-weight: bold; border-color: var(--text-accent); }
.matrix-view-wrapper { padding: 20px 40px; height: calc(100% - 80px); overflow-y: auto; }
</style>
