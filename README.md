
# ici-agent（Ascentium 销售助手）

一个围绕 Ascentium 销售场景的本地工作空间，用于：
- 管理越南 / 东南亚相关的知识库（`knowledge/`）
- 通过自定义技能（`/.cursor/skills`）辅助销售准备会议、产出话术与文档
- 将 `output/` 下的交付物按主题归档，并可一键打包发送邮件

## 目录结构

- `knowledge/`：内部知识文档（如越南设厂、园区对比、沟通技巧等）
- `output/`：对外交付物与会议材料（按「日期-主题」建子目录，不纳入 Git 管理）
- `.cursor/skills/`：
  - `ascentium-sales-enablement/`：销售赋能总控 Skill，负责拆任务、分派和质检
  - `trusted-sources/`：统一定义可信信息源（Knowledge、Neo4j、Asia Briefing 等）
  - `output-zip-email/`：将某个 `output/<主题>/` 文件夹压缩并发送到指定邮箱

## 快速开始

1. **克隆仓库并进入目录**
   ```bash
   git clone https://github.com/qianping-sara/ici-agent.git
   cd ici-agent
   ```

2. **配置邮件发送（可选，用于打包并发邮件）**
   在项目根目录创建 `.env`（不会被提交到 Git）：
   ```env
   SMTP_HOST=smtp.example.com
   SMTP_PORT=465
   SMTP_USER=your@example.com
   SMTP_PASSWORD=授权码或应用密码
   FROM_EMAIL=your@example.com
   ```

3. **压缩 output 主题并发送到邮箱**
   ```bash
   python3 .cursor/skills/output-zip-email/scripts/zip_and_email.py "2026-02-20-越南设厂30分钟电话" "your@recipient.com"
   ```
   - 会在 `output/` 下生成对应的 zip 文件
   - 若 SMTP 配置正确，会自动将 zip 作为附件发送到指定邮箱

## MCP 配置（可选）

本仓库的 `trusted-sources` 等技能会用到 **Neo4j** 与 **Tavily**。若需在 Cursor 中启用对应 MCP，请将下方配置合并到你的 Cursor MCP 配置文件（如 `~/.cursor/mcp.json`），并**自行填入密码与 API Key**（勿提交到 Git）。

```json
{
  "mcpServers": {
    "neo4j-mcp": {
      "type": "stdio",
      "command": "neo4j-mcp",
      "args": [],
      "env": {
        "NEO4J_URI": "neo4j://127.0.0.1:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "<你的 Neo4j 密码>",
        "NEO4J_DATABASE": "<你的 DB>",
        "NEO4J_READ_ONLY": "true"
      }
    },
    "tavily-mcp-server": {
      "type": "command",
      "command": "npx",
      "args": ["-y", "tavily-mcp@latest"],
      "env": {
        "TAVILY_API_KEY": "<你的 Tavily API Key>"
      }
    }
  }
}
```

- **Neo4j**：需本地或远程已启动 Neo4j，并创建好 `ici-china` 数据库。
- **Tavily**：API Key 可在 [Tavily](https://tavily.com) 获取。

## 注意事项

- `output/` 目录仅作为**输出与留痕**，不会被模型当作事实来源，也不会被提交到 Git。
- `.env` 中可能包含账号与密钥信息，**务必不要提交到远程仓库**（已在 `.gitignore` 中忽略）。
- MCP 配置中的 `NEO4J_PASSWORD`、`TAVILY_API_KEY` 等为敏感信息，请仅在本地 `mcp.json` 中配置，勿写入本仓库。

