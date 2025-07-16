<template>
  <div class="als-reader-container">
    <!-- 返回主页的按钮 -->
    <button @click="goHome" class="back-button">
      <i data-lucide="arrow-left" class="mr-2"></i>
      返回主页
    </button>

    <div class="content-wrapper">
      <header class="mb-8 text-center">
        <h1 class="text-5xl font-bold text-white">ALS Reader</h1>
        <p class="text-gray-400 mt-2 text-lg">上传您的 Medidata Rave Architect Loader Sheet (ALS) 文件</p>
      </header>

      <!-- 文件上传区域 -->
      <div class="upload-section">
        <div @click="triggerFileInput" @dragover.prevent @drop.prevent="handleFileDrop" class="upload-box">
          <div class="flex justify-center mb-6">
            <div class="upload-icon-wrapper">
              <i data-lucide="upload-cloud" class="w-16 h-16 text-cyan-300"></i>
            </div>
          </div>
          <h3 class="text-2xl font-semibold text-white">点击此处或拖拽文件上传</h3>
          <p class="text-gray-400 mt-2">请选择一个 .xlsx 格式的 ALS 文件</p>
          <input type="file" ref="fileInput" @change="handleFileSelect" class="hidden" accept=".xlsx, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet">
        </div>

        <!-- 文件信息和进度条 -->
        <div v-if="fileName" class="mt-6 text-white">
          <p>已选择文件: {{ fileName }}</p>
          <!-- 可以在这里添加解析进度条 -->
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import * as XLSX from 'xlsx';

const router = useRouter();
const fileInput = ref(null);
const fileName = ref('');

onMounted(() => {
  // 确保图标在页面加载后渲染
  lucide.createIcons();
});

const goHome = () => {
  router.push('/');
};

const triggerFileInput = () => {
  fileInput.value.click();
};

const handleFileSelect = (event) => {
  const file = event.target.files[0];
  if (file) {
    processFile(file);
  }
};

const handleFileDrop = (event) => {
  const file = event.dataTransfer.files[0];
  if (file) {
    processFile(file);
  }
};

const processFile = (file) => {
  fileName.value = file.name;
  console.log(`准备解析文件: ${file.name}`);

  const reader = new FileReader();
  reader.onload = (e) => {
    const data = new Uint8Array(e.target.result);
    const workbook = XLSX.read(data, { type: 'array' });

    // 示例：打印出所有工作表的名称
    console.log('文件中的工作表 (Sheets):', workbook.SheetNames);

    // 示例：读取 "Forms" 工作表的内容
    const formsSheet = workbook.Sheets['Forms'];
    if (formsSheet) {
      const formsJson = XLSX.utils.sheet_to_json(formsSheet);
      console.log('--- Forms 工作表内容 ---');
      console.table(formsJson);
      alert(`成功解析文件！在浏览器的开发者工具(F12)的Console中查看 "Forms" 表的内容。`);
    } else {
      alert('在文件中没有找到名为 "Forms" 的工作表！');
    }
  };
  reader.readAsArrayBuffer(file);
};
</script>

<style scoped>
.als-reader-container {
  min-height: 100vh;
  background: #0f0c29;
  padding: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}
.back-button {
  position: absolute;
  top: 40px;
  left: 40px;
  display: flex;
  align-items: center;
  padding: 10px 20px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-weight: bold;
  transition: all 0.3s ease;
}
.back-button:hover {
  background: rgba(0, 255, 255, 0.2);
}
.content-wrapper {
  width: 100%;
  max-width: 800px;
}
.upload-section {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  padding: 40px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}
.upload-box {
  border: 2px dashed rgba(0, 255, 255, 0.4);
  border-radius: 15px;
  padding: 60px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}
.upload-box:hover {
  border-color: #00FFFF;
  background: rgba(0, 255, 255, 0.05);
}
.upload-icon-wrapper {
  display: inline-flex;
  padding: 20px;
  border-radius: 50%;
  background: rgba(0, 255, 255, 0.1);
  margin-bottom: 20px;
}
</style>
