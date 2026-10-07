# AnySearch Skill - API 参考文档

## CLI 用法

```bash
python scripts/anysearch_cli.py --query "搜索词" [options]
```

### 主要参数

| 参数 | 说明 |
|------|------|
| `--query` | 搜索关键词 |
| `--api_key` | API密钥（优先于.env） |
| `--domain` | 垂类领域（23个可选） |
| `--output` | 输出文件路径 |
| `--format` | 输出格式（json/markdown） |
| `--lang` | 语言（zh/en/ja/ko） |

## 多语言实现

| 语言 | 文件 | 说明 |
|------|------|------|
| Python | scripts/anysearch_cli.py | 主实现（651行） |
| JavaScript | scripts/anysearch_cli.js | Node.js版本 |
| PowerShell | scripts/anysearch_cli.ps1 | Windows原生 |
| Shell | scripts/anysearch_cli.sh | Unix/macOS |

## 报告生成

```bash
python scripts/generate.py --query "关键词" --output report.md
```

## 环境变量

| 变量 | 说明 |
|------|------|
| ANYSEARCH_API_KEY | API密钥 |
| ANYSEARCH_API_URL | API地址 |

## CI/CD
- .github/workflows/ci.yml: 自动化测试+多语言验证
