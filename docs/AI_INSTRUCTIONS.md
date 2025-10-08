# 🤖 AI Instructions — AI-Driven Clinical Trial Tool  
*(Generated on 2025-10-07 14:13)*  

---

## 🧭 1. 项目简介 / Project Overview
本文件定义了 ChatGPT 在本项目中协作开发的所有规则、风格与结构约定。  
This document defines how ChatGPT should collaborate, ensuring consistent outputs and structure.

**项目名称 / Project Name**: AI-Driven Clinical Trial Tool  
**核心定位 / Core Purpose**: 多模块临床数据工具（ALS Reader, QC Console, Dictionary Viewer 等）  
**架构 / Stack**:  
- Frontend: Vue 3 + Vite + Pinia  
- Backend: Node.js (Express)  
- AI Services: Python + FastAPI  
- Data: PostgreSQL + MinIO/S3  
- Optional: Redis/RabbitMQ + Celery/RQ  

---

## ⚙️ 2. 输出原则 / Output Principles

| 原则 | Principle | 描述 |
|------|------------|------|
| 一致性 | Consistency | 输出需遵守项目架构与目录规范 |
| 可解释性 | Explainability | 初学者友好，首次出现概念需解释 |
| 渐进式 | Incremental | 先给出可运行版本，再讲解扩展 |
| 结构化 | Structured | 每次输出包含路径、代码、说明 |
| 不破坏现有结构 | Stable Integration | 不创建新框架或改变核心栈 |
| 视觉一致 | UI Consistency | 遵循 Tech-Soft Pink 设计规范 |
| 安全与可维护 | Safe & Maintainable | 禁止敏感数据、保持可读性 |

---

## 🧩 3. 输出格式 / Output Format

AI 输出示例格式如下：

````markdown
### 🧱 文件说明 / File Description
简要说明此模块功能与依赖。

### 📂 文件路径 / File Path
**`src/views/Home.vue`**

```vue
<template>...</template>
<script setup>...</script>
<style scoped>...</style>
```

### 💬 使用说明 / Explanation
- 说明关键逻辑与调用路径  
- 若使用外部接口，注明 URL 与返回结构  
````

---

## 🗂️ 4. 项目结构 / Project Structure

```
root/
├── src/                   # 前端（Vue 3 + Vite）
│   ├── apps/registry.ts   # 工具清单（唯一真相）
│   ├── views/             # 页面组件
│   ├── router/            # 路由模块化
│   ├── stores/            # Pinia 状态管理
│   ├── services/          # 封装 API 请求
│   └── components/        # 可复用组件
│
├── server/                # Node.js API 网关
│   ├── index.ts
│   ├── routes/            # 按功能模块拆分路由
│   ├── services/          # 调用 Python / DB / S3
│   └── utils/             # 通用函数
│
├── ai_service/            # Python 微服务层
│   ├── main.py
│   ├── core/              # 解析与逻辑
│   └── workers/           # 异步任务
│
└── docs/                  # 项目文档
    ├── PROJECT_GUIDE.md
    ├── styleguide.md
    ├── api_reference.md
    ├── architecture.mmd
    └── AI_INSTRUCTIONS.md
```

---

## 💡 5. 风格与语气 / Tone & Style

| 项目 | 要求 |
|------|------|
| 语气 | 教练式、温和、逻辑清晰 |
| 结构 | 分层说明（说明 → 示例 → 扩展） |
| 注释 | 每个功能块前写注释，如 `// 上传解析逻辑` |
| 视觉 | 使用粉科技风（Tech-Soft Pink） |
| Mermaid 图 | 每图独立代码块，Notion/GitHub 兼容 |

---

## 🧮 6. 模块指令 / AI Command Patterns

| 指令 | 功能 |
|------|------|
| `AI_TASK: create module` | 创建新功能模块（含 Home.vue 注册） |
| `AI_TASK: refactor async` | 将同步逻辑改为异步任务 |
| `AI_TASK: add ai service` | 新增 FastAPI 微服务 |
| `AI_TASK: doc update` | 更新 `/docs/api_reference.md` |
| `AI_TASK: ui unify` | 校对 UI 风格与组件样式 |

---

## 🧱 7. 输出一致性模板 / Stable Output Template

每次输出应遵循以下模板：

````markdown
### 📂 File Path
`src/views/AlsReaderView.vue`

### 🧠 Purpose
Explain what this module does and how it connects.

### 💻 Code
```ts
// Example code here
```

### 💬 Notes
Explain new concepts (if any), and how to test the result.
````

---

## 🎨 8. UI 设计语言 / UI Language

| 元素 | 色号 | 用途 |
|------|------|------|
| 主色 | `#F7C8E0` | 按钮、卡片主背景 |
| 强调色 | `#FF77C9` | 悬停或激活 |
| 基调灰 | `#E4E4E7` | 边框和中性背景 |
| 高光蓝 | `#D7E3F4` | 阴影与渐变亮点 |

**字体建议**：Inter / Source Sans Pro  
**背景渐变**：`linear-gradient(145deg, #fdfbfb 0%, #ebedee 100%)`

---

## 🧰 9. 文件命名与代码规范 / Naming Rules

| 类型 | 命名方式 | 示例 |
|------|-----------|------|
| Vue 文件 | PascalCase | `HomeView.vue` |
| JS/TS 文件 | camelCase | `parseMatrix.ts` |
| Python 文件 | snake_case | `matrix_worker.py` |
| 样式文件 | kebab-case | `tech-soft-theme.css` |

**注释规范**
```ts
// 🧩 Function: parseMatrix
// Purpose: Extract folder/form relationships from uploaded Excel
// Input: file (Buffer)
// Output: JSON matrix mapping
```

---

## 🔁 10. 开发阶段 / Dev Phases

| 阶段 | 目标 | AI 协作任务 |
|------|------|--------------|
| Phase 1 | 实现 Home 与 ALS Reader MVP | 生成基本模块与接口 |
| Phase 2 | 引入异步任务机制 | 改造 Node + FastAPI |
| Phase 3 | 扩展 AI 模块 | 新增 QC / NLP 分析 |
| Phase 4 | 统一 UI 风格 | 组件美化与风格优化 |
| Phase 5 | 文档自动更新 | 同步 API 与架构文件 |

---

## 🧭 11. System Prompt 模板（用于新对话）

当你开启新的 ChatGPT 对话时，请复制以下提示词放在最前：

> ```
> You are the AI collaborator for the project "AI-Driven Clinical Trial Tool".
> Always follow the structure, principles, and design guidelines in /docs/AI_INSTRUCTIONS.md.
> Explain new concepts in beginner-friendly language.
> Keep consistent architecture: Vue 3 + Node.js + FastAPI + PostgreSQL + S3.
> Use the Tech-Soft Pink UI theme.
> Output in structured sections (file path, code, explanation).
> ```

---

## ✅ 附录：AI 输出必须包含
1. 文件路径  
2. 完整代码块  
3. 功能说明  
4. 如涉及 UI → 遵循粉科技风  
5. 新概念 → 附带简短解释  

---

*End of Instructions — Ready for Continuous AI Collaboration.*
