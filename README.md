# ⭐ 众星云集 (Star-Studded)

> **每一颗星星都有自己的光芒，聚在一起才能照亮夜空。**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2%2B-green)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/License-Apache%202.0-orange)](LICENSE)

**众星云集** 是一个开源的多智能体 AI 图像生成编排框架。它将复杂的图像创作流程拆解为多个专业智能体，每个智能体专注于自己擅长的领域，通过协作完成从意图理解到图像生成的全链路任务。

用户只需说出简单的想法描述，剩下的交给星星们。

让每一个人都可以简单的将心中的想法变为现实生活中的一张张图片。

---

## ✨ 核心亮点

### 🌟 九星协作，各做各的，不打架

| 星星 | 名字 | 专长 | 性格 |
|:---:|:---:|:---|:---|
| ⭐ | **小调** | 调度中心，决定调用哪些专家 | 热情活泼的组织者 |
| 👁️ | **小视** | 视觉分析，看懂图片里的每一个细节 | 敏锐细致的观察家 |
| 🎨 | **小风** | 风格识别，从赛博朋克到浮世绘无所不知 | 文艺有品味的艺术家 |
| 💭 | **小情** | 情绪捕捉，读懂画面背后的情感 | 温柔敏感的心灵捕手 |
| 🔮 | **小融** | 融合大师，把各路专家的意见拧成一股绳 | 智慧统筹的融合大师 |
| 🎯 | **小选** | 模型选择，为每个任务匹配最合适的生成模型 | 果断专业的决策者 |
| ✍️ | **小词** | 提示词工程，把模糊的想法变成专业的摄影指令 | 严谨专业的技术控 |
| 🔍 | **小审** | 安全审查，确保每一张图都合规 | 严肃正义的守护者 |
| 🖼️ | **小画** | 图像生成，把精心设计的提示词变成画面 | 富有创造力的画家 |

### 🧠 不是"你选模型"，而是"智能体懂你"

传统 AI 画图工具：
```
用户：我想画一张赛博朋克风格的猫
系统：请选择模型（Stable Diffusion / Midjourney / DALL-E / Flux...）
用户：？？？
```

众星云集：
```
用户：我想画一张赛博朋克风格的猫
小调：收到！我请来小风和小情帮忙分析 ✨
小风：赛博朋克风格，霓虹灯光，机械义体元素...
小情：酷炫、未来感、略带神秘...
小融：融合完成！主题是「赛博朋克猫」
小选：这个任务交给 Seedream 最合适
小词：设计提示词：85mm镜头，f/1.4光圈，侧逆光，青紫色调...
小审：审查通过 ✅
小画：画好啦！🎨
```

### 🔧 模型无关的意图表示层

众星云集定义了一套与模型无关的 `IntentRepresentation` 协议：

```json
{
  "mode": "style_transfer",
  "subject": {
    "entity": "猫",
    "attributes": ["机械义体", "霓虹眼睛"],
    "pose": "侧脸凝视"
  },
  "style": {
    "genre": "赛博朋克",
    "references": ["银翼杀手", "攻壳机动队"],
    "intensity": 0.8
  },
  "output": {
    "format": "image",
    "aspect_ratio": "1:1",
    "quality": "high"
  }
}
```

新增生成模型只需实现一个 `BaseAdapter`，零侵入核心架构。

### 🎨 六维提示词工程

小词（PromptEngineer）从六个维度设计专业提示词，让 AI 画出"有摄影感"的图：

- **📷 摄影参数**：焦段（35mm/85mm）、光圈（f/1.4/f/2.8）、色温（3200K/5600K）、胶片颗粒
- **💡 光影细节**：方向（侧光/逆光）、质感（硬/软）、布光方案、氛围（体积雾/雨夜）
- **🖼️ 构图法则**：景别（特写/全景）、视角（平视/俯视）、三分法/对称/引导线
- **🎨 色彩科学**：主色调、互补色、HEX 色码、胶片色（Portra 400 / Cinestill 800T）
- **📖 情绪叙事**："一个瞬间的故事"而非单纯形容词
- **✨ 质量约束**：超精细 / 8K / 专业摄影

### 🔄 多轮追问，越聊越懂

输入模糊？星星们会追问，最多 6 轮补充：

```
用户：给我画张图
小调：你想画什么主题呢？比如人物、风景、动物...
用户：我家猫
小调：想要什么风格？赛博朋克、油画、动漫...
用户：赛博朋克
小调：要像照片还是像画？
用户：像画
→ 生成！
```

