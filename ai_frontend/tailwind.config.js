/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      animation: {
        'bounce-slow': 'bounce 2s infinite',
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'), // 如果需要更好的markdown样式，建议安装这个插件，这里暂时手写样式
  ],
}