import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from '@/App.vue'
import router from '@/router'

import 'unfonts.css'
import 'animate.css'
import '@assets/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
