<template>
  <div class="design-system-demo">
    <!-- 背景装饰 -->
    <DuoBackground />

    <div class="demo-container">
      <h1 class="demo-title duo-animate-fade-in">Duolingo 设计系统组件库</h1>
      <p class="demo-subtitle duo-animate-slide-up">友好、愉悦、游戏化的学习体验</p>

      <!-- 按钮组件 -->
      <section class="demo-section duo-animate-slide-up">
        <h2 class="section-title">按钮 (DuoButton)</h2>

        <div class="demo-group">
          <h3>变体 - 点击查看波纹效果</h3>
          <div class="button-row">
            <DuoButton variant="primary" @click="handleButtonClick">Primary</DuoButton>
            <DuoButton variant="success" @click="handleButtonClick">Success</DuoButton>
            <DuoButton variant="warning" @click="handleButtonClick">Warning</DuoButton>
            <DuoButton variant="danger" @click="handleButtonClick">Danger</DuoButton>
            <DuoButton variant="info" @click="handleButtonClick">Info</DuoButton>
            <DuoButton variant="secondary" @click="handleButtonClick">Secondary</DuoButton>
          </div>
        </div>

        <div class="demo-group">
          <h3>尺寸</h3>
          <div class="button-row">
            <DuoButton size="small">Small</DuoButton>
            <DuoButton size="medium">Medium</DuoButton>
            <DuoButton size="large">Large</DuoButton>
          </div>
        </div>

        <div class="demo-group">
          <h3>状态</h3>
          <div class="button-row">
            <DuoButton :loading="true">Loading</DuoButton>
            <DuoButton :disabled="true">Disabled</DuoButton>
            <DuoButton block>Block Button</DuoButton>
          </div>
        </div>

        <div class="demo-group">
          <h3>交互动效测试</h3>
          <div class="button-row">
            <DuoButton variant="success" @click="playSuccess">
              成功动画
            </DuoButton>
            <DuoButton variant="danger" @click="playError">
              错误抖动
            </DuoButton>
            <DuoButton variant="info" @click="playPulse">
              脉冲效果
            </DuoButton>
          </div>
        </div>
      </section>

      <!-- 卡片组件 -->
      <section class="demo-section">
        <h2 class="section-title">卡片 (DuoCard)</h2>

        <div class="card-grid">
          <DuoCard title="默认卡片" subtitle="这是一个默认样式的卡片">
            <p>卡片内容区域，可以放置任何内容。</p>
          </DuoCard>

          <DuoCard variant="success" title="成功卡片" badge="NEW">
            <p>恭喜！你已经完成了今天的学习任务。</p>
          </DuoCard>

          <DuoCard variant="warning" title="警告卡片" hoverable>
            <p>你有一个任务即将到期，请尽快完成。</p>
          </DuoCard>

          <DuoCard variant="danger" title="错误卡片" clickable @click="handleCardClick">
            <p>点击查看错误详情。</p>
          </DuoCard>

          <DuoCard variant="info" title="信息卡片">
            <template #header>
              <div style="display: flex; align-items: center; gap: 8px;">
                <h3 style="margin: 0;">自定义标题</h3>
                <DuoBadge variant="info" size="small">HOT</DuoBadge>
              </div>
            </template>
            <p>使用插槽自定义卡片头部和底部。</p>
            <template #footer>
              <DuoButton size="small">查看详情</DuoButton>
            </template>
          </DuoCard>
        </div>
      </section>

      <!-- 进度条组件 -->
      <section class="demo-section">
        <h2 class="section-title">进度条 (DuoProgress)</h2>

        <div class="progress-list">
          <DuoProgress :percentage="90" label="内容准确性" variant="success" />
          <DuoProgress :percentage="75" label="语言表达" variant="info" />
          <DuoProgress :percentage="60" label="完整性" variant="warning" />
          <DuoProgress :percentage="40" label="逻辑连贯性" variant="danger" />
          <DuoProgress :percentage="85" label="总体进度" variant="primary" striped />
        </div>

        <div class="demo-group">
          <h3>不同尺寸</h3>
          <div class="progress-list">
            <DuoProgress :percentage="70" size="small" />
            <DuoProgress :percentage="70" size="medium" />
            <DuoProgress :percentage="70" size="large" />
          </div>
        </div>
      </section>

      <!-- 徽章组件 -->
      <section class="demo-section">
        <h2 class="section-title">徽章 (DuoBadge)</h2>

        <div class="demo-group">
          <h3>变体</h3>
          <div class="badge-row">
            <DuoBadge variant="primary">Primary</DuoBadge>
            <DuoBadge variant="success">Success</DuoBadge>
            <DuoBadge variant="warning">Warning</DuoBadge>
            <DuoBadge variant="danger">Danger</DuoBadge>
            <DuoBadge variant="info">Info</DuoBadge>
            <DuoBadge variant="secondary">Secondary</DuoBadge>
          </div>
        </div>

        <div class="demo-group">
          <h3>尺寸</h3>
          <div class="badge-row">
            <DuoBadge size="small">Small</DuoBadge>
            <DuoBadge size="medium">Medium</DuoBadge>
            <DuoBadge size="large">Large</DuoBadge>
          </div>
        </div>

        <div class="demo-group">
          <h3>特殊样式</h3>
          <div class="badge-row">
            <DuoBadge dot variant="success" />
            <DuoBadge dot variant="danger" />
            <DuoBadge pulse variant="success">在线</DuoBadge>
            <DuoBadge pulse variant="danger">离线</DuoBadge>
          </div>
        </div>
      </section>

      <!-- 综合示例 -->
      <section class="demo-section">
        <h2 class="section-title">综合示例</h2>

        <DuoCard title="今日学习任务" subtitle="完成以下任务获得奖励" hoverable badge="3">
          <div class="task-list">
            <div class="task-item">
              <div class="task-info">
                <span class="task-name">听力练习</span>
                <DuoBadge variant="success" size="small">已完成</DuoBadge>
              </div>
              <DuoProgress :percentage="100" variant="success" size="small" :show-percentage="false" />
            </div>

            <div class="task-item">
              <div class="task-info">
                <span class="task-name">口语练习</span>
                <DuoBadge variant="warning" size="small">进行中</DuoBadge>
              </div>
              <DuoProgress :percentage="65" variant="warning" size="small" :show-percentage="false" />
            </div>

            <div class="task-item">
              <div class="task-info">
                <span class="task-name">阅读理解</span>
                <DuoBadge variant="secondary" size="small">未开始</DuoBadge>
              </div>
              <DuoProgress :percentage="0" variant="info" size="small" :show-percentage="false" />
            </div>
          </div>

          <template #footer>
            <DuoButton variant="primary" block>继续学习</DuoButton>
          </template>
        </DuoCard>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import DuoButton from '@/components/common/DuoButton.vue'
