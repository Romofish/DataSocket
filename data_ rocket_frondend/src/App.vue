<template>
  <div id="app-wrapper">
    <RouterView />

    <div class="global-actions-top-left">
      <button @click="goHome" class="action-button" title="Back to Home">
        <i data-lucide="home"></i>
      </button>
    </div>

    <div class="persistent-buttons-bottom-right">
      <ThemeToggleButton />
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
    </div>

    <div id="ai-chat-window" :class="{ 'active': isChatOpen }">
      <div class="p-4 text-center text-white">AI Chat Window Content</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { RouterView, useRouter } from 'vue-router'; // 导入 useRouter
import ThemeToggleButton from './components/ThemeToggleButton.vue';
import { useThemeStore } from './stores/themeStore';

useThemeStore();

const router = useRouter(); // 初始化 router
const isChatOpen = ref(false);

const toggleChat = () => {
  isChatOpen.value = !isChatOpen.value;
};

// 返回主页的函数
const goHome = () => {
  router.push('/');
};

onMounted(() => {
  lucide.createIcons();
});
</script>

<style scoped>
.global-actions-top-left {
    position: fixed;
    top: 20px;
    left: 20px;
    z-index: 1000;
}
.action-button {
  background-color: var(--background-interactive);
  color: var(--text-secondary);
  border: 1px solid var(--border-interactive);
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
}
.action-button:hover {
  transform: scale(1.1);
  border-color: var(--border-accent);
  color: var(--text-accent);
}

.persistent-buttons-bottom-right {
    position: fixed;
    bottom: 30px;
    right: 30px;
    z-index: 1000;
    display: flex;
    flex-direction: column;
    gap: 15px;
    align-items: center;
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
    bottom: 180px; /* 调整位置以避开按钮 */
    right: 30px;
    width: 380px;
    height: 500px;
    z-index: 999;
    transition: all 0.3s ease-in-out;
    transform: translateY(20px) scale(0.95);
    opacity: 0;
    pointer-events: none;
    background-color: var(--background-secondary-translucent);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    border: 1px solid var(--border-primary);
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}
#ai-chat-window.active {
    transform: translateY(0) scale(1);
    opacity: 1;
    pointer-events: auto;
}
</style>