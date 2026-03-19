# 健康管理系统 - 基于Kimi AI
## 项目概述

本项目是一个基于 **Kimi AI 技术** 的全流程健康管理平台，旨在为健康检测机构提供智能化的健康数据分析、个性化健康管理方案、体检流程优化等服务。

### 核心功能

| 功能模块 | 描述 | 技术特点 |
|---------|------|---------|
| **AI数智健管师** | 健康风险评估、个性化指导、疾病预防管理 | 自然语言对话、流式响应、联网搜索、对话历史管理 |
| **健康管理** | 记录和分析身体指标（心率、血氧、睡眠等） | 数据可视化、趋势分析、健康预警 |
| **体检流程优化** | 智能预约、体检结果分析 | 在线预约、报告自动解析、AI解读 |
| **智能报告解读** | 体检报告智能解读与可视化展示 | 指标分析、异常预警、个性化建议 |
| **健康文章管理** | 健康知识文章发布与浏览 | 富文本编辑、分类管理、轮播图 |

## 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                      前端层 (Vue.js 3)                   │
│                   端口: 19000 (开发) / 80 (生产)          │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│              API网关 / 负载均衡 (Nginx)                  │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼───────┐  ┌───────▼───────┐  ┌───────▼───────┐
│   后端服务     │  │   AI服务      │  │   数据库      │
│ (Spring Boot) │  │  (FastAPI)    │  │  MySQL/Redis  │
│   端口: 19001 │  │   端口: 19002 │  │ 3300/6379     │
└───────────────┘  └───────────────┘  └───────────────┘
                            │
                    ┌───────▼───────┐
                    │   Kimi API    │
                    │ Moonshot API  │
                    └───────────────┘
