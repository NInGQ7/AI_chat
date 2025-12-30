import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router' // 必须引入 router

const app = createApp(App)
app.use(router) // 必须挂载
app.mount('#app')