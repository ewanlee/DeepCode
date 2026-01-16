# 产品需求文档 (PRD): Paper2Sim 混合仿真引擎

| 文档属性 | 详情 |
| :--- | :--- |
| **项目名称** | Paper2Sim: Hybrid OR/LLM Simulation Engine |
| **版本** | v1.0 (Draft) |
| **状态** | 规划中 |
| **受众** | AI 工程师, 运筹学专家, 后端开发团队 |
| **核心理念** | **Environment as Law (Math), Agent as Brain (LLM)** |

---

## 1. 项目背景与愿景 (Executive Summary)

传统的运筹学/管理科学（OR/OM/MS）研究依赖于高度简化的数学模型（Stylized Models），虽然理论严谨但缺乏现实世界的行为复杂性。纯粹的基于大模型（LLM）的社会仿真虽然具备行为逼真度，但缺乏可验证性和逻辑一致性，常被视为“黑盒”。

**Paper2Sim** 旨在构建一种**混合架构（Hybrid Architecture）**，自动化地将学术论文转化为高保真的仿真代码。

- **输入**：一篇包含数学模型的 PDF 论文。
- **核心逻辑**：利用数学模型构建确定性的“物理环境”，利用 LLM 构建具备认知能力的“智能体”。
- **输出**：一套通过理论验证的 Python 仿真系统，以及基于该系统的行为学分析报告。

---

## 2. 系统架构原则 (System Principles)

本系统严格遵循以下**“白盒环境，灰盒决策”**的设计原则：

1.  **物理法则不可违背 (Hard Constraints)**：环境的状态转移（State Transition）、收益计算（Payoff）、以及硬性约束必须由**确定性的 Python 代码**实现，直接映射论文公式。LLM 不允许“想象”收益，只能“感知”收益。
2.  **理性基准先行 (Rationality First)**：在开启任何高级仿真前，LLM Agent 必须通过“图灵测试”般的理论验证，证明其在 Temperature=0 时能复现论文的 Proposition。
3.  **认知层叠加 (Cognitive Layering)**：在理论验证通过后，才允许引入记忆、情感、自然语言交互等“软因素”，观察系统涌现。

---

## 3. 功能详述：核心流水线 (Core Pipeline Specs)

### Phase 1: 解构与形式化 (Deconstruction)
**目标**：将非结构化的论文转化为结构化的 `Simulation Spec JSON`。

#### 1.1 模块：The Theorist (理论解析器)
*   **输入**：PDF/LaTeX 文本。
*   **功能要求**：
    *   识别并提取博弈四元组 $<N, S, A, U>$。
    *   **关键输出字段**：
        *   `state_variables`: 定义变量名、类型、取值范围 (e.g., `prior_belief: float [0,1]`).
        *   `transition_logic`: 提取贝叶斯更新或状态转移公式 (LaTeX -> SymPy/Python Lambda)。
        *   `payoff_functions`: 提取各方效用函数。
*   **验收标准**：生成的 JSON 必须能被下游代码生成器无歧义解析。

#### 1.2 模块：The Critic (基准生成器)
*   **功能要求**：
    *   提取论文中的 `Proposition`, `Lemma`, `Corollary`。
    *   将自然语言推论转化为 Python `unittest` 用例。
*   **Use Case 示例**：
    *   *原文*："Proposition 1: When cost c < threshold, the physician always tests."
    *   *生成代码*：`def test_prop1(): assert agent.decide(c=0.1) == 'TEST'`

### Phase 2: 架构与编码 (Architecture & Coding)
**目标**：生成“环境-代理”分离的 Python 代码。

#### 2.1 模块：The Architect & Engineer (代码生成引擎)
*   **核心逻辑**：
    *   **Environment Class (White-box)**: 必须包含 `step(actions) -> observation, reward, done, info`。此部分代码**严禁**使用 LLM 调用，必须是纯数学逻辑运算。
    *   **Agent Class (LLM-based)**: 必须包含 `decide(observation, memory) -> action`。此部分封装 LLM API 调用，模拟 agent 之间的 socialized interactions。
*   **Prompt Engineering 自动化**：
    *   将 Phase 1 提取的 `Utility Function` 自动翻译为 Agent 的 System Prompt（例如：“你的目标是最大化利润，利润计算公式为...”）。

### Phase 3: 验证与校准 (Verification)
**目标**：确保仿真器的“理论保真度”。

