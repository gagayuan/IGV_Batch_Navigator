#!/usr/bin/env python3
"""
IGV 综合导航器 v4
优化：预生成每批 BAM 的 session XML，切换时单次调用完成清空+加载
依赖: pip install requests
前置: IGV → View → Preferences → Advanced → Enable port (默认 60151)
"""

import requests
import urllib.parse
import sys
import os
import tempfile
import atexit

# ============================================================
#  配置区域：根据需要修改
# ============================================================

IGV_PORT = 60151
GENOME   = "hg38"   # 与 IGV 左上角基因组名称一致

BAM_PATHS = [
    "D:\\suda_qiu\\test_out_dir\\bam_out\\NG211184-1.sorted.markdup.realigned.bqsr.bam",
    "D:\\suda_qiu\\test_out_dir\\bam_out\\NG211184-7.sorted.markdup.realigned.bqsr.bam",
    "D:\\suda_qiu\\test_out_dir\\bam_out\\NG211777-1.sorted.markdup.realigned.bqsr.bam",
    "D:\\suda_qiu\\test_out_dir\\bam_out\\NG211777-2.sorted.markdup.realigned.bqsr.bam",
    "D:\\suda_qiu\\test_out_dir\\bam_out\\NG211777-3.sorted.markdup.realigned.bqsr.bam",
    "D:\\suda_qiu\\test_out_dir\\bam_out\\NG211777-6.sorted.markdup.realigned.bqsr.bam",
    "D:\\suda_qiu\\test_out_dir\\bam_out\\NG211777-7.sorted.markdup.realigned.bqsr.bam",
    "D:\\suda_qiu\\test_out_dir\\bam_out\\NG211857-1.sorted.markdup.realigned.bqsr.bam",
    "D:\\suda_qiu\\test_out_dir\\bam_out\\NG211857-10.sorted.markdup.realigned.bqsr.bam",
    "D:\\suda_qiu\\test_out_dir\\bam_out\\NG211857-8.sorted.markdup.realigned.bqsr.bam",
]

BAM_BATCH_SIZE = 2

POSITION_BATCHES = [
    [
        "chr2:197400802",
        "chr2:197403046",
        "chr2:197418581",
        "chr2:208237181",
        "chr2:208251575",
    ],
    [
        "chr1:36471458",
        "chr1:64844806",
        "chr1:64855705",
        "chr1:64860287",
        "chr2:25799434",
    ],
    [
        "chr2:197393071",
        "chr2:197397953",
        "chr2:197398422",
        "chr2:197400446",
        "chr2:197400449",
    ],
]

# ============================================================
#  以下代码无需修改
# ============================================================

def _make_session_xml(genome: str, bam_paths: list) -> str:
    """为一批 BAM 生成 session XML，写入临时文件，返回路径"""
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
    atexit.register(lambda p=f.name: os.unlink(p) if os.path.exists(p) else None)
    return f.name


def make_bam_batches(paths, batch_size):
    return [paths[i:i + batch_size] for i in range(0, len(paths), batch_size)]


def igv_cmd(command: str, params: dict = None) -> bool:
    url = f"http://localhost:{IGV_PORT}/{command}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    try:
        requests.get(url, timeout=15)
        return True
    except requests.exceptions.ConnectionError:
        print("\n  ✗ 无法连接 IGV，请确认：")
        print(f"    1. IGV 已打开")
        print(f"    2. View → Preferences → Advanced → Enable port 已勾选（端口 {IGV_PORT}）")
        return False
    except Exception as e:
        print(f"\n  ✗ 请求失败：{e}")
        return False


def load_bam_batch(session_file: str) -> bool:
    """单次调用加载整批 BAM（清空旧轨道 + 加载新文件 一步完成）"""
    print("  加载 BAM 批次...", end=" ", flush=True)
    ok = igv_cmd("load", {"file": session_file})
    print("✓" if ok else "✗")
    return ok


