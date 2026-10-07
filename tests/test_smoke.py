"""冒烟测试: anysearch-skill CLI可导入、基本功能可用"""
import os, sys, subprocess
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(SKILL_ROOT, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

passed = 0; failed = 0
def check(name, func):
    global passed, failed
    try:
        func(); print(f"  PASS: {name}"); passed += 1
    except Exception as e:
        print(f"  FAIL: {name} -> {type(e).__name__}: {e}"); failed += 1

print("=== Module Imports ===")
check('anysearch_cli', lambda: __import__('anysearch_cli'))
check('generate', lambda: __import__('generate'))

print()
print("=== CLI Help ===")
def cli_help():
    r = subprocess.run([sys.executable, os.path.join(SCRIPTS_DIR, "anysearch_cli.py"), "--help"],
                       capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, f"exit code {r.returncode}"
    assert "usage" in r.stdout.lower() or "anysearch" in r.stdout.lower()
check('cli_help', cli_help)

print()
print("=== Constants ===")
def check_constants():
    import anysearch_cli
    assert hasattr(anysearch_cli, "CLIENT_HEADER")
    assert "skill/" in anysearch_cli.CLIENT_HEADER
check('client_header', check_constants)

print()
print(f"=== 结果: {passed} passed, {failed} failed ===")
sys.exit(1 if failed > 0 else 0)