#### 3.1 模块：The QA Specialist (自动校准闭环)
*   **执行逻辑**：
    1.  设置 LLM Temperature = 0。
    2.  运行 Phase 1.2 生成的所有单元测试。
    3.  **失败处理**：若 Agent 行为违反 Proposition，触发 **CoT Debugging**：
        *   让 Agent 输出决策思维链。
        *   分析是“计算错误”还是“动机误解”。
        *   自动修正 System Prompt（例如添加：“请注意，长期声誉对你也很重要”或引入 Python Calculator Tool）。
*   **里程碑**：只有当所有 Unit Tests 通过，系统才标记为 `Calibrated`，允许进入 Phase 4。

---

## 4. 高级特性：深度涌现 (Phase 4 Specs)

此阶段是产品的**核心差异化竞争力**，旨在探索论文模型未能覆盖的“真实世界复杂性”。

### 4.1 特性：认知路径依赖 (Cognitive Path Dependence)
*   **负责 Agent**: `The Historian`
*   **功能描述**：
    *   为每个 Agent 挂载一个 **Vector Database (如 ChromaDB)** 作为长期记忆。
    *   **Memory Retrieval**: 在决策前，检索 Top-K 相关历史事件（例如：“上次面对这类病人，我被投诉了”）。
    *   **Psychological State Injection**: 基于检索结果，动态修改 Prompt 中的 `Current Mood/Bias` 字段。
*   **用户价值**：模拟信任崩塌、职业倦怠等非马尔可夫效应。

### 4.2 特性：语义博弈层 (Semantic Layer)
*   **负责 Agent**: `The Narrative Designer`
*   **功能描述**：
    *   **Encoding**: 将数学动作（Action=High Effort）转化为自然语言（“我会尽全力救治...”）。
    *   **Framing**: 允许 Agent 使用“框架效应”话术（e.g., 强调“90%存活”而非“10%死亡”）。
    *   **Decoding**: 接收方 Agent 需解析对方的语言，判断其真实意图（识别欺骗）。
*   **用户价值**：验证信息不对称下的语言操纵对均衡的影响。

### 4.3 特性：机制红队测试 (Mechanism Red Teaming)
*   **负责 Agent**: `The Red Teamer`
*   **功能描述**：
    *   **Meta-Goal**: 赋予 Agent “寻找系统漏洞”的最高指令。
    *   **Evolutionary Strategy**: 允许 Agent 变异其 Persona，尝试极端策略（如合谋、刷单、对抗性输入）。
    *   **Goodhart's Law Detection**: 自动检测当某个指标成为目标后，是否不再有效。
*   **输出报告**：生成《机制鲁棒性分析报告》，指出论文模型的潜在失效边界。

---

## 5. 技术栈与非功能需求 (Technical Requirements)

*   **Backend**: Python 3.10+
*   **LLM Orchestration**: 基于 DeepCode main branch 代码库。
*   **LLM Model Support**:
    *   *Reasoning (Phase 1-3)*: GPT-4o / Claude 3.5 Sonnet (高智商，强指令遵循)。
    *   *Simulation (Phase 4)*: GPT-4o-mini / Llama-3-70B (高并发，低成本，更像人类的随机性)。
*   **Memory Store**: ChromaDB / Pinecone。
*   **Visualization**: Streamlit (用于展示仿真过程的动态图表)。

---

## 6. 交付物清单 (Deliverables)

1.  **Simulation Codebase**: 包含 `env.py` (数学环境), `agents.py` (LLM 智能体), `runner.py` (主循环)。
2.  **Verification Report**: 显示 Agent 在多大程度上复现了论文的理论推论（Pass/Fail Rate）。
3.  **Emergence Log**: 记录 Phase 4 中出现的非理论预期行为（如自发合谋、非理性恐慌等）。

---

## 7. 风险评估 (Risk Assessment)

*   **风险点**：LLM 数学能力不足，导致在 Phase 3 无法通过简单的算术测试。
    *   **缓解方案**：为 LLM 配备 `Python REPL Tool`，强制其通过写代码来计算期望收益，而不是心算。
*   **风险点**：仿真成本过高。
    *   **缓解方案**：在 Phase 4 的大规模蒙特卡洛模拟中，使用蒸馏后的小模型（Distilled Models）或量化模型。