def goto_loci(loci: list) -> bool:
    print("  跳转位置...", end=" ", flush=True)
    ok = igv_cmd("goto", {"locus": " ".join(loci)})
    print("✓" if ok else "✗")
    return ok


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


def print_status(bam_idx, bam_batches, pos_idx):
    total_bam = len(bam_batches)
    total_pos = len(POSITION_BATCHES)
    w = 54
    print()
    print("┌" + "─" * w + "┐")
    header = f"  BAM 批次  [{bam_idx + 1}/{total_bam}]"
    print(f"│{header:<{w}}│")
    for path in bam_batches[bam_idx]:
        line = f"    • {sample_name(path)}"
        print(f"│{line:<{w}}│")
    print("│" + " " * w + "│")
    header2 = f"  位置批次  [{pos_idx + 1}/{total_pos}]"
    print(f"│{header2:<{w}}│")
    for loc in POSITION_BATCHES[pos_idx]:
        line = f"    • {loc}"
        print(f"│{line:<{w}}│")
    print("└" + "─" * w + "┘")
    print()
    print("  Enter/n → 下一批位置    p  → 上一批位置")
    print("  nb      → 下一批 BAM    pb → 上一批 BAM")
    print("  r       → 重载当前 BAM  q  → 退出")
    print()


def main():
    bam_batches = make_bam_batches(BAM_PATHS, BAM_BATCH_SIZE)
    total_bam   = len(bam_batches)
    total_pos   = len(POSITION_BATCHES)

    print("=" * 56)
    print("  IGV 综合导航器 v4")
    print(f"  BAM : {len(BAM_PATHS)} 个，每批 {BAM_BATCH_SIZE} 个 → 共 {total_bam} 批")
    print(f"  位置: 共 {total_pos} 批")
    print("=" * 56)

    # ── 启动时预生成所有批次的 session XML（本地操作，极快）──
    print("\n预生成 session 文件...", end=" ", flush=True)
    session_files = [
        _make_session_xml(GENOME, batch) for batch in bam_batches
    ]
    print(f"完成（{total_bam} 个）")

    bam_idx = pos_idx = 0

    print(f"\n初始化：加载第 1 批 BAM...")
    if not load_bam_batch(session_files[0]):
        sys.exit(1)
    goto_loci(POSITION_BATCHES[0])
    print("  ✓ 就绪\n")

    while True:
        print_status(bam_idx, bam_batches, pos_idx)

        try:
            cmd = input("  命令: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n已退出")
            sys.exit(0)

        print()

        if cmd in ("", "n"):
            pos_idx = (pos_idx + 1) % total_pos
            goto_loci(POSITION_BATCHES[pos_idx])

        elif cmd == "p":
            pos_idx = (pos_idx - 1) % total_pos
            goto_loci(POSITION_BATCHES[pos_idx])

        elif cmd == "nb":
            bam_idx = (bam_idx + 1) % total_bam
            pos_idx = 0
            print(f"  → 切换到 BAM 批次 [{bam_idx + 1}/{total_bam}]")
            if load_bam_batch(session_files[bam_idx]):
                goto_loci(POSITION_BATCHES[pos_idx])

        elif cmd == "pb":
            bam_idx = (bam_idx - 1) % total_bam
            pos_idx = 0
            print(f"  → 切换到 BAM 批次 [{bam_idx + 1}/{total_bam}]")
            if load_bam_batch(session_files[bam_idx]):
                goto_loci(POSITION_BATCHES[pos_idx])

        elif cmd == "r":
            print(f"  → 重载 BAM 批次 [{bam_idx + 1}/{total_bam}]")
            if load_bam_batch(session_files[bam_idx]):
                goto_loci(POSITION_BATCHES[pos_idx])

        elif cmd == "q":
            print("已退出")
            sys.exit(0)

        else:
            print(f"  ? 未知命令 '{cmd}'")


if __name__ == "__main__":
    main()