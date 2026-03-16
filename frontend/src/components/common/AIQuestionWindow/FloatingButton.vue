<template>
  <div
    class="ai-floating-button"
    @click.stop="handleClick"
  >
    <div class="ai-icon">
      <svg
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id="aiGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#FFFFFF;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#F0F0F0;stop-opacity:1" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="1.5" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <g filter="url(#glow)">
          <path d="M12 2L12 4" stroke="url(#aiGradient)" stroke-width="2" stroke-linecap="round" />
          <circle cx="12" cy="1.5" r="1" fill="url(#aiGradient)" />
          <rect
            x="6"
            y="5"
            width="12"
            height="10"
            rx="3"
            stroke="url(#aiGradient)"
            stroke-width="2"
            fill="none"
          />
          <circle cx="9" cy="10" r="1.5" fill="url(#aiGradient)" />
          <circle cx="15" cy="10" r="1.5" fill="url(#aiGradient)" />
          <rect x="10" y="12" width="4" height="1.5" rx="0.5" fill="url(#aiGradient)" />
          <path d="M8 15L8 17" stroke="url(#aiGradient)" stroke-width="2" stroke-linecap="round" />
          <path d="M12 15L12 17" stroke="url(#aiGradient)" stroke-width="2" stroke-linecap="round" />
          <path d="M16 15L16 17" stroke="url(#aiGradient)" stroke-width="2" stroke-linecap="round" />
          <rect x="7" y="17" width="2" height="3" rx="0.5" fill="url(#aiGradient)" />
          <rect x="15" y="17" width="2" height="3" rx="0.5" fill="url(#aiGradient)" />
          <path d="M4 8L2 8" stroke="url(#aiGradient)" stroke-width="2" stroke-linecap="round" />
          <path d="M4 12L2 12" stroke="url(#aiGradient)" stroke-width="2" stroke-linecap="round" />
          <path d="M20 8L22 8" stroke="url(#aiGradient)" stroke-width="2" stroke-linecap="round" />
          <path d="M20 12L22 12" stroke="url(#aiGradient)" stroke-width="2" stroke-linecap="round" />
        </g>
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits<{ click: [] }>()

const handleClick = () => {
  emit('click')
}
</script>

<style scoped>
.ai-floating-button {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #8c7cf0, #c6b9ff);
  border-radius: 50%;
  box-shadow: 0 4px 16px rgba(140, 124, 240, 0.4);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9998;
  transition: all 0.3s ease;
  user-select: none;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    box-shadow: 0 4px 16px rgba(140, 124, 240, 0.4), 0 0 0 rgba(140, 124, 240, 0.2);
  }
  50% {
    box-shadow: 0 4px 24px rgba(140, 124, 240, 0.6), 0 0 20px rgba(140, 124, 240, 0.3);
  }
}

.ai-floating-button:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(140, 124, 240, 0.6);
  background: linear-gradient(135deg, #7b6ce0, #b5a5ff);
  animation: none;
}

.ai-floating-button:active {
  transform: scale(0.95);
}

.ai-icon {
  width: 32px;
  height: 32px;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-icon svg {
  width: 100%;
  height: 100%;
  animation: rotate 20s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .ai-floating-button {
    width: 56px;
    height: 56px;
    bottom: 16px;
    right: 16px;
  }
  .ai-icon {
    width: 28px;
    height: 28px;
  }
}
</style>

