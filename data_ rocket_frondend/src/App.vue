<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <!-- 
    RouterView 是一个占位符组件，
    它会根据当前的网址，自动显示对应的页面组件 (比如我们的 HomeView)。
  -->
  <RouterView />
</template>

<style>
/* 这里是全局样式区域。
  我们之前删除的 base.css 和 main.css 的内容，
  实际上已经被 HomeView.vue 里的 <style scoped> 替代了。
  所以这里暂时保持为空。
*/
</style>
