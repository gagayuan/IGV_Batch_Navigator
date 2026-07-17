<p align="center">
  <img src="https://img.shields.io/badge/version-V260716-blue" alt="Version">
  <img src="https://img.shields.io/badge/python-3.7+-green" alt="Python">
  <img src="https://img.shields.io/badge/platform-Windows-lightgrey" alt="Platform">
  <img src="https://img.shields.io/badge/license-GPL%20v3-blue" alt="License">
</p>

<details open>
<summary><b>中文</b></summary>

# IGV Batch Navigator — IGV 批量导航器

由**中科苏州智能计算技术研究院**开发，用于批次切换 [IGV](https://igv.org) 的染色体位置和轨道文件，支持 TSV/CSV/XLSX 表格解析、手动输入、样本-BAM 智能匹配（K 关系），大幅加速基因组数据的人工审阅流程。

---

## 目录

- [下载安装](#下载安装)
- [源码构建](#源码构建)
- [使用教程](#使用教程)
  - [准备工作](#准备工作)
  - [位置信息来源](#位置信息来源)
  - [列名设置](#列名设置表格文件模式)
  - [手动输入格式](#手动输入格式)
  - [基因组 / 附加文件](#基因组--附加文件)
  - [轨道文件 BAM](#轨道文件bam)
  - [批次数设置](#批次数设置)
  - [过滤选项](#过滤选项)
  - [后处理命令](#后处理命令tcp)
  - [K 关系（样本-BAM 智能匹配）](#k-关系样本-bam-智能匹配)
  - [导航操作](#导航操作)
  - [运行流程](#运行流程)
- [快捷键](#快捷键)
- [常见问题](#常见问题)
- [联系方式](#联系方式)

---

## 下载安装

前往 [Releases](../../releases) 页面下载最新版 `IGV_Batch_Navigator_V*.exe`，**无需安装，双击即可运行**。

> **要求**：Windows 系统，已安装 [IGV](https://igv.org/doc/desktop/) 桌面版。

---

## 源码构建

```bash
# 1. 安装依赖
pip install pyinstaller PyQt5 requests openpyxl pillow

# 2. 构建 exe
build.bat
```

构建脚本会自动生成版本号（格式 `VYYMMDD`），产物位于 `dist/` 目录。

> 构建使用 PyInstaller 单文件模式（`--onefile --windowed`）。

---

## 使用教程

### 准备工作

1. 打开 IGV，启用端口：**View → Preferences → Advanced → 勾选 "Enable port"**，默认端口 **60151**（可在程序底部「IGV 端口」输入框自定义）。
2. 准备好包含位置信息的表格文件（TSV/CSV/XLSX），或预先整理好位置列表。

### 位置信息来源

**二选一：**

| 模式 | 说明 |
|------|------|
| **表格文件模式（默认）** | 选择 TSV、CSV 或 XLSX 文件。TSV/CSV 不限后缀，程序自动识别分隔符（制表符/逗号）；XLSX 会读取所有 sheet 并拼接。 |
| **手动输入模式** | 勾选「手动输入位置信息」复选框，在文本框中逐行输入位置。 |

### 列名设置（表格文件模式）

| 设置项 | 说明 | 默认值 |
|--------|------|--------|
| **染色体:位置列名** | 包含位置信息的列名，数据格式必须为 `chr:position`（如 `chr1:12345678`） | `CHROM:POS` |
| **样本列名（可选）** | 包含样本名称的列，用于与 BAM 文件建立 K 关系 | `sample` |

### 手动输入格式

- **仅位置**：每行 `chr:position`，如 `chr1:12345678`
- **位置 + 样本**：用 Tab 或逗号分隔，如 `chr1:12345678	sampleA` 或 `chr1:12345678,sampleA`
- 以 `#` 开头的行视为注释，自动跳过

### 基因组 / 附加文件

- 程序启动时自动扫描 `%USERPROFILE%\igv\genomes\*.genome`，列出已下载基因组
- **第一个勾选且识别为基因组的项**（hg38、hg19 或本地 .fa/.fasta/.genome）作为参考基因组
- 其余勾选的文件（.gtf/.gff/.bed/.vcf/.bw 等）作为附加资源加载
- 点击「浏览本地...」添加本地文件，「移除选中」删除列表项

### 轨道文件（BAM）

- 「添加轨道文件」：手动选择 .bam 文件（支持多选）
- 「自动寻找表格文件对应的轨道文件」：从表格路径向上查找 `final_out` 目录，在同级 `bam_out` 目录中扫描所有 .bam 并自动加载（手动输入模式下不可用）
- 「移除选中」/「移除所有」管理轨道列表

### 批次数设置

| 参数 | 说明 | 设为 0 表示 |
|------|------|-------------|
| **位置批次数** | 每个批次包含的位置数 | 全部位置归入一个批次 |
| **轨道批次数** | 每个批次包含的 BAM 数 | 全部轨道归入一个批次 |

> 例：位置批次数=5、轨道批次数=2 → 每个导航网格 = 5 个位置 × 2 个 BAM

### 过滤选项

| 选项 | 位置 | 默认 | 作用 |
|------|------|------|------|
| **过滤无样本对应的轨道** | 轨道批次数下方 | ✅ 勾选 | **解析阶段**从源头丢弃无 K 关系的轨道，精简网格结构 |
| **IGV不展示无位置对应的轨道** | 轨道批次数右侧 | ✅ 勾选 | **导航阶段**在有关网格中仅展示有 K 关系的轨道 |

### 后处理命令（TCP）

- 默认命令：`sort base`（按碱基排序全部轨道）
- 多行可写多条命令，逐条发送
- 点击「命令参考」查看常用 IGV 端口命令
- 重试机制：最多 6 次，间隔 0.8 秒

### K 关系（样本-BAM 智能匹配）

当提供样本列信息时，程序将样本名与 BAM 文件名（去后缀）进行**前缀匹配**：

- 样本 `sampleA` → 匹配 `sampleA.sorted.markdup.bam`

K 关系体现在：

- **绿色 ●**：导航网格中有关网格的标识
- **绿色高亮详情**：有关网格的位置/轨道以绿色加粗显示，附带全局编号和配对对象名
- **对应批次导航**：绿色按钮仅在有关网格间跳转

### 导航操作

| 按钮 | 快捷键 | 功能 |
|------|--------|------|
| ◀ 上一个对应批次 | `Ctrl+,` | 跳转到上一个有关网格 |
| 下一个对应批次 ▶ | `Ctrl+.` | 跳转到下一个有关网格 |
| ◀ 上一个位置批次 | `Ctrl+4` | 前一个位置批次 |
| 下一个位置批次 ▶ | `Ctrl+6` | 后一个位置批次 |
| ◀ 上一个轨道批次 | `Ctrl+8` | 前一个轨道批次 |
| 下一个轨道批次 ▶ | `Ctrl+2` | 后一个轨道批次 |

网格交互：

- **鼠标点击**网格单元格直接跳转
- **方向键**移动活动单元格，**Enter** 确认跳转
- 当前位置以蓝色背景标识

### 运行流程

点击「解析」后：

1. 检查 IGV 端口是否可用
2. 解析位置信息，提取样本信息（如有）
3. 计算 K 关系，生成批次导航网格
4. **首次加载批次**：生成 Session XML，通过 HTTP `/load` 一次性加载基因组 + BAM
5. 加载附加文件（.gtf/.bed/.vcf 等），逐个 HTTP `/load`
6. 通过 HTTP `/goto` 跳转到当前批次位置
7. 延迟执行后处理 TCP 命令（BAM 切换 2.5s，仅位置切换 0.8s）

---

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+,` / `Ctrl+.` | 上/下一个对应批次 |
| `Ctrl+4` / `Ctrl+6` | 上/下一个位置批次 |
| `Ctrl+8` / `Ctrl+2` | 上/下一个轨道批次 |
| `Ctrl+L` | 打开运行日志查看器 |

---

## 常见问题

1. **IGV 无响应**：检查 IGV 端口是否已启用（View → Preferences → Advanced → Enable port），确认程序底部端口号一致。
2. **解析失败**：检查列名是否与表头完全一致（区分大小写），数据格式是否为 `chr:position`。
3. **同一轨道批次内切换位置**：不会重新加载 BAM，仅刷新 goto 位置，速度更快。
4. **样本列存在但无 K 关系**：检查样本名是否为 BAM 文件名的前缀（大小写不敏感）。`sampleA` 可匹配 `sampleA.sorted.bam`，不能匹配 `mysampleA.bam`。
5. **基因组加载缓慢**：IGV 首次使用 hg19/hg38 会自动下载，建议提前下载或使用本地文件。
6. **手动输入模式下自动寻找轨道不可用**：无表格文件路径，请手动添加轨道文件。
7. **批次数设为 0**：0 = 全部，位置 0 = 所有位置一个批次，轨道 0 = 所有轨道一个批次。

---

## 联系方式

有任何问题或者有新的需求合作意向请联系 **中科苏州智能计算技术研究院 徐锡** — [xuxi@iict.ac.cn](mailto:xuxi@iict.ac.cn)

</details>

<details>
<summary><b>English</b></summary>

# IGV Batch Navigator

Developed by **Institute of Intelligent Computing Technology, Suzhou, CAS (IICT)**, this tool switches [IGV](https://igv.org) chromosome loci and track files in batches. It supports TSV/CSV/XLSX table parsing, manual input, and sample-BAM smart matching (K-relation), significantly accelerating manual review of genomic data.

---

## Table of Contents

- [Download](#download)
- [Build from Source](#build-from-source)
- [Usage Guide](#usage-guide)
  - [Preparation](#preparation)
  - [Locus Source](#locus-source)
  - [Column Settings](#column-settings-table-mode)
  - [Manual Input Format](#manual-input-format)
  - [Genome / Additional Files](#genome--additional-files)
  - [Track Files (BAM)](#track-files-bam)
  - [Batch Size Settings](#batch-size-settings)
  - [Filter Options](#filter-options)
  - [Post-processing Commands (TCP)](#post-processing-commands-tcp)
  - [K-Relation (Sample-BAM Smart Matching)](#k-relation-sample-bam-smart-matching)
  - [Navigation](#navigation)
  - [Workflow](#workflow)
- [Shortcuts](#shortcuts)
- [FAQ](#faq)
- [Contact](#contact)

---

## Download

Go to the [Releases](../../releases) page and download the latest `IGV_Batch_Navigator_V*.exe`. **No installation required — just double-click to run.**

> **Requirement**: Windows OS with [IGV Desktop](https://igv.org/doc/desktop/) installed.

---

## Build from Source

```bash
# 1. Install dependencies
pip install pyinstaller PyQt5 requests openpyxl pillow

# 2. Build
build.bat
```

The build script auto-generates a version number (format `VYYMMDD`). The executable is placed in the `dist/` directory.

> Uses PyInstaller single-file mode (`--onefile --windowed`).

---

## Usage Guide

### Preparation

1. Open IGV and enable the port: **View → Preferences → Advanced → Check "Enable port"**, default port is **60151** (customizable in the "IGV Port" field at the bottom).
2. Prepare a table file with position information (TSV/CSV/XLSX), or organize a position list in advance.

### Locus Source

**Choose one:**

| Mode | Description |
|------|-------------|
| **Table File Mode (default)** | Select TSV, CSV, or XLSX file. TSV/CSV files auto-detect delimiter (tab/comma); XLSX reads all sheets and concatenates results. |
| **Manual Input Mode** | Check "Enter positions manually"; positions are entered line by line in the text box. |

### Column Settings (Table Mode)

| Setting | Description | Default |
|---------|-------------|---------|
| **Chr:Pos Column Name** | Column containing position info, in `chr:position` format (e.g. `chr1:12345678`) | `CHROM:POS` |
| **Sample Column Name (optional)** | Column containing sample names, used for K-relation with BAM files | `sample` |

### Manual Input Format

- **Position only**: One `chr:position` per line, e.g. `chr1:12345678`
- **Position + Sample**: Tab or comma separated, e.g. `chr1:12345678	sampleA` or `chr1:12345678,sampleA`
- Lines starting with `#` are treated as comments and skipped

### Genome / Additional Files

- Auto-scans `%USERPROFILE%\igv\genomes\*.genome` on startup, listing all downloaded genomes
- **First checked item recognized as a genome** (hg38, hg19, or local .fa/.fasta/.genome) serves as the reference genome
- Other checked files (.gtf/.gff/.bed/.vcf/.bw, etc.) are loaded as additional resources
- "Browse Local..." to add files; "Remove Selected" to delete items

### Track Files (BAM)

- "Add Track Files": manually select .bam files (multi-select supported)
- "Auto-Find Tracks for Table": searches upward from the table path for a `final_out` directory, then scans the sibling `bam_out` directory for all .bam files and auto-loads them (not available in manual input mode)
- "Remove Selected" / "Remove All" to manage the track list

### Batch Size Settings

| Parameter | Description | 0 means |
|-----------|-------------|---------|
| **Position Batch Size** | Positions per batch | All positions in one batch |
| **Track Batch Size** | BAM files per batch | All tracks in one batch |

> Example: Position=5, Track=2 → each grid cell = 5 positions × 2 BAM tracks

### Filter Options

| Option | Location | Default | Effect |
|--------|----------|---------|--------|
| **Filter tracks w/o matching samples** | Below track batch size | ✅ On | **Parsing stage**: discards tracks without K-relations from pipeline |
| **Hide tracks w/o matching loci in IGV** | Right of track batch size | ✅ On | **Navigation stage**: only shows tracks with K-relations in relevant grids |

### Post-processing Commands (TCP)

- Default command: `sort base` (sorts all tracks by base)
- Multiple lines = multiple commands, sent sequentially
- Click "Cmd Reference" to view common IGV port commands
- Retry mechanism: up to 6 attempts, 0.8s intervals

### K-Relation (Sample-BAM Smart Matching)

When sample column info is provided, the program performs **prefix matching** between sample names and BAM filenames (without extension):

- Sample `sampleA` → matches `sampleA.sorted.markdup.bam`

K-relations are reflected in:

- **Green ●**: indicator on relevant grids in the navigation matrix
- **Green highlighted details**: positions/tracks with K-relations shown in green bold with global numbers and paired object names
- **Relevant batch navigation**: green buttons jump only between relevant grids

### Navigation

| Button | Shortcut | Function |
|--------|----------|----------|
| ◀ Prev Relevant Batch | `Ctrl+,` | Jump to previous grid with K-relation |
| Next Relevant Batch ▶ | `Ctrl+.` | Jump to next grid with K-relation |
| ◀ Prev Position Batch | `Ctrl+4` | Previous position batch |
| Next Position Batch ▶ | `Ctrl+6` | Next position batch |
| ◀ Prev Track Batch | `Ctrl+8` | Previous track batch |
| Next Track Batch ▶ | `Ctrl+2` | Next track batch |

Grid interaction:

- **Mouse click** on a grid cell navigates directly
- **Arrow keys** move the active cell, **Enter** confirms navigation
- Current position highlighted with blue background

### Workflow

After clicking "Parse":

1. Check if IGV port is available
2. Parse locus information, extract sample info (if any)
3. Compute K-relations and generate batch navigation grid
4. **First-time batch load**: generate Session XML, load genome + BAM via HTTP `/load`
5. Load additional files (.gtf/.bed/.vcf, etc.) via individual HTTP `/load`
6. Navigate to current batch positions via HTTP `/goto`
7. Execute post-processing TCP commands after delay (2.5s on BAM switch, 0.8s on position-only switch)

---

## Shortcuts

| Shortcut | Function |
|----------|----------|
| `Ctrl+,` / `Ctrl+.` | Prev/Next relevant batch |
| `Ctrl+4` / `Ctrl+6` | Prev/Next position batch |
| `Ctrl+8` / `Ctrl+2` | Prev/Next track batch |
| `Ctrl+L` | Open run log viewer |

---

## FAQ

1. **IGV not responding**: Check if IGV port is enabled (View → Preferences → Advanced → Enable port) and the port matches.
2. **Parse failed**: Check column names match table headers exactly (case-sensitive), data format is `chr:position`.
3. **Switching positions within same track batch**: BAM files are NOT reloaded; only goto is refreshed, making it faster.
4. **Sample column exists but no K-relation**: Check if sample name is a prefix of BAM filename (case-insensitive). `sampleA` matches `sampleA.sorted.bam` but NOT `mysampleA.bam`.
5. **Slow genome loading**: IGV auto-downloads hg19/hg38 on first use; pre-download or use local files.
6. **Auto-find tracks unavailable in manual input mode**: No table file path; add track files manually.
7. **Batch size 0**: 0 = all; position 0 = all positions in one batch, track 0 = all tracks in one batch.

---

## Contact

For any questions or new collaboration inquiries, contact **Xu Xi, Institute of Intelligent Computing Technology, Suzhou, CAS (IICT)** — [xuxi@iict.ac.cn](mailto:xuxi@iict.ac.cn)

</details>