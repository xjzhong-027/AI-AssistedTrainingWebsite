<template>
  <button
    :class="[
      'duo-button',
      `duo-button--${variant}`,
      `duo-button--${size}`,
      {
        'duo-button--block': block,
        'duo-button--loading': loading,
        'duo-button--disabled': disabled
      }
    ]"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="duo-button__loading">
      <i class="duo-icon-loading"></i>
    </span>
    <span class="duo-button__content">
      <slot></slot>
    </span>
  </button>
</template>

<script setup lang="ts">
interface Props {
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'secondary'
  size?: 'small' | 'medium' | 'large'
  block?: boolean
  loading?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'medium',
  block: false,
  loading: false,
  disabled: false
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped lang="scss">
@import '@/styles/duolingo-design-system.scss';

.duo-button {
  @include duo-button-base;
  position: relative;
  overflow: hidden;

  // 按钮内容
  &__content {
    display: flex;
    align-items: center;
    gap: $duo-spacing-2;
  }

  // 加载状态
  &__loading {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);

    .duo-icon-loading {
      display: inline-block;
      width: 16px;
      height: 16px;
      border: 2px solid currentColor;
      border-top-color: transparent;
      border-radius: 50%;
      animation: duo-spin 0.6s linear infinite;
    }
  }

  &--loading &__content {
    opacity: 0;
  }

  // 变体样式
  &--primary {
    background: $duo-green-primary;
    color: $duo-text-inverse;
    box-shadow: $duo-shadow-green;

    &:hover:not(:disabled) {
      background: $duo-green-hover;
      transform: translateY(-2px);
    }

    &:active:not(:disabled) {
      background: $duo-green-active;
      transform: translateY(2px);
      box-shadow: none;
    }
  }

  &--success {
    background: $duo-blue-primary;
    color: $duo-text-inverse;
    box-shadow: $duo-shadow-blue;

    &:hover:not(:disabled) {
      background: $duo-blue-hover;
      transform: translateY(-2px);
    }

    &:active:not(:disabled) {
      background: $duo-blue-active;
      transform: translateY(2px);
      box-shadow: none;
    }
  }

  &--warning {
    background: $duo-yellow-primary;
    color: $duo-text-primary;
    box-shadow: $duo-shadow-yellow;

    &:hover:not(:disabled) {
      background: $duo-yellow-hover;
      transform: translateY(-2px);
    }

    &:active:not(:disabled) {
      background: $duo-yellow-active;
      transform: translateY(2px);
      box-shadow: none;
    }
  }

  &--danger {
    background: $duo-red-primary;
    color: $duo-text-inverse;
    box-shadow: $duo-shadow-red;

    &:hover:not(:disabled) {
      background: $duo-red-hover;
      transform: translateY(-2px);
    }

    &:active:not(:disabled) {
      background: $duo-red-active;
      transform: translateY(2px);
      box-shadow: none;
    }
  }

  &--info {
    background: $duo-gray-100;
    color: $duo-text-primary;
    border: 2px solid $duo-gray-500;
    box-shadow: 0 4px 0 $duo-gray-500;

    &:hover:not(:disabled) {
      background: $duo-gray-200;
      transform: translateY(-2px);
    }

    &:active:not(:disabled) {
      background: $duo-gray-300;
      transform: translateY(2px);
      box-shadow: none;
    }
  }

  &--secondary {
    background: transparent;
    color: $duo-text-primary;
    border: 2px solid $duo-gray-500;

    &:hover:not(:disabled) {
      background: $duo-gray-200;
    }

    &:active:not(:disabled) {
      background: $duo-gray-300;
    }
  }

  // 尺寸
  &--small {
    padding: $duo-spacing-2 $duo-spacing-4;
    font-size: $duo-font-size-sm;
    border-radius: $duo-radius-base;
  }

  &--medium {
    padding: $duo-spacing-3 $duo-spacing-6;
    font-size: $duo-font-size-base;
    border-radius: $duo-radius-lg;
  }

  &--large {
    padding: $duo-spacing-4 $duo-spacing-8;
    font-size: $duo-font-size-lg;
    border-radius: $duo-radius-xl;
  }

  // 块级按钮
  &--block {
    width: 100%;
  }

  // 禁用状态
  &--disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

@keyframes duo-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
