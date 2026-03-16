<template>
  <div class="overdue-rules-page">
      <el-card>
        <template #header>
          <div class="card-header">
            <h3>逾期扣分规则管理</h3>
            <el-button @click="goBack">返回</el-button>
          </div>
        </template>

        <!-- 规则列表 -->
        <el-table :data="rulesList" v-loading="loading" stripe border>
          <el-table-column prop="rule_name" label="规则名称" min-width="150">
            <template #default="{ row }">{{ row.rule_name || row.name }}</template>
          </el-table-column>
          <el-table-column prop="description" label="规则描述" min-width="200"></el-table-column>
          <el-table-column prop="is_default" label="默认规则" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_default ? 'success' : 'info'">
                {{ row.is_default ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="扣分阶段" width="100">
            <template #default="{ row }">
              {{ row.periods?.length || 0 }} 个阶段
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="viewRuleDetail(row.id)">查看详情</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 空状态 -->
        <el-empty v-if="!loading && rulesList.length === 0" description="暂无逾期扣分规则"></el-empty>
      </el-card>

      <!-- 规则详情对话框 -->
      <el-dialog v-model="detailDialogVisible" title="逾期扣分规则详情" width="600px">
        <div v-if="currentRule" class="rule-detail">
          <div class="detail-item">
            <span class="label">规则名称：</span>
            <span class="value">{{ currentRule.rule_name || currentRule.name }}</span>
          </div>
          <div class="detail-item">
            <span class="label">规则描述：</span>
            <span class="value">{{ currentRule.description }}</span>
          </div>
          <div class="detail-item">
            <span class="label">默认规则：</span>
            <el-tag :type="currentRule.is_default ? 'success' : 'info'">
              {{ currentRule.is_default ? '是' : '否' }}
            </el-tag>
          </div>

          <!-- 扣分阶段列表 -->
          <div class="detail-item" style="margin-top: 20px">
            <span class="label">扣分阶段：</span>
          </div>
          <el-table :data="currentRule.periods" border style="margin-top: 10px">
            <el-table-column label="时间范围" min-width="150">
              <template #default="{ row }">
                {{ row.min_days }}-{{ row.max_days ?? '∞' }} 天
              </template>
            </el-table-column>
            <el-table-column label="扣分比例" width="120">
              <template #default="{ row }">
                <el-tag type="warning">{{ ((1 - Number(row.deduction_rate)) * 100).toFixed(0) }}%</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="说明" min-width="150"></el-table-column>
          </el-table>
        </div>
        <div v-else class="loading-container">
          <el-skeleton :rows="3" animated />
        </div>
        <template #footer>
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </template>
      </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getOverdueRules, getOverdueRuleDetail } from '@/api/query'
import { formatDateTime } from '@/utils/format'
import type { OverdueRule } from '@/types/query'

const router = useRouter()
const loading = ref(false)
const rulesList = ref<OverdueRule[]>([])
const detailDialogVisible = ref(false)
const currentRule = ref<OverdueRule | null>(null)

// 加载规则列表
const loadRules = async () => {
  loading.value = true
  try {
    rulesList.value = await getOverdueRules()
  } catch (error: any) {
    console.error('加载逾期规则失败', error)
    ElMessage.error(error.message || '加载逾期规则失败')
  } finally {
    loading.value = false
  }
}

// 查看规则详情
const viewRuleDetail = async (ruleId: number) => {
  detailDialogVisible.value = true
  currentRule.value = null

  try {
    currentRule.value = await getOverdueRuleDetail(ruleId)
  } catch (error: any) {
    console.error('加载规则详情失败', error)
    ElMessage.error(error.message || '加载规则详情失败')
    detailDialogVisible.value = false
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  loadRules()
})
</script>

<style scoped>
.overdue-rules-page {
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

.rule-detail {
  padding: 20px;
}

.detail-item {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
}

.detail-item .label {
  font-weight: 500;
  color: #606266;
  min-width: 100px;
}

.detail-item .value {
  color: #1A1A1A;
}

.loading-container {
  padding: 20px;
}

:deep(.el-card) {
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-dialog) {
  border-radius: 20px;
}
</style>
