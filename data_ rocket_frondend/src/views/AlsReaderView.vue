<template>
  <div class="als-reader-container">
    <!-- 初始上传视图 -->
    <div v-if="!alsStore.isParsed" class="initial-view">
      <button @click="goHome" class="back-button">
        <i data-lucide="arrow-left" class="mr-2"></i>返回主页
      </button>
      <div class="content-wrapper">
        <header class="mb-8 text-center">
          <h1 class="text-5xl font-bold text-white">ALS Reader</h1>
          <p class="text-gray-400 mt-2 text-lg">上传、解析并预览您的 Medidata Rave Architect Loader Sheet</p>
        </header>
        <div class="upload-section">
          <div @click="triggerFileInput" @dragover.prevent @drop.prevent="handleFileDrop" class="upload-box">
            <div class="upload-icon-wrapper"><i data-lucide="upload-cloud" class="w-16 h-16 text-cyan-300"></i></div>
            <h3 class="text-2xl font-semibold text-white">点击此处或拖拽文件上传</h3>
            <p class="text-gray-400 mt-2">请选择一个 .xlsx 格式的 ALS 文件</p>
            <input type="file" ref="fileInput" @change="handleFileSelect" class="hidden" accept=".xlsx, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet">
          </div>
        </div>
      </div>
    </div>

    <!-- 解析后显示的数据视图 -->
    <div v-else class="data-view">
      <aside class="sidebar">
        <div class="sidebar-header">
          <h2 class="text-xl font-bold">Forms</h2>
          <p class="text-sm text-gray-400 truncate" :title="alsStore.fileName">{{ alsStore.fileName }}</p>
        </div>
        <nav class="form-list">
          <a v-for="form in alsStore.sheets.forms" :key="form.OID" @click="selectForm(form)"
             :class="{ 'active': selectedForm && selectedForm.OID === form.OID }">
            {{ form.OID }}
          </a>
        </nav>
        <button @click="resetView" class="reset-button">上传新文件</button>
      </aside>

      <main class="main-content">
        <!-- 预览区头部 -->
        <div class="preview-header">
          <div class="header-info">
            <h1 v-if="selectedForm" class="text-3xl font-bold text-white">{{ selectedForm.OID }}</h1>
            <h1 v-else class="text-3xl font-bold text-gray-500">请选择一个 Form</h1>
            <p v-if="selectedForm" class="text-gray-400">{{ fieldsForPreview.length }} 个字段可见</p>
          </div>
          <div class="controls">
            <div class="control-group">
              <label for="role-selector">角色</label>
              <select id="role-selector" v-model="selectedRole" class="selector">
                <option v-for="role in alsStore.getAllRoles" :key="role" :value="role">{{ role }}</option>
              </select>
            </div>
            <div class="control-group">
              <label>标签</label>
              <div class="toggle-group">
                <button @click="labelMode = 'DraftFieldName'" :class="{active: labelMode === 'DraftFieldName'}">Name</button>
                <button @click="labelMode = 'SASLabel'" :class="{active: labelMode === 'SASLabel'}">SAS Label</button>
                <button @click="labelMode = 'Both'" :class="{active: labelMode === 'Both'}">Both</button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 预览区主体 -->
        <div v-if="!selectedForm" class="placeholder">
          <i data-lucide="mouse-pointer-square" class="w-24 h-24 text-gray-600 mb-4"></i>
          <h2 class="text-2xl font-bold text-gray-400">请从左侧选择一个 Form 进行预览</h2>
        </div>
        
        <div v-else class="form-preview-area">
          <div class="form-fields-container">
            <div v-for="field in fieldsForPreview" :key="field.OID" class="field-item" :style="{ marginLeft: (field.IndentLevel || 0) * 40 + 'px' }">
              <label class="field-label">
                <span class="prefix-symbol">{{ field.displayPrefix }}</span>
                <span v-if="labelMode === 'DraftFieldName'">{{ field.DraftFieldName }}</span>
                <span v-else-if="labelMode === 'SASLabel'">{{ field.SASLabel || '(No SAS Label)' }}</span>
                <span v-else-if="labelMode === 'Both'">{{ field.DraftFieldName }} [{{ field.SASLabel || 'N/A' }}]</span>
              </label>

              <p v-if="field.PreText" class="field-pretext">
                <i data-lucide="info" class="inline-block w-4 h-4 mr-2 shrink-0"></i><span>{{ field.PreText }}</span>
              </p>

              <div :class="{'entry-restricted': field.isEntryRestricted}" :title="field.isEntryRestricted ? '此角色限制输入' : ''">
                <div v-if="field.ControlType === 'Text'">
                  <input type="text" :placeholder="field.OID" class="field-input" :disabled="field.isEntryRestricted">
                </div>
                <div v-else-if="field.dictionaryEntries.length > 0">
                  <div class="radio-group">
                    <div v-for="entry in field.dictionaryEntries" :key="entry.UserData" class="radio-option">
                      <label class="radio-label">
                        <input type="radio" :name="field.OID" :value="entry.UserData" @change="handleRadioChange(field.OID, entry)" :disabled="field.isEntryRestricted" class="radio-input">
                        <span>{{ entry.UserDataString || entry.UserData }}</span>
                      </label>
                      <input v-if="entry.Specify && specifyState[field.OID] === entry.UserData" type="text" placeholder="请详细说明..." class="specify-input" :disabled="field.isEntryRestricted">
                    </div>
                  </div>
                </div>
                <div v-else>
                  <input type="text" :placeholder="`${field.OID} (${field.ControlType})`" class="field-input-unknown" :disabled="field.isEntryRestricted">
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useAlsStore } from '@/stores/alsStore';

