# Git 常用命令快速参考

## 📊 当前仓库配置

```
项目路径: /Users/albert/QuantDinger

远程仓库:
  fork     -> https://github.com/princealbert/QuantDinger.git (你的仓库)
  upstream -> https://github.com/brokermr810/QuantDinger.git (原作者仓库)

本地分支:
  main                              (稳定版本 V2.1.1)
  dev                               (开发分支) ← 当前分支
  backup/v2.1.1-frontend-open-source (备份分支，包含完整前端源码)
```

---

## 🔄 日常操作

### 查看状态
```bash
# 查看当前分支
git branch

# 查看所有分支（包括远程）
git branch -a

# 查看当前状态
git status

# 查看提交历史
git log --oneline -10

# 查看带图形的提交历史
git log --oneline --graph --all -10

# 查看分支提交关系
git log --oneline --all --decorate -5
```

### 切换分支
```bash
# 切换到 dev 分支
git checkout dev

# 切换到 main 分支
git checkout main

# 切换到备份分支
git checkout backup/v2.1.1-frontend-open-source
```

### 创建新分支
```bash
# 从 dev 创建功能分支
git checkout dev
git checkout -b feature/your-feature-name

# 从 dev 创建修复分支
git checkout dev
git checkout -b fix/your-bug-fix

# 从 main 创建紧急修复分支
git checkout main
git checkout -b hotfix/critical-fix
```

### 提交和推送
```bash
# 添加所有更改
git add .

# 添加特定文件
git add path/to/file.py

# 提交
git commit -m "type: description"

# 推送到你的 fork（dev 分支）
git push fork dev

# 推送新分支并设置追踪
git push fork -u feature/your-feature

# 推送所有分支
git push fork --all
```

### 合并分支
```bash
# 合并 feature 分支到 dev
git checkout dev
git merge feature/your-feature

# 合并并删除分支
git merge --no-ff feature/your-feature
git branch -d feature/your-feature

# 解决合并冲突后继续
git add .
git commit
```

---

## ⚠️ 上游同步（谨慎操作！）

### 查看上游更新
```bash
# 获取上游更新（不合并）
git fetch upstream

# 查看上游提交历史
git log upstream/main --oneline -10

# 查看本地和上游的差异
git log dev..upstream/main --oneline

# 查看差异的文件统计
git diff dev upstream/main --stat
```

### 安全的同步策略

#### 方法 1：仅查看后端改动
```bash
# 查看后端改动
git diff dev upstream/main --stat backend_api_python/

# 查看具体文件的改动
git diff dev upstream/main backend_api_python/app/xxx.py
```

#### 方法 2：选择性挑选提交
```bash
# 查看上游提交
git log upstream/main --oneline -20

# 挑选特定提交（仅后端相关的）
git cherry-pick <commit-hash>

# 如果有冲突，解决后：
git add .
git cherry-pick --continue
```

#### 方法 3：手动复制后端文件
```bash
# 创建临时分支
git checkout -b temp/upstream-test
git fetch upstream
git merge upstream/main

# 检查前端源码是否被删除
ls -la quantdinger_vue/src/views/
find quantdinger_vue/src -name "*.vue" | wc -l

# 如果前端源码还在，检查是否闭源（文件数量应 > 20）
# 如果前端源码被删除或闭源，撤销合并
git reset --hard HEAD~1
git checkout dev
git branch -D temp/upstream-test
```

---

## 🔒 保护操作

### 从备份恢复前端
```bash
# 如果误删了前端源码，从备份恢复
git checkout backup/v2.1.1-frontend-open-source -- quantdinger_vue/

# 检查恢复的文件
git status
```

### 回滚到之前的状态
```bash
# 查看提交历史
git log --oneline

# 回滚到指定提交（软回滚，保留更改）
git reset --soft <commit-hash>

# 回滚到指定提交（硬回滚，丢弃更改）
git reset --hard <commit-hash>

# 如果已推送，强制推送（谨慎使用！）
git push fork dev --force
```

### 创建标签
```bash
# 创建轻量标签
git tag v2.1.2

# 创建带注释的标签
git tag -a v2.1.2 -m "Release v2.1.2"

# 推送标签
git push fork v2.1.2

# 推送所有标签
git push fork --tags

# 查看标签
git tag

# 查看标签详情
git show v2.1.2
```

