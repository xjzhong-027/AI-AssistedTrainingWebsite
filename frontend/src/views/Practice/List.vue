<template>
  <div class="practice-list-page">
      <div class="container card">
        <h1>可用练习</h1>
        <div v-if="loading" class="loading">加载中...</div>
        <ul v-else class="practice-list">
          <li
            v-for="(practice, index) in practiceList"
            :key="practice.id"
            :class="{ selected: selectedIndex === index }"
            @click="selectPractice(index, practice.id)"
          >
            <div class="practice-info">
              <h3>{{ practice.unit_name }}</h3>
              <p class="practice-description">练习类型: {{ practice.unit_type === 'practice' ? '练习' : '考试' }}</p>
              <div class="practice-meta">
                <span class="practice-time">单元ID: {{ practice.id }}</span>
              </div>
            </div>
            <div class="practice-actions">
              <button class="start-button" @click.stop="handleStartPractice(practice.id)">开始练习</button>
            </div>
          </li>
        </ul>
        <div v-if="!loading && practiceList.length === 0" class="no-practices">
          <p>暂无可用练习</p>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getAllPractices, startPractice as startPracticeAPI } from '@/api/practice'
import { useUserStore } from '@/stores/user'
import type { Unit } from '@/api/practice'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const selectedIndex = ref<number | null>(null)
const practiceList = ref<Unit[]>([])

const selectPractice = (index: number, id: number) => {
  selectedIndex.value = selectedIndex.value === index ? null : index
}

const formatDate = (date: string) => {
  if (!date) return '-'
  const d = new Date(date)
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleStartPractice = async (unitId: number) => {
  try {
    const record = await startPracticeAPI(unitId)
    ElMessage.success('练习已开始')
    router.push(`/practice/${unitId}/take`)
  } catch (error) {
    console.error('开始练习失败', error)
    ElMessage.error('开始练习失败，请稍后重试')
  }
}

const loadPractices = async () => {
  loading.value = true
  try {
    const practices = await getAllPractices()
    practiceList.value = practices
  } catch (error) {
    console.error('加载练习列表失败', error)
    ElMessage.error('加载练习列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPractices()
})
</script>

<style scoped>
.practice-list-page {
  width: 100%;
  padding: 0;
}

.container {
  max-width: 800px;
  margin: 50px auto;
  padding: 40px;
}

h1 {
  text-align: center;
  color: #1A1A1A;
  margin-bottom: 30px;
  font-size: 36px;
  font-weight: 700;
  position: relative;
  z-index: 1;
}

h1::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, #99B6B4, #D48982);
  border-radius: 2px;
}

.practice-list {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.practice-list li {
  background-color: rgba(186, 207, 206, 0.1);
  padding: 18px 20px;
  margin-bottom: 12px;
  border-radius: 12px;
  border: 1px solid #BACFCE;
  border-left: 4px solid #99B6B4;
  transition: all 0.3s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.practice-list li:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-3px);
  background-color: rgba(186, 207, 206, 0.15);
  border-left-color: #D48982;
}

.practice-list li.selected {
  background-color: #1A1A1A;
  color: #FFFFFF;
  border-left-color: #D48982;
}

.practice-list li.selected * {
  color: #FFFFFF;
}

.practice-info {
  flex: 1;
}

.practice-info h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: inherit;
}

.practice-description {
  font-size: 14px;
  color: #666;
  margin: 0 0 8px 0;
}

.practice-list li.selected .practice-description {
  color: rgba(255, 255, 255, 0.8);
}

.practice-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #999;
}

.practice-list li.selected .practice-meta {
  color: rgba(255, 255, 255, 0.7);
}

.practice-time {
  color: inherit;
}

.practice-actions {
  margin-left: 20px;
}

.start-button {
  padding: 8px 16px;
  background-color: #D48982;
  color: #FFFFFF;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.start-button:hover {
  background-color: #c07770;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.practice-list li.selected .start-button {
  background-color: #FFFFFF;
  color: #1A1A1A;
}

.practice-list li.selected .start-button:hover {
  background-color: rgba(255, 255, 255, 0.9);
}

.no-practices {
  text-align: center;
  padding: 40px;
  color: #666;
}
</style>

