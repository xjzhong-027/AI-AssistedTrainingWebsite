<template>
  <div class="duo-background">
    <!-- 渐变背景 -->
    <div class="duo-background__gradient"></div>

    <!-- 装饰圆圈 -->
    <div class="duo-background__circles">
      <div class="circle circle--1"></div>
      <div class="circle circle--2"></div>
      <div class="circle circle--3"></div>
      <div class="circle circle--4"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 纯装饰组件，无需逻辑
</script>

<style scoped lang="scss">
@import '@/styles/duolingo-design-system.scss';

.duo-background {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: -1;
  overflow: hidden;
  pointer-events: none;

  // 渐变背景
  &__gradient {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(
      135deg,
      $duo-blue-lighter 0%,
      $duo-green-lighter 50%,
      $duo-yellow-lighter 100%
    );
    opacity: 0.3;
  }

  // 装饰圆圈
  &__circles {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;

    .circle {
      position: absolute;
      border-radius: 50%;
      opacity: 0.1;
      animation: float 20s ease-in-out infinite;

      &--1 {
        width: 300px;
        height: 300px;
        background: $duo-green-primary;
        top: -150px;
        left: -150px;
        animation-delay: 0s;
      }

      &--2 {
        width: 200px;
        height: 200px;
        background: $duo-blue-primary;
        top: 20%;
        right: -100px;
        animation-delay: 5s;
      }

      &--3 {
        width: 250px;
        height: 250px;
        background: $duo-yellow-primary;
        bottom: -125px;
        left: 30%;
        animation-delay: 10s;
      }

      &--4 {
        width: 180px;
        height: 180px;
        background: $duo-red-primary;
        bottom: 20%;
        right: 10%;
        animation-delay: 15s;
      }
    }
  }
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(20px, -20px) scale(1.1);
  }
  50% {
    transform: translate(-20px, 20px) scale(0.9);
  }
  75% {
    transform: translate(20px, 20px) scale(1.05);
  }
}
</style>
