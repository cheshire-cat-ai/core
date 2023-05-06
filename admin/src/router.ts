import { createRouter, createWebHistory } from 'vue-router'
import SettingsView from '@views/SettingsView.vue'
import PluginsView from '@views/PluginsView.vue'

const router = createRouter({
  linkExactActiveClass: "active",
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('@views/HomeView.vue')
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView
    },
    {
      path: '/plugins',
      name: 'plugins',
      component: PluginsView
    }
  ]
})

export default router