```

### 技术栈

| 层级 | 技术选型 | 版本 |
|------|---------|------|
| 前端 | Vue.js 3 + Element Plus + ECharts + GSAP | ^3.4.15 |
| 后端 | Spring Boot + MyBatis Plus + JWT | 3.2.0 |
| AI服务 | Python + FastAPI + OpenAI SDK | 3.11+ |
| 数据库 | MySQL 8.0 + Redis 7 | 8.0 / 7.x |
| 构建工具 | Maven (后端) + Vite (前端) | - |

### 端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端 (Vite Dev) | 19000 | 开发环境前端页面 |
| 前端 (Nginx) | 80 | 生产环境前端页面 |
| 后端 (Spring Boot) | 19001 | Java后端API服务 |
| AI服务 (FastAPI) | 19002 | Python AI服务 |
| MySQL | 3300 | 数据库服务 (映射自3306) |
| Redis | 6379 | 缓存服务 |

## 项目结构

```
health-management-system/
├── backend/                    # 后端服务 (Spring Boot 3.2)
│   ├── src/main/java/com/health/
│   │   ├── annotation/         # 自定义注解
│   │   │   └── RequireAdmin.java      # 管理员权限注解
│   │   ├── config/             # 配置类
│   │   │   ├── MyBatisPlusConfig.java # MyBatis Plus配置
│   │   │   ├── SecurityConfig.java    # Spring Security配置
│   │   │   └── WebConfig.java         # Web配置
│   │   ├── controller/         # 控制器层 - REST API接口
│   │   │   ├── AdminController.java      # 管理员接口
│   │   │   ├── ArticleController.java    # 健康文章接口
│   │   │   ├── AuthController.java       # 认证接口
│   │   │   ├── HealthController.java     # 健康管理接口
│   │   │   ├── HospitalController.java   # 医院管理接口
│   │   │   ├── PhysicalExamController.java # 体检管理接口
│   │   │   ├── ReportController.java     # 报告管理接口
│   │   │   └── UserController.java       # 用户管理接口
│   │   ├── dto/                # 数据传输对象 - API入参
│   │   │   ├── BindEmailDTO.java
│   │   │   ├── BindPhoneDTO.java
│   │   │   ├── ChangePasswordDTO.java
│   │   │   ├── DeleteAccountDTO.java
│   │   │   ├── HealthRecordDTO.java
│   │   │   ├── LoginDTO.java
│   │   │   ├── PhysicalExamAppointmentDTO.java
│   │   │   ├── RegisterDTO.java
│   │   │   └── UpdateUserDTO.java
│   │   ├── entity/             # 实体类 - 数据库映射
│   │   │   ├── Carousel.java
│   │   │   ├── ExamIndicator.java
│   │   │   ├── HealthArticle.java
│   │   │   ├── HealthRecord.java
│   │   │   ├── Hospital.java
│   │   │   ├── PhysicalExamAppointment.java
│   │   │   ├── PhysicalExamReport.java
│   │   │   └── User.java
│   │   ├── exception/          # 全局异常处理
│   │   │   └── GlobalExceptionHandler.java
│   │   ├── interceptor/        # 拦截器
│   │   │   └── AdminInterceptor.java    # 管理员权限拦截
│   │   ├── mapper/             # 数据访问层 - MyBatis接口
│   │   │   ├── ExamIndicatorMapper.java
│   │   │   ├── HealthRecordMapper.java
│   │   │   ├── HospitalMapper.java
│   │   │   ├── PhysicalExamAppointmentMapper.java
│   │   │   ├── PhysicalExamReportMapper.java
│   │   │   └── UserMapper.java
│   │   ├── repository/         # Spring Data JPA仓库
│   │   │   ├── CarouselRepository.java
│   │   │   └── HealthArticleRepository.java
│   │   ├── security/           # 安全相关
│   │   │   └── JwtAuthenticationFilter.java # JWT认证过滤器
│   │   ├── service/            # 服务层 - 业务逻辑
│   │   │   ├── impl/           # 服务实现类
│   │   │   │   └── CarouselServiceImpl.java
│   │   │   ├── CarouselService.java
│   │   │   ├── HealthArticleService.java
│   │   │   ├── HealthService.java
│   │   │   ├── HospitalService.java
│   │   │   ├── PhysicalExamService.java
│   │   │   ├── ReportService.java
│   │   │   └── UserService.java
│   │   ├── utils/              # 工具类
│   │   │   ├── FileUtil.java
│   │   │   └── JwtUtil.java
│   │   ├── vo/                 # 视图对象 - API出参
│   │   │   ├── ResultVO.java
│   │   │   └── UserVO.java
│   │   └── HealthManagementApplication.java # 应用入口
│   ├── src/main/resources/
│   │   └── application.yml     # 主配置文件
│   ├── uploads/                # 上传文件目录
│   │   ├── avatar/             # 头像上传目录
│   │   └── carousel/           # 轮播图上传目录
│   └── pom.xml                 # Maven依赖配置
│
├── frontend/                   # 前端应用 (Vue.js 3)
│   ├── src/
│   │   ├── api/                # API接口封装
│   │   │   ├── admin.js        # 管理员接口
│   │   │   ├── aiDoctor.js     # AI医生接口
│   │   │   ├── amap.js         # 高德地图接口
│   │   │   ├── article.js      # 健康文章接口
│   │   │   ├── health.js       # 健康管理接口
│   │   │   ├── hospital.js     # 医院接口
│   │   │   ├── physicalExam.js # 体检管理接口
│   │   │   ├── report.js       # 报告管理接口
│   │   │   └── user.js         # 用户相关接口
│   │   ├── assets/             # 静态资源
│   │   │   └── main.css
│   │   ├── components/         # 公共组件
│   │   │   ├── AppFooter.vue
│   │   │   ├── AuroraBackground.vue
│   │   │   ├── BackToTop.vue
│   │   │   ├── EvilEye.vue     # 动态眼睛组件
│   │   │   ├── FeatureCard.vue
│   │   │   ├── ImageCropper.vue
│   │   │   ├── PrismBackground.vue
│   │   │   ├── SectionTitle.vue
│   │   │   ├── SolutionCard.vue
│   │   │   └── StatCard.vue
│   │   ├── composables/        # 组合式函数
│   │   │   ├── useAuth.js      # 认证逻辑
│   │   │   └── useAuth.spec.js # 认证测试
│   │   ├── config/             # 配置文件
│   │   │   └── amap.config.js  # 高德地图配置
│   │   ├── constants/          # 常量定义
│   │   │   └── avatar.js       # 头像常量
│   │   ├── router/             # 路由配置
│   │   │   └── index.js
│   │   ├── stores/             # Pinia状态管理
│   │   │   ├── user.js         # 用户状态
│   │   │   └── user.spec.js    # 状态测试
│   │   ├── styles/             # 样式文件
│   │   │   └── animations.scss
│   │   ├── utils/              # 工具函数
│   │   │   ├── animations.js   # 动画工具
│   │   │   ├── auth.js         # 认证工具
│   │   │   ├── healthAnalysis.js # 健康分析工具
│   │   │   ├── image.js        # 图片处理
│   │   │   └── request.js      # HTTP请求封装
│   │   ├── views/              # 页面视图
│   │   │   ├── about/          # 关于我们
│   │   │   │   └── index.vue
│   │   │   ├── admin/          # 管理后台
│   │   │   │   ├── AdminArticleEdit.vue   # 文章编辑
│   │   │   │   ├── AdminArticles.vue      # 文章管理
│   │   │   │   ├── AdminCarousel.vue      # 轮播图管理
│   │   │   │   └── AdminLayout.vue        # 管理布局
│   │   │   ├── ai-doctor/      # AI健管师
│   │   │   │   └── index.vue
│   │   │   ├── article/        # 健康文章
│   │   │   │   ├── ArticleDetail.vue
│   │   │   │   └── ArticleList.vue
│   │   │   ├── dashboard/      # 数据概览首页
│   │   │   │   ├── index.spec.js
│   │   │   │   └── index.vue
│   │   │   ├── error/          # 错误页面
│   │   │   │   └── 404.vue
│   │   │   ├── health/         # 健康管理
│   │   │   │   └── index.vue
│   │   │   ├── layout/         # 布局组件
│   │   │   │   └── index.vue
│   │   │   ├── login/          # 登录页面
│   │   │   │   ├── index.spec.js
│   │   │   │   └── index.vue
│   │   │   ├── physical-exam/  # 体检管理
│   │   │   │   └── index.vue
│   │   │   ├── profile/        # 个人中心
│   │   │   │   └── index.vue
│   │   │   ├── report/         # 报告查看
│   │   │   │   └── index.vue
│   │   │   └── dashboard/      # 数据概览
│   │   │       └── index.vue
│   │   ├── App.vue             # 根组件
│   │   └── main.js             # 应用入口
│   ├── public/                 # 公共资源
│   ├── dist/                   # 构建输出
│   ├── vite.config.js          # Vite配置
│   ├── vitest.config.js        # Vitest测试配置
│   └── package.json            # npm依赖
│
├── ai-service/                 # AI服务 (Python FastAPI)
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes.py       # API路由定义
│   │   │   └── voice_routes.py # 语音相关路由
│   │   ├── core/
│   │   │   ├── auth.py         # JWT认证
│   │   │   ├── config.py       # 应用配置
│   │   │   └── __init__.py
│   │   ├── db/
│   │   │   ├── database.py     # 数据库连接
│   │   │   ├── models.py       # 数据模型
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   ├── chat_history_service.py  # 对话历史服务
│   │   │   ├── kimi_service.py          # Kimi AI服务封装
│   │   │   └── __init__.py
│   │   ├── utils/
│   │   │   ├── content_validator.py     # 内容验证器
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── logs/                   # 日志目录
│   │   └── ai_service.log
│   ├── main.py                 # 服务入口
│   ├── requirements.txt        # Python依赖
│   ├── .env                    # 环境变量配置
│   └── .env.example            # 环境变量示例
│
├── database/
│   ├── health_record.sql       # 健康记录相关表
│   └── init.sql                # 数据库初始化脚本 (15+张表)
│
├── tools/                      # 开发工具
│   └── moonpalace/             # MoonPalace本地AI测试工具
│       ├── README.md
│       ├── application-dev.yml
│       ├── start-moonpalace.ps1
│       └── test-ai-with-moonpalace.ps1
│
├── start-all.ps1               # 一键启动脚本 (PowerShell)
├── start-project.bat           # Windows启动脚本
├── startup.config.json         # 启动配置
├── test-ai-moonpalace.bat      # AI测试脚本
└── README.md                   # 项目说明文档
```

## 快速开始

### 环境要求

| 环境 | 版本要求 | 说明 |
|------|---------|------|
| Java | 21+ | 后端运行环境 |
| Node.js | 18+ | 前端构建环境 |
| Python | 3.11+ | AI服务运行环境 |
| MySQL | 8.0+ | 数据存储 |
| Redis | 7+ | 缓存服务 |

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd health-management-system
```