### 🛡️ 内置安全审查

小审（PromptAuditor）在生成前拦截风险内容：
- 黑名单关键词检测（NSFW / 暴力 / 政治敏感 / Prompt Injection）
- 重复字符检测（同一字符连续 >50 次）
- 特殊字符比例异常检测（>30%）
- 自动清洗替换敏感词

---

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/yourname/star-studded.git
cd star-studded
pip install -r requirements.txt
```

### 配置环境变量

```bash
# LLM API Keys
export DEEPSEEK_API_KEY="sk-..."
export DASHSCOPE_API_KEY="sk-..."      # 阿里云百炼（Qwen-VL）
export ARK_API_KEY="ark-..."           # 豆包（Seedream）

# 数据库（可选，用于模型调度台）
export DB_HOST="localhost"
export DB_PORT="3306"
export DB_USER="root"
export DB_PASSWORD="..."
export DB_NAME="renwei"

# 加密密钥
export RENWEI_SECRET_KEY="your-secret-key-at-least-32-characters"
```

### 启动服务

```bash
python app.py
```

打开浏览器访问 `http://localhost:5000`，和星星们对话吧！

---

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                      用户层                              │
│              自然语言输入 + 图片上传                      │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  ⭐ 小调 · Scheduler                                    │
│  分析意图 → 决定调用哪些专家 → 支持增量/澄清检测          │
└─────────────────────────────────────────────────────────┘
                           ↓ 并行分发
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ 👁️ 小视      │  │ 🎨 小风      │  │ 💭 小情      │
│ VisionExpert │  │ StyleExpert  │  │ MoodExpert   │
│ 图像内容分析  │  │ 风格流派识别  │  │ 情绪氛围分析  │
└─────────────┘  └─────────────┘  └─────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  🔮 小融 · FusionAgent                                  │
│  整合专家输出 → 解决冲突 → 输出 IntentRepresentation     │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  🎯 小选 · SelectorAgent                                │
│  动态评分选择最优生成模型（能力/速度/质量/可用性）        │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  ✍️ 小词 · PromptEngineer                               │
│  六维提示词设计 → 模型适配（Seedream/Flux/Midjourney/SD）│
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  🔍 小审 · PromptAuditor                                │
│  安全审查 → 风险评分 → 清洗/拦截                         │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  🖼️ 小画 · GeneratorAgent                               │
│  调用具体模型生成图像/视频                               │
└─────────────────────────────────────────────────────────┘
```

### 技术栈

- **智能体编排**：LangGraph + LangChain
- **LLM 客户端**：OpenAI 兼容 SDK（DeepSeek / Qwen / 豆包）
- **数据库**：MySQL + SQLAlchemy（模型注册表、调用日志、会话记忆）
- **后端**：Flask / FastAPI + SSE 流式输出
- **前端**：纯 HTML/CSS/JS，响应式设计

---

## 📁 项目结构

```
star-studded/
├── src/
│   ├── config/
│   │   ├── settings.py          # 环境变量配置
│   │   └── prompt_styles.yaml   # 7种风格映射表
│   ├── database/
│   │   ├── connection.py        # MySQL 连接池
│   │   └── models.py            # ORM 模型
│   ├── models/
│   │   └── intent.py            # IntentRepresentation 数据类
│   ├── agents/
│   │   ├── scheduler.py         # ⭐ 小调 · 调度
│   │   ├── experts/
│   │   │   ├── vision_expert.py    # 👁️ 小视 · 视觉
│   │   │   ├── style_expert.py     # 🎨 小风 · 风格
│   │   │   ├── mood_expert.py      # 💭 小情 · 情绪
│   │   │   └── prompt_engineer.py  # ✍️ 小词 · 提示词
│   │   ├── fusion.py            # 🔮 小融 · 融合
│   │   ├── selector.py          # 🎯 小选 · 选择
│   │   └── generator.py         # 🖼️ 小画 · 生成
│   ├── services/
│   │   ├── llm_client.py        # 统一 LLM 客户端
│   │   ├── model_manager.py     # 模型 CRUD + 加密
│   │   ├── model_validator.py   # API 验证
│   │   └── prompt_auditor.py    # 🔍 小审 · 审查
│   ├── graph/
│   │   └── workflow.py          # LangGraph 状态图
│   ├── memory/
│   │   └── session_memory.py    # 会话记忆 + 增量更新
│   └── api/
│       └── model_console.py     # 模型调度台接口
├── static/
│   └── index.html               # 对话式前端
├── sql/
│   └── create_database.sql      # 建表 SQL
├── app.py                       # Flask 服务入口
└── test_graph.py                # 测试脚本
```

---

## 🎯 支持的生成模型

|       模型        | 提供商 | 状态 | 特点 |
|:---------------:|:---:|:---:|:---|
|  Seedream 5.0   | 豆包（火山） | ✅ 已验证 | 中文提示词友好，速度快 |
| DeepSeek-v4-pro | DeepSeek | ✅ 已验证 | 调度/融合/分析 |
|  Qwen3.6-plus   | 阿里云百炼 | ✅ 已验证 | 视觉分析、OCR |
|      通义万相       | 阿里云 | ⏸️ 预留 | 图像生成、风格迁移 |
|       可灵        | 快手 | ⏸️ 预留 | 视频生成、动作控制 |
|      Flux       | Black Forest Labs | ⏸️ 预留 | 开源，照片级真实感 |
|       ...       | ... | ... | ... |

新增模型只需：
1. 在模型调度台注册 API Key
2. 实现 `BaseAdapter` 接口
3. 系统自动识别并纳入评分选择

我希望可以将所有优秀的模型都加入进来，让众星真正云集。

---

## 🔌 扩展开发

### 自定义生成适配器

```python
from src.tools.generators.base import BaseAdapter

