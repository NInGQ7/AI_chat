<template>
  <div class="flex flex-col h-full bg-white relative">
    <!-- 顶部导航栏 -->
    <header class="h-16 bg-white border-b border-gray-100 flex items-center justify-between px-6 z-10 flex-shrink-0">
      <div class="flex items-center gap-4">
        <!-- 移动端侧边栏切换 -->
        <button @click="$emit('toggle-sidebar')" class="lg:hidden p-2 hover:bg-gray-50 rounded-full text-gray-500">
          <Bars3Icon class="w-6 h-6" />
        </button>
        <h1 class="font-bold text-gray-700 text-lg truncate max-w-[200px]">{{ currentTitle || 'AI 全能助手' }}</h1>
      </div>

      <!-- 功能开关 -->
      <div class="flex items-center gap-6">
        <label class="flex items-center gap-2 cursor-pointer select-none group">
          <span class="text-xs font-semibold text-gray-500 group-hover:text-blue-600 transition-colors">联网</span>
          <div class="relative inline-flex items-center">
            <input type="checkbox" v-model="config.webSearchEnabled" class="sr-only peer">
            <div class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-500"></div>
          </div>
        </label>
        <!--
        <label class="flex items-center gap-2 cursor-pointer select-none group">
          <span class="text-xs font-semibold text-gray-500 group-hover:text-purple-600 transition-colors">深度思考</span>
          <div class="relative inline-flex items-center">
            <input type="checkbox" v-model="config.knowledgeBaseEnabled" class="sr-only peer">
            <div class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-purple-600"></div>
          </div>
        </label>
        -->
      </div>
    </header>

    <!-- 消息列表 -->
    <div ref="chatContainer" class="flex-1 overflow-y-auto p-4 sm:p-8 space-y-8 scroll-smooth">
      <!-- 空状态 -->
      <div v-if="!currentSessionId" class="flex flex-col items-center justify-center h-full text-gray-300">
        <ChatBubbleLeftEllipsisIcon class="w-16 h-16 mb-4 opacity-30" />
        <p class="text-sm">左侧新建对话，开始你的创意之旅</p>
      </div>
      
      <div v-else-if="chatHistory.length === 0" class="flex flex-col items-center justify-center h-full text-gray-400">
         <p class="text-sm bg-gray-50 px-4 py-2 rounded-full border border-gray-100">有什么可以帮你？</p>
      </div>

      <template v-else v-for="(msg, index) in chatHistory" :key="index">
        <!-- User 消息 (蓝色气泡) -->
        <div v-if="msg.role === 'user'" class="flex justify-end animate-fade-in-up">
          <div class="bg-blue-600 text-white px-5 py-3.5 rounded-2xl rounded-tr-sm shadow-sm text-sm leading-relaxed max-w-[85%]">
            {{ msg.content }}
          </div>
        </div>
        
        <!-- AI 消息 (白色背景) -->
        <div v-else class="flex justify-start gap-4 max-w-[90%] animate-fade-in-up">
          <div class="flex-shrink-0 mt-1">
            <div class="w-9 h-9 rounded-full bg-white border border-purple-100 flex items-center justify-center shadow-sm">
              <SparklesIcon class="w-5 h-5 text-purple-600" />
            </div>
          </div>
          <div 
            class="prose prose-sm max-w-none bg-white border border-gray-100 px-6 py-5 rounded-2xl rounded-tl-sm shadow-sm text-gray-700"
            v-html="renderMarkdown(msg.content)"
          ></div>
        </div>
      </template>

      <!-- Loading 状态 -->
      <div v-if="isProcessing && !isTyping" class="flex items-center gap-3 ml-14 animate-pulse">
         <div class="flex gap-1">
             <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></div>
             <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
             <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
         </div>
         <span class="text-xs font-medium text-gray-400">{{ statusText }}</span>
      </div>
      
      <div class="h-4"></div>
    </div>

<!-- 底部输入区域 -->
    <div class="p-6 bg-white border-t border-gray-100">
      <!-- 
         使用 flex gap-3 items-end 布局 
         items-end 保证当输入框因为文字变多而增高时，左侧按钮依然停留在底部，保持对齐
      -->
      <div class="relative max-w-4xl mx-auto flex gap-3 items-end">
        
        <!-- 1. 左侧附件按钮 -->
        <!-- 核心修改：显式设置 h-[50px] w-[50px] 以匹配输入框的计算高度 -->
        <div class="relative flex-shrink-0 h-[50px] w-[50px]">
          <input 
            type="file" 
            @change="handleSessionUpload" 
            class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
            :disabled="!currentSessionId || isProcessing"
            title="上传文件到当前会话"
          />
          <button 
            class="w-full h-full flex items-center justify-center bg-gray-50 text-gray-500 rounded-xl hover:bg-gray-100 hover:text-blue-600 transition-colors border border-gray-200"
            :class="{'opacity-50 cursor-not-allowed': !currentSessionId || isProcessing}"
          >
            <PaperClipIcon class="w-6 h-6" />
          </button>
        </div>

        <!-- 2. 中间输入框容器 -->
        <div class="relative flex-1">
          <!-- 
            核心修改：
            1. min-h-[50px]: 强制最小高度为 50px
            2. py-3 (12px * 2 = 24px)
            3. leading-6 (24px)
            4. border (2px)
            计算：24 + 24 + 2 = 50px，与左侧完美一致
          -->
          <textarea 
            v-model="inputMessage" 
            @keydown.enter.prevent="sendMessage"
            :disabled="!currentSessionId || isProcessing"
            placeholder="输入消息，Ctrl+Enter 发送..." 
            class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 pr-14 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 resize-none shadow-inner transition-all text-sm leading-6 block"
            rows="1"
            style="min-height: 50px; max-height: 150px;"
          ></textarea>
          
          <!-- 3. 发送按钮 -->
          <!-- 
             输入框总高 50px
             发送按钮高 34px (h-[34px])
             剩余空间 16px -> 上下各 8px -> bottom-2
          -->
          <button 
            @click="sendMessage"
            :disabled="!currentSessionId || isProcessing || !inputMessage.trim()"
            class="absolute right-2 bottom-2 h-[34px] w-[34px] flex items-center justify-center bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-all shadow-md active:scale-95"
          >
            <PaperAirplaneIcon class="w-5 h-5" />
          </button>
        </div>
      </div>
      <p class="text-center text-[10px] text-gray-300 mt-2">AI生成内容仅供参考</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, nextTick, computed } from 'vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { useTypewriter } from '../composables/useTypewriter';
