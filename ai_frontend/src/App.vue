<template>
  <!-- 1. 未登录状态：显示登录组件 -->
  <Login v-if="!isLoggedIn" @login-success="handleLoginSuccess" />

  <!-- 2. 已登录状态：主布局 -->
  <div v-else class="flex h-screen bg-gray-50 text-slate-800 font-sans overflow-hidden">
    
    <!-- 左侧边栏 (清爽白色风格) -->
    <aside 
      class="bg-white border-r border-gray-200 flex flex-col transition-all duration-300 z-30 h-full flex-shrink-0 absolute lg:relative"
      :class="isSidebarOpen ? 'w-64 translate-x-0 shadow-xl lg:shadow-none' : '-translate-x-full lg:w-0 lg:translate-x-0 lg:overflow-hidden lg:opacity-0'"
    >
      <!-- Logo区域 -->
      <div class="p-5 border-b border-gray-100 flex items-center gap-3 bg-white">
        <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center font-bold text-lg text-white shadow-sm shadow-blue-200">AI</div>
        <span class="font-bold text-lg text-gray-700 tracking-wide">全能助手</span>
        <!-- 移动端关闭按钮 -->
        <button @click="isSidebarOpen = false" class="lg:hidden ml-auto text-gray-400 hover:text-gray-600 p-1">
          <XMarkIcon class="w-6 h-6"/>
        </button>
      </div>

      <!-- 新建会话按钮 -->
      <div class="p-5 pb-2">
        <button 
          @click="handleNewChat"
          class="w-full flex items-center justify-center gap-2 bg-blue-50 text-blue-600 border border-blue-200 hover:bg-blue-600 hover:text-white hover:border-blue-600 py-2.5 rounded-xl transition-all font-medium active:scale-95 group shadow-sm"
        >
          <PlusIcon class="w-5 h-5 transition-transform group-hover:rotate-90" />
          <span>新建对话</span>
        </button>
      </div>

      <!-- 导航菜单区 (知识库) -->
      <div class="px-3 mt-2">
        <router-link 
          to="/kb" 
          class="flex items-center gap-3 p-3 rounded-xl text-gray-600 hover:bg-gray-100 hover:text-blue-600 transition-colors"
          active-class="bg-gray-100 text-blue-700 font-bold"
          @click="handleNavClick"
        >
          <ArchiveBoxIcon class="w-5 h-5" />
          <span class="text-sm">知识库管理</span>
        </router-link>
      </div>

      <!-- 会话列表 (Scroll) -->
      <div class="flex-1 overflow-y-auto px-3 py-2 space-y-1 mt-2 border-t border-gray-50 custom-scrollbar">
        <h3 class="text-xs font-bold text-gray-400 px-3 mb-2 uppercase tracking-wider flex justify-between items-center">
          历史会话
          <span class="text-[10px] bg-gray-100 px-1.5 py-0.5 rounded-full text-gray-500">{{ sessions.length }}</span>
        </h3>
        
        <div 
          v-for="session in sessions" 
          :key="session.id"
          @click="selectSession(session.id)"
          class="group relative flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-all border border-transparent"
          :class="currentSessionId === session.id && $route.path === '/' ? 'bg-blue-600 text-white shadow-md shadow-blue-200' : 'text-gray-600 hover:bg-gray-100'"
        >
          <ChatBubbleLeftIcon 
            class="w-5 h-5 flex-shrink-0 transition-colors" 
            :class="currentSessionId === session.id && $route.path === '/' ? 'text-white' : 'text-gray-400 group-hover:text-blue-500'" 
          />
          
          <!-- 编辑标题输入框 -->
          <input 
            v-if="editingSessionId === session.id"
            v-model="session.title"
            @blur="saveTitle(session)"
            @keydown.enter="saveTitle(session)"
            @click.stop
            ref="titleInput"
            class="bg-white text-gray-800 text-sm px-2 py-0.5 rounded w-full outline-none border-2 border-blue-400 shadow-sm"
          />
          <!-- 标题显示 -->
          <span v-else class="text-sm truncate flex-1 font-medium">{{ session.title }}</span>

          <!-- 悬浮操作按钮组 -->
          <div 
            class="absolute right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity p-0.5 rounded-lg"
            :class="currentSessionId === session.id && $route.path === '/' ? '' : 'bg-white shadow-sm border border-gray-100'"
          >
            <button 
              @click.stop="startEdit(session)" 
              class="p-1.5 rounded-md transition-colors" 
              :class="currentSessionId === session.id ? 'hover:bg-blue-500 text-blue-100' : 'hover:bg-gray-100 text-gray-400 hover:text-blue-500'" 
              title="重命名"
            >
              <PencilSquareIcon class="w-3.5 h-3.5" />
            </button>
            <button 
              @click.stop="deleteSession(session.id)" 
              class="p-1.5 rounded-md transition-colors" 
              :class="currentSessionId === session.id ? 'hover:bg-blue-500 text-blue-100' : 'hover:bg-gray-100 text-gray-400 hover:text-red-500'" 
              title="删除"
            >
              <TrashIcon class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
        
        <!-- 空状态提示 -->
        <div v-if="sessions.length === 0" class="text-center py-10 text-gray-400 text-xs">
          暂无历史会话
        </div>
      </div>

      <!-- 底部用户信息 -->
      <div class="p-4 border-t border-gray-100 bg-gray-50/30">
        <div class="flex items-center gap-3 group cursor-pointer p-2 rounded-xl hover:bg-white hover:shadow-sm transition-all border border-transparent hover:border-gray-100" @click="logout" title="点击退出登录">
          <div class="w-9 h-9 rounded-full bg-gradient-to-tr from-blue-500 to-cyan-400 flex items-center justify-center text-sm font-bold text-white shadow-sm ring-2 ring-white">
            {{ username.slice(0,1).toUpperCase() }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-bold text-gray-700 truncate group-hover:text-blue-600 transition-colors">{{ username }}</p>
            <p class="text-xs text-gray-400 flex items-center gap-1 group-hover:text-red-500 transition-colors mt-0.5">
              <ArrowRightOnRectangleIcon class="w-3 h-3" /> 退出登录
            </p>
          </div>
        </div>
      </div>
    </aside>

    <!-- 移动端遮罩层 -->
    <div 
      v-if="isSidebarOpen" 
      @click="isSidebarOpen = false" 
      class="fixed inset-0 bg-slate-900/20 backdrop-blur-sm z-20 lg:hidden transition-opacity"
    ></div>

    <!-- 右侧内容区 (路由出口) -->
    <main class="flex-1 h-full relative overflow-hidden bg-white w-full">
      <router-view 
        :currentSessionId="currentSessionId" 
        :sessions="sessions"
        @toggle-sidebar="isSidebarOpen = !isSidebarOpen"
        @session-updated="handleSessionUpdate"
        @refresh-sessions="loadSessions"
      ></router-view>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import Login from './components/Login.vue';
import api from './api';
import { 
  ChatBubbleLeftIcon, PlusIcon, ArchiveBoxIcon, ArrowRightOnRectangleIcon, 
  PencilSquareIcon, TrashIcon, XMarkIcon 
} from '@heroicons/vue/24/outline';

const router = useRouter();
const route = useRoute();

const isLoggedIn = ref(false);
const username = ref('');
// 默认在PC端展开，移动端收起
const isSidebarOpen = ref(window.innerWidth > 1024);
const sessions = ref([]);
const currentSessionId = ref(null);
const editingSessionId = ref(null);
const titleInput = ref(null);

// --- 初始化与认证 ---
onMounted(() => {
  const token = localStorage.getItem('token');
  if (token) {
    username.value = localStorage.getItem('username') || 'User';
    isLoggedIn.value = true;
    loadSessions();
  }
});

const handleLoginSuccess = () => {
  username.value = localStorage.getItem('username');
  isLoggedIn.value = true;
  loadSessions();
};

const logout = () => {
  if(!confirm('确定要退出登录吗？')) return;
  localStorage.removeItem('token');
  isLoggedIn.value = false;
  sessions.value = [];
  currentSessionId.value = null;
  router.push('/');
};

// --- 核心会话逻辑 ---

// 加载会话列表
const loadSessions = async () => {
  try {
    const { data } = await api.getSessions();
    sessions.value = data;
    
    // 如果当前没有选中会话，且列表不为空，自动选中最新的一个
    if (!currentSessionId.value && sessions.value.length > 0) {
      currentSessionId.value = sessions.value[0].id;
    }
  } catch (e) {
    console.error("加载会话失败:", e);
    if(e.response && e.response.status === 401) logout();
  }
};

// 新建对话
const handleNewChat = async () => {
  try {
    const { data } = await api.createSession();
    // 1. 添加到列表最前
    sessions.value.unshift(data);
    // 2. 选中新会话
    currentSessionId.value = data.id;
    // 3. 确保跳转回聊天页
    router.push('/');
    // 4. 移动端收起侧边栏
    if(window.innerWidth < 1024) isSidebarOpen.value = false;
  } catch (e) {
    console.error(e);
    alert('新建会话失败: ' + (e.response?.data?.detail || e.message));
  }
};

// 选中会话
const selectSession = (id) => {
  currentSessionId.value = id;
  router.push('/'); // 确保在聊天页
  if(window.innerWidth < 1024) isSidebarOpen.value = false;
};

// 删除会话
const deleteSession = async (id) => {
  if (!confirm('确认删除该会话？聊天记录将无法恢复。')) return;
  
  try {
    await api.deleteSession(id);
    
    // 从列表中移除
    sessions.value = sessions.value.filter(s => s.id !== id);
    
    // 如果删除的是当前选中的会话
    if (currentSessionId.value === id) {
      if (sessions.value.length > 0) {
        // 还有其他会话，选中第一个
        currentSessionId.value = sessions.value[0].id;
      } else {
        // 没有会话了，置空
        currentSessionId.value = null;
        // 可选：自动新建一个
        // handleNewChat(); 
      }
    }
  } catch (e) { 
    console.error(e);
    alert('删除失败: ' + (e.response?.data?.detail || '网络错误'));
  }
};

// 移动端点击导航链接后自动收起
const handleNavClick = () => {
  if(window.innerWidth < 1024) isSidebarOpen.value = false;
};

// --- 标题编辑逻辑 ---
const startEdit = (session) => {
  editingSessionId.value = session.id;
  // 等待 DOM 更新后聚焦输入框
  nextTick(() => {
    if(titleInput.value && titleInput.value[0]) {
      titleInput.value[0].focus();
    }
  });
};

const saveTitle = async (session) => {
  editingSessionId.value = null;
  const oldTitle = session.title;
  // 如果为空，设置默认值
  if (!session.title || !session.title.trim()) {
    session.title = "无标题会话";
  }
  
  try {
    await api.updateSessionTitle(session.id, session.title);
  } catch (e) { 
    console.error(e);
    session.title = oldTitle; // 失败回滚
    alert("重命名失败");
  }
};

// 监听子组件（如聊天窗口）传来的更新事件（如自动生成标题）
const handleSessionUpdate = ({ id, title }) => {
  const s = sessions.value.find(s => s.id === id);
  if (s) s.title = title;
};
</script>

<style>
/* 自定义细滚动条 */
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 2px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}
</style>