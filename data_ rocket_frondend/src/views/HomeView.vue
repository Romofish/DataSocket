<template>
  <div class="w-full h-screen overflow-hidden flex flex-col items-center justify-center home-view-container">
    <div class="animated-background"></div>

    <header class="absolute top-0 left-0 w-full p-6 z-10">
        <h1 class="text-4xl font-bold text-center flex items-center justify-center tracking-widest header-title">
            <i data-lucide="hexagon" class="inline-block mr-4 text-cyan-400"></i>
            CLINICAL TOOLS PLATFORM
        </h1>
    </header>

    <div class="swiper-container">
        <div class="swiper-wrapper">
            <div class="swiper-slide">
                <div class="tool-card">
                    <div class="h-48 flex items-center justify-center card-icon-bg" style="background: linear-gradient(to top right, #6d28d9, #4f46e5);">
                        <i data-lucide="file-spreadsheet" class="w-20 h-20 text-white opacity-80"></i>
                    </div>
                    <div class="p-6 flex-grow flex flex-col card-content">
                        <h3 class="text-3xl font-bold mb-2">ALS Reader</h3>
                        <p class="mb-4 flex-grow card-description">解析并清晰地展示您的 Architect Loader Sheet (ALS) 文件结构。</p>
                        <button @click="goToAlsReader" class="w-full bg-indigo-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-indigo-500 transition-colors glow-button" style="color:#fff; box-shadow-color: #6d28d9;">启动工具</button>
                    </div>
                </div>
            </div>
            
            <div class="swiper-slide">
                <div class="tool-card border-2 border-cyan-400" style="box-shadow: 0 0 25px rgba(0, 255, 255, 0.3);">
                    <div class="h-48 flex items-center justify-center card-icon-bg" style="background: linear-gradient(to top right, #f59e0b, #d97706);">
                        <i data-lucide="git-compare-arrows" class="w-20 h-20 text-white opacity-80"></i>
                    </div>
                    <div class="p-6 flex-grow flex flex-col card-content">
                        <h3 class="text-3xl font-bold mb-2">ALS Compare Tool</h3>
                        <p class="mb-4 flex-grow card-description">比对不同版本的 ALS 文件，高亮显示差异，追踪研究变更。</p>
                        <button class="w-full bg-amber-500 text-white font-bold py-3 px-4 rounded-lg hover:bg-amber-400 transition-colors glow-button" style="color:#fff; box-shadow-color: #f59e0b;">启动工具</button>
                    </div>
                </div>
            </div>

            <div class="swiper-slide">
                <div class="tool-card coming-soon">
                    <div class="h-48 flex items-center justify-center card-icon-bg" style="background: linear-gradient(to top right, #52525b, #3f3f46);">
                        <i data-lucide="file-text" class="w-20 h-20 text-white opacity-50"></i>
                    </div>
                    <div class="p-6 flex-grow flex flex-col relative card-content">
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
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

onMounted(() => {
  // We still need to create icons for this specific view
  lucide.createIcons();

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

const goToAlsReader = () => {
   router.push('/als-reader'); 
};
</script>

<style scoped>
.home-view-container {
  background-color: var(--background-primary);
}
.header-title {
  color: var(--text-primary);
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
html.light-theme .animated-background {
    display: none;
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
    background: var(--background-secondary);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border-radius: 20px;
    border: 1px solid var(--border-primary);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    height: 100%;
}
.card-content {
    color: var(--text-primary);
}
.card-description {
    color: var(--text-secondary);
}
.tool-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 16px 40px 0 rgba(0, 0, 0, 0.5);
    border: 1px solid var(--border-accent);
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
}
.glow-button:hover {
    box-shadow: 0 0 10px, 0 0 25px, 0 0 50px;
}
.swiper-pagination-bullet {
    background: var(--text-accent) !important;
    opacity: 0.5;
}
.swiper-pagination-bullet-active {
    opacity: 1;
}
</style>