import api from '../api';
import { 
  Bars3Icon, SparklesIcon, PaperAirplaneIcon, ChatBubbleLeftEllipsisIcon, PaperClipIcon 
} from '@heroicons/vue/24/outline';

const props = defineProps(['currentSessionId', 'sessions']);
const emit = defineEmits(['toggle-sidebar', 'session-updated']);

const inputMessage = ref('');
const isProcessing = ref(false);
const chatContainer = ref(null);
const chatHistory = ref([]);
const statusText = ref('AI 正在思考...');
const { displayedText, startTyping, isTyping } = useTypewriter();

const config = reactive({
  webSearchEnabled: false,
  knowledgeBaseEnabled: true,
  memoryEnabled: true
});

const currentTitle = computed(() => {
  const s = props.sessions.find(s => s.id === props.currentSessionId);
  return s ? s.title : '';
});

// 监听 Session 切换
watch(() => props.currentSessionId, async (newId) => {
  if (newId) {
    chatHistory.value = []; 
    try {
      const { data } = await api.getSessionMessages(newId);
      chatHistory.value = data;
      scrollToBottom();
    } catch (e) { console.error(e); }
  } else {
    chatHistory.value = [];
  }
}, { immediate: true });

// 发送消息逻辑
// ... 前面的代码不变 ...

const sendMessage = async () => {
  const text = inputMessage.value.trim();
  if (!text || !props.currentSessionId || isProcessing.value) return;

  chatHistory.value.push({ role: 'user', content: text });
  inputMessage.value = '';
  scrollToBottom();

  isProcessing.value = true;

  // -----------------------------------------------------------
  // 【修改点】根据开关状态，动态设置提示文案
  // -----------------------------------------------------------
  if (config.webSearchEnabled) {
  statusText.value = 'AI 正在联网检索...';
} else {
  // 统一文案，因为查不查库现在是 AI 内部的决定
  statusText.value = 'AI 正在思考与调度技能...';
}
  // -----------------------------------------------------------

  try {
    const { data } = await api.chat({
      session_id: props.currentSessionId,
      message: text,
      ...config
    });

    if (data.new_title) {
       emit('session-updated', { id: props.currentSessionId, title: data.new_title });
    }

    const aiMsgIndex = chatHistory.value.push({ role: 'assistant', content: '' }) - 1;
    const unwatch = watch(displayedText, (val) => {
      chatHistory.value[aiMsgIndex].content = val;
      scrollToBottom();
    });
    await startTyping(data.response);
    unwatch();
  } catch (e) {
    chatHistory.value.push({ role: 'assistant', content: '⚠️ ' + (e.response?.data?.detail || '网络错误') });
  } finally {
    isProcessing.value = false;
    scrollToBottom();
  }
};



// [新增] 会话级文件上传逻辑
const handleSessionUpload = async (event) => {
  const file = event.target.files[0];
  if (!file || !props.currentSessionId) return;

  // 1. 乐观 UI：显示正在上传
  chatHistory.value.push({ 
    role: 'assistant', 
    content: `🔄 正在读取文件 **${file.name}**...` 
  });
  scrollToBottom();

  const formData = new FormData();
  formData.append('file', file);

  try {
    // 2. 调用上传接口
    await api.uploadSessionFile(props.currentSessionId, formData);
    
    // 3. 更新最后一条消息为成功状态
    chatHistory.value.pop();
    chatHistory.value.push({ 
        role: 'assistant', 
        content: `✅ 文件 **${file.name}** 已上传并解析到当前会话记忆中。` 
    });
  } catch (e) {
    chatHistory.value.pop();
    chatHistory.value.push({ 
        role: 'assistant', 
        content: `❌ 上传失败: ${e.response?.data?.detail || e.message}` 
    });
  } finally {
    event.target.value = ''; // 重置 input 以便允许上传同名文件
    scrollToBottom();
  }
};

const scrollToBottom = async () => {
  await nextTick();
  if (!chatContainer.value) return;
  const el = chatContainer.value;
  // 简单节流
  requestAnimationFrame(() => {
    el.scrollTop = el.scrollHeight;
  });
};

const renderMarkdown = (text) => {
  if (!text) return '';
  return DOMPurify.sanitize(marked.parse(text));
};
</script>

<style scoped>
.animate-fade-in-up { animation: fadeInUp 0.3s ease-out forwards; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>