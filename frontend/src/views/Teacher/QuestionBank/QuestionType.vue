<template>
  <div class="question-type-page">
    <!-- 顶部插画 -->
    <div class="illustration-header">
      <div class="illustration-content">
        <svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2" fill="#E8E4FF" stroke="#8C7CF0"/>
          <line x1="16" y1="2" x2="16" y2="6" stroke="#8C7CF0"/>
          <line x1="8" y1="2" x2="8" y2="6" stroke="#8C7CF0"/>
          <line x1="3" y1="10" x2="21" y2="10" stroke="#8C7CF0"/>
          <path d="M8 14h2" stroke="#8C7CF0"/>
          <path d="M14 14h2" stroke="#8C7CF0"/>
          <path d="M8 18h8" stroke="#8C7CF0"/>
          <circle cx="12" cy="14" r="1" fill="#FFB347"/>
          <circle cx="12" cy="18" r="1" fill="#FFB347"/>
        </svg>
      </div>
    </div>

    <div class="question-type-card">
      <div class="card-header">
        <div class="header-left">
          <div class="header-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7,10 12,15 17,10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
          </div>
          <h2>添加题目 - 选择题型</h2>
        </div>
        <el-button @click="goBack" type="default" class="secondary-button">返回</el-button>
      </div>

      <p class="tip">请选择要添加的题目类型：</p>
      <div class="type-options">
        <div class="type-card batch-card" @click="goBatchImport">
          <div class="card-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7,10 12,15 17,10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
          </div>
          <span class="type-label">批量导入选择题</span>
          <p class="type-desc">按格式批量导入多道选择题</p>
        </div>
        
        <div class="type-card" @click="goEdit('choice')">
          <div class="card-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="m9 12 2 2 4-4"></path>
            </svg>
          </div>
          <span class="type-label">选择题</span>
          <p class="type-desc">单选题、多选题等</p>
        </div>
        
        <div class="type-card" @click="goEdit('matching')">
          <div class="card-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M16 3h6v6"></path>
              <path d="M8 21H2v-6"></path>
              <path d="M3 3v18h18"></path>
              <path d="M10 14 2 22"></path>
              <path d="M14 10l8 8"></path>
            </svg>
          </div>
          <span class="type-label">连线题</span>
          <p class="type-desc">左右项配对</p>
        </div>
        
        <div class="type-card" @click="goEdit('correction')">
          <div class="card-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m18 6-12 12"></path>
              <path d="m6 6 12 12"></path>
            </svg>
          </div>
          <span class="type-label">改错题</span>
          <p class="type-desc">改错、填空等</p>
        </div>
        
        <div class="type-card" @click="goEdit('fill-blank')">
          <div class="card-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14,2 14,8 20,8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10,9 9,9 8,9"></polyline>
            </svg>
          </div>
          <span class="type-label">填空题</span>
          <p class="type-desc">输入文本后双击单词生成填空</p>
        </div>
        
        <div class="type-card" @click="goEdit('comprehension')">
          <div class="card-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
          </div>
          <span class="type-label">主观题</span>
          <p class="type-desc">简答题、理解题、总结题（主旨题）</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const goBack = () => {
  router.push({ name: 'QuestionBank' })
}

const goEdit = (type: string) => {
  router.push({
    name: 'QuestionEditByType',
    params: { materialId: route.params.materialId, type }
  })
}

const goBatchImport = () => {
  router.push({
    name: 'BatchImport',
    params: { materialId: route.params.materialId }
  })
}
</script>

<style scoped>
.question-type-page {
  padding: 32px;
  background-color: #FAFBFC;
  min-height: 100vh;
}

/* 插画样式 */
.illustration-header {
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
  animation: fadeIn 0.8s ease-out;
}

.illustration-content {
  position: relative;
  animation: float 3s ease-in-out infinite;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

/* 卡片样式 */
.question-type-card {
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  padding: 24px;
  position: relative;
  overflow: hidden;
}

.question-type-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
}

/* 头部样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #F0F2F5;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.3);
  animation: float 3s ease-in-out infinite;
}

.card-header h2 {
  margin: 0;
  color: #1A202C;
  font-size: 18px;
  font-weight: 600;
}

/* 按钮样式 */
.secondary-button {
  background: #FFFFFF !important;
  border: 1px solid #E2E8F0 !important;
  color: #4A5568 !important;
  border-radius: 12px !important;
  padding: 10px 20px !important;
  font-weight: 500 !important;
  transition: all 0.3s ease !important;
}

.secondary-button:hover {
  border-color: #8C7CF0 !important;
  color: #8C7CF0 !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.2) !important;
}

/* 提示文本 */
.tip {
  margin-bottom: 24px;
  color: #606266;
  font-size: 14px;
  padding-left: 8px;
  border-left: 4px solid #8C7CF0;
}

/* 题型选项 */
.type-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.type-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.1);
  position: relative;
  overflow: hidden;
}

.type-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.type-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(140, 124, 240, 0.2);
  border-color: #8C7CF0;
}

.type-card:hover::before {
  transform: scaleX(1);
}

.card-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #E8E4FF, #F0ECFF);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  color: #8C7CF0;
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.2);
  transition: all 0.3s ease;
}

.type-card:hover .card-icon {
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
  color: #FFFFFF;
  transform: scale(1.05);
}

.type-label {
  font-size: 16px;
  font-weight: 600;
  color: #1A202C;
  display: block;
  margin-bottom: 8px;
}

.type-desc {
  font-size: 14px;
  color: #8B9BB4;
  margin: 0;
  line-height: 1.4;
}

.batch-card {
  border: 2px dashed #8C7CF0;
  background: rgba(140, 124, 240, 0.05);
}

.batch-card .card-icon {
  background: linear-gradient(135deg, #8C7CF0, #C6B9FF);
  color: #FFFFFF;
}

.batch-card:hover {
  background: rgba(140, 124, 240, 0.1);
  border-style: solid;
}
</style>
