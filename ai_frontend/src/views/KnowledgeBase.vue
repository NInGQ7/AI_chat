<template>
  <div class="p-8 h-full bg-gray-50 flex flex-col">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">知识库管理</h1>
        <p class="text-gray-500 mt-1">上传文档，让 AI 学习并基于这些内容回答问题。</p>
      </div>
      <div class="lg:hidden">
         <button @click="$emit('toggle-sidebar')" class="p-2 bg-white rounded-md shadow"><Bars3Icon class="w-6 h-6"/></button>
      </div>
    </div>

    <!-- 上传卡片 -->
    <div class="bg-white p-8 rounded-2xl shadow-sm border border-gray-200 text-center mb-8">
      <div 
        class="border-2 border-dashed border-gray-300 rounded-xl py-12 px-4 hover:bg-blue-50 hover:border-blue-400 transition-colors cursor-pointer relative"
      >
        <input 
          type="file" 
          @change="handleFileUpload" 
          class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          :disabled="isUploading"
        />
        <CloudArrowUpIcon class="w-16 h-16 text-blue-500 mx-auto mb-4" :class="{'animate-bounce': isUploading}" />
        <h3 class="text-lg font-medium text-gray-700">
          {{ isUploading ? '正在上传并解析...' : '点击或拖拽文件上传' }}
        </h3>
        <p class="text-gray-400 mt-2 text-sm">支持 PDF, TXT, DOCX ，EXCEL(最大 10MB)</p>
      </div>
    </div>

    <!-- 文件列表 -->
    <div class="flex-1 bg-white rounded-2xl shadow-sm border border-gray-200 flex flex-col overflow-hidden">
      <div class="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
        <h3 class="font-bold text-gray-700">已收录文件 ({{ uploadedFiles.length }})</h3>
        <button @click="fetchFiles" class="text-blue-600 text-sm hover:underline flex items-center gap-1">
          <ArrowPathIcon class="w-4 h-4" /> 刷新列表
        </button>
      </div>
      
      <div class="flex-1 overflow-y-auto p-4 custom-scrollbar">
        <ul class="space-y-3">
          <li v-for="(file, index) in uploadedFiles" :key="index" class="flex items-center p-4 bg-gray-50 rounded-xl hover:bg-blue-50 transition-colors group border border-transparent hover:border-blue-100">
            <DocumentTextIcon class="w-10 h-10 text-gray-400 group-hover:text-blue-500 mr-4 transition-colors" />
            <div class="flex-1 min-w-0">
              <p class="font-medium text-gray-800 truncate">{{ file.name }}</p>
              <p class="text-xs text-gray-500">上传时间: {{ file.date || '未知' }}</p>
            </div>
            
            <!-- 删除按钮 -->
            <button 
              @click="deleteFile(file.name)" 
              class="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg opacity-100 lg:opacity-0 group-hover:opacity-100 transition-all"
              title="删除文件"
            >
               <TrashIcon class="w-5 h-5" />
            </button>
          </li>
          
          <!-- 空状态 -->
          <li v-if="uploadedFiles.length === 0" class="text-center py-12 flex flex-col items-center">
            <DocumentTextIcon class="w-16 h-16 text-gray-200 mb-2" />
            <p class="text-gray-400">暂无知识库文件</p>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api';
import { CloudArrowUpIcon, DocumentTextIcon, TrashIcon, Bars3Icon, ArrowPathIcon } from '@heroicons/vue/24/outline';

const uploadedFiles = ref([]);
const isUploading = ref(false);
const emit = defineEmits(['toggle-sidebar']);

// 初始化加载
onMounted(() => {
    fetchFiles();
});

// 获取真实文件列表
const fetchFiles = async () => {
    try {
        const { data } = await api.getKnowledgeFiles();
        uploadedFiles.value = data;
    } catch (e) {
        console.error("加载文件列表失败:", e);
    }
};

// 上传逻辑
const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  isUploading.value = true;
  const formData = new FormData();
  formData.append('file', file);

  try {
    await api.uploadFile(formData);
    // 上传成功后，重新拉取列表
    await fetchFiles();
    alert(`文件 ${file.name} 已成功存入知识库！`);
  } catch (error) {
    alert('上传失败: ' + (error.response?.data?.detail || error.message));
  } finally {
    isUploading.value = false;
    event.target.value = '';
  }
};

// 删除逻辑
const deleteFile = async (filename) => {
    if(!confirm(`确定要删除 "${filename}" 吗？\n删除后 AI 将无法检索到该文件的内容。`)) return;

    try {
        await api.deleteKnowledgeFile(filename);
        // 乐观更新 UI (立即移除)
        uploadedFiles.value = uploadedFiles.value.filter(f => f.name !== filename);
    } catch (e) {
        alert('删除失败: ' + (e.response?.data?.detail || e.message));
        // 如果失败，重新拉取列表以保持一致
        fetchFiles();
    }
};
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}
</style>