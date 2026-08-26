# Scientific Agent Toolkit（中文）

一个面向科研绘图、论文图表、科研示意图和可编辑报告图的 **精选 Agent Skills Registry**。

它不是“把几十个 GitHub 链接堆在一起”的 awesome-list，也不直接复制上游源码。仓库重点解决三个问题：**怎么选、什么时候调用、如何合法且可复现地安装**。

## 核心原则

1. **科学语义优先于审美**：不能为了好看改变数据、统计含义、坐标尺度或模型拓扑。
2. **职责明确**：数据图、方法示意图、模型架构图、PPTX 重建分别路由。
3. **可编辑/可复现优先**：代码、SVG、Draw.io、原生 PPTX 优先于无法追溯的生成式位图。
4. **Registry-first**：本仓库只维护精选元数据、评分、路由和安装器；源码从上游拉取。
5. **许可证硬门槛**：没有明确许可证的候选只能作为 Reference，不能由安装器自动安装。

## 推荐 Core 7

| Skill | 主要职责 | 分数 |
|---|---|---:|
| `scientific-visualization` | 科研真实性、可访问性、publication QA 的总规范层 | 93 |
| `sci-plot` | 从 claim/evidence 出发设计、修改、审查科研数据图 | 95 |
| `paper-figures` | 论文 + 原始数据 → 统计 → 图表/三线表/报告 | 91 |
| `chart-aesthetic-logic` | 已有 Python 图表的视觉逻辑与美化 | 86 |
| `scientific-figure-design` | 从科研主张创建可编辑 Draw.io/SVG/PDF 示意图 | 94 |
| `ml-architecture-diagram` | 从模型代码恢复真实架构后生成论文级架构图 | 96 |
| `sci-diagram-pptx` | 将已有科研框架图忠实重建为原生可编辑 PPTX | 90 |

## 为什么没有继续无限加 Skill

`matplotlib-skill` 很不错，但与 `chart-aesthetic-logic`、`sci-plot` 的职责重叠较多，因此保留为 Reference；`figures4papers` 是非常强的真实论文案例库，但当前未发现足够明确的仓库级许可证，所以不自动安装；`science-plot-formatter` 同样因为许可证门槛只作为参考；PaperBanana 适合探索生成式科研插图，但不作为正式数据图/拓扑关键图的默认链路。

材料科学用户可按需安装 `huitu`，不让所有用户默认背负领域专用依赖。

## 路由

```text
我要做科研图
│
├─ 含义主要由数据、坐标轴、尺度、统计承载？
│  ├─ 从整篇论文和原始数据出图 → paper-figures
│  ├─ 设计/修改/审查科研证据图 → sci-plot
│  ├─ 图已经正确，只需要视觉优化 → chart-aesthetic-logic
│  └─ 投稿前科学与出版质量检查 → scientific-visualization
│
├─ 含义主要由节点、箭头、模块、拓扑承载？
│  ├─ 方法图/系统框架/研究流程 → scientific-figure-design
│  ├─ 必须从真实模型代码恢复结构 → ml-architecture-diagram
│  └─ 已有参考图要变成可编辑 PPTX → sci-diagram-pptx
│
└─ 材料/电化学/光谱/DFT 专用图 → huitu（Extension）
```

## 安装

```bash
python3 scripts/install.py --list
python3 scripts/install.py --agent codex --tier core
python3 scripts/install.py --agent claude --skill sci-plot chart-aesthetic-logic
```

安装器会：

- 从上游 GitHub 拉取；
- 只复制真正的 Skill 子目录；
- 记录最终解析到的 commit SHA；
- 保存上游 URL、许可证与安装时间；
- 尽可能复制上游 LICENSE；
- 对 `license.status != verified` 的条目 fail closed。

详细见：

- [Skill 选择矩阵](docs/selection-guide.md)
- [评分规则](docs/scoring.md)
- [许可证与 attribution](docs/licensing.md)

## 目录

```text
registry/skills.json          # 所有候选的统一元数据
schema/skill.schema.json      # metadata JSON Schema
docs/selection-guide.md       # 路由/选择矩阵
docs/scoring.md               # 100 分评分体系
docs/licensing.md             # 上游许可证与归属机制
scripts/install.py            # 零第三方 Python 依赖安装器
scripts/validate_registry.py  # Registry 校验
```

本仓库自己的代码和元数据使用 MIT；上游 Skill 始终保持其原始许可证，本仓库不会替上游重新授权。
