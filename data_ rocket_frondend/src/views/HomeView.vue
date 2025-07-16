<template>
  <div class="w-full h-screen overflow-hidden flex flex-col items-center justify-center">
    <div class="animated-background"></div>

    <header class="absolute top-0 left-0 w-full p-6 z-10">
        <h1 class="text-4xl font-bold text-white text-center flex items-center justify-center tracking-widest">
            <i data-lucide="hexagon" class="inline-block mr-4 text-cyan-400"></i>
            CLINICAL TOOLS PLATFORM
        </h1>
    </header>

    <div class="swiper-container">
        <div class="swiper-wrapper">
            <!-- 卡片 1: ALS Reader -->
            <div class="swiper-slide">
                <div class="tool-card">
                    <div class="h-48 flex items-center justify-center" style="background: linear-gradient(to top right, #6d28d9, #4f46e5);">
                        <i data-lucide="file-spreadsheet" class="w-20 h-20 text-white opacity-80"></i>
                    </div>
                    <div class="p-6 flex-grow flex flex-col text-white">
                        <h3 class="text-3xl font-bold mb-2">ALS Reader</h3>
                        <p class="text-gray-300 mb-4 flex-grow">解析并清晰地展示您的 Architect Loader Sheet (ALS) 文件结构。</p>
                        <button @click="goToAlsReader" class="w-full bg-indigo-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-indigo-500 transition-colors glow-button" style="color:#fff; box-shadow-color: #6d28d9;">启动工具</button>
                    </div>
                </div>
            </div>
            
            <!-- 卡片 2: Compare Tool -->
            <div class="swiper-slide">
                <div class="tool-card border-2 border-cyan-400" style="box-shadow: 0 0 25px rgba(0, 255, 255, 0.3);">
                    <div class="h-48 flex items-center justify-center" style="background: linear-gradient(to top right, #f59e0b, #d97706);">
                        <i data-lucide="git-compare-arrows" class="w-20 h-20 text-white opacity-80"></i>
                    </div>
                    <div class="p-6 flex-grow flex flex-col text-white">
                        <h3 class="text-3xl font-bold mb-2">ALS Compare Tool</h3>
                        <p class="text-gray-300 mb-4 flex-grow">比对不同版本的 ALS 文件，高亮显示差异，追踪研究变更。</p>
                        <button class="w-full bg-amber-500 text-white font-bold py-3 px-4 rounded-lg hover:bg-amber-400 transition-colors glow-button" style="color:#fff; box-shadow-color: #f59e0b;">启动工具</button>
                    </div>
                </div>
            </div>

            <!-- 卡片 3: Protocol Reader (Coming Soon) -->
            <div class="swiper-slide">
                <div class="tool-card coming-soon">
                    <div class="h-48 flex items-center justify-center" style="background: linear-gradient(to top right, #52525b, #3f3f46);">
                        <i data-lucide="file-text" class="w-20 h-20 text-white opacity-50"></i>
                    </div>
                    <div class="p-6 flex-grow flex flex-col relative text-white">
                         <div class="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-gray-700 text-white px-3 py-1 rounded-full text-sm font-bold">即将推出</div>
                        <h3 class="text-3xl font-bold mb-2 text-gray-400">Protocol Reader</h3>
                        <p class="text-gray-400 mb-4 flex-grow">智能解析临床试验方案，快速提取关键信息。</p>
                        <button class="w-full bg-gray-600 text-gray-400 font-bold py-3 px-4 rounded-lg cursor-not-allowed">敬请期待</button>
                    </div>
                </div>
            </div>
        </div>
        <div class="swiper-pagination"></div>
    </div>

    <!-- AI 聊天按钮 -->
    <div id="ai-chat-button">
        <button @click="toggleChat" class="w-24 h-24 flex items-center justify-center group">
            <div class="robot-container floating-robot">
                <svg width="80" height="80" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <g>
                        <path d="M78.5 45.5C87.0604 45.5 94 52.4396 94 61V73C94 77.4183 90.4183 81 86 81H69.5" stroke="#00FFFF" stroke-width="4" stroke-linecap="round"/>
                        <path d="M21.5 45.5C12.9396 45.5 6 52.4396 6 61V73C6 77.4183 9.58172 81 14 81H30.5" stroke="#00FFFF" stroke-width="4" stroke-linecap="round"/>
                        <rect x="22" y="34" width="56" height="54" rx="27" fill="#24243e" stroke="#00FFFF" stroke-width="4"/>
                        <rect x="36" y="52" width="8" height="8" rx="4" fill="#00FFFF"/>
                        <rect x="56" y="52" width="8" height="8" rx="4" fill="#00FFFF"/>
                        <path d="M36 70C36 67.2386 38.2386 65 41 65H59C61.7614 65 64 67.2386 64 70" stroke="#00FFFF" stroke-width="3" stroke-linecap="round"/>
                        <path d="M50 34V20C50 16.6863 47.3137 14 44 14H42C38.6863 14 36 16.6863 36 20V22" stroke="#00FFFF" stroke-width="4" stroke-linecap="round"/>
                        <circle cx="34" cy="22" r="3" fill="#00FFFF"/>
                    </g>
                </svg>
            </div>
        </button>
    </div>

    <!-- AI 聊天窗口 -->
    <div id="ai-chat-window" :class="{ 'active': isChatOpen }">
      <!-- ... (聊天窗口的 HTML 保持不变) ... -->
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isChatOpen = ref(false);

