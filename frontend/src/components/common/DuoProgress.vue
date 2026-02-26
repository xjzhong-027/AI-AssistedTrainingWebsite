<template>
  <div class="duo-progress">
    <!-- 标签 -->
    <div v-if="label || showPercentage" class="duo-progress__label">
      <span class="duo-progress__text">{{ label }}</span>
      <span v-if="showPercentage" class="duo-progress__percentage">
        {{ Math.round(percentage) }}%
      </span>
    </div>

    <!-- 进度条 -->
    <div
      :class="[
        'duo-progress__bar',
        `duo-progress__bar--${variant}`,
        `duo-progress__bar--${size}`
      ]"
    >
      <div
        class="duo-progress__fill"
        :style="{
          width: `${Math.min(100, Math.max(0, percentage))}%`,
          transition: animated ? `width ${duration}ms ${easing}` : 'none'
        }"
      >
        <div v-if="striped" class="duo-progress__stripes"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  percentage: number
  label?: string
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'primary'
  size?: 'small' | 'medium' | 'large'
  showPercentage?: boolean
  striped?: boolean
  animated?: boolean
  duration?: number
  easing?: string
}

const props = withDefaults(defineProps<Props>(), {
  percentage: 0,
  variant: 'success',
  size: 'medium',
  showPercentage: true,
  striped: false,
  animated: true,
  duration: 600,
  easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
})
</script>

<style scoped lang="scss">
@import '@/styles/duolingo-design-system.scss';

.duo-progress {
  width: 100%;

  // 标签
  &__label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $duo-spacing-2;
  }

  &__text {
    font-size: $duo-font-size-sm;
    font-weight: $duo-font-weight-semibold;
    color: $duo-text-primary;
  }

  &__percentage {
    font-size: $duo-font-size-sm;
    font-weight: $duo-font-weight-bold;
    color: $duo-text-secondary;
  }

  // 进度条容器
  &__bar {
    position: relative;
    width: 100%;
    background: $duo-gray-400;
    border-radius: $duo-radius-full;
    overflow: hidden;

    &--small {
      height: 8px;
    }

    &--medium {
      height: 12px;
    }

    &--large {
      height: 16px;
    }
  }

  // 进度填充
  &__fill {
    position: relative;
    height: 100%;
    border-radius: $duo-radius-full;
    overflow: hidden;
  }

  // 条纹效果
  &__stripes {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: linear-gradient(
      45deg,
      rgba(255, 255, 255, 0.15) 25%,
      transparent 25%,
      transparent 50%,
      rgba(255, 255, 255, 0.15) 50%,
      rgba(255, 255, 255, 0.15) 75%,
      transparent 75%,
      transparent
    );
    background-size: 20px 20px;
    animation: duo-progress-stripes 1s linear infinite;
  }

  // 变体颜色
  &__bar--success &__fill {
    background: linear-gradient(90deg, $duo-green-primary 0%, $duo-green-light 100%);
  }

  &__bar--warning &__fill {
    background: linear-gradient(90deg, $duo-yellow-primary 0%, $duo-yellow-light 100%);
  }

  &__bar--danger &__fill {
    background: linear-gradient(90deg, $duo-red-primary 0%, $duo-red-light 100%);
  }

  &__bar--info &__fill {
    background: linear-gradient(90deg, $duo-blue-primary 0%, $duo-blue-light 100%);
  }

  &__bar--primary &__fill {
    background: linear-gradient(90deg, $duo-green-primary 0%, $duo-blue-primary 100%);
  }
}

@keyframes duo-progress-stripes {
  from {
    background-position: 0 0;
  }
  to {
    background-position: 20px 0;
  }
}
</style>
