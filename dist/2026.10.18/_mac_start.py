#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""墨川导演台 · macOS 启动引导（仅连接云端）

只启动导演台网页服务：不启动本地 ComfyUI、不加载本地模型。
推理走「云部署」页里配置的云端 ComfyUI（SSH 隧道转发）。
"""
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
os.chdir(str(HERE))
sys.path.insert(0, str(HERE))

CONF_CANDIDATES = [
    HERE.parent.parent / "云端配置.txt",
    HERE.parent / "云端配置.txt",
    HERE / "云端配置.txt",
]


def _read_conf():
    for path in CONF_CANDIDATES:
        try:
            if not path.is_file():
                continue
            data = {}
            for raw in path.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                if key:
                    data[key] = value
            return data
        except OSError:
            continue
    return {}


def main():
    conf = _read_conf()
    for key, value in conf.items():
        if key.isupper() and value:
            os.environ.setdefault(key, value)
    os.environ.setdefault("DIRECTOR_MANAGE_COMFY", "0")
    os.environ.setdefault("DIRECTOR_LICENSE_BYPASS", "0")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    os.environ.setdefault("PYTHONUTF8", "1")

    # macOS: python.org 的 Python 若未运行过 Install Certificates.command，会缺 CA 证书，
    # 导致 HTTPS（DeepSeek/Ollama 等）报 CERTIFICATE_VERIFY_FAILED。用 certifi 兜底。
    try:
        import ssl as _ssl
        import certifi as _certifi
        _cafile = _ssl.get_default_verify_paths().cafile
        if not _cafile or not os.path.exists(_cafile):
            os.environ["SSL_CERT_FILE"] = _certifi.where()
    except Exception:
        pass

    for rel in ("ComfyUI/output", "ComfyUI/input", "ComfyUI/models", "icon",
                "web_frontend_compiled/director_uploads", "web_frontend_compiled/director_frames"):
        try:
            (HERE.parent / rel).mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
    for rel in ("director_uploads", "director_frames", "mv_cache", "director_backups"):
        try:
            (HERE / rel).mkdir(parents=True, exist_ok=True)
        except OSError:
            pass

    try:
        import server
    except Exception as exc:  # noqa: BLE001
        print("[director] 后端加载失败：" + repr(exc), flush=True)
        raise

    try:
        server.FRONTEND_PORT = int(os.environ.get("FRONTEND_PORT") or 8199)
    except (TypeError, ValueError):
        pass

    print("[director] macOS 云端连接版：不启动本地 ComfyUI", flush=True)
    print("[director] 云端 ComfyUI 请在「云部署」页配置并连接", flush=True)
    server.mac_launch()


if __name__ == "__main__":
    main()
