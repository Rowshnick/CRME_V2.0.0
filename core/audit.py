import os

BASE = os.path.expanduser("~/CRME")

structure = {
    "core/memory_engine.py": "Core memory engine",
    "core/run.py": "Test runner",
    "scripts": "Scripts folder",
    "templates": "Templates folder",
    "docs": "Docs folder",
    "memory": "Local memory storage (should NOT be empty in real use)",
    "memory/latest.md": "Active memory state file",
    "memory/packs": "Generated memory packs",
    ".gitignore": "Security rules"
}

print("\n🧠 CRME SYSTEM AUDIT\n")
print("="*40)

ok = 0
missing = 0

for path, desc in structure.items():
    full_path = os.path.join(BASE, path)

    if os.path.exists(full_path):
        print(f"✔ EXISTS  : {path}")
        ok += 1
    else:
        print(f"❌ MISSING : {path}")
        missing += 1

print("\n" + "="*40)
print(f"✔ OK: {ok}")
print(f"❌ Missing: {missing}")

if missing == 0:
    print("\n🚀 SYSTEM STATUS: HEALTHY")
else:
    print("\n⚠️ SYSTEM STATUS: NEEDS FIXING")

print("\n📌 Next step suggestion:")
print("- Fix missing components OR initialize pipeline")