#### 2. 配置环境变量

```bash
# AI服务配置
cp ai-service/.env.example ai-service/.env
# 编辑 .env 文件，填写 Kimi API Key
```

`.env` 文件示例：
```env
# Kimi API配置
MOONSHOT_API_KEY=your-api-key-here
MOONSHOT_BASE_URL=https://api.moonshot.cn/v1
MOONSHOT_MODEL=moonshot-v1-8k

# 数据库配置
DATABASE_URL=mysql+pymysql://root:password@localhost:3300/health_management

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
```

#### 3. 初始化数据库

```bash
# 登录MySQL
mysql -u root -p

# 执行初始化脚本
source database/init.sql
```

#### 4. 启动后端服务

```bash
cd backend

# 使用Maven启动
mvn spring-boot:run
```

#### 5. 启动AI服务

```bash
cd ai-service

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

#### 6. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

#### 7. 访问应用

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端页面 | http://localhost:19000 | Vue.js开发服务器 |
| 后端API | http://localhost:19001/api | Spring Boot服务 |
| AI服务 | http://localhost:19002 | FastAPI服务 |
| AI接口文档 | http://localhost:19002/docs | Swagger文档 |

### 一键启动（Windows）

```powershell
# 使用PowerShell启动所有服务
.\start-all.ps1
```

## 数据库设计

### 表结构概览

| 表名 | 说明 | 核心字段 |
|------|------|---------|
| sys_user | 用户表 | id, username, password, email, phone, status |
| sys_role | 角色表 | id, role_name, role_code |
| sys_user_role | 用户角色关联表 | user_id, role_id |
| ai_chat_history | AI对话历史表 | user_id, session_id, message_role, message_content, tokens_used |
| health_record | 健康记录表 | user_id, metric_type, metric_value, record_date |
| physical_exam_appointment | 体检预约表 | user_id, appointment_date, exam_package, status |
| physical_exam_report | 体检报告表 | user_id, exam_date, overall_result, ai_analysis |
| exam_indicator | 体检指标表 | report_id, indicator_name, indicator_value, status |
| health_articles | 健康文章表 | id, title, content, category, author, status |
| carousel | 轮播图表 | id, title, image_url, link_url, sort_order, status |

### ER图

```
┌─────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  sys_user   │       │ health_record   │       │ ai_chat_history │
│  (用户表)    │◄──────┤ (健康记录)       │       │ (AI对话历史)     │
└──────┬──────┘       └─────────────────┘       └─────────────────┘
       │
       │       ┌─────────────────┐       ┌─────────────────┐
       ├──────►│ physical_exam_  │◄──────┤ exam_indicator  │
       │       │ appointment     │       │ (体检指标)       │
       │       │ (体检预约)       │       └─────────────────┘
       │       └────────┬────────┘
       │                │
       │       ┌────────▼────────┐
       │       │ physical_exam_  │
       └──────►│ report          │
               │ (体检报告)       │
               └─────────────────┘
