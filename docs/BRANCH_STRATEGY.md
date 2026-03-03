# 分支管理策略

## 🎯 核心原则

**⚠️ 重要提醒：上游仓库（upstream）在 V2.2+ 版本已将前端闭源，因此需要谨慎处理上游更新！**

当前版本：**V2.1.1** - 这是最后一个前端完全开源的版本
- 提交：`ae82cc0` - fix: Improve System Overview tab UI
- 前端状态：✅ 完全开源
- 后端状态：✅ 完全开源

---

## 📊 分支结构

```
main
├── backup/v2.1.1-frontend-open-source  ✅ 已创建
│   └── 备份分支，包含完整前端源码
│
├── dev                                  ✅ 已创建
│   ├── feature/xxx                      功能开发分支
│   ├── fix/xxx                          Bug 修复分支
│   ├── hotfix/xxx                       紧急修复分支
│   └── refactor/xxx                     重构分支
│
└── [其他功能分支]
```

---

## 🌿 分支说明

### 1️⃣ **main** (稳定分支)
- **用途**: 生产环境稳定版本
- **状态**: 当前指向 V2.1.1（前端开源版本）
- **保护**: 受保护分支，需要 PR 才能合并
- **同步**: ⚠️ **不要同步上游更新**（会丢失前端源码）

### 2️⃣ **backup/v2.1.1-frontend-open-source** (备份分支)
- **用途**: 永久备份前端开源版本
- **状态**: 锁定，不进行修改
- **内容**: 包含完整的 `quantdinger_vue/` 源码
- **用途**: 
  - 如果需要恢复前端源码，可以从此分支复制
  - 作为二次开发的基准版本
  - 防止误操作删除前端代码

### 3️⃣ **dev** (开发分支)
- **用途**: 主要开发分支
- **状态**: 当前基于 main
- **合并策略**: 
  - 从 feature/fix/hotfix 分支合并
  - 定期合并到 main（发布新版本）
- **同步**: ⚠️ **谨慎同步上游更新**

### 4️⃣ **feature/*** (功能分支)
- **命名规范**: `feature/功能描述`
- **示例**: `feature/add-new-indicator`
- **来源**: 从 dev 分支创建
- **合并**: 完成后合并回 dev

### 5️⃣ **fix/*** (Bug 修复分支)
- **命名规范**: `fix/问题描述`
- **示例**: `fix/backtest-timing-issue`
- **来源**: 从 dev 分支创建
- **合并**: 完成后合并回 dev

### 6️⃣ **hotfix/*** (紧急修复分支)
- **命名规范**: `hotfix/问题描述`
- **示例**: `hotfix/critical-security-fix`
- **来源**: 从 main 分支创建
- **合并**: 修复后同时合并到 main 和 dev

---

## ⚠️ 上游同步策略

### 🚫 **高风险操作**
```bash
# ❌ 不要这样做！会删除前端源码
git merge upstream/main  # V2.2+ 前端已闭源
```

### ✅ **安全的上游同步策略**

#### 场景 1：仅同步后端改进
```bash
# 1. 创建临时分支测试上游更新
git checkout -b test/upstream-sync

# 2. 拉取上游更新
git fetch upstream
git merge upstream/main

# 3. 检查前端目录
ls -la quantdinger_vue/

# 4. 如果前端源码被删除，撤销合并
git reset --hard HEAD~1

# 5. 如果前端还在，检查前端是否闭源（源文件是否保留）
find quantdinger_vue/src -name "*.vue" | wc -l
# 应该有 28+ 个 vue 文件，如果是 0 或很少，说明已闭源

# 6. 如果确认安全，合并到 dev
git checkout dev
git merge test/upstream-sync
```

#### 场景 2：选择性合并上游后端文件
```bash
# 1. 获取上游更新但不合并
git fetch upstream

# 2. 查看后端改动
git diff dev upstream/main --stat backend_api_python/

# 3. 仅合并后端特定文件
git checkout dev
git cherry-pick <commit-hash>  # 只挑选需要的后端提交
```

#### 场景 3：手动复制上游后端改进
```bash
# 1. 创建临时分支
git checkout -b temp/upstream-checkout
git fetch upstream
git merge upstream/main

# 2. 仅复制需要的后端文件到 dev
git checkout dev
cp ../temp/upstream-checkout/backend_api_python/xxx.py ./backend_api_python/

# 3. 删除临时分支
git branch -D temp/upstream-checkout
```

---

## 📋 工作流程

