---
name: output-zip-email
description: Compresses an output topic folder (output/<topic>/) into a zip and sends it to a specified email. Use when the user wants to zip an output theme folder and email the archive, or says "压缩 output 某主题并发邮件" / "把某主题打包发到邮箱".
---

# Output 主题压缩并邮件发送

将 `output/<主题>/` 下整个文件夹打包为 zip，并发送到用户指定邮箱。

## 何时使用

- 用户明确要求把 output 下某个主题文件夹压缩并发到指定邮箱。
- 用户说「把 xxx 主题打包发我邮箱」「压缩 2026-02-20-越南设厂 并发到 xxx@example.com」等。

## 前置条件

1. **主题目录存在**：`output/<主题名>/` 必须存在（主题名即子目录名，如 `2026-02-20-越南设厂30分钟电话`）。
2. **邮件配置**：发送邮件需 SMTP 环境变量，见下方「环境变量」。

## 执行步骤

1. **确认主题与邮箱**  
   - 若用户只给主题未给邮箱，或只给邮箱未给主题，向用户确认另一项。  
   - 主题名 = output 下的子目录名（不含 `output/` 前缀）。

2. **执行脚本**  
   在项目根目录执行（`python3` 或 `python` 均可）：
   ```bash
   python3 .cursor/skills/output-zip-email/scripts/zip_and_email.py "<主题名>" "<收件人邮箱>"
   ```
   例如：
   ```bash
   python3 .cursor/skills/output-zip-email/scripts/zip_and_email.py "2026-02-20-越南设厂30分钟电话" "user@example.com"
   ```

3. **若未配置 SMTP**  
   脚本会先生成 zip 到 `output/<主题名>.zip`，并提示用户未配置邮件或发送失败。此时告知用户：
   - zip 已生成，路径为 `output/<主题名>.zip`；
   - 若需自动发邮件，需在环境中配置 SMTP 变量后重新运行脚本，或手动将 zip 作为附件发送。

## 环境变量（发送邮件时必选）

| 变量 | 说明 | 示例 |
|------|------|------|
| `SMTP_HOST` | SMTP 服务器 | `smtp.gmail.com` |
| `SMTP_PORT` | 端口（TLS 常用 587） | `587` |
| `SMTP_USER` | 登录用户名/邮箱 | `your@gmail.com` |
| `SMTP_PASSWORD` | 密码或应用专用密码 | — |
| `FROM_EMAIL` | 发件人地址（可与 SMTP_USER 相同） | `your@gmail.com` |

未设置时脚本仅打包不发送，并提示配置方式。

## 行为说明

- **仅打包 output 下指定主题**：只压缩 `output/<主题名>/` 内全部文件（含子目录），不包含 output 下其他主题。
- **Zip 路径**：生成 `output/<主题名>.zip`，便于与主题同处一处；发送成功后是否删除 zip 可由用户偏好决定，默认保留。
- **不读取 output 内容做推理**：本技能只调用脚本对 output 做打包与发邮件，不把 output 内文件内容读入对话上下文。
