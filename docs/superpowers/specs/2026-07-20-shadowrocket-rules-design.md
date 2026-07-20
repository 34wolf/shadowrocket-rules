# Shadowrocket 公开分流规则仓库设计

## 目标

创建一个 GitHub Public 仓库，只保存可以公开的 Shadowrocket 分流规则。仓库每天从 Johnshall 的发布分支下载最新版 `sr_top500_banlist_ad.conf`，把用户逐条确认过的个人规则放到 `[Rule]` 段最前面，并生成 `output/my_shadowrocket.conf`。

## 安全边界

- `input/` 始终只保存在本机，并通过 `.gitignore` 排除；其中的 `lz.conf` 不进入 Git，也不上传 GitHub。
- 只分析导出配置的 `[Rule]` 段。`[General]`、`[URL Rewrite]`、`[MITM]` 以及节点、订阅、证书和密码内容不会进入候选规则或公开仓库。
- 与上游规则不同只代表“候选规则”，不代表“个人规则”。每条候选规则必须由用户单独确认后，才能写入公开的 `custom_rules.conf`。
- 含 URL、认证参数或疑似秘密的候选内容需要额外警告；未经明确确认不得公开。
- 覆盖、删除或公开任何文件前，先说明准确对象和影响。
- 不索取 GitHub 密码、Personal Access Token、节点订阅地址或服务器密码。GitHub Actions 只使用仓库自动提供的 `GITHUB_TOKEN`。

## 采用的方案

使用 Python 标准库实现本地分析和配置生成，不安装第三方包。这样在 Mac 和 GitHub Actions 中都容易运行、测试和排查。

仓库默认名称为 `shadowrocket-rules`。主要文件职责如下：

- `AGENTS.md`：记录本项目的安全边界和协作规则。
- `README.md`：说明仓库用途、文件结构和最终订阅地址。
- `BEGINNER_GUIDE.md`：面向零编程经验用户的一步一步操作说明。
- `.gitignore`：阻止 `input/`、本地候选清单和临时下载进入 Git。
- `custom_rules.conf`：只包含用户已经逐条确认、同意公开的个人规则。
- `scripts/find_candidates.py`：只在本地读取导出配置和上游配置，生成被 Git 忽略的候选清单。
- `scripts/build_config.py`：下载或读取上游配置，并把确认规则插入 `[Rule]` 标题之后。
- `tests/`：验证规则提取、插入顺序、重复处理和异常输入。
- `.github/workflows/update.yml`：每天自动更新，也支持在 GitHub 页面手动运行。
- `output/my_shadowrocket.conf`：Mac 和 iPhone 最终订阅的公开配置。

## 数据流程

1. 从 Johnshall 的官方 GitHub 发布位置获取最新 `sr_top500_banlist_ad.conf`。
2. 本地脚本只读取 `input/lz.conf` 的 `[Rule]` 段，将标准化后的规则与上游 `[Rule]` 段比较。
3. 差异写入一个被 Git 忽略的本地候选文件；差异不会自动进入 `custom_rules.conf`。
4. Codex 每次展示一条候选规则及简短解释，用户回复保留或跳过。
5. 只有确认保留且同意公开的规则才写入 `custom_rules.conf`。
6. 生成脚本验证上游配置恰好包含可用的 `[Rule]` 段，把去重后的个人规则插在该段最前面，并写入 `output/my_shadowrocket.conf`。
7. GitHub Actions 每天北京时间 11:15（UTC 03:15）运行；上游有变化时重新生成并提交输出，没有变化时不产生提交。

## 失败处理

- 下载失败、HTTP 状态异常、文件为空或缺少 `[Rule]` 段时立即失败，并保留仓库中上一次成功生成的配置。
- `custom_rules.conf` 中存在格式错误、重复规则或疑似秘密时，验证失败，不生成新输出。
- 自动更新只提交预定的公开文件，不使用 `git add .`，避免意外收录本地文件。
- GitHub Actions 失败时不会覆盖可用输出，用户可从 Actions 页面看到红色失败标记和错误说明。

## 验证标准

- Git 状态和最终 GitHub 文件列表中都不存在 `input/lz.conf` 或任何节点信息。
- 每条写入 `custom_rules.conf` 的规则都有用户逐条确认记录。
- 输出配置中 `[Rule]` 标题后的第一批有效规则与 `custom_rules.conf` 一致，随后才是 Johnshall 的规则。
- 自动化测试覆盖正常插入、空个人规则、重复规则、缺失 `[Rule]`、下载失败和疑似秘密拦截。
- GitHub Actions 可以手动成功运行，并能在上游无变化时保持仓库不变。
- 最终 Raw 地址可被 Mac 和 iPhone Shadowrocket 读取。创建仓库后，从已登录的 GitHub 账户读取用户名；地址末尾固定为 `/shadowrocket-rules/main/output/my_shadowrocket.conf`。

## 分阶段交付

1. 建立安全的本地仓库骨架，首先验证 `input/` 不会被跟踪。
2. 创建 GitHub Public 仓库并上传不含秘密的骨架。
3. 获取上游配置并在本地生成候选规则。
4. 逐条确认候选规则，形成公开的 `custom_rules.conf`。
5. 构建和验证最终配置。
6. 配置并验证每日 GitHub Actions。
7. 在 Mac 和 iPhone 上验证最终 Raw 订阅地址。
