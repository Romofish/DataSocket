import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
// 🧩 1. 导入你的 LoginView 组件
import LoginView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },

    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/als-reader',
      name: 'als-reader',
      component: () => import('../views/AlsReaderView.vue')
    },

    {
      path: '/matrix',
      name: 'matrix',
      component: () => import('../views/MatrixReview.vue')
    },

    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
  ],
})

export default router
