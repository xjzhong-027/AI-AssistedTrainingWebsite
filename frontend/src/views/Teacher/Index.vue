<template>
  <div class="download-page">
    <div class="illustration-bg">
      <div class="illustration-circle circle-1"></div>
      <div class="illustration-circle circle-2"></div>
      <div class="illustration-star star-1"></div>
      <div class="illustration-star star-2"></div>
      <div class="illustration-star star-3"></div>
    </div>

    <div class="illustration-header">
      <div class="illustration-download">
        <div class="download-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
        </div>
        <div class="download-shine"></div>
      </div>
    </div>

    <div class="main-card">
      <div class="card-header">
        <h1 class="page-title">附件下载</h1>
      </div>

      <div class="file-list">
        <div
          v-for="(file, index) in files"
          :key="index"
          class="file-item"
        >
          <div class="file-info">
            <div class="file-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
              </svg>
            </div>
            <div class="file-details">
              <h3 class="file-name">{{ file.name }}</h3>
              <p class="file-description">{{ file.description }}</p>
            </div>
          </div>
          <button 
            :data-filename="file.filename" 
            @click="downloadFile"
            class="download-btn"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            下载
          </button>
        </div>
      </div>
    </div>
    <AIWindow :show-grade-button="false" />
  </div>
</template>

<script setup lang="ts">
import AIWindow from '@/components/common/AIWindow/index.vue'

const files = [
  {
    name: '文件导入模板',
    description: '用于批量导入数据的标准模板',
    filename: '模板.docx'
  },
  {
    name: '周任务文件导入模板（分页）',
    description: '支持分页导入的周任务模板',
    filename: '分页模板.docx'
  },
  {
    name: '模板说明',
    description: '详细的模板使用说明文档',
    filename: '说明文件.docx'
  }
]

const downloadFile = (event: Event) => {
  const button = event.currentTarget as HTMLButtonElement
  const filename = button.getAttribute('data-filename')
  if (filename) {
    // 使用 Django 后端的下载接口
    window.location.href = `/teacher/download/${encodeURIComponent(filename)}/`
  }
}
</script>

<style scoped>
.download-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f4f8 0%, #e9ecef 100%);
  position: relative;
  overflow: hidden;
  padding: 40px 20px;
}

/* 背景装饰 */
.illustration-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
}

.illustration-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
}

.circle-1 {
  width: 300px;
  height: 300px;
  background: #8C7CF0;
  top: -100px;
  right: -100px;
}

.circle-2 {
  width: 200px;
  height: 200px;
  background: #FF6B6B;
  bottom: -80px;
  left: -80px;
}

.illustration-star {
  position: absolute;
  color: #8C7CF0;
  opacity: 0.1;
  font-size: 40px;
}

.star-1 {
  top: 20%;
  left: 10%;
}

.star-2 {
  top: 60%;
  right: 15%;
}

.star-3 {
  bottom: 20%;
  left: 25%;
}

/* 头部插图 */
.illustration-header {
  display: flex;
  justify-content: center;
  margin-bottom: 40px;
  position: relative;
  z-index: 1;
}

.illustration-download {
  position: relative;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.download-icon {
  color: #8C7CF0;
  position: relative;
  z-index: 2;
}

.download-shine {
  position: absolute;
  top: -20px;
  left: -20px;
  right: -20px;
  bottom: -20px;
  background: radial-gradient(circle, rgba(140, 124, 240, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 0.5;
  }
}

/* 主卡片 */
.main-card {
  max-width: 800px;
  margin: 0 auto;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  padding: 40px;
  position: relative;
  z-index: 1;
  overflow: hidden;
}

.main-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #8C7CF0, #6B46C1);
}

.card-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #2D3748;
  margin: 0;
  position: relative;
  display: inline-block;
}

.page-title::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 4px;
  background: linear-gradient(90deg, #8C7CF0, #6B46C1);
  border-radius: 2px;
}

/* 文件列表 */
.file-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: #F8FAFC;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.file-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, #8C7CF0, #6B46C1);
  border-radius: 4px 0 0 4px;
}

.file-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(140, 124, 240, 0.15);
  border-color: #8C7CF0;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.file-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #F6F3FF 0%, #EDE9FE 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8C7CF0;
  flex-shrink: 0;
}

.file-details {
  flex: 1;
}

.file-name {
  font-size: 18px;
  font-weight: 600;
  color: #2D3748;
  margin: 0 0 4px 0;
}

.file-description {
  font-size: 14px;
  color: #718096;
  margin: 0;
  line-height: 1.4;
}

/* 下载按钮 */
.download-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #8C7CF0 0%, #6B46C1 100%);
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.download-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s ease;
}

.download-btn:hover::before {
  left: 100%;
}

.download-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(140, 124, 240, 0.4);
  background: linear-gradient(135deg, #7C69E8 0%, #553C9A 100%);
}

.download-btn:active {
  transform: translateY(0);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .download-page {
    padding: 30px 15px;
  }

  .main-card {
    padding: 30px 20px;
  }

  .page-title {
    font-size: 24px;
  }

  .file-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .file-info {
    width: 100%;
  }

  .download-btn {
    align-self: flex-start;
    width: 100%;
    justify-content: center;
  }

  .illustration-download {
    width: 100px;
    height: 100px;
  }

  .download-icon svg {
    width: 50px;
    height: 50px;
  }
}

@media (max-width: 480px) {
  .main-card {
    padding: 20px 15px;
  }

  .file-item {
    padding: 16px;
  }

  .file-name {
    font-size: 16px;
  }

  .download-btn {
    padding: 10px 20px;
  }
}
</style>





