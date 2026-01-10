# 贡献指南 (Contributing Guide)

> **更新时间**: 2026-01-10
> **适用对象**: 所有项目开发人员

---

## 📋 目录

1. [开发环境准备](#开发环境准备)
2. [分支管理策略](#分支管理策略)
3. [开发流程](#开发流程)
4. [代码规范](#代码规范)
5. [提交规范](#提交规范)
6. [Pull Request流程](#pull-request流程)
7. [测试要求](#测试要求)

---

## 🔧 开发环境准备

### 后端环境

```bash
# Python版本
Python 3.8+

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 创建测试用户
python create_test_users.py

# 启动开发服务器
python manage.py runserver
```

### 前端环境

```bash
# Node.js版本
Node.js 16+

# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

### API文档访问

- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- OpenAPI Schema: http://localhost:8000/api/schema/

---

## 🌿 分支管理策略

采用 **Git Flow** 分支策略：

### 主要分支

| 分支 | 说明 | 保护级别 |
|------|------|---------|
| `main` | 生产环境代码，只接受合并 | 🔒 保护 |
| `dev` | 开发主分支，集成测试 | 🔒 保护 |
| `feature/*` | 功能开发分支 | 📝 普通 |
| `bugfix/*` | Bug修复分支 | 📝 普通 |
| `hotfix/*` | 紧急修复分支 | 📝 普通 |

### 分支命名规范

```bash
# 功能开发
feature/user-management
feature/admin-dashboard

# Bug修复
bugfix/login-error
bugfix/api-timeout

# 紧急修复
hotfix/security-patch
hotfix/database-migration
```

### 分支创建和合并

```bash
# 从dev创建功能分支
git checkout dev
git pull origin dev
git checkout -b feature/your-feature-name

# 开发完成后，推送到远程
git push origin feature/your-feature-name

# 在GitHub/GitLab上创建Pull Request到dev分支
# 经过代码审查后合并
```

---

## 💻 开发流程

### 1. 认领任务

- 在项目看板（GitHub Issues/Jira）中认领任务
- 将任务状态改为"进行中"
- 评估工作量和完成时间

### 2. 创建分支

```bash
git checkout dev
git pull origin dev
git checkout -b feature/task-name
```

### 3. 开发实现

- 遵循代码规范
- 编写单元测试
- 更新API文档（如有新增API）
- 更新相关文档

### 4. 本地测试

```bash
# 后端测试
python manage.py test

# 前端测试
npm run test

# 代码格式检查
npm run lint
```

### 5. 提交代码

```bash
git add .
git commit -m "feat: add user management feature"
git push origin feature/task-name
```

### 6. 创建Pull Request

- 填写PR模板
- 关联相关Issue
- 请求代码审查
- 等待CI/CD检查通过

### 7. 代码审查

- 至少1人审查通过
- 解决所有审查意见
- CI/CD检查通过

### 8. 合并和部署

- 合并到dev分支
- 自动部署到测试环境
- 测试验证
- 定期合并到main分支并部署生产环境

---

## 📝 代码规范

### Python/Django规范

```python
# 1. 使用Service层，禁止直接操作models
# ❌ 错误
from Account.models import Students
students = Students.objects.all()

# ✅ 正确
from Account.services.user_service_impl import UserServiceImpl
students = UserServiceImpl.get_all_students()

# 2. 使用统一的Result响应格式
from common.api.response import Result

def my_view(request):
    return Result.success(data=data, message='操作成功')

# 3. API视图使用@extend_schema装饰器
from drf_spectacular.utils import extend_schema

@extend_schema(tags=['用户管理'])
class MyView(APIView):
    pass

# 4. 序列化器命名规范
class StudentSerializer(serializers.ModelSerializer):  # 读取
class StudentCreateSerializer(serializers.ModelSerializer):  # 创建
class StudentUpdateSerializer(serializers.ModelSerializer):  # 更新
```

### TypeScript/Vue规范

```typescript
// 1. 使用Composition API
import { ref, onMounted } from 'vue'

// 2. 类型定义
interface User {
  id: number
  username: string
  role: UserRole
}

// 3. API调用使用统一封装
import { getUserById } from '@/api/user'

// 4. 错误处理
try {
  const user = await getUserById(id)
} catch (error: any) {
  ElMessage.error(error.message || '操作失败')
}

// 5. 命名规范
const userName = ref('')  // camelCase
const UserProfile = {}    // PascalCase for components
```

### 代码格式化

```bash
# 后端（Python）
black .
flake8 .

# 前端（TypeScript/Vue）
npm run lint
npm run format
```

---

## 📦 提交规范

采用 **Conventional Commits** 规范：

### 提交类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: add user management page` |
| `fix` | Bug修复 | `fix: resolve login timeout issue` |
| `docs` | 文档更新 | `docs: update API documentation` |
| `style` | 代码格式（不影响功能） | `style: format code with prettier` |
| `refactor` | 重构（不改变功能） | `refactor: extract common logic to service` |
| `test` | 测试相关 | `test: add unit tests for user service` |
| `chore` | 构建/工具相关 | `chore: update dependencies` |

### 提交消息格式

```bash
<type>(<scope>): <subject>

<body>

<footer>
```

### 示例

```bash
# 简单提交
git commit -m "feat: add user management API"

# 完整提交
git commit -m "feat(user): add batch import functionality

- Support Excel file upload
- Validate student data
- Auto-assign to classes

Closes #123"
```

### Co-authored提交

```bash
git commit -m "feat: implement user dashboard

Co-Authored-By: Alice <alice@example.com>
Co-Authored-By: Bob <bob@example.com>"
```

---

## 🔄 Pull Request流程

### PR创建清单

- [ ] 分支是从最新的dev创建的
- [ ] 所有测试通过
- [ ] 代码已格式化
- [ ] 文档已更新（如有必要）
- [ ] PR标题遵循提交规范
- [ ] 填写了PR描述模板
- [ ] 关联了相关Issue

### PR模板

```markdown
## 功能描述
<!-- 简要描述这个PR实现了什么功能 -->

## 变更类型
- [ ] 新功能 (feat)
- [ ] Bug修复 (fix)
- [ ] 重构 (refactor)
- [ ] 文档更新 (docs)
- [ ] 其他

## 相关Issue
Closes #<issue-number>

## 实现说明
<!-- 详细描述实现方案、技术选型等 -->

## 测试说明
<!-- 如何测试这个功能 -->
- [ ] 单元测试通过
- [ ] 手动测试完成
- [ ] API文档已更新

## 截图/演示
<!-- 如有UI变更，请提供截图 -->

## 检查清单
- [ ] 代码遵循项目规范
- [ ] 无控制台错误或警告
- [ ] 已测试多种场景
- [ ] 文档已更新
```

### 代码审查要点

**审查者应检查**：
1. **功能正确性**：实现是否符合需求
2. **代码质量**：遵循规范、可读性、可维护性
3. **安全性**：是否有SQL注入、XSS等漏洞
4. **性能**：是否有性能问题（N+1查询等）
5. **测试覆盖**：是否有足够的测试
6. **文档完整性**：API文档、注释是否完整

**审查意见类型**：
- 🔴 **必须修改**：阻塞合并的严重问题
- 🟡 **建议修改**：可选的优化建议
- 💬 **讨论**：需要讨论的技术决策
- ✅ **认可**：代码没有问题

---

## 🧪 测试要求

### 后端测试

```python
# 单元测试
python manage.py test

# 覆盖率测试
coverage run --source='.' manage.py test
coverage report

# API测试（使用Postman集合）
# 见 docs/02-设计文档/.../任务2.4-Postman测试方案.md
```

### 前端测试

```bash
# 单元测试
npm run test

# E2E测试
npm run test:e2e

# 类型检查
npm run type-check

# 代码检查
npm run lint
```

### 测试覆盖率要求

| 类型 | 最低覆盖率 |
|------|----------|
| Service层 | 80% |
| API视图 | 70% |
| 前端组件 | 60% |

---

## 📚 相关文档

- [开发原则](.cursor/rules/development-principles.mdc)
- [API文档](http://localhost:8000/api/docs/)
- [项目架构](docs/01-需求文档/系统架构总结-2024-12.md)
- [前后端分离进度](docs/02-设计文档/前后端分离设计/frontend-backend-separation/progress.md)

---

## 🤝 获取帮助

### 文档
- 开发文档: `docs/`
- API文档: http://localhost:8000/api/docs/

### 沟通渠道
- 技术问题: 在Issue中提问
- 代码审查: 在PR中讨论
- 紧急问题: 联系项目负责人

---

## ⚠️ 注意事项

### 禁止事项
- ❌ 直接push到main或dev分支
- ❌ 跳过代码审查直接合并
- ❌ 提交包含敏感信息的代码（密码、密钥等）
- ❌ 提交未测试的代码
- ❌ 直接操作models，必须使用Service层

### 最佳实践
- ✅ 小步提交，每次提交只做一件事
- ✅ 编写清晰的提交消息
- ✅ 及时同步dev分支的更新
- ✅ 代码审查时友善沟通
- ✅ 遇到问题及时求助

---

**欢迎加入团队！Happy Coding! 🎉**
