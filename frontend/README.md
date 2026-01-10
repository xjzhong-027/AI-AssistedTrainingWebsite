# 在线考试系统前端

基于 Vue 3 + TypeScript + Element Plus 开发的在线考试系统前端。

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **TypeScript** - JavaScript 的超集
- **Vite** - 下一代前端构建工具
- **Vue Router 4** - 官方路由管理器
- **Pinia** - Vue 的状态管理库
- **Element Plus** - 基于 Vue 3 的组件库
- **Axios** - HTTP 客户端

## 项目结构

```
frontend/
├── public/              # 静态资源
├── src/
│   ├── api/            # API接口定义
│   ├── components/     # 公共组件
│   │   ├── Layout/    # 布局组件
│   │   └── common/    # 通用组件
│   ├── views/         # 页面组件
│   ├── stores/        # Pinia状态管理
│   ├── utils/         # 工具函数
│   ├── types/         # TypeScript类型定义
│   ├── composables/   # 组合式函数
│   ├── router/        # 路由配置
│   ├── styles/        # 全局样式
│   ├── App.vue        # 根组件
│   └── main.ts        # 入口文件
├── .eslintrc.cjs      # ESLint配置
├── .prettierrc        # Prettier配置
├── vite.config.ts     # Vite配置
└── package.json        # 依赖配置
```

## 开发

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

开发服务器将在 `http://localhost:3000` 启动。

### 构建生产版本

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## 配置说明

### 后端API地址

后端API地址配置在 `vite.config.ts` 中的代理设置：

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8080',
      changeOrigin: true,
    }
  }
}
```

如果后端运行在不同的地址或端口，请修改此配置。

## 功能模块

### 已实现

- ✅ 项目初始化和配置
- ✅ 用户登录/注册
- ✅ 路由配置和守卫
- ✅ Layout布局组件
- ✅ 用户状态管理（Pinia）
- ✅ API请求封装
- ✅ 工具函数（存储、格式化等）

### 待实现

- ⏳ 考试管理模块（列表、创建、编辑、删除）
- ⏳ 题目管理模块（列表、创建、编辑、删除）
- ⏳ 答题模块（参加考试、答题界面、提交）
- ⏳ 成绩管理模块（查看成绩、统计、手动评分）
- ⏳ 个人中心

## 开发规范

### 代码风格

项目使用 ESLint + Prettier 进行代码规范检查。

### 提交规范

- 使用有意义的提交信息
- 每次提交前运行 `npm run lint` 检查代码

## 注意事项

1. 确保后端服务已启动（默认端口 8080）
2. 首次使用需要先注册用户
3. 不同角色（学生/教师/管理员）看到的功能不同

## 许可证

MIT
