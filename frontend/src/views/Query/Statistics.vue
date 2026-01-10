<template>
  <Layout>
    <div class="statistics-page">
      <el-card>
        <template #header>
          <div class="card-header">
            <h3>数据统计分析</h3>
            <el-button @click="goBack">返回</el-button>
          </div>
        </template>

        <!-- 统计类型选择 -->
        <el-tabs v-model="activeTab" @tab-change="handleTabChange">
          <el-tab-pane label="班级统计" name="class">
            <!-- 班级选择 -->
            <el-form :inline="true" class="query-form">
              <el-form-item label="选择班级">
                <el-select v-model="selectedClassId" placeholder="请选择班级" style="width: 200px" @change="loadClassStatistics">
                  <el-option
                    v-for="cls in classList"
                    :key="cls.id"
                    :label="cls.class_name"
                    :value="cls.id"
                  ></el-option>
                </el-select>
              </el-form-item>
            </el-form>

            <!-- 班级统计数据 -->
            <div v-if="classStatistics && !loading" class="statistics-content">
              <el-row :gutter="20">
                <el-col :span="6">
                  <div class="stat-card">
                    <div class="stat-value">{{ classStatistics.total_students }}</div>
                    <div class="stat-label">总学生数</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="stat-card">
                    <div class="stat-value">{{ classStatistics.completed_students }}</div>
                    <div class="stat-label">完成人数</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="stat-card">
                    <div class="stat-value">{{ classStatistics.completion_rate.toFixed(1) }}%</div>
                    <div class="stat-label">完成率</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="stat-card">
                    <div class="stat-value">{{ classStatistics.average_score.toFixed(1) }}</div>
                    <div class="stat-label">平均分</div>
                  </div>
                </el-col>
              </el-row>

              <el-row :gutter="20" style="margin-top: 20px">
                <el-col :span="12">
                  <div class="stat-card">
                    <div class="stat-value">{{ classStatistics.exam_count }}</div>
                    <div class="stat-label">考试任务数</div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="stat-card">
                    <div class="stat-value">{{ classStatistics.practice_count }}</div>
                    <div class="stat-label">练习任务数</div>
                  </div>
                </el-col>
              </el-row>

              <!-- 图表展示区域 - 预留 -->
              <div class="chart-container" style="margin-top: 30px">
                <div class="chart-placeholder">
                  <el-empty description="图表功能待完善（可使用 Chart.js 或 ECharts）"></el-empty>
                </div>
              </div>
            </div>

            <el-empty v-if="!loading && !classStatistics" description="请选择班级查看统计数据"></el-empty>
          </el-tab-pane>

          <el-tab-pane label="单元统计" name="unit">
            <!-- 单元选择 -->
            <el-form :inline="true" class="query-form">
              <el-form-item label="选择单元">
                <el-select v-model="selectedUnitId" placeholder="请选择单元" style="width: 300px" @change="loadUnitStatistics">
                  <el-option
                    v-for="unit in unitList"
                    :key="unit.id"
                    :label="unit.unit_name"
                    :value="unit.id"
                  ></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="班级筛选">
                <el-select v-model="unitClassFilter" placeholder="全部班级" clearable style="width: 200px" @change="loadUnitStatistics">
                  <el-option
                    v-for="cls in classList"
                    :key="cls.id"
                    :label="cls.class_name"
                    :value="cls.id"
                  ></el-option>
                </el-select>
              </el-form-item>
            </el-form>

            <!-- 单元统计数据 -->
            <div v-if="unitStatistics && !loading" class="statistics-content">
              <el-row :gutter="20">
                <el-col :span="6">
                  <div class="stat-card">
                    <div class="stat-value">{{ unitStatistics.total_students }}</div>
                    <div class="stat-label">总学生数</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="stat-card">
                    <div class="stat-value">{{ unitStatistics.completed_students }}</div>
                    <div class="stat-label">完成人数</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="stat-card">
                    <div class="stat-value">{{ unitStatistics.completion_rate.toFixed(1) }}%</div>
                    <div class="stat-label">完成率</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="stat-card">
                    <div class="stat-value">{{ unitStatistics.average_score.toFixed(1) }}</div>
                    <div class="stat-label">平均分</div>
                  </div>
                </el-col>
              </el-row>

              <el-row :gutter="20" style="margin-top: 20px">
                <el-col :span="8">
                  <div class="stat-card">
                    <div class="stat-value">{{ unitStatistics.highest_score }}</div>
                    <div class="stat-label">最高分</div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="stat-card">
                    <div class="stat-value">{{ unitStatistics.lowest_score }}</div>
                    <div class="stat-label">最低分</div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="stat-card">
                    <div class="stat-value">{{ unitStatistics.unit_name }}</div>
                    <div class="stat-label">单元名称</div>
                  </div>
                </el-col>
              </el-row>

              <!-- 图表展示区域 - 预留 -->
              <div class="chart-container" style="margin-top: 30px">
                <div class="chart-placeholder">
                  <el-empty description="图表功能待完善（可使用 Chart.js 或 ECharts）"></el-empty>
                </div>
              </div>
            </div>

            <el-empty v-if="!loading && !unitStatistics" description="请选择单元查看统计数据"></el-empty>
          </el-tab-pane>
        </el-tabs>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="5" animated />
        </div>
      </el-card>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import Layout from '@/components/Layout/index.vue'