```

## API 接口文档

### 认证接口

| 接口 | 方法 | 描述 | 请求体 | 响应 |
|------|------|------|--------|------|
| `/api/auth/login` | POST | 用户登录 | `{username, password}` | `{token, user}` |
| `/api/auth/register` | POST | 用户注册 | `{username, password, confirmPassword, email}` | `{user}` |
| `/api/auth/logout` | POST | 用户登出 | - | `{message}` |

### 用户接口

| 接口 | 方法 | 描述 | 认证 |
|------|------|------|------|
| `/api/user/info` | GET | 获取当前用户信息 | 需要 |
| `/api/user/info` | PUT | 更新用户信息 | 需要 |
| `/api/user/password` | PUT | 修改密码 | 需要 |
| `/api/user/avatar` | POST | 上传头像 | 需要 |
| `/api/user/bind-email` | POST | 绑定邮箱 | 需要 |
| `/api/user/bind-phone` | POST | 绑定手机 | 需要 |

### 健康管理接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/health/records` | GET | 获取健康记录列表 |
| `/api/health/records` | POST | 添加健康记录 |
| `/api/health/records/{id}` | PUT | 更新健康记录 |
| `/api/health/records/{id}` | DELETE | 删除健康记录 |
| `/api/health/statistics` | GET | 获取健康统计 |
| `/api/health/latest` | GET | 获取最新指标数据 |