// 在组件挂载后（即 HTML 渲染到页面后）执行
onMounted(() => {
  // 初始化 Lucide Icons
  lucide.createIcons();

  // 初始化 Swiper
  new Swiper('.swiper-container', {
      effect: 'coverflow',
      grabCursor: true,
      centeredSlides: true,
      slidesPerView: 'auto',
      coverflowEffect: {
          rotate: 30,
          stretch: 0,
          depth: 150,
          modifier: 1,
          slideShadows: true,
      },
      pagination: {
          el: '.swiper-pagination',
          clickable: true,
      },
      initialSlide: 1,
  });
});

const toggleChat = () => {
  isChatOpen.value = !isChatOpen.value;
};

// 点击“启动工具”按钮时，跳转到 ALS Reader 页面
const goToAlsReader = () => {
   router.push('/als-reader'); 
};
</script>

<style scoped>
/* 将 v3 原型中的所有 <style> 内容复制到这里 */
body, html {
  background-color: #0f0c29;
}
body {
    font-family: 'Rajdhani', sans-serif;
    color: #e0e0e0;
}
.animated-background {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
    background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1c1c3c);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.swiper-container {
    width: 100%;
    height: 100%;
    padding-top: 80px;
    padding-bottom: 80px;
}
.swiper-slide {
    width: 340px;
    height: 480px;
    transition: transform 0.5s;
    background: transparent;
}
.tool-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    height: 100%;
    transition: all 0.3s ease;
}
.tool-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 16px 40px 0 rgba(0, 0, 0, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.4);
}
.tool-card.coming-soon {
    filter: grayscale(50%);
    opacity: 0.6;
}
.swiper-slide-shadow-left, .swiper-slide-shadow-right {
    border-radius: 20px;
}
.glow-button {
    box-shadow: 0 0 5px, 0 0 15px, 0 0 25px;
    transition: all 0.3s ease;
}
.glow-button:hover {
    box-shadow: 0 0 10px, 0 0 25px, 0 0 50px;
}
#ai-chat-button {
    position: fixed;
    bottom: 30px;
    right: 30px;
    z-index: 1000;
}
#ai-chat-button .robot-container {
    transition: transform 0.3s ease;
}
#ai-chat-button:hover .robot-container {
    transform: scale(1.1);
}
@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
    100% { transform: translateY(0px); }
}
.floating-robot {
    animation: float 4s ease-in-out infinite;
}
#ai-chat-window {
    position: fixed;
    bottom: 100px;
    right: 30px;
    width: 380px;
    height: 500px;
    z-index: 999;
    transition: all 0.3s ease-in-out;
    transform: translateY(20px) scale(0.95);
    opacity: 0;
    pointer-events: none;
    background: rgba(30, 30, 50, 0.8);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.2);
}
#ai-chat-window.active {
    transform: translateY(0) scale(1);
    opacity: 1;
    pointer-events: auto;
}
/* Swiper pagination color */
.swiper-pagination-bullet {
    background: rgba(0, 255, 255, 0.5) !important;
}
.swiper-pagination-bullet-active {
    background: #00FFFF !important;
}
</style>
