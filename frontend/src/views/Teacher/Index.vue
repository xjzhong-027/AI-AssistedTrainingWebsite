<template>
  <div class="main">
    <h1>附件下载</h1>
    <table>
      <tbody>
        <tr>
          <th>文件</th>
          <th>*</th>
        </tr>
        <tr>
          <td>文件导入模板</td>
          <td>
            <button data-filename="模板.docx" @click="downloadFile">下载</button>
          </td>
        </tr>
        <tr>
          <td>周任务文件导入模板（分页）</td>
          <td>
            <button data-filename="分页模板.docx" @click="downloadFile">下载</button>
          </td>
        </tr>
        <tr>
          <td>模板说明</td>
          <td>
            <button data-filename="说明文件.docx" @click="downloadFile">下载</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
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
.main {
  max-width: 800px;
  margin: 40px auto;
  padding: 30px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.main h1 {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin-bottom: 30px;
  text-align: center;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

/* 表格样式 */
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

th,
td {
  padding: 15px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f9f9f9;
  font-weight: 600;
  color: #555;
}

tr:hover {
  background-color: #f8f8f8;
}

/* 按钮样式 */
button {
  padding: 10px 20px;
  background-color: #007bff;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
}

button:hover {
  background-color: #0056b3;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main {
    padding: 20px;
    margin: 20px;
  }

  table {
    display: block;
    overflow-x: auto;
  }

  th,
  td {
    padding: 10px;
  }

  button {
    padding: 8px 16px;
  }
}
</style>