### 文章管理接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/articles` | GET | 获取文章列表 |
| `/api/articles/{id}` | GET | 获取文章详情 |
| `/api/articles` | POST | 创建文章 (管理员) |
| `/api/articles/{id}` | PUT | 更新文章 (管理员) |
| `/api/articles/{id}` | DELETE | 删除文章 (管理员) |

### AI服务接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/v1/chat` | POST | 流式AI对话 |
| `/api/v1/model/info` | GET | 获取模型信息 |
| `/api/v1/history` | GET | 获取对话历史 |
| `/api/v1/history/{session_id}` | GET | 获取指定会话历史 |
| `/api/v1/history/delete` | POST | 批量删除对话记录 |
| `/api/v1/history/clear-all` | POST | 清空所有对话历史 |
| `/api/v1/sessions` | GET | 获取用户会话列表 |
| `/api/v1/analyze/health` | POST | 健康数据分析 |
| `/api/v1/report/generate` | POST | 生成体检报告解读 |
更多接口详见 [API文档](http://localhost:19002/docs)

## 核心功能说明

### 1. AI数智健管师

- **智能对话**：基于Kimi大模型的自然语言对话，支持流式响应
- **联网搜索**：可选开启联网搜索功能，获取最新健康资讯
- **内容验证**：自动验证用户输入，确保对话内容健康相关
- **对话历史**：自动保存对话历史，支持会话管理和历史查看
- **Token管理**：智能管理对话上下文，避免超出模型限制

### 2. 健康管理

- **多指标记录**：支持静息心率、血氧、睡眠效率、步数等多种指标
- **数据可视化**：使用ECharts展示健康数据趋势图表
- **异常预警**：自动识别异常指标并生成预警
- **历史对比**：支持历史数据对比分析

### 3. 体检流程优化

- **在线预约**：支持体检套餐选择和时间段预约
- **报告上传**：支持PDF、图片格式的体检报告上传
- **AI解读**：自动解析体检报告，生成解读和建议
- **指标跟踪**：历史指标对比和趋势分析

### 4. 健康文章管理

- **文章发布**：支持富文本编辑的文章发布
- **分类管理**：文章分类和标签管理
- **轮播图管理**：首页轮播图配置
- **浏览统计**：文章浏览量统计

## 开发规范

### 代码规范

- **Java**：遵循阿里巴巴Java开发手册
- **Python**：遵循PEP 8规范
- **JavaScript/Vue**：使用ESLint + Prettier

### Git提交规范

```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 重构
perf: 性能优化
test: 测试相关
chore: 构建/工具相关
```

### 分支管理

- `main`：主分支，稳定版本
- `develop`：开发分支
- `feature/*`：功能分支
- `hotfix/*`：紧急修复分支

## 部署指南

### 生产环境部署

#### 1. 后端部署

```bash
cd backend
mvn clean package -DskipTests
java -jar target/health-management-backend-1.0.0.jar
```

#### 2. AI服务部署

```bash
cd ai-service
pip install -r requirements.txt
# 使用gunicorn部署
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app -b 0.0.0.0:19002
```

#### 3. 前端部署

```bash
cd frontend
npm run build
# 将dist目录部署到Nginx
```

#### 4. Nginx配置

```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        root /path/to/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:19001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /ai-service {
        proxy_pass http://localhost:19002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 常见问题

### Q: 启动后端时报数据库连接错误？

A: 请检查：
1. MySQL服务是否已启动
2. application.yml中的数据库配置是否正确
3. 数据库health_management是否已创建

### Q: AI服务无法连接到Kimi API？

A: 请检查：
1. .env文件中的MOONSHOT_API_KEY是否正确
2. 网络连接是否正常
3. API密钥是否有足够的额度

### Q: 前端登录后提示"登录已过期"？

A: 请检查：
1. 后端服务是否正常运行
2. JWT密钥配置是否一致
3. 浏览器LocalStorage中token是否存在

## 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- 项目主页：[GitHub Repository](https://github.com/yourusername/health-management-system)
- 问题反馈：[Issues](https://github.com/yourusername/health-management-system/issues)
- 邮箱：support@health-management.com

## 致谢

- [Kimi AI](https://www.moonshot.cn/) - 提供强大的AI能力支持
- [Element Plus](https://element-plus.org/) - 优秀的前端组件库
- [Spring Boot](https://spring.io/projects/spring-boot) - 后端框架
- [FastAPI](https://fastapi.tiangolo.com/) - Python高性能Web框架
