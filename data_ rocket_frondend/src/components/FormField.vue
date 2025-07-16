<template>
  <div class="field-item" :style="{ marginLeft: (field.IndentLevel || 0) * 40 + 'px' }">
    <div class="field-label-container">
      <div class="field-label">
        <span v-if="props.labelMode === 'DraftFieldName'">{{ field.DraftFieldName }}</span>
        <span v-else-if="props.labelMode === 'SASLabel'">{{ field.SASLabel || '(No SAS Label)' }}</span>
        <span v-else-if="props.labelMode === 'Both'">{{ field.DraftFieldName }} [{{ field.SASLabel || 'N/A' }}]</span>
      </div>
    </div>
    
    <div class="field-header">
       <p v-if="field.PreText" class="field-pretext">
        <i data-lucide="info" class="inline-block w-4 h-4 mr-2 shrink-0"></i><span>{{ field.PreText }}</span>
      </p>
      <div class="field-oid-container">
        <span class="prefix-symbol">{{ field.displayPrefix }}</span>
        <h4 class="field-oid-header">{{ field.OID }}</h4>
      </div>
    </div>

    <div :class="{'entry-restricted': field.isEntryRestricted}" :title="field.isEntryRestricted ? 'Entry restricted for this role' : ''" class="field-control-wrapper">
      
      <div v-if="field.ControlType === 'Long Text'">
        <textarea :placeholder="field.DataFormat || 'Long Text'" class="field-textarea" :disabled="field.isEntryRestricted"></textarea>
      </div>
      
      <div v-else-if="field.ControlType === 'Text'">
        <input type="text" :placeholder="field.DataFormat || 'Text Input'" class="field-input" :disabled="field.isEntryRestricted">
      </div>
      
      <div v-else-if="field.dictionaryEntries.length > 0">
        <div v-if="props.previewMode === 'dropdown'" class="custom-dropdown">
          <button @click="toggleDropdown" class="dropdown-trigger" :disabled="field.isEntryRestricted">
            <span>{{ selectedOptionLabel || 'Dropdown List' }}</span>
            <i data-lucide="chevron-down" class="dropdown-chevron" :class="{'rotate-180': isDropdownOpen}"></i>
          </button>
          <transition name="dropdown">
            <div v-if="isDropdownOpen" class="dropdown-panel">
              <div v-for="entry in field.dictionaryEntries" :key="entry.CodedData" @click="selectOption(entry)" class="dropdown-option">
                {{ entry.UserDataString || entry.CodedData }}
              </div>
            </div>
          </transition>
        </div>
        <div v-else class="radio-group">
          <div v-for="entry in field.dictionaryEntries" :key="entry.CodedData" class="radio-option">
            <label class="radio-label">
              <input 
                type="radio" 
                :name="field.OID" 
                :value="entry.CodedData"
                :checked="selectedEntry?.CodedData === entry.CodedData"
                @change="selectOption(entry)" 
                :disabled="field.isEntryRestricted" 
                class="radio-input">
              <span>{{ entry.UserDataString || entry.CodedData }}</span>
            </label>
          </div>
        </div>
        
        <input v-if="specifyText" type="text" placeholder="Please specify..." class="specify-input" :disabled="field.isEntryRestricted">
      </div>

      <div v-else>
        <input type="text" :placeholder="`${field.ControlType} | ${field.DataFormat || 'No Format'}`" class="field-input-unknown" :disabled="field.isEntryRestricted">
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';

const props = defineProps({
  field: { type: Object, required: true },
  labelMode: { type: String, default: 'DraftFieldName' },
  previewMode: { type: String, default: 'dropdown' }
});

onMounted(() => { lucide.createIcons(); });

const isDropdownOpen = ref(false);
const selectedEntry = ref(null);

const selectedOptionLabel = computed(() => {
  if (!selectedEntry.value) return null;
  return selectedEntry.value.UserDataString || selectedEntry.value.CodedData;
});

