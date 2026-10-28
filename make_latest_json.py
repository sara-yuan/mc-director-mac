#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 Mac 版一键更新 latest.json（白名单清单 + sha256/size 校验）。

用法：
    python make_latest_json.py

说明：
    - 扫描 dist/<VERSION>/ 下文件，按 FILES 白名单生成 latest.json。
    - server.cpython-312-darwin.so 必须来自 Mac 最新一次编译（含授权/更新源码改动），
      本地旧 .so 切勿混入；缺失时会打印告警并跳过，待补齐后重新运行本脚本。
"""
import hashlib
import json
import os
import sys

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
VERSION = "2026.10.18"
REPO = "sara-yuan/mc-director-mac"
DIST = os.path.join(REPO_DIR, "dist", VERSION)

# (文件名, mode)。mode=replace 直接覆盖；后端 .so 在进程退出后 replace 即可（macOS rename 不占用）。
FILES = [
    ("director.html.enc", "replace"),
    ("director_logpopup.html.enc", "replace"),
    ("director_web.html.enc", "replace"),
    ("cloud_path_providers.json", "replace"),
    ("server.cpython-312-darwin.so", "replace"),
    ("_mac_start.py", "replace"),
    ("_app_version.txt", "replace"),
]

REQUIRED = {
    "server.cpython-312-darwin.so",
    "director.html.enc",
    "director_web.html.enc",
    "_app_version.txt",
}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if not os.path.isdir(DIST):
        print("[错误] 缺少 dist 目录：%s" % DIST)
        return 1
    entries = []
    missing = []
    for name, mode in FILES:
        path = os.path.join(DIST, name)
        if not os.path.isfile(path):
            missing.append(name)
            print("[警告] 缺少文件（跳过）：%s" % name)
            continue
        size = os.path.getsize(path)
        digest = sha256_file(path)
        entries.append({"path": name, "sha256": digest, "size": size, "mode": mode})
        print("  %-38s size=%-10d sha=%s" % (name, size, digest))
    if missing and missing[0] in REQUIRED:
        print("\n[注意] 缺少必需文件：%s —— 请从 Mac 取回最新编译产物后重跑本脚本。" % ", ".join(missing))
    manifest = {
        "version": VERSION,
        "channel": "stable",
        "notes": "Mac 云端连接版 %s：授权激活、双击 .app 启动、一键更新（独立更新源）。" % VERSION,
        "base": "https://raw.githubusercontent.com/%s/main/dist/%s/" % (REPO, VERSION),
        "restart": "launcher",
        "oneshot_clean": [],
        "files": entries,
        "comfy_files": [],
        "cloud": None,
    }
    out = os.path.join(REPO_DIR, "latest.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("\n[成功] 已生成 %s（%d 个文件）" % (out, len(entries)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
