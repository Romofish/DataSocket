import { defineStore } from 'pinia';
import * as XLSX from 'xlsx';

// Helper function to safely split comma-separated strings
const safeSplit = (str) => {
  if (typeof str === 'string' && str.length > 0) {
    return str.split(',').map(s => s.trim());
  }
  return [];
};

export const useAlsStore = defineStore('als', {
  state: () => ({
    isParsed: false,
    fileName: '',
    sheets: {
      forms: [],
      fields: [],
      dataDictionaries: [],
      dataDictionaryEntries: [],
    },
  }),

  getters: {
  /**
    * From Fields 表中提取所有出现过的独立角色
    * @param {object} state - The store's state.
    * @returns {Array<string>} An array of unique role names.
    */
  getAllRoles: (state) => {
    if (!state.isParsed) return [];
    const roles = new Set();
    state.sheets.fields.forEach(field => {
      safeSplit(field.ViewRestrictions).forEach(role => roles.add(role));
      safeSplit(field.EntryRestrictions).forEach(role => roles.add(role));
    });
    // 返回一个包含 'All' 作为默认选项的排序后的角色列表
    return ['All', ...Array.from(roles).sort()];
  },

  /**
    * 根据 Form OID 和当前选择的角色，获取处理过的字段列表
    * @param {object} state - The store's state.
    * @returns {function(string, string): Array<object>} A function that takes formOid and selectedRole.
    */
  getFieldsForPreview: (state) => {
    return (formOid, selectedRole = 'All') => {
      if (!formOid || !state.isParsed) return [];
      
      const relatedFields = state.sheets.fields.filter(field => field.FormOID === formOid);

      return relatedFields
        .map(field => {
          // 1. 权限处理
          const viewRoles = safeSplit(field.ViewRestrictions);
          const entryRoles = safeSplit(field.EntryRestrictions);
          
          const isVisible = selectedRole === 'All' || !viewRoles.includes(selectedRole);
          const isEntryRestricted = selectedRole !== 'All' && entryRoles.includes(selectedRole);

          // 2. 特殊标识处理
          let prefix = '';
          if (field.IsRequired === 'Yes') prefix += '*';
          if (field.QueryFutureDate === 'Yes') prefix += '#';
          if (field.QueryNonConformance === 'Yes') prefix += '^';
          if (field.DoesNotBreakSignature === 'No') prefix += '$';

          // 3. 数据字典关联 (FIXED LOGIC)
          let entries = [];
          if (field.DataDictionaryName) {
            entries = state.sheets.dataDictionaryEntries
              .filter(e => e.DataDictionaryName === field.DataDictionaryName)
              .map(e => ({
                ...e,
                // 将 'Yes'/'TRUE' 等统一处理为布尔值
                Specify: ['yes', 'true'].includes(String(e.Specify).toLowerCase()),
              }))
              .sort((a, b) => a.Order - b.Order);
          }

          return {
            ...field,
            displayPrefix: prefix,
            dictionaryEntries: entries,
            isVisible,
            isEntryRestricted,
          };
        })
        .filter(field => field.isVisible) // 只返回可见的字段
        .sort((a, b) => a.Ordinal - b.Ordinal);
    };
  },
},


  actions: {
    async parseFile(file) {
      this.fileName = file.name;
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data);
      const requiredSheets = ['Forms', 'Fields', 'DataDictionaries', 'DataDictionaryEntries'];

      for (const sheetName of requiredSheets) {
        const sheet = workbook.Sheets[sheetName];
        const stateKey = sheetName.charAt(0).toLowerCase() + sheetName.slice(1);
        if (sheet) {
          this.sheets[stateKey] = XLSX.utils.sheet_to_json(sheet);
          console.log(`成功解析: ${sheetName}`);
        } else {
          this.sheets[stateKey] = []; // 如果工作表不存在，则设置为空数组
          console.warn(`警告: 在文件中未找到工作表 "${sheetName}"`);
        }
      }
      this.isParsed = true;
    },
    reset() {
      this.$reset();
    }
  },
});