---

## 🧹 清理操作

### 删除分支
```bash
# 删除本地分支（已合并）
git branch -d feature/old-feature

# 强制删除本地分支（未合并）
git branch -D feature/old-feature

# 删除远程分支
git push fork --delete feature/old-feature
```

### 清理未追踪的文件
```bash
# 查看未追踪的文件
git clean -n

# 删除未追踪的文件（不删除 .gitignore 中的文件）
git clean -f

# 删除未追踪的文件和目录
git clean -fd
```

### 清理历史
```bash
# 清理远程已删除的分支引用
git remote prune fork

# 清理未使用的对象
git gc

# 深度清理（释放磁盘空间）
git gc --aggressive --prune=now
```

---

## 🚨 紧急操作

### 撤销最近一次提交（保留更改）
```bash
git reset --soft HEAD~1
```

### 撤销最近一次提交（丢弃更改）
```bash
git reset --hard HEAD~1
```

### 修改最后一次提交信息
```bash
git commit --amend -m "新的提交信息"
```

### 暂存当前更改
```bash
# 暂存所有更改
git stash

# 暂存并添加说明
git stash save "工作未完成"

# 查看暂存列表
git stash list

# 恢复最近一次暂存
git stash pop

# 恢复特定暂存
git stash apply stash@{0}

# 删除暂存
git stash drop stash@{0}
```

---

## 📊 比较操作

### 比较分支
```bash
# 比较两个分支的差异
git diff dev main

# 比较分支的文件列表
git diff dev main --name-only

# 比较分支的文件统计
git diff dev main --stat

# 查看分支独有的提交
git log dev ^main --oneline
```

### 比较提交
```bash
# 比较两个提交
git diff <commit1> <commit2>

# 查看提交的改动
git show <commit-hash>
```

---

## 🔍 查询操作

### 搜索提交
```bash
# 搜索提交信息
git log --grep="关键词"

# 搜索包含特定文件改动的提交
git log --oneline -- backend_api_python/app/xxx.py

# 搜索特定作者的提交
git log --author="princealbert"
```

### 搜索代码
```bash
# 搜索当前代码
git grep "search_term"

# 搜索特定分支的代码
git grep "search_term" dev

# 搜索所有分支的代码
git grep "search_term" $(git rev-parse --all)
```

---

## 📈 性能优化

### 查看仓库大小
```bash
# 查看总大小
du -sh .git

# 查看各部分大小
du -sh .git/objects .git/refs
```

### 优化仓库
```bash
# 清理引用
git remote prune fork

# 垃圾回收
git gc

# 压缩仓库
git repack -a -d --depth=250 --window=250
```

---

## 🎯 开发工作流示例

### 完整功能开发流程
```bash
# 1. 切换到 dev
git checkout dev
git pull fork dev

# 2. 创建功能分支
git checkout -b feature/add-new-indicator

# 3. 开发...
# 编辑文件...

# 4. 提交更改
git add .
git commit -m "feat: add RSI indicator"

# 5. 推送到你的 fork
git push fork -u feature/add-new-indicator

# 6. 测试...

# 7. 合并到 dev
git checkout dev
git merge feature/add-new-indicator

# 8. 推送 dev
git push fork dev

# 9. 删除功能分支（可选）
git branch -d feature/add-new-indicator
git push fork --delete feature/add-new-indicator
```

---

## 📝 提交信息规范

### 类型前缀
- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 文档更新
- `style:` 代码格式（不影响代码运行）
- `refactor:` 重构（既不是新功能也不是修复）
- `perf:` 性能优化
- `test:` 测试相关
- `chore:` 构建过程或辅助工具的变动
- `revert:` 回滚之前的提交

### 提交信息示例
```bash
git commit -m "feat: add MACD indicator support"
git commit -m "fix: resolve backtest timing issue"
git commit -m "docs: update API documentation"
git commit -m "refactor: simplify data source architecture"
```

---

**最后更新**: 2026-02-24
**维护者**: princealbert
**基础版本**: QuantDinger V2.1.1