import DuoCard from '@/components/common/DuoCard.vue'
import DuoProgress from '@/components/common/DuoProgress.vue'
import DuoBadge from '@/components/common/DuoBadge.vue'
import DuoBackground from '@/components/common/DuoBackground.vue'
import { ElMessage } from 'element-plus'
import {
  createRipple,
  playSuccessAnimation,
  playErrorShake,
  pulse
} from '@/utils/duoAnimations'

const handleCardClick = () => {
  ElMessage.success('卡片被点击了！')
}

const handleButtonClick = (event: MouseEvent) => {
  createRipple(event, 'rgba(255, 255, 255, 0.6)')
}

const playSuccess = (event: MouseEvent) => {
  const button = event.currentTarget as HTMLElement
  playSuccessAnimation(button)
  ElMessage.success('成功！')
}

const playError = (event: MouseEvent) => {
  const button = event.currentTarget as HTMLElement
  playErrorShake(button)
  ElMessage.error('错误！')
}

const playPulse = (event: MouseEvent) => {
  const button = event.currentTarget as HTMLElement
  pulse(button, 1.1)
}
</script>

<style scoped lang="scss">
@import '@/styles/duolingo-design-system.scss';

.design-system-demo {
  min-height: 100vh;
  padding: $duo-spacing-8 $duo-spacing-4;
  position: relative;
}

.demo-container {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.demo-title {
  font-size: $duo-font-size-4xl;
  font-weight: $duo-font-weight-extrabold;
  color: $duo-text-primary;
  text-align: center;
  margin: 0 0 $duo-spacing-2;
}

.demo-subtitle {
  font-size: $duo-font-size-lg;
  color: $duo-text-secondary;
  text-align: center;
  margin: 0 0 $duo-spacing-12;
}

.demo-section {
  background: $duo-bg-primary;
  border-radius: $duo-radius-2xl;
  padding: $duo-spacing-8;
  margin-bottom: $duo-spacing-8;
  box-shadow: $duo-shadow-lg;
}

.section-title {
  font-size: $duo-font-size-2xl;
  font-weight: $duo-font-weight-bold;
  color: $duo-text-primary;
  margin: 0 0 $duo-spacing-6;
  padding-bottom: $duo-spacing-4;
  border-bottom: 3px solid $duo-gray-400;
}

.demo-group {
  margin-bottom: $duo-spacing-6;

  &:last-child {
    margin-bottom: 0;
  }

  h3 {
    font-size: $duo-font-size-lg;
    font-weight: $duo-font-weight-semibold;
    color: $duo-text-secondary;
    margin: 0 0 $duo-spacing-4;
  }
}

.button-row {
  display: flex;
  flex-wrap: wrap;
  gap: $duo-spacing-4;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: $duo-spacing-6;
}

.progress-list {
  display: flex;
  flex-direction: column;
  gap: $duo-spacing-4;
}

.badge-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: $duo-spacing-3;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: $duo-spacing-4;
}

.task-item {
  display: flex;
  flex-direction: column;
  gap: $duo-spacing-2;
}

.task-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-name {
  font-size: $duo-font-size-base;
  font-weight: $duo-font-weight-semibold;
  color: $duo-text-primary;
}

@include duo-responsive(md) {
  .demo-container {
    padding: 0 $duo-spacing-6;
  }
}
</style>