import { getClassStatistics, getUnitStatistics } from '@/api/query'
import { getAllClasses } from '@/api/user'
import { getAllExams } from '@/api/exam'
import type { ClassStatistics, UnitStatistics } from '@/types/query'

const router = useRouter()
const loading = ref(false)
const activeTab = ref('class')

// 班级统计
const classList = ref<any[]>([])
const selectedClassId = ref<number | undefined>(undefined)
const classStatistics = ref<ClassStatistics | null>(null)

// 单元统计
const unitList = ref<any[]>([])
const selectedUnitId = ref<number | undefined>(undefined)
const unitClassFilter = ref<number | undefined>(undefined)
const unitStatistics = ref<UnitStatistics | null>(null)

// 获取班级列表
const loadClasses = async () => {
  try {
    classList.value = await getAllClasses()
    if (classList.value.length > 0 && !selectedClassId.value) {
      selectedClassId.value = classList.value[0].id
    }
  } catch (error: any) {
    console.error('加载班级列表失败', error)
    ElMessage.error(error.message || '加载班级列表失败')
  }
}

// 获取单元列表
const loadUnits = async () => {
  try {
    unitList.value = await getAllExams()
  } catch (error: any) {
    console.error('加载单元列表失败', error)
    ElMessage.error(error.message || '加载单元列表失败')
  }
}

// 加载班级统计
const loadClassStatistics = async () => {
  if (!selectedClassId.value) return

  loading.value = true
  try {
    classStatistics.value = await getClassStatistics(selectedClassId.value)
  } catch (error: any) {
    console.error('加载班级统计失败', error)
    ElMessage.error(error.message || '加载班级统计失败')
  } finally {
    loading.value = false
  }
}

// 加载单元统计
const loadUnitStatistics = async () => {
  if (!selectedUnitId.value) return

  loading.value = true
  try {
    unitStatistics.value = await getUnitStatistics(selectedUnitId.value, unitClassFilter.value)
  } catch (error: any) {
    console.error('加载单元统计失败', error)
    ElMessage.error(error.message || '加载单元统计失败')
  } finally {
    loading.value = false
  }
}

// 切换标签页
const handleTabChange = (tabName: string) => {
  if (tabName === 'class' && selectedClassId.value) {
    loadClassStatistics()
  } else if (tabName === 'unit' && selectedUnitId.value) {
    loadUnitStatistics()
  }
}

const goBack = () => {
  router.back()
}

onMounted(async () => {
  await Promise.all([loadClasses(), loadUnits()])
  if (selectedClassId.value) {
    loadClassStatistics()
  }
})
</script>

<style scoped>
.statistics-page {
  padding: 20px;
  background-color: #F9F8F3;
  min-height: 100vh;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
}

.query-form {
  margin: 20px 0;
}

.statistics-content {
  margin-top: 20px;
}

.stat-card {
  background: linear-gradient(135deg, #99B6B4 0%, #BACFCE 100%);
  padding: 30px;
  border-radius: 12px;
  text-align: center;
  color: #FFFFFF;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.chart-container {
  background: #FFFFFF;
  padding: 20px;
  border-radius: 12px;
  min-height: 300px;
}

.chart-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.loading-container {
  padding: 20px;
}

:deep(.el-card) {
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

:deep(.el-tabs__item) {
  font-size: 16px;
  font-weight: 500;
}
</style>