const router = useRouter();
const alsStore = useAlsStore();

const fileInput = ref(null);
const selectedForm = ref(null);
const selectedRole = ref('All');
const labelMode = ref('DraftFieldName');
const specifyState = ref({});

onMounted(() => {
  lucide.createIcons();
});

watch(selectedForm, async () => {
  selectedRole.value = 'All';
  labelMode.value = 'DraftFieldName';
  specifyState.value = {};
  await nextTick(); // 等待 DOM 更新
  lucide.createIcons(); // 重新渲染图标
});

const fieldsForPreview = computed(() => {
  if (!selectedForm.value) return [];
  return alsStore.getFieldsForPreview(selectedForm.value.OID, selectedRole.value);
});

const handleRadioChange = (fieldOid, entry) => {
  if (entry.Specify) {
    specifyState.value[fieldOid] = entry.UserData;
  } else if (specifyState.value[fieldOid]) {
    delete specifyState.value[fieldOid];
  }
};

const goHome = () => router.push('/');
const triggerFileInput = () => fileInput.value.click();
const handleFileSelect = (e) => { if (e.target.files[0]) alsStore.parseFile(e.target.files[0]); };
const handleFileDrop = (e) => { if (e.dataTransfer.files[0]) alsStore.parseFile(e.dataTransfer.files[0]); };
const selectForm = (form) => { selectedForm.value = form; };
const resetView = () => { alsStore.reset(); selectedForm.value = null; };
</script>