class MyModelAdapter(BaseAdapter):
    def translate(self, intent: IntentRepresentation) -> str:
        # 将 IntentRepresentation 转换为目标模型的提示词语法
        return f"{intent.subject.entity}, {intent.style.genre}, 8k, ultra detailed"

    def get_params(self, intent: IntentRepresentation) -> dict:
        # 返回模型特定参数
        return {"size": "1024x1024", "seed": 42}

    def generate(self, prompt: str, **kwargs) -> str:
        # 调用模型 API，返回图片 URL
        response = self.client.images.generate(...)
        return response.data[0].url
```

### 自定义专家

```python
class MyExpert:
    def analyze(self, user_input: str, context: dict) -> dict:
        # 你的分析逻辑
        return {
            "expert": "my_expert",
            "output": {"key": "value"}
        }
```

然后在 `scheduler.py` 的 prompt 里告诉小调："新增了一个 my_expert 专家，负责 xxx"。

---

## 🤝 参与贡献

我欢迎各种形式的贡献：

- 🐛 提交 Bug 报告
- 💡 提出新功能建议
- 🔧 提交 Pull Request
- 📖 完善文档
- 🌟 给项目点 Star

### 开发规范

1. 每个专家独立开发，互不干扰
2. 新增专家需更新 `IntentRepresentation` 协议文档
3. 所有 LLM 调用需支持 JSON 格式 + 重试兜底
4. 错误处理：打印日志 + 返回前端友好提示

---

## 📜 开源协议

Apache License 2.0

---

## 🙏 致谢

- [LangGraph](https://langchain-ai.github.io/langgraph/) - 智能体编排框架
- [DeepSeek](https://deepseek.com/) - 调度/融合/分析模型
- [阿里云百炼](https://bailian.aliyun.com/) - Qwen-VL 视觉模型
- [豆包](https://www.volcengine.com/product/doubao) - Seedream 图像生成

---

> **"变的是工具，不变的是想象本身。"**
>
> 众星云集，让每一颗星星都发光。

---

## 📬 联系我

**项目维护者**：王柄屹

- 📧 **邮箱**：3446457920@qq.com（欢迎技术交流、合作洽谈）
- 🎓 **背景**：长春师范大学人工智能专业大三，专业前10%
- 💼 **状态**：目前正在寻找实习机会，方向为大模型应用/AI应用开发或Python后端开发
- ⏰ **可实习时间**：可全职实习6个月以上
- 💻 **技术栈**：Python后端、MySQL、Git、LangChain、RAG、AI Agent、本地LLM部署
- 🏆 **经历**：2年实验室负责人经验

> 如果你对大模型应用开发、多智能体系统感兴趣，或者有任何合作想法，欢迎随时邮件联系！

---

## 📜 开源协议

本项目采用 [Apache License 2.0](LICENSE) 开源协议。

```
Copyright 2026 王柄屹

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
