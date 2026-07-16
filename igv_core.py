"""
IGV 通信核心模块
从 run.py 提取，供 GUI 客户端直接调用
依赖: pip install requests
前置: IGV → View → Preferences → Advanced → Enable port (默认 60151，可通过 set_port() 修改)
"""

import requests
import urllib.parse
import os
import tempfile
import atexit
import logging
import time
import socket

logger = logging.getLogger(__name__)

IGV_PORT = 60151


def set_port(port: int):
    """更新 IGV 通信端口"""
    global IGV_PORT
    IGV_PORT = port


GENOME = "hg38"

_temp_files = []


def _cleanup():
    for p in _temp_files:
        try:
            if os.path.exists(p):
                os.unlink(p)
        except OSError:
            pass


atexit.register(_cleanup)


def set_genome(genome: str):
    global GENOME
    GENOME = genome


def _make_session_xml(genome: str, bam_paths: list) -> str:
    """生成 IGV session XML（仅包含基因组和 BAM 轨道，附加文件通过独立 load 命令加载）"""
    resources = "\n".join(
        f'        <Resource path="{p}"/>' for p in bam_paths
    )
    xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<Session genome="{genome}" locus="All" version="8">
    <Resources>
{resources}
    </Resources>
</Session>"""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False)
    f.write(xml)
    f.close()
    _temp_files.append(f.name)
    return f.name


def make_bam_batches(paths: list, batch_size: int) -> list:
    if batch_size <= 0:
        return [paths]
    return [paths[i:i + batch_size] for i in range(0, len(paths), batch_size)]


def _igv_request(command: str, params: dict = None) -> str:
    """发送 IGV HTTP 命令，返回响应体文本（如 'OK'）；成功但无响应体（204）也返回 'OK'；网络错误返回 None"""
    url = f"http://localhost:{IGV_PORT}/{command}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    try:
        resp = requests.get(url, timeout=15,
                            proxies={"http": None, "https": None})
        # IGV 的 /load 返回 HTTP 204（无响应体，表示成功）
        # /goto 返回 HTTP 200，响应体为 "OK"
        if resp.ok:
            return resp.text.strip() or "OK"
        return None
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None


def _raw_tcp_cmd(cmd_text: str) -> str:
    """通过原始 TCP socket 发送纯文本命令（和 telnet 一样），返回响应文本"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)
    try:
        s.connect(("127.0.0.1", IGV_PORT))
        s.sendall((cmd_text + "\r\n").encode("utf-8"))
        # IGV 对简单命令返回单行响应，如 "OK" 或 "ERROR ..."
        resp = s.recv(4096).decode("utf-8", errors="replace").strip()
        return resp
    except (socket.timeout, ConnectionRefusedError, OSError):
        return None
    finally:
        s.close()


def igv_cmd(command: str, params: dict = None) -> bool:
    """发送 IGV HTTP 命令，返回 True 表示 IGV 返回了 'OK'"""
    return _igv_request(command, params) == "OK"


def load_bam_batch(bam_paths: list) -> bool:
    """单次调用加载整批 BAM（清空旧轨道 + 加载新文件，一步完成）。附加文件需通过 igv_cmd('load', ...) 单独加载。"""
    logger.info("load_bam_batch: genome=%s, bam_count=%d",
                GENOME, len(bam_paths))
    session_file = _make_session_xml(GENOME, bam_paths)
    return igv_cmd("load", {"file": session_file})


def goto_loci(loci: list) -> bool:
    ok = igv_cmd("goto", {"locus": " ".join(loci)})
    if not ok:
        logger.warning("goto_loci 失败: %d 个位置未成功跳转", len(loci))
    return ok


# ============================================================
# TCP 后处理命令（sort base / collapse 等）
# ============================================================

_TCP_MAX_RETRIES = 6       # 最多尝试 6 次
_TCP_RETRY_DELAY = 0.8     # 每次间隔 0.8 秒


def _send_one_tcp_cmd(cmd: str) -> bool:
    """通过 TCP 发送一条命令，带重试"""
    for attempt in range(1, _TCP_MAX_RETRIES + 1):
        resp = _raw_tcp_cmd(cmd)
        if resp and "OK" in resp:
            logger.info("TCP 命令 '%s' 成功（第 %d 次尝试）", cmd, attempt)
            return True
        if resp is None:
            logger.warning("TCP 命令 '%s' 第 %d 次尝试网络错误", cmd, attempt)
        elif "UNKNOWN" in resp.upper() or "ERROR" in resp.upper():
            logger.error("TCP 命令 '%s' IGV 错误响应: %s", cmd, resp)
            return False
        else:
            logger.warning("TCP 命令 '%s' 第 %d 次响应异常: %s", cmd, attempt, resp)
        if attempt < _TCP_MAX_RETRIES:
            time.sleep(_TCP_RETRY_DELAY)
    logger.error("TCP 命令 '%s' 重试 %d 次后仍未成功", cmd, _TCP_MAX_RETRIES)
    return False


def run_tcp_commands(commands: list) -> bool:
    """
    通过 TCP 依次执行多条命令（如 sort base、collapse all 等），每条带重试。
    IGV 会对当前已加载的全部 track 生效。

    Args:
        commands: 命令字符串列表，如 ["sort base", "collapse all"]
    Returns:
        True 表示所有命令均成功（空列表视为成功）
    """
    if not commands:
        return True
    cmds = [c.strip() for c in commands if c.strip()]
    if not cmds:
        return True
    logger.info("run_tcp_commands: 开始执行 %d 条命令", len(cmds))
    fail_count = 0
    for cmd in cmds:
        if not _send_one_tcp_cmd(cmd):
            fail_count += 1
    logger.info("run_tcp_commands: 完成，成功 %d/%d",
                len(cmds) - fail_count, len(cmds))
    return fail_count == 0


def sample_name(path: str) -> str:
    name = os.path.basename(path)
    for suffix in [
        ".sorted.markdup.realigned.bqsr.bam",
        ".sorted.markdup.bam",
        ".sorted.bam",
        ".bam",
    ]:
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def check_igv_port() -> bool:
    """检测 IGV 端口是否可用（使用当前 IGV_PORT）"""
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect(("127.0.0.1", IGV_PORT))
        return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False
    finally:
        s.close()