#!/usr/bin/env python3
"""
将 output/<主题>/ 打包为 zip，并可选通过 SMTP 发送到指定邮箱。
用法: python zip_and_email.py "<主题名>" "<收件人邮箱>"
环境变量（可选）: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL
也支持在项目根目录使用 .env 文件配置上述变量（KEY=VALUE 形式），脚本会自动加载。
"""
import os
import sys
import smtplib
import zipfile
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path


def find_project_root() -> Path:
    """从脚本位置推断项目根（ici2）。"""
    script_dir = Path(__file__).resolve().parent
    # .cursor/skills/output-zip-email/scripts -> 向上 4 级到项目根
    return script_dir.parent.parent.parent.parent


def load_dotenv_if_exists(root: Path) -> None:
    """
    若项目根下存在 .env，则按 KEY=VALUE 解析并写入 os.environ（不覆盖已存在的变量）。
    解析规则简单：忽略空行和以 # 开头的注释行，仅处理包含 "=" 的行。
    """
    env_path = root / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def zip_folder(src_dir: Path, zip_path: Path) -> None:
    """将 src_dir 下所有文件打包到 zip_path。"""
    src_dir, zip_path = src_dir.resolve(), zip_path.resolve()
    if not src_dir.is_dir():
        raise FileNotFoundError(f"目录不存在: {src_dir}")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(src_dir):
            for f in files:
                fp = Path(root) / f
                arcname = fp.relative_to(src_dir)
                zf.write(fp, arcname)


def send_email_with_attachment(
    to_email: str,
    zip_path: Path,
    subject: str,
    body: str,
) -> None:
    host = os.environ.get("SMTP_HOST")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASSWORD")
    from_email = os.environ.get("FROM_EMAIL") or user
    if not all([host, user, password]):
        raise RuntimeError(
            "未配置邮件：请设置环境变量 SMTP_HOST, SMTP_USER, SMTP_PASSWORD（以及可选 SMTP_PORT, FROM_EMAIL）"
        )
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    msg.attach(MIMEText(body, "plain", "utf-8"))
    with open(zip_path, "rb") as f:
        part = MIMEBase("application", "zip")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        "attachment",
        filename=zip_path.name,
    )
    msg.attach(part)
    if port == 465:
        with smtplib.SMTP_SSL(host, port) as smtp:
            smtp.login(user, password)
            smtp.sendmail(from_email, [to_email], msg.as_string())
    else:
        with smtplib.SMTP(host, port) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.sendmail(from_email, [to_email], msg.as_string())


def main() -> None:
    if len(sys.argv) != 3:
        print("用法: python zip_and_email.py \"<主题名>\" \"<收件人邮箱>\"", file=sys.stderr)
        sys.exit(1)
    topic = sys.argv[1].strip()
    to_email = sys.argv[2].strip()
    if not topic or not to_email:
        print("主题名和收件人邮箱均不能为空。", file=sys.stderr)
        sys.exit(1)
    root = find_project_root()
    load_dotenv_if_exists(root)
    src_dir = root / "output" / topic
    zip_path = root / "output" / f"{topic}.zip"
    try:
        zip_folder(src_dir, zip_path)
        print(f"已打包: {zip_path}")
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        sys.exit(2)
    try:
        send_email_with_attachment(
            to_email,
            zip_path,
            subject=f"Output 主题打包: {topic}",
            body=f"请查收附件：output 主题「{topic}」的压缩包。",
        )
        print(f"已发送到: {to_email}")
    except Exception as e:
        print(f"发送邮件失败: {e}", file=sys.stderr)
        print("zip 已生成，你可手动将以下文件作为附件发送:", file=sys.stderr)
        print(f"  {zip_path}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
