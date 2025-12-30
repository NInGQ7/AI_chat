<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="bg-white p-8 rounded-xl shadow-md w-96">
      <h2 class="text-2xl font-bold mb-6 text-center text-gray-700">AI Assistant</h2>
      
      <div class="flex gap-4 mb-6 border-b">
        <button @click="isLogin = true" :class="isLogin ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500'" class="pb-2 flex-1">登录</button>
        <button @click="isLogin = false" :class="!isLogin ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500'" class="pb-2 flex-1">注册</button>
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-600 mb-1">用户名</label>
          <input v-model="form.username" type="text" required class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
        </div>
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-600 mb-1">密码</label>
          <input v-model="form.password" type="password" required class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
        </div>
        <button type="submit" class="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition">
          {{ isLogin ? '进入系统' : '立即注册' }}
        </button>
        <p v-if="errorMsg" class="mt-4 text-red-500 text-sm text-center">{{ errorMsg }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import api from '../api';

const isLogin = ref(true);
const form = reactive({ username: '', password: '' });
const errorMsg = ref('');
const emit = defineEmits(['login-success']);

const handleSubmit = async () => {
  errorMsg.value = '';
  try {
    if (isLogin.value) {
      const { data } = await api.login(form.username, form.password);
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('username', form.username);
      emit('login-success'); // 通知父组件
    } else {
      await api.register(form.username, form.password);
      alert('注册成功，请登录');
      isLogin.value = true;
    }
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || '操作失败';
  }
};
</script>