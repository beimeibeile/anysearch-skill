"""示例1: 最小可用 - CLI搜索"""
import os, sys, subprocess
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(SKILL_ROOT, "scripts", "anysearch_cli.py")

def main():
    # 显示CLI帮助
    r = subprocess.run([sys.executable, CLI, "--help"], capture_output=True, text=True)
    print(r.stdout)

if __name__ == "__main__":
    main()
