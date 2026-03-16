<template>
  <div class="recommendation">
    <div class="recommendation-header">
      <h5>核心主题</h5>
      <p>{{ recommendation.core_theme }}</p>
    </div>
    
    <div class="recommendation-header">
      <h5>学习动机</h5>
      <p>{{ recommendation.theme_motivation }}</p>
    </div>
    
    <div class="recommendation-header">
      <h5>关键词汇</h5>
      <div class="keywords">
        <el-tag 
          v-for="(word, index) in recommendation.key_vocabulary" 
          :key="index"
          size="small"
          class="keyword-tag"
        >
          {{ word }}
        </el-tag>
      </div>
    </div>
    
    <div class="recommendation-header">
      <h5>推荐学习素材</h5>
      <div class="materials">
        <div 
          v-for="(material, index) in recommendation.materials" 
          :key="index"
          class="material-item"
        >
          <span class="material-type">{{ material.type === 'video' ? '视频' : '文章' }}</span>
          <a :href="material.url" target="_blank" class="material-title">{{ material.title }}</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  recommendation: {
    type: Object,
    required: true
  }
})
</script>

<style scoped>
.recommendation {
  background: rgba(255, 255, 255, 0.95);
  padding: 32px;
  border-radius: 24px;
  border: 1px solid rgba(198, 185, 255, 0.2);
  box-shadow: 0 8px 32px rgba(140, 124, 240, 0.08);
  backdrop-filter: blur(10px);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

.recommendation-header {
  margin-bottom: 24px;
}

.recommendation-header h5 {
  margin: 0 0 12px 0;
  background: linear-gradient(135deg, #8C7CF0 0%, #C6B9FF 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.3px;
}

.recommendation-header p {
  margin: 0;
  font-size: 15px;
  line-height: 1.8;
  color: #5A5A7E;
  font-weight: 500;
}

.keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.keyword-tag {
  background: linear-gradient(135deg, #E8E4FF 0%, #F0EFFF 100%);
  border: 1px solid rgba(198, 185, 255, 0.4);
  color: #8C7CF0;
  font-weight: 600;
  padding: 10px 20px;
  border-radius: 12px;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.1);
  transition: all 0.3s ease;
}

.keyword-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(140, 124, 240, 0.2);
}

.materials {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.material-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, #F8F7FF 0%, #F0EFFF 100%);
  border-radius: 20px;
  border: 1px solid rgba(198, 185, 255, 0.2);
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(140, 124, 240, 0.08);
}

.material-item:hover {
  transform: translateX(6px);
  box-shadow: 0 6px 20px rgba(140, 124, 240, 0.15);
  background: linear-gradient(135deg, #F0EFFF 0%, #E8E4FF 100%);
}

.material-type {
  min-width: 50px;
  font-size: 13px;
  font-weight: 700;
  background: linear-gradient(135deg, #8C7CF0 0%, #A898F0 100%);
  color: white;
  padding: 8px 16px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(140, 124, 240, 0.3);
}

.material-title {
  flex: 1;
  font-size: 15px;
  color: #5A5A7E;
  text-decoration: none;
  transition: all 0.3s ease;
  font-weight: 600;
  line-height: 1.5;
}

.material-title:hover {
  color: #8C7CF0;
  text-decoration: underline;
}
</style>

