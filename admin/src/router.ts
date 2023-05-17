import { createRouter, createWebHistory } from 'vue-router'
import SettingsView from '@views/SettingsView.vue'
import ErrorView from '@views/ErrorView.vue'
import PluginsView from '@views/PluginsView.vue'
import MemoryView from '@views/MemoryView.vue'

const router = createRouter({
  linkExactActiveClass: "active",
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      // Lazy-load when the route is visited.
      component: () => import('@views/HomeView.vue')
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView,
      children: [
        { 
          path: '',
          name: 'providers',
          // Lazy-load when the route is visited.
          component: () => import('@views/ProvidersView.vue')
        },
        { 
          path: '',
          name: 'embedders',
          // Lazy-load when the route is visited.
          component: () => import('@views/EmbeddersView.vue')
        },
      ],
    },
    {
      path: '/memory',
      name: 'memory',
      component: MemoryView
    },
    {
      path: '/plugins',
      name: 'plugins',
      component: PluginsView
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'error',
      component: ErrorView,
    }
  ]
})

export default router