const specifyText = computed(() => {
  return selectedEntry.value?.Specify ? selectedEntry.value.CodedData : null;
});

const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value;
  nextTick(() => { lucide.createIcons(); });
};

const selectOption = (entry) => {
  selectedEntry.value = entry;
  isDropdownOpen.value = false;
};
</script>

<style scoped>
.field-item { background-color: var(--background-secondary); padding: 20px; border-radius: 10px; border-left: 3px solid transparent; }
.field-item:hover { border-left-color: var(--border-accent); background-color: var(--background-interactive-hover); }
.field-label-container { margin-bottom: 8px; }
.field-label { font-weight: bold; color: var(--text-primary); font-size: 1.1rem; }
.field-header { display: flex; flex-direction: column; align-items: flex-start; gap: 8px; }
.field-oid-container { display: flex; align-items: center; gap: 8px; }
.prefix-symbol { color: #FF5555; font-weight: bold; font-size: 1.2rem; }
.field-oid-header { font-family: 'Courier New', Courier, monospace; font-size: 1rem; color: var(--text-accent); font-weight: bold; }
.field-pretext { font-size: 0.9rem; color: var(--text-secondary); background-color: var(--background-interactive); padding: 8px 12px; border-radius: 5px; display: flex; align-items: center; width: fit-content; margin-top: 0; }
.field-control-wrapper { margin-top: 15px; }
.field-input, .field-textarea, .field-input-unknown { width: 100%; max-width: 450px; background-color: var(--background-interactive); border: 1px solid var(--border-interactive); color: var(--text-primary); padding: 10px; border-radius: 5px; }
.field-input:focus, .field-textarea:focus { outline: none; border-color: var(--border-accent); }
.field-textarea { min-height: 80px; resize: vertical; }
.field-input-unknown { border-style: dashed; }
.entry-restricted { cursor: not-allowed; opacity: 0.6; }
.custom-dropdown { position: relative; width: 100%; max-width: 450px; }
.dropdown-trigger { display: flex; justify-content: space-between; align-items: center; width: 100%; background-color: var(--background-interactive); border: 1px solid var(--border-interactive); color: var(--text-primary); padding: 10px; border-radius: 5px; cursor: pointer; text-align: left; }
.dropdown-trigger:disabled { cursor: not-allowed; }
.dropdown-chevron { transition: transform 0.3s ease; }
.dropdown-chevron.rotate-180 { transform: rotate(180deg); }
.dropdown-panel { position: absolute; top: calc(100% + 5px); left: 0; width: 100%; background-color: var(--background-secondary); border: 1px solid var(--border-interactive); border-radius: 5px; z-index: 20; max-height: 200px; overflow-y: auto; box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
.dropdown-option { padding: 10px; color: var(--text-secondary); cursor: pointer; }
.dropdown-option:hover { background-color: var(--background-interactive-hover); color: var(--text-primary); }
.dropdown-enter-active, .dropdown-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; transform: translateY(-10px); }
.radio-group { display: flex; flex-direction: column; gap: 10px; }
.radio-option { display: flex; align-items: center; gap: 10px; }
.radio-label { display: flex; align-items: center; cursor: pointer; color: var(--text-secondary); }
.radio-label:hover { color: var(--text-primary); }
.radio-input { appearance: none; width: 18px; height: 18px; border: 2px solid var(--border-interactive); border-radius: 50%; margin-right: 8px; cursor: pointer; position: relative; flex-shrink: 0; }
.radio-input:checked { border-color: var(--text-accent); }
.radio-input:checked::after { content: ''; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 8px; height: 8px; border-radius: 50%; background: var(--text-accent); }
.specify-input { background: rgba(0,0,0,0.5); border: 1px solid #6d28d9; color: var(--text-primary); padding: 8px; border-radius: 5px; margin-top: 10px; width: 100%; max-width: 450px; }
html.light-theme .specify-input { background-color: #f3e8ff; border-color: #a855f7; }
</style>