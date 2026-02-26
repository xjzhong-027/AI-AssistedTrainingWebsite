<template>
  <span
    :class="[
      'duo-badge',
      `duo-badge--${variant}`,
      `duo-badge--${size}`,
      {
        'duo-badge--dot': dot,
        'duo-badge--pulse': pulse
      }
    ]"
  >
    <slot></slot>
  </span>
</template>

<script setup lang="ts">
interface Props {
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'primary' | 'secondary'
  size?: 'small' | 'medium' | 'large'
  dot?: boolean
  pulse?: boolean
}

withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'medium',
  dot: false,
  pulse: false
})
</script>

<style scoped lang="scss">
@import '@/styles/duolingo-design-system.scss';

.duo-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: $duo-font-family;
  font-weight: $duo-font-weight-bold;
  line-height: 1;
  border-radius: $duo-radius-full;
  white-space: nowrap;
  transition: all $duo-duration-base $duo-ease-out;

  // 尺寸
  &--small {
    padding: $duo-spacing-1 $duo-spacing-2;
    font-size: $duo-font-size-xs;
  }

  &--medium {
    padding: $duo-spacing-1 $duo-spacing-3;
    font-size: $duo-font-size-sm;
  }

  &--large {
    padding: $duo-spacing-2 $duo-spacing-4;
    font-size: $duo-font-size-base;
  }

  // 变体颜色
  &--primary {
    background: $duo-green-primary;
    color: $duo-text-inverse;
  }

  &--success {
    background: $duo-blue-primary;
    color: $duo-text-inverse;
  }

  &--warning {
    background: $duo-yellow-primary;
    color: $duo-text-primary;
  }

  &--danger {
    background: $duo-red-primary;
    color: $duo-text-inverse;
  }

  &--info {
    background: $duo-gray-600;
    color: $duo-text-inverse;
  }

  &--secondary {
    background: $duo-gray-400;
    color: $duo-text-primary;
  }

  // 圆点样式
  &--dot {
    width: 8px;
    height: 8px;
    padding: 0;
    border-radius: 50%;
  }

  // 脉冲动画
  &--pulse {
    animation: duo-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
}

@keyframes duo-pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
