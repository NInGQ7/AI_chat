import { ref } from 'vue';

export function useTypewriter() {
  const displayedText = ref('');
  const isTyping = ref(false);

  /**
   * 开始打字效果
   * @param {String} fullText 完整文本
   * @param {Number} minSpeed 最小间隔(ms)
   * @param {Number} maxSpeed 最大间隔(ms)
   */
  const startTyping = (fullText, minSpeed = 10, maxSpeed = 30) => {
    return new Promise((resolve) => {
      displayedText.value = ''; // 清空
      isTyping.value = true;
      let currentIndex = 0;

      const typeChar = () => {
        if (currentIndex >= fullText.length) {
          isTyping.value = false;
          resolve();
          return;
        }

        // 每次追加 1 到 4 个字符，模拟不均匀的打字速度
        const chunkSize = Math.floor(Math.random() * 4) + 1;
        displayedText.value += fullText.substring(currentIndex, currentIndex + chunkSize);
        currentIndex += chunkSize;

        // 随机延迟
        const delay = Math.floor(Math.random() * (maxSpeed - minSpeed + 1)) + minSpeed;
        setTimeout(typeChar, delay);
      };

      typeChar();
    });
  };

  return {
    displayedText,
    isTyping,
    startTyping
  };
}