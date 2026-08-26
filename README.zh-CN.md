# Scientific Agent Toolkit（中文）

一个面向科研绘图、论文图表、科研示意图和可编辑报告图的 **精选 Agent Skills Registry**。

它不是“把几十个 GitHub 链接堆在一起”的 awesome-list，也不直接复制上游源码。仓库重点解决三个问题：**怎么选、什么时候调用、如何合法且可复现地安装与评测**。

[Skill 选择矩阵](docs/selection-guide.md) · [Benchmark](evals/README.md) · [评分规则](docs/scoring.md) · [自动化](docs/automation.md) · [许可证](docs/licensing.md)

## v0.2：开始给“精选”提供证据

v0.1 建立了 Registry、路由、安装器、许可证门槛和人工 curator score。v0.2 新增两个彼此独立的证据层：

- **Benchmark / Eval Framework**：统一 run manifest、交付物契约检查、精确 upstream commit provenance、40 分自动检查 + 60 分人工科研 rubric。
- **Upstream Health + Lockfile**：定时检查仓库/ref/skill 路径/license，并用 `upstream-lock.json` 记录实际解析到的 commit，而不会偷偷修改人工策展判断。

Curator score 与 benchmark score 严格分开：前者回答“这个项目是否值得进入工具箱”，后者回答“某个 Skill 在某个固定任务上的一次运行表现如何”。

## 核心原则

1. **科学语义优先于审美**：不能为了好看改变数据、统计含义、坐标尺度或模型拓扑。
2. **职责明确**：数据图、方法示意图、模型架构图、PPTX 重建分别路由。
3. **可编辑/可复现优先**：代码、SVG、Draw.io、原生 PPTX 优先于无法追溯的生成式位图。
4. **Registry-first**：本仓库只维护精选元数据、评分、路由和安装器；源码从上游拉取。
5. **许可证硬门槛**：没有明确许可证的候选只能作为 Reference，不能由安装器自动安装。

## 推荐 Core 7

| Skill | 主要职责 | Curator Score |
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

## Benchmark / Eval

Benchmark 不绑定某个模型或 Agent，而是评价 Skill 最终交付的科研产物。

```bash
# 校验 benchmark 定义
python3 scripts/eval_runner.py --validate

# 为一次测试生成统一 manifest
python3 scripts/eval_runner.py \
  --init-run claim-to-data-figure sci-plot \
  --output eval-results/sci-plot/run.json

# 完成产物登记、provenance 和人工评分后计算成绩
python3 scripts/eval_runner.py --score eval-results/sci-plot/run.json
```

评分固定拆成：

- 40 分机器可验证：交付物角色/格式、文件存在性、精确 upstream commit provenance；
- 60 分专家判断：科学正确性、证据忠实度、视觉清晰度、可编辑/可复现性、可访问性。

如果人工评分还没完成，runner 只返回 `needs-human-review`，不会为了“有个数字”伪造 100 分总成绩。

详见 [evals/README.md](evals/README.md)。

## Upstream Health 与 Lockfile

```bash
GITHUB_TOKEN=... python3 scripts/check_upstreams.py \
  --output /tmp/upstream-health.json \
  --fail-on-critical

python3 scripts/update_upstream_lock.py \
  --health /tmp/upstream-health.json
```

这里采用双层设计：

- `registry/skills.json`：人工策展政策，包括 tier、role、license 判断、curator score、路由；
- `registry/upstream-lock.json`：机器观测事实，包括 resolved commit、observed license、archived、pushed_at、subdir 状态。

API 限流或临时网络失败只会标为 `unknown`，不会被误判成“上游已损坏”。定时 GitHub Workflow 只有在 lock 的稳定内容真正变化时才创建/刷新自动化 PR，而且**绝不自动 merge upstream 升级**。

详见 [docs/automation.md](docs/automation.md)。

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

## 目录

```text
registry/skills.json             # 人工策展元数据
registry/upstream-lock.json      # 机器观测的稳定 upstream 状态
schema/skill.schema.json         # metadata JSON Schema
evals/benchmark.json             # Core benchmark cases + 评分定义
evals/result.schema.json         # 单次测试 manifest schema
evals/README.md                  # benchmark 使用说明
docs/selection-guide.md          # 路由/选择矩阵
docs/scoring.md                  # curator 100 分评分体系
docs/automation.md               # health/lock/自动 PR 机制
docs/licensing.md                # 上游许可证与归属机制
scripts/install.py               # 零第三方 Python 依赖安装器
scripts/eval_runner.py           # benchmark manifest + scorer
scripts/check_upstreams.py       # 上游健康检查
scripts/update_upstream_lock.py  # 稳定 lockfile 更新器
scripts/validate_registry.py     # Registry + Lock invariant 校验
```

本仓库自己的代码和元数据使用 MIT；上游 Skill 始终保持其原始许可证，本仓库不会替上游重新授权。
