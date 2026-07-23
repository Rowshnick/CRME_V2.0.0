import os
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README_PATH = os.path.join(PROJECT_ROOT, "README.md")


def fix_headers(text: str) -> str:
    # تبدیل ## ## یا # # به استاندارد
    text = re.sub(r"^\s*#\s+#", "##", text, flags=re.MULTILINE)
    text = re.sub(r"^#{3,}", lambda m: "#" * 3, text, flags=re.MULTILINE)
    text = re.sub(r"^#\s{2,}", "# ", text, flags=re.MULTILINE)
    return text


def fix_spacing(text: str) -> str:
    # حذف خطوط خالی بیش از حد
    text = re.sub(r"\n{3,}", "\n\n", text)

    # فاصله قبل و بعد از section ها
    text = re.sub(r"\n# ", "\n\n# ", text)

    return text


def fix_lists(text: str) -> str:
    # جدا کردن لیست‌ها از متن چسبیده
    text = re.sub(r"([a-zA-Z0-9])\n-", r"\1\n\n-", text)
    return text


def fix_code_blocks(text: str) -> str:
    # اگر ``` باز مانده باشد ببند
    if text.count("```") % 2 != 0:
        text += "\n```"
    return text


def normalize(text: str) -> str:
    text = fix_headers(text)
    text = fix_spacing(text)
    text = fix_lists(text)
    text = fix_code_blocks(text)
    return text


def main():
    if not os.path.exists(README_PATH):
        print("❌ README.md not found")
        return

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    print("🔧 Fixing README structure...")

    fixed = normalize(content)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(fixed)

    print("✔ README fixed successfully")


if __name__ == "__main__":
    main()

