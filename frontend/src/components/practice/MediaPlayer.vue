<template>
  <div class="media-player">
    <div class="player-container">
      <video
        v-if="isVideo"
        :src="mediaUrl"
        controls
        playsinline
        class="media-element"
      ></video>
      <audio
        v-else
        :src="mediaUrl"
        controls
        class="media-element"
      ></audio>
    </div>
    
    <div v-if="transcript" class="transcript-section">
      <h5>视频文本</h5>
      <div class="transcript-content">{{ transcript }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  mediaUrl: {
    type: String,
    required: true
  },
  transcript: {
    type: String,
    default: ''
  },
  isVideo: {
    type: Boolean,
    default: true
  }
})
</script>

<style scoped>
.media-player {
  background: #FFFFFF;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(140, 124, 240, 0.15);
  border: 1px solid #F0F2F5;
}

.player-container {
  margin-bottom: 20px;
}

.media-element {
  width: 100%;
  max-height: 360px;
  border-radius: 12px;
  background: linear-gradient(135deg, #E8E4FF, #F5F3FF);
  border: 2px solid #F0F2F5;
}

.transcript-section {
  margin-top: 20px;
}

.transcript-section h5 {
  margin: 0 0 12px 0;
  color: #1A202C;
  font-size: 14px;
  font-weight: 600;
}

.transcript-content {
  padding: 16px;
  background: #F8F9FA;
  border-radius: 12px;
  border: 1px solid #E9ECEF;
  font-size: 14px;
  line-height: 1.6;
  color: #495057;
  white-space: pre-wrap;
}
</style>

