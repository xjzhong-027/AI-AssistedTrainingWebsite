import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { ElMessage } from 'element-plus'
import { storage } from '@/utils/storage'
import type { User } from '@/types/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login/index.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register/index.vue'),
    meta: { title: '注册' }
  },
  {
    path: '/',
    component: () => import('@/components/Layout/index.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard/index.vue'),
        meta: { title: '首页' }
      },
      {
        path: 'exams',
        name: 'ExamList',
        component: () => import('@/views/Exam/List.vue'),
        meta: { title: '考试列表' }
      },
      {
        path: 'exams/create',
        name: 'ExamCreate',
        component: () => import('@/views/Exam/Create.vue'),
        meta: { title: '创建考试', roles: ['TEACHER', 'ADMIN'] }
      },
      {
        path: 'exams/:id/take',
        name: 'ExamTake',
        component: () => import('@/views/Exam/TakePage.vue'),
        meta: { title: '参加考试', roles: ['STUDENT'] }
      },
      {
        path: 'exams/:id/result',
        name: 'ExamResult',
        component: () => import('@/views/Exam/Result.vue'),
        meta: { title: '考试结果', roles: ['STUDENT'] }
      },
      {
        path: 'exams/:id/edit',
        name: 'ExamEdit',
        component: () => import('@/views/Exam/Edit.vue'),
        meta: { title: '编辑考试', roles: ['TEACHER', 'ADMIN'] }
      },
      {
        path: 'exams/:id',
        name: 'ExamDetail',
        component: () => import('@/views/Exam/Detail.vue'),
        meta: { title: '考试详情' }
      },
      {
        path: 'questions',
        name: 'QuestionList',
        component: () => import('@/views/Question/List.vue'),
        meta: { title: '题目列表', roles: ['TEACHER', 'ADMIN'] }
      },
      {
        path: 'questions/create',
        name: 'QuestionCreate',
        component: () => import('@/views/Question/Create.vue'),
        meta: { title: '创建题目', roles: ['TEACHER', 'ADMIN'] }
      },
      {
        path: 'questions/:id',
        name: 'QuestionDetail',
        component: () => import('@/views/Question/Detail.vue'),
        meta: { title: '题目详情', roles: ['TEACHER', 'ADMIN'] }
      },
      {
        path: 'questions/:id/edit',
        name: 'QuestionEdit',
        component: () => import('@/views/Question/Edit.vue'),
        meta: { title: '编辑题目', roles: ['TEACHER', 'ADMIN'] }
      },
      {
        path: 'scores',
        name: 'ScoreList',
        component: () => import('@/views/Score/List.vue'),
        meta: { title: '成绩列表' }
      },
      {
        path: 'scores/pending',
        name: 'ScorePending',
        component: () => import('@/views/Score/Pending.vue'),
        meta: { title: '待批改', roles: ['TEACHER', 'ADMIN'] }
      },
      {
        path: 'scores/:id',
        name: 'ScoreDetail',
        component: () => import('@/views/Score/Detail.vue'),
        meta: { title: '成绩详情' }
      },
      {
        path: 'exams/:id/scores',
        name: 'ExamScores',
        component: () => import('@/views/Score/ExamScores.vue'),
        meta: { title: '考试成绩', roles: ['TEACHER', 'ADMIN'] }
      },
      {
        path: 'scores/grade/:examRecordId',
        name: 'ScoreGrade',
        component: () => import('@/views/Score/Grade.vue'),
        meta: { title: '手动评分', roles: ['TEACHER', 'ADMIN'] }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/Profile/index.vue'),
        meta: { title: '个人中心' }
      },
      {
        path: 'student/index',
        name: 'StudentIndex',
        component: () => import('@/views/Dashboard/index.vue'),
        meta: { title: '学生主页', roles: ['STUDENT'] }
      },
      {
        path: 'student/dashboard',
        name: 'StudentDashboard',
        component: () => import('@/views/Student/Dashboard.vue'),
        meta: { title: '学生仪表板', roles: ['STUDENT'] }
      },
      {
        path: 'practice/list',
        name: 'PracticeList',
        component: () => import('@/views/Practice/List.vue'),
        meta: { title: '练习列表', roles: ['STUDENT'] }
      },
      {
        path: 'practice/:id/take',
        name: 'PracticeTake',
        component: () => import('@/views/Practice/Take.vue'),
        meta: { title: '开始练习', roles: ['STUDENT'] }
      },
      {
        path: 'practice/:id/result',
        name: 'PracticeResult',
        component: () => import('@/views/Practice/Result.vue'),
        meta: { title: '练习结果', roles: ['STUDENT'] }
      },
      {
        path: 'forum',
        name: 'ForumStudent',
        component: () => import('@/views/Forum/Student.vue'),
        meta: { title: '论坛', roles: ['STUDENT'] }
      },
      {
        path: 'forum/post/:id',
        name: 'ForumPostDetail',
        component: () => import('@/views/Forum/Detail.vue'),
        meta: { title: '帖子详情' }
      },
      {
        path: 'announcements',
        name: 'AnnouncementsStudent',
        component: () => import('@/views/Announcement/Student.vue'),
        meta: { title: '公告栏', roles: ['STUDENT'] }
      },
      {
        path: 'announcements/:id',
        name: 'AnnouncementDetail',
        component: () => import('@/views/Announcement/Detail.vue'),
        meta: { title: '公告详情' }
      },
      {
        path: 'messages',
        name: 'MessagesList',
        component: () => import('@/views/Message/List.vue'),
        meta: { title: '消息箱', roles: ['STUDENT'] }
      },
      {
        path: 'messages/:id',
        name: 'MessageDetail',
        component: () => import('@/views/Message/Detail.vue'),
        meta: { title: '消息详情' }
      },
      {
        path: 'teacher/index',
        name: 'TeacherIndex',
        component: () => import('@/views/Teacher/Index.vue'),
        meta: { title: '附件下载', roles: ['TEACHER', 'ADMIN'] }
      },
      {
        path: 'teacher/week-task',
        name: 'WeekTask',
        component: () => import('@/views/Teacher/WeekTask/index.vue'),
        meta: { title: '周任务', roles: ['TEACHER', 'ADMIN'] }
      },
      {
        path: 'teacher/question-bank',
        name: 'QuestionBank',
        component: () => import('@/views/Teacher/QuestionBank/index.vue'),
        meta: { title: '题库管理', roles: ['TEACHER', 'ADMIN'] }
      },
      {
        path: 'teacher/exam-bank',
        name: 'ExamBank',
        component: () => import('@/views/Teacher/ExamBank/index.vue'),
        meta: { title: '任务管理', roles: ['TEACHER', 'ADMIN'] }
      },
      {
        path: 'teacher/units/:id/edit',
        name: 'UnitEdit',
        component: () => import('@/views/Teacher/Unit/Edit.vue'),
        meta: { title: '编辑任务', roles: ['TEACHER', 'ADMIN'] }
      },
      {
        path: 'teacher/units/create',
        name: 'CreateUnit',
        component: () => import('@/views/Teacher/Unit/Create.vue'),
        meta: { title: '新建任务包', roles: ['TEACHER', 'ADMIN'] }
      },
      {
        path: 'teacher/pages/create/:materialId',
        name: 'CreatePaperPage',
        component: () => import('@/views/Teacher/Page/Create.vue'),
        meta: { title: '组卷', roles: ['TEACHER', 'ADMIN'] }
      },
      {
        path: 'teacher/units/:id',
        name: 'UnitDetail',
        component: () => import('@/views/Teacher/Unit/Detail.vue'),
        meta: { title: '任务详情', roles: ['TEACHER', 'ADMIN'] }
      },
      {
        path: 'teacher/forum',
        name: 'ForumTeacher',
        component: () => import('@/views/Teacher/Forum/index.vue'),
        meta: { title: '论坛管理', roles: ['TEACHER', 'ADMIN'] }
      },
      {
        path: 'announce/announcements',
        name: 'AnnouncementsTeacher',
        component: () => import('@/views/Announcement/Student.vue'),
        meta: { title: '公告管理', roles: ['TEACHER', 'ADMIN'] }
      },
      {
        path: 'announce/messages',
        name: 'MessagesTeacher',
        component: () => import('@/views/Message/List.vue'),
        meta: { title: '消息箱', roles: ['TEACHER', 'ADMIN'] }
      },
      {
        path: 'query',
        name: 'Query',
        component: () => import('@/views/Query/index.vue'),
        meta: { title: '检索面板', roles: ['TEACHER', 'ADMIN'] }
      },
      {
        path: 'query/attendance',
        name: 'QueryAttendance',
        component: () => import('@/views/Query/Attendance.vue'),
        meta: { title: '考勤管理', roles: ['TEACHER', 'ADMIN'] }
      },
      {
        path: 'query/learning-record',
        name: 'QueryLearningRecord',
        component: () => import('@/views/Query/LearningRecord.vue'),
        meta: { title: '学习记录管理', roles: ['TEACHER', 'ADMIN'] }
      },
      {
        path: 'query/statistics',
        name: 'QueryStatistics',
        component: () => import('@/views/Query/Statistics.vue'),
        meta: { title: '数据统计分析', roles: ['TEACHER', 'ADMIN'] }
      },
      {
        path: 'query/overdue-rules',
        name: 'QueryOverdueRules',
        component: () => import('@/views/Query/OverdueRules.vue'),
        meta: { title: '逾期扣分规则', roles: ['TEACHER', 'ADMIN'] }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '404' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 检查是否需要登录
  if (to.meta.requiresAuth) {
    const userInfo = storage.get<User>('userInfo')
    if (!userInfo) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }

    // 检查角色权限
    if (to.meta.roles) {
      if (!to.meta.roles.includes(userInfo.role)) {
        ElMessage.warning('您没有权限访问此页面')
        next({ name: 'Dashboard' })
        return
      }
    }
  }

  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 在线考试系统`
  }

  // 调试信息
  if (import.meta.env.DEV) {
    console.log('路由跳转:', { from: from.path, to: to.path, name: to.name })
  }

  next()
})

export default router
