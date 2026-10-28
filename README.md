# Mac 版一键更新仓库（准备中，未公开）

> 对应 GitHub 仓库：`sara-yuan/mc-director-mac`（需你先在 GitHub 建库；建好后我把本目录推上去，等你确认后再公开）。

## 目录结构
```
latest.json                     # 更新清单（版本/文件/校验）
dist/2026.10.18/                # 本次更新文件（全部就绪）
  director.html.enc             # 导演台前端（Mac 版）
  director_logpopup.html.enc    # 日志弹窗前端
  director_web.html.enc         # 手机监控前端
  cloud_path_providers.json     # 云端镜像/路径配置
  _mac_start.py                 # Mac 后端入口脚本
  _app_version.txt              # 当前版本号（2026.10.18）
  server.cpython-312-darwin.so  # Mac 后端（已含授权 + POSIX 更新机制）
make_latest_json.py             # 重新计算 sha256/size 并生成 latest.json
```

## 状态
- 全部 7 个文件就绪，sha256/size 已写入 latest.json。
- 一键更新机制已移植 macOS：进程结束（lsof/kill）、启动器定位与重启（.command/.app）、后端文件名（.so）、进程拉起（start_new_session）均已做 POSIX 分支，`/api/app/update/check` 在 Mac 上返回 supported=true。

## 待办
- 你在 GitHub 建库 `sara-yuan/mc-director-mac` 后，我推送本目录，等你确认再公开。
