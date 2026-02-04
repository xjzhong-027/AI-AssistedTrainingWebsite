<template>
  <div class="exam-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>任务管理 - 高级功能</span>
          <el-button @click="goBack">返回任务列表</el-button>
        </div>
      </template>

      <div class="content">
        <p class="desc">
          原系统此处为「exam_management」：支持通过 Word 文档导入并解析题目内容（.docx），进行批量处理。
        </p>
        <p class="desc">
          前后端分离后，该功能需后端提供对应 REST API（如：上传 Word、解析、写入题目）后再在此处对接。当前仅保留入口，待 API 就绪后实现。
        </p>
        <el-empty v-if="!hasApi" description="高级功能待后端 API 支持后开放" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const hasApi = ref(false)

const goBack = () => {
  router.push({ name: 'ExamBank' })
}

onMounted(() => {
  // 后续可在此检测后端是否暴露高级接口，如 hasApi = true 则展示实际表单
})
</script>

<style scoped>
.exam-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content {
  padding: 20px 0;
}

.desc {
  color: #606266;
  line-height: 1.8;
  margin-bottom: 16px;
}
</style>