### 日常开发流程
```bash
# 1. 切换到 dev 分支
git checkout dev

# 2. 创建功能分支
git checkout -b feature/your-feature

# 3. 开发和提交
git add .
git commit -m "feat: 添加你的功能"

# 4. 推送到你的 fork
git push fork feature/your-feature

# 5. 完成后合并回 dev
git checkout dev
git merge feature/your-feature

# 6. 删除功能分支（可选）
git branch -d feature/your-feature
```

### 发布新版本流程
```bash
# 1. 从 dev 创建发布分支
git checkout -b release/v2.1.2

# 2. 测试和修复
# ...

# 3. 合并到 main
git checkout main
git merge release/v2.1.2

# 4. 打标签
git tag -a v2.1.2 -m "Release v2.1.2"

# 5. 推送
git push fork main --tags
```

---

## 🔒 保护分支设置（推荐）

在 GitHub 上设置分支保护：

### main 分支保护规则：
- ✅ 需要至少 1 个 PR review
- ✅ 需要 status checks 通过
- ✅ 禁止强制推送
- ✅ 要求更新分支前为最新

设置方式：
1. 访问 https://github.com/princealbert/QuantDinger/settings/branches
2. 点击 "Add rule"
3. 分支名：`main`
4. 勾选上述保护选项

---

## 📦 版本规划

| 版本 | 基础分支 | 前端状态 | 后端状态 | 备注 |
|------|---------|---------|---------|------|
| v2.1.1 | main | ✅ 完全开源 | ✅ 完全开源 | **当前版本** |
| v2.1.2-dev | dev | ✅ 完全开源 | ✅ 完全开源 | 开发中 |
| v2.2.0+ | - | ❌ 闭源 | ✅ 完全开源 | **不升级** |

---

## 🚨 应急预案

### 如果误操作删除了前端源码

```bash
# 从备份分支恢复
git checkout backup/v2.1.1-frontend-open-source -- quantdinger_vue/

# 恢复后检查
git status
git diff
```

### 如果需要回滚到之前的状态

```bash
# 查看提交历史
git log --oneline

# 回滚到指定提交
git reset --hard <commit-hash>

# 如果已经推送，需要强制推送
git push fork main --force
```

---

## 📝 分支命名规范

| 类型 | 前缀 | 示例 | 说明 |
|------|------|------|------|
| 功能 | `feature/` | `feature/add-rsi-indicator` | 新功能开发 |
| 修复 | `fix/` | `fix/backtest-timing-bug` | Bug 修复 |
| 紧急修复 | `hotfix/` | `hotfix/security-patch` | 紧急问题修复 |
| 重构 | `refactor/` | `refactor/data-source-architecture` | 代码重构 |
| 文档 | `docs/` | `docs/update-api-guide` | 文档更新 |
| 测试 | `test/` | `test/add-unit-tests` | 测试相关 |
| 备份 | `backup/` | `backup/v2.1.1-frontend-open-source` | 备份分支 |

---

## 🔄 远程仓库操作

### 推送到你的 fork
```bash
git push fork <branch-name>
```

### 同步上游（谨慎操作！）
```bash
# 仅查看上游更新
git fetch upstream
git log dev..upstream/main --oneline

# 详细检查后手动合并
git cherry-pick <commit-hash>
```

### 删除远程分支
```bash
git push fork --delete feature/old-feature
```

---

## 📊 当前分支状态

```bash
# 查看所有分支
git branch -a

# 查看当前分支
git branch

# 查看分支提交历史
git log --oneline --graph --all -10
```

---

## 🎯 开发建议

### ✅ 推荐做法
1. 在 `dev` 分支进行日常开发
2. 每个功能使用独立的 `feature/*` 分支
3. 定期推送到你的 fork 仓库
4. 重要节点打标签（如 `v2.1.2`）
5. 保护 `main` 分支
6. 谨慎同步上游更新

### ❌ 避免做法
1. 不要直接在 `main` 分支开发
2. 不要随意同步 `upstream/main`（会丢失前端源码）
3. 不要删除 `backup/v2.1.1-frontend-open-source` 分支
4. 不要强制推送 `main` 分支（除非确实需要）
5. 不要在备份分支上进行开发

---

## 📚 参考资料

- [Git 分支最佳实践](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)
- [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow)
- [语义化版本](https://semver.org/lang/zh-CN/)

---

**最后更新**: 2026-02-24
**维护者**: princealbert
**基础版本**: QuantDinger V2.1.1 (前端开源)
