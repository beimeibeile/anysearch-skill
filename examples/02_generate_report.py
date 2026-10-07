"""示例2: 生成搜索报告"""
import os, sys
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(SKILL_ROOT, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)
from generate import generate_report

def main():
    print("AnySearch 报告生成器")
    print("使用方法: python scripts/generate.py --query '你的搜索词'")
    print("支持23个垂类领域，输出结构化Markdown报告")

if __name__ == "__main__":
    main()
