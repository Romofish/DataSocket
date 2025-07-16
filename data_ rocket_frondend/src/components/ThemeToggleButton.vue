<template>
  <button @click="themeStore.toggleTheme" class="theme-toggle-button" :title="'Switch to ' + (themeStore.theme === 'dark' ? 'light' : 'dark') + ' mode'">
    <i data-lucide="sun" v-if="themeStore.theme === 'dark'"></i>
    <i data-lucide="moon" v-else></i>
  </button>
</template>

<script setup>
import { onMounted } from 'vue';
import { useThemeStore } from '@/stores/themeStore';

const themeStore = useThemeStore();

onMounted(() => {
  lucide.createIcons();
});
</script>

<style scoped>
.theme-toggle-button {
  background-color: var(--background-interactive);
  color: var(--text-secondary);
  border: 1px solid var(--border-interactive);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
}
.theme-toggle-button:hover {
  transform: scale(1.1);
  border-color: var(--border-accent);
  color: var(--text-accent);
}
</style>