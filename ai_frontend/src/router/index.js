import { createRouter, createWebHistory } from 'vue-router';
// 确保这两个文件存在于 views 文件夹下
import ChatBoard from '../views/ChatBoard.vue';
import KnowledgeBase from '../views/KnowledgeBase.vue';

const routes = [
  { 
    path: '/', 
    name: 'Chat',
    component: ChatBoard,
    props: true // 允许传参
  },
  { 
    path: '/kb', 
    name: 'KnowledgeBase',
    component: KnowledgeBase 
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;