<style scoped>
/* 初始上传视图样式 */
.initial-view { display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 40px; position: relative; }
.back-button { position: absolute; top: 40px; left: 40px; display: flex; align-items: center; padding: 10px 20px; border-radius: 10px; background: rgba(255, 255, 255, 0.1); font-weight: bold; transition: all 0.3s ease; }
.back-button:hover { background: rgba(0, 255, 255, 0.2); }
.content-wrapper { width: 100%; max-width: 800px; }
.upload-section { background: rgba(255, 255, 255, 0.05); border-radius: 20px; padding: 40px; border: 1px solid rgba(255, 255, 255, 0.2); }
.upload-box { border: 2px dashed rgba(0, 255, 255, 0.4); border-radius: 15px; padding: 60px 20px; text-align: center; cursor: pointer; transition: all 0.3s ease; }
.upload-box:hover { border-color: #00FFFF; background: rgba(0, 255, 255, 0.05); }
.upload-icon-wrapper { display: inline-flex; padding: 20px; border-radius: 50%; background: rgba(0, 255, 255, 0.1); margin-bottom: 20px; }

/* 数据视图样式 */
.als-reader-container { min-height: 100vh; background: #0f0c29; color: white; }
.data-view { display: flex; height: 100vh; }
.sidebar { width: 280px; background: #1c1c3c; border-right: 1px solid rgba(0, 255, 255, 0.2); display: flex; flex-direction: column; flex-shrink: 0; }
.sidebar-header { padding: 20px; border-bottom: 1px solid rgba(0, 255, 255, 0.2); }
.form-list { flex-grow: 1; overflow-y: auto; }
.form-list a { display: block; padding: 15px 20px; color: #a0a0a0; text-decoration: none; transition: all 0.2s ease; border-left: 3px solid transparent; cursor: pointer; }
.form-list a:hover { background: rgba(0, 255, 255, 0.1); color: white; }
.form-list a.active { background: rgba(0, 255, 255, 0.2); color: #00FFFF; border-left-color: #00FFFF; font-weight: bold; }
.reset-button { padding: 20px; background: #6d28d9; text-align: center; font-weight: bold; cursor: pointer; transition: background 0.3s; }
.reset-button:hover { background: #8b5cf6; }

.main-content { display: flex; flex-direction: column; flex-grow: 1; overflow-y: auto; }
.preview-header { position: sticky; top: 0; background: #1c1c3cDD; backdrop-filter: blur(10px); padding: 20px 40px; border-bottom: 1px solid rgba(0, 255, 255, 0.2); z-index: 10; display: flex; justify-content: space-between; align-items: center; }
.controls { display: flex; gap: 30px; }
.control-group { display: flex; flex-direction: column; gap: 8px; }
.control-group label { font-size: 0.8rem; color: #a0a0a0; font-weight: bold; }
.selector { background: rgba(0,0,0,0.3); border: 1px solid #4a4a6a; color: white; padding: 8px 12px; border-radius: 5px; }
.toggle-group button { background: rgba(0,0,0,0.3); border: 1px solid #4a4a6a; color: #a0a0a0; padding: 8px 12px; cursor: pointer; }
.toggle-group button:first-child { border-radius: 5px 0 0 5px; border-right: none;}
.toggle-group button:last-child { border-radius: 0 5px 5px 0; border-left: none;}
.toggle-group button.active { background: #00FFFF; color: #0f0c29; font-weight: bold; border-color: #00FFFF; }

.placeholder { display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%; }
.form-preview-area { padding: 40px; }
.form-fields-container { display: grid; grid-template-columns: 1fr; gap: 15px; }
.field-item { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 10px; border-left: 3px solid transparent; transition: all 0.3s ease; }
.field-item:hover { border-left-color: #00FFFF; background: rgba(255, 255, 255, 0.08); }
.field-label { display: block; font-weight: bold; color: #E0E0E0; margin-bottom: 5px; font-size: 1.1rem; }
.prefix-symbol { color: #FF5555; font-weight: bold; margin-right: 8px; font-size: 1.2rem; }
.field-pretext { font-size: 0.9rem; color: #a0a0a0; margin-bottom: 12px; background: rgba(255, 255, 255, 0.05); padding: 8px 12px; border-radius: 5px; display: flex; align-items: center; }
.field-input, .field-input-unknown { width: 100%; max-width: 400px; background: rgba(0,0,0,0.3); border: 1px solid #4a4a6a; color: white; padding: 10px; border-radius: 5px; }
.field-input-unknown { border-style: dashed; }
.entry-restricted { cursor: not-allowed; opacity: 0.6; }
.radio-group { display: flex; flex-direction: column; gap: 10px; }
.radio-option { display: flex; align-items: center; gap: 10px; }
.radio-label { display: flex; align-items: center; cursor: pointer; color: #c0c0c0; }
.radio-label:hover { color: white; }
.radio-input { appearance: none; width: 18px; height: 18px; border: 2px solid #4a4a6a; border-radius: 50%; margin-right: 8px; cursor: pointer; position: relative; transition: all 0.2s; flex-shrink: 0; }
.radio-input:checked { border-color: #00FFFF; }
.radio-input:checked::after { content: ''; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 8px; height: 8px; border-radius: 50%; background: #00FFFF; }
.radio-input:disabled { cursor: not-allowed; }
.specify-input { background: rgba(0,0,0,0.5); border: 1px solid #6d28d9; color: white; padding: 8px; border-radius: 5px; margin-left: 10px; flex-grow: 1; }
</style>
