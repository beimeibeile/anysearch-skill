# 官方 API 兼容性说明（Official API Compatibility）

> ⚠️ **必读**：本 Skill 为**自研版本**（仓库：`github.com/beimeibeile/anysearch-skill`），
> 参照官方仓库（`github.com/anysearch-ai/anysearch-skill`）的 API 语义开发，**依赖官方公开 API**。
> 任何对官方 API 的改动都可能影响本 Skill 功能，须定期检查官方动向。

## 一、依赖关系

| 项 | 说明 |
|---|---|
| 官方 API 服务 | `https://api.anysearch.com`（search / batch_search / extract / get_sub_domains） |
| 参照官方仓库 | `https://github.com/anysearch-ai/anysearch-skill` |
| 自研仓库 | `https://github.com/beimeibeile/anysearch-skill` |
| 客户端协议标识 | `CLIENT_HEADER = skill/3.1.1`（对齐官方 v3.1.1，2026-09-02 发布） |
| 自研版本号 | `SKILL.md version: 3.1.0`（自研包版本，独立演进，与官方协议版本解耦） |

## 二、版本对齐规则

- `CLIENT_HEADER`（4 个 CLI：py / js / ps1 / sh 中的版本常量）表示**对官方 API 的客户端协议版本**，
  应跟随官方最新 Release 升级。
- `SKILL.md version` 表示**自研包版本**，仅在本 Skill 自身功能演进时递增，不随官方版本机械同步。
- 协议版本与自研版本**解耦**：官方出 v3.1.2 时只需评估 API 协议是否有变化，无变化则不必升级 CLIENT_HEADER。

## 三、定期检查（SOP）

官方 API 可能出现：端点变更、参数新增/废弃、垂类（domain/sub_domain）调整、限流策略变化。

**检查频率建议**：每月一次；或官方 Release 发布后立即检查。

```powershell
# 1. 查看官方最新标签与 main
git ls-remote --tags https://github.com/anysearch-ai/anysearch-skill.git
git ls-remote --heads https://github.com/anysearch-ai/anysearch-skill.git

# 2. 对比本地与官方最新 tag 的 API 相关文件差异
git fetch https://github.com/anysearch-ai/anysearch-skill.git refs/tags/<latest>:refs/remotes/canonical/<latest>
git diff HEAD canonical/<latest> -- scripts/ scripts/shared/
```

**兼容性判断**：
1. 差异集中在 `scripts/shared/constants.json` 的 domain 列表、CLI 的 CLIENT_HEADER、文档 → 仅需对齐 CLIENT_HEADER。
2. 出现新的端点/参数/请求结构 → 需评估自研 CLI 与调用方（ai-video-editor、anysearch_inspiration、material_search_aggregator）是否受影响，决定是否兼容更新。
3. 官方 API 服务地址或认证方式变化 → 必须立即跟进。

## 四、开发与部署约定（重要）

- **唯一开发目录**：`D:\DobaoWork_Project\anysearch-skill`。所有关于 anysearch-skill 的开发、修改、提交均在此目录进行。
- **安装目录（只部署，不开发）**：以下两个目录是豆包 / 豆包工作的 Skill 安装目录，仅通过 `git pull` 同步部署，禁止直接在其中修改代码：
  - 豆包：`C:\Users\Administrator\AppData\Local\Doubao\User Data\Default\.doubao\agent_mode\workspace\.user_skills\anysearch-skill`
  - 豆包工作：`C:\Users\Administrator\AppData\Local\DoubaoWork\User Data\Default\.doubaowork\agent_mode\workspace\.user_skills\anysearch-skill`
- **发布流程**：开发目录 `git commit` → `git push`（origin = beimeibeile/anysearch-skill）→ 两个安装目录 `git pull`。

## 五、历史记录

- 2026-11-02：CLIENT_HEADER 从 `skill/3.0.1` 对齐至 `skill/3.1.1`（官方 v3.1.1 无 API 功能变更，仅安全校验与版本同步工程化；本次为预防性协议标识对齐）。
