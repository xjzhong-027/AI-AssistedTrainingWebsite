# GitHub 任务管理指南

> **更新时间**: 2026-01-10
> **适用对象**: 所有项目团队成员

---

## 📋 目录

1. [任务发布流程](#任务发布流程)
2. [任务认领流程](#任务认领流程)
3. [标签系统](#标签系统)
4. [项目看板](#项目看板)
5. [里程碑管理](#里程碑管理)

---

## 🎯 任务发布流程

### 1. 创建 Issue

**项目负责人或团队成员可以创建任务：**

1. 进入 GitHub 仓库页面
2. 点击 **Issues** 标签
3. 点击 **New Issue** 按钮
4. 选择合适的模板：
   - **🆕 功能需求 (Feature Request)**: 新功能开发
   - **🐛 Bug 报告 (Bug Report)**: 问题修复
   - **📋 开发任务 (Development Task)**: 具体的开发任务

### 2. 填写任务信息

使用模板填写以下信息：

```markdown
标题格式：[类型] 简短描述
示例：
- [FEATURE] 实现管理员用户管理界面
- [BUG] 修复登录页面密码验证错误
- [TASK] 完成 API 文档更新
```

**必填字段：**
- 📋 任务描述：清晰描述要做什么
- 🎯 任务目标：具体的完成目标
- ✅ 验收标准：如何判断任务完成

**可选字段：**
- 📂 涉及文件/模块
- 🔧 技术要求
- 📊 工作量估算
- 🏷️ 优先级

### 3. 添加标签 (Labels)

根据任务类型添加合适的标签：

| 标签 | 说明 | 颜色 |
|------|------|------|
| `enhancement` | 新功能 | 🟢 绿色 |
| `bug` | Bug 修复 | 🔴 红色 |
| `task` | 开发任务 | 🔵 蓝色 |
| `documentation` | 文档相关 | 📘 浅蓝 |
| `frontend` | 前端相关 | 🎨 紫色 |
| `backend` | 后端相关 | ⚙️ 灰色 |
| `priority:high` | 高优先级 | 🔥 橙色 |
| `priority:medium` | 中优先级 | 🟡 黄色 |
| `priority:low` | 低优先级 | 🟢 绿色 |
| `good first issue` | 适合新手 | 💚 深绿 |
| `help wanted` | 需要帮助 | 💙 深蓝 |

### 4. 设置里程碑 (Milestone)

将任务关联到相应的里程碑：
- **v1.0 - 前后端分离完成**
- **v1.1 - 管理员功能开发**
- **v2.0 - 功能增强**

### 5. 分配任务 (可选)

- 如果已知道由谁负责，可以直接 Assign 给对应成员
- 如果开放认领，留空等待成员认领

---

## 👥 任务认领流程

### 对于开发者

#### 1. 浏览可认领的任务

访问 Issues 页面，筛选条件：
```
is:issue is:open no:assignee label:task
```

或查找特定类型：
```
is:issue is:open label:"good first issue"    # 新手友好任务
is:issue is:open label:"help wanted"         # 需要帮助的任务
is:issue is:open label:frontend              # 前端任务
is:issue is:open label:backend               # 后端任务
```

#### 2. 认领任务

在 Issue 评论区留言：
```
@项目负责人 我想认领这个任务

我的开发计划：
1. [简要描述实现思路]
2. 预计完成时间：X天

如有问题会及时沟通。
```

#### 3. 等待分配

项目维护者会：
- 审核你的申请
- 将任务 Assign 给你
- 在评论中确认并提供额外指导

#### 4. 开始开发

**创建功能分支：**
```bash
# 1. 确保在最新的 dev 分支
git checkout dev
git pull origin dev

# 2. 创建功能分支（根据任务类型命名）
git checkout -b feature/user-management      # 新功能
git checkout -b bugfix/login-error           # Bug 修复
git checkout -b docs/api-documentation       # 文档更新

# 3. 开始开发
```

**开发过程中：**
- 定期在 Issue 中更新进度
- 遇到问题及时在 Issue 中提问
- 提交代码时关联 Issue 号：
  ```bash
  git commit -m "feat: add user list page (#123)"
  ```

#### 5. 提交 Pull Request

开发完成后：

```bash
# 1. 推送到远程
git push origin feature/user-management

# 2. 在 GitHub 上创建 Pull Request
# 3. 填写 PR 模板
# 4. 在 PR 描述中关联 Issue：Closes #123
```

**PR 标题格式：**
```
feat: add user management interface (#123)
fix: resolve login password validation (#124)
docs: update API documentation (#125)
```

#### 6. 代码审查

- 等待至少 1 人审查通过
- 根据审查意见修改代码
- CI/CD 检查全部通过

#### 7. 合并和关闭

- PR 合并后，关联的 Issue 会自动关闭
- 任务标记为完成

---

## 🏷️ 标签系统

### 设置项目标签

**项目维护者需要在 GitHub 设置以下标签：**

访问：`Settings` → `Labels` → `New label`

#### 类型标签
```
enhancement       # 新功能           颜色: #84cc16
bug              # Bug 修复         颜色: #dc2626
task             # 开发任务         颜色: #3b82f6
documentation    # 文档相关         颜色: #06b6d4
refactor         # 重构             颜色: #8b5cf6
test             # 测试             颜色: #f59e0b
```

#### 模块标签
```
frontend         # 前端相关         颜色: #a855f7
backend          # 后端相关         颜色: #6b7280
database         # 数据库           颜色: #14b8a6
api              # API 相关         颜色: #f97316
ui/ux            # 界面设计         颜色: #ec4899
```

#### 优先级标签
```
priority:high    # 高优先级         颜色: #ef4444
priority:medium  # 中优先级         颜色: #fbbf24
priority:low     # 低优先级         颜色: #22c55e
```

#### 状态标签
```
in progress      # 进行中           颜色: #60a5fa
blocked          # 被阻塞           颜色: #f87171
needs review     # 需要审查         颜色: #fbbf24
duplicate        # 重复问题         颜色: #94a3b8
wontfix          # 不会修复         颜色: #64748b
```

#### 帮助标签
```
good first issue # 适合新手         颜色: #10b981
help wanted      # 需要帮助         颜色: #3b82f6
question         # 问题讨论         颜色: #a855f7
```

---

## 📊 项目看板

### 创建项目看板

1. 进入仓库页面，点击 **Projects** 标签
2. 点击 **New project**
3. 选择 **Board** 视图
4. 设置看板列：

```
📋 Backlog (待办)     - 所有待处理的任务
🎯 To Do (计划中)     - 已分配，准备开始
🔄 In Progress (进行中) - 正在开发
👀 Review (审查中)     - 等待代码审查
✅ Done (已完成)       - 已完成并合并
```

### 使用看板

**移动任务卡片：**
- 认领任务后 → 移动到 **To Do**
- 开始开发 → 移动到 **In Progress**
- 提交 PR → 移动到 **Review**
- PR 合并 → 自动移动到 **Done**

**自动化设置：**
```yaml
When: Issue is opened
Then: Add to project → Backlog

When: Issue is assigned
Then: Move to → To Do

When: PR is created
Then: Move to → Review

When: PR is merged
Then: Move to → Done
```

---

## 🎯 里程碑管理

### 创建里程碑

1. 进入 **Issues** → **Milestones**
2. 点击 **New milestone**
3. 填写信息：

```
标题: v1.1 - 管理员功能开发
描述: 完成管理员用户管理、权限控制等核心功能
截止日期: 2026-02-15
```

### 使用里程碑

**将任务关联到里程碑：**
- 创建 Issue 时选择对应的 Milestone
- 或在 Issue 页面右侧面板中设置

**跟踪进度：**
- 里程碑页面会显示完成百分比
- 可以看到哪些任务已完成，哪些还在进行

**里程碑示例：**
```
✅ v1.0 - 前后端分离完成 (100%)
  - 完成所有 API 接口开发
  - 完成学生端前端页面
  - 完成教师端前端页面

🔄 v1.1 - 管理员功能开发 (35%)
  - 用户管理界面
  - 班级管理功能
  - 权限控制系统
  - 数据导入导出

📋 v2.0 - 功能增强 (0%)
  - 图表可视化
  - 数据分析报告
  - 移动端适配
```

---

## 📱 快速命令参考

### GitHub 搜索语法

```bash
# 查找未分配的任务
is:issue is:open no:assignee label:task

# 查找高优先级 Bug
is:issue is:open label:bug label:priority:high

# 查找自己的任务
is:issue assignee:@me

# 查找特定里程碑的任务
is:issue milestone:"v1.1"

# 查找前端相关的开放任务
is:issue is:open label:frontend
```

### Git 提交关联 Issue

```bash
# 提交时关联 Issue
git commit -m "feat: add user list (#123)"

# PR 中自动关闭 Issue
在 PR 描述中添加：
Closes #123
Fixes #124
Resolves #125
```

---

## 💡 最佳实践

### 对于项目维护者

1. **及时响应认领请求**：24 小时内回复
2. **清晰的任务描述**：提供足够的上下文信息
3. **合理的任务拆分**：一个任务不超过 3 天工作量
4. **定期更新里程碑**：每周检查进度
5. **鼓励新人参与**：标记 "good first issue"

### 对于开发者

1. **先沟通再认领**：确保理解任务需求
2. **及时更新进度**：遇到问题及时反馈
3. **小步提交**：不要一次提交太多改动
4. **完整测试**：提交前充分测试
5. **清晰的 PR 描述**：说明改动内容和测试情况

---

## 🔗 相关资源

- [GitHub Issues 文档](https://docs.github.com/en/issues)
- [GitHub Projects 文档](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [贡献指南](./CONTRIBUTING.md)
- [PR 模板](../../.github/PULL_REQUEST_TEMPLATE.md)

---

## ❓ 常见问题

### Q1: 我可以同时认领多个任务吗？
**A**: 建议新成员一次只认领 1 个任务，熟悉流程后可以同时进行 2-3 个不同类型的任务。

### Q2: 认领后发现任务太难怎么办？
**A**: 及时在 Issue 中说明情况，寻求帮助或请求重新分配。

### Q3: 任务做到一半需要暂停怎么办？
**A**: 在 Issue 中更新状态，说明原因和预计恢复时间。如果长时间无法继续，应该释放任务。

### Q4: 如何知道哪些任务适合我？
**A**:
- 新手：查找 `good first issue` 标签
- 前端开发：查找 `frontend` 标签
- 后端开发：查找 `backend` 标签
- 查看任务的技能要求部分

### Q5: Issue 讨论太长，关键信息找不到怎么办？
**A**: 项目维护者会在 Issue 顶部添加 📌 置顶评论，总结关键决策和进展。

---

**欢迎参与项目开发！Happy Coding! 🎉**
