<template>
  <div class="schedule-adjustment-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>调课补课管理</span>
          <el-button @click="goBack">返回检索面板</el-button>
        </div>
      </template>
      <div class="placeholder-content">
        <p>
          <strong>调课补课</strong> 功能需后端提供 REST API 后对接。
        </p>
        <p class="desc">
          原系统在 Query 模块下通过 Django 模板实现：调课表单、补课表单、调课/补课记录列表及批量删除。前后端分离后需在 <code>Query/api/views.py</code> 中新增调课/补课列表、创建、删除等接口，再在此处实现表单与列表。
        </p>
        <el-button type="primary" @click="goBack">返回</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.push('/query')
}
</script>

<style scoped>
.schedule-adjustment-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.placeholder-content {
  padding: 40px 20px;
  text-align: center;
}

.placeholder-content p {
  margin-bottom: 16px;
  color: #606266;
}

.placeholder-content .desc {
  font-size: 14px;
  color: #909399;
  margin-bottom: 24px;
}

.placeholder-content code {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}
</style>
