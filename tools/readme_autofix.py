import os
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README_PATH = os.path.join(PROJECT_ROOT, "README.md")


def clean_text(text: str) -> str:
    # حذف فاصله‌های اضافی
    text = re.sub(r"\n{3,}", "\n\n", text)

    # حذف فاصله‌های انتهای خطوط
    text = "\n".join(line.rstrip() for line in text.splitlines())

    # اصلاح فاصله‌های Markdown خراب
    text = text.replace("  \n", "\n")

    return text


def normalize_headers(text: str) -> str:
    # یکنواخت کردن heading spacing
    text = re.sub(r"\n#([^\n])", r"\n# \1", text)
    return text


def fix_code_blocks(text: str) -> str:
    # جلوگیری از باز بودن code block های ناقص
    if text.count("```") % 2 != 0:
        text += "\n```"
    return text


def auto_fix_readme():
    if not os.path.exists(README_PATH):
        print("README.md not found")
        return

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    print("🔧 Fixing README...")

    content = clean_text(content)
    content = normalize_headers(content)
    content = fix_code_blocks(content)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("✔ README fixed and updated")


if __name__ == "__main__":
    auto_fix_readme()

