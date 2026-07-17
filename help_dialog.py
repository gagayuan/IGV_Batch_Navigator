"""
帮助对话框
显示使用说明文档 (支持中英文双语)
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QDialogButtonBox

from i18n import T, LANG
from version import VERSION


class HelpDialog(QDialog):
    def __init__(self, parent=None, lang='zh'):
        super().__init__(parent)
        self._lang = lang
        self._browser = None
        self._build_html_strings()
        self.setWindowTitle(T('help_title'))
        self.setMinimumSize(640, 560)
        self.resize(700, 620)
        self._init_ui()

    def _build_html_strings(self):
        # ── 中文 HTML ──
        self._html_zh = f"""
<h2>IGV 批量导航器 {VERSION}</h2>
<p>本工具由<strong>中科苏州智能计算技术研究院</strong>开发，用于批次切换 IGV 的染色体位置和轨道文件，
支持 TSV/CSV/XLSX 表格解析、手动输入、样本-BAM 智能匹配（K 关系），大幅加速基因组数据的人工审阅流程。</p>

<h3>准备工作</h3>
<ol>
  <li>打开 IGV，确保端口已启用：<b>View → Preferences → Advanced → 勾选 "Enable port"</b>，端口号默认为 <b>60151</b>（可在程序底部"IGV 端口"输入框中自定义）。</li>
  <li>准备好包含位置信息的表格文件（TSV/CSV/XLSX），或者预先整理好位置列表。</li>
</ol>

<h3>参数说明</h3>

<h4>位置信息来源（二选一）</h4>
<ul>
  <li><b>表格文件模式（默认）</b>：选择 TSV、CSV 或 XLSX 格式的表格文件。TSV/CSV 文件不限后缀，程序自动识别分隔符（制表符/逗号）；XLSX 文件会读取所有 sheet 并拼接结果。</li>
  <li><b>手动输入模式</b>：勾选"手动输入位置信息"复选框，表格文件与列名行自动隐藏，在文本框中逐行输入位置。</li>
</ul>

<h4>列名设置（表格文件模式，适用于 TSV/CSV/XLSX）</h4>
<ul>
  <li><b>染色体:位置列名</b>：表格中包含位置信息的列名，该列数据格式必须为 <code>染色体:位置</code>（如 <code>chr1:12345678</code>）。默认值 <code>CHROM:POS</code>，支持持久化。</li>
  <li><b>样本列名（可选）</b>：表格中包含样本名称的列，用于与 BAM 轨道文件建立 K 关系（见下文）。默认值 <code>sample</code>，支持持久化。如果留空或表格中不存在该列，则样本功能关闭。</li>
</ul>

<h4>手动输入格式</h4>
<ul>
  <li><b>仅位置</b>：每行 <code>染色体:位置</code>，如 <code>chr1:12345678</code>。</li>
  <li><b>位置 + 样本</b>：用制表符（Tab）或逗号分隔，如 <code>chr1:12345678 sampleA</code> 或 <code>chr1:12345678,sampleA</code>。
  程序根据首行自动判断是否包含样本列。</li>
  <li>以 <code>#</code> 开头的行视为注释，自动跳过。</li>
</ul>

<h4>基因组 / 附加文件</h4>
<ul>
  <li>程序启动时自动扫描 <code>%USERPROFILE%\\igv\\genomes\\*.genome</code> 目录，列出所有已下载基因组。</li>
  <li>列表中 <b>第一个被勾选且识别为基因组的项</b>（内置名称如 hg38、hg19，或本地 .fa / .fasta / .genome 文件）将作为参考基因组传给 IGV。</li>
  <li>其余勾选的文件（.gtf、.gff、.bed、.vcf、.bw、.bigwig 等）作为附加资源加载到 IGV 中。</li>
  <li>点击 <b>"浏览本地..."</b> 可添加本地基因组或附加文件；<b>"移除选中"</b> 可删除列表中的项。</li>
  <li>勾选状态和列表顺序均持久化，下次启动自动恢复。</li>
</ul>

<h4>轨道文件（BAM）</h4>
<ul>
  <li>点击 <b>"添加轨道文件"</b> 手动选择 .bam 文件（支持多选）。</li>
  <li>点击 <b>"自动寻找表格文件对应的轨道文件"</b>，程序会从表格文件所在路径向上查找 <code>final_out</code> 目录，然后在其同级 <code>bam_out</code> 目录中扫描所有 .bam 文件并自动加载。
  此功能在手动输入模式下不可用。</li>
  <li><b>"移除选中"</b> 可删除轨道文件列表中的选中项；<b>"移除所有"</b> 可一键清空全部轨道文件。</li>
</ul>

<h4>批次数设置</h4>
<ul>
  <li><b>位置批次数</b>：每个位置批次包含多少个位置。设为 <b>0</b> 代表所有位置归入一个批次。</li>
  <li><b>轨道批次数</b>：每个轨道批次包含多少个 BAM 文件。设为 <b>0</b> 代表所有轨道归入一个批次。</li>
  <li>例如：位置批次数=5、轨道批次数=2 → 每个导航网格单元格包含 5 个位置 × 2 个 BAM 轨道。</li>
</ul>

<h4>过滤无样本对应的轨道（勾选框）</h4>
<ul>
  <li>位于<b>轨道批次数</b>和"IGV不展示无位置对应的轨道"之间，<b>默认勾选</b>。</li>
  <li><b>勾选时</b>：K 关系计算完成后，程序直接<b>丢弃</b>所有不存在 K 关系的轨道文件，后续的批次划分、导航网格、IGV 加载等全部仅基于有 K 关系的轨道进行。未被任何样本匹配的 BAM 文件从流程中彻底移除。</li>
  <li><b>取消勾选时</b>：所有添加的轨道文件均参与下游处理（与旧版行为一致）。</li>
  <li>与"IGV不展示无位置对应的轨道"的区别：前者在<b>解析阶段</b>从源头剔除无关轨道；后者在<b>导航阶段</b>按网格过滤展示和加载。</li>
  <li>适用场景：轨道文件数量庞大但仅有少数与样本相关时，可大幅精简网格结构和 IGV 加载的复杂度。</li>
</ul>

<h4>IGV不展示无位置对应的轨道（勾选框）</h4>
<ul>
  <li>位于<b>轨道批次数</b>输入框右侧，<b>默认勾选</b>。</li>
  <li><b>勾选时</b>：在导航到<b>有关网格</b>（带绿色 "●" 的网格）时，IGV 仅加载和展示该网格中存在 K 关系的轨道文件，无匹配关系的轨道被忽略；下方<b>轨道批次详情</b>区域也仅显示有 K 关系的轨道。</li>
  <li><b>取消勾选时</b>：恢复原有行为——每个网格中全部轨道文件完整加载到 IGV，详情区域也显示全部轨道（有 K 关系的以绿色标识，无关系的以普通样式显示）。</li>
  <li>该设置<b>仅影响有关网格</b>，对无关网格（无 K 关系的网格）无效果。</li>
  <li>适用场景：当样本较多、轨道文件复杂时，勾选此选项可以减少无关轨道的干扰，使 IGV 界面更加整洁，聚焦于与当前位置存在匹配关系的样本。</li>
</ul>

<h4>后处理命令（TCP）</h4>
<ul>
  <li>在轨道和位置加载完成后，通过原始 TCP 协议向 IGV 发送命令。</li>
  <li>默认命令：<code>sort base</code>（按碱基排序全部轨道）。多行可写多条命令，逐条发送。</li>
  <li>点击 <b>"命令参考"</b> 查看常用 IGV 端口命令列表。</li>
  <li>命令执行带重试机制（最多 6 次，间隔 0.8 秒）。</li>
</ul>

<h3>K 关系（样本-BAM 智能匹配）</h3>
<p>当提供样本列信息时，程序会将每个位置所在行的<b>样本名</b>与所有 BAM 文件的<b>文件名（去后缀）</b>进行前缀匹配：</p>
<ul>
  <li>样本名 <code>sampleA</code> 可匹配 BAM 文件 <code>sampleA.sorted.markdup.bam</code>。</li>
  <li>匹配成功后建立 <b>K 关系</b>：位置 ↔ BAM 轨道文件。</li>
</ul>
<p>K 关系体现在以下几个方面：</p>
<ul>
  <li><b>绿色圆圈</b>：导航网格中，至少包含一条 K 关系的单元格会显示一个绿色 "●" 标识，称为<b>"有关网格"</b>。无关网格不显示。</li>
  <li><b>绿色高亮详情</b>：选中有关网格时，下方位置/轨道详情区域中，具有 K 关系的位置和轨道以<b>绿色加粗</b>显示，并附带全局编号（如 (1)、(2)），以及配对对象的名称，方便快速定位。</li>
  <li><b>对应批次导航</b>：两个绿色按钮"上一个对应批次"/"下一个对应批次"仅在有关网格之间跳转，自动跳过无关网格。无样本列或无 K 关系时按钮禁用。</li>
</ul>

<h3>导航操作</h3>

<h4>六按钮导航</h4>
<table border="1" cellpadding="4" cellspacing="0" style="border-collapse:collapse;">
<tr><th>按钮</th><th>快捷键</th><th>功能</th></tr>
<tr><td>◀ 上一个对应批次</td><td><b>Ctrl+&lt;</b></td><td>跳转到上一个有关网格（跳过无关网格）</td></tr>
<tr><td>下一个对应批次 ▶</td><td><b>Ctrl+&gt;</b></td><td>跳转到下一个有关网格（跳过无关网格）</td></tr>
<tr><td>◀ 上一个位置批次</td><td><b>Ctrl+4</b></td><td>切换位置批次（前一个），到边界时切换轨道批次并回绕</td></tr>
<tr><td>下一个位置批次 ▶</td><td><b>Ctrl+6</b></td><td>切换位置批次（后一个），到边界时切换轨道批次并回绕</td></tr>
<tr><td>◀ 上一个轨道批次</td><td><b>Ctrl+8</b></td><td>切换轨道批次（前一个），循环</td></tr>
<tr><td>下一个轨道批次 ▶</td><td><b>Ctrl+2</b></td><td>切换轨道批次（后一个），循环</td></tr>
</table>
<p>六个按钮与原有四个按钮功能互相配合，可任意组合使用。</p>

<h4>网格交互</h4>
<ul>
  <li><b>鼠标点击</b>网格单元格直接跳转到对应批次。</li>
  <li><b>方向键</b>移动活动单元格（到达行末/行首可换行），<b>Enter</b> 确认跳转。</li>
  <li>当前位置以蓝色背景标识。</li>
</ul>

<h4>其他快捷键</h4>
<ul>
  <li><b>Ctrl+L</b> — 打开运行日志查看器，查看程序运行状态和 IGV 通信日志。</li>
</ul>

<h3>运行流程（点击"解析"后）</h3>
<ol>
  <li>检查 IGV 端口是否可用（端口号可在程序底部"IGV 端口"输入框设置，需与 IGV 中一致）。</li>
  <li>解析位置信息（表格或手动输入），提取样本信息（如有）。</li>
  <li>计算 K 关系并生成批次导航网格。</li>
  <li><b>首次加载批次</b>：生成 IGV Session XML（仅含参考基因组 + BAM 轨道），通过 HTTP <code>/load</code> 一次性加载。</li>
  <li>加载附加文件（.gtf/.bed/.vcf 等）通过独立 HTTP <code>/load</code> 命令逐个加载。</li>
  <li>通过 HTTP <code>/goto</code> 跳转到当前批次的位置列表。</li>
  <li>延迟执行后处理 TCP 命令（BAM 切换时延迟 2.5 秒，仅位置切换时延迟 0.8 秒）。</li>
</ol>

<h3>常见问题</h3>
<ul>
  <li><b>IGV 无响应</b>：检查 IGV 端口是否已启用（View → Preferences → Advanced → Enable port），并确认端口号与程序底部"IGV 端口"设置一致。</li>
  <li><b>解析失败</b>：检查列名是否与表格表头完全一致（区分大小写），数据格式是否为 <code>chr:position</code>。TSV/CSV 文件注意分隔符是否正确；XLSX 文件注意数据是否分布在多个 sheet 中（程序会自动读取全部 sheet）。</li>
  <li><b>同一轨道批次内切换位置</b>：不会重新加载 BAM 文件，仅刷新 goto 位置，速度更快。</li>
  <li><b>样本列存在但无 K 关系</b>：检查样本名是否为 BAM 文件名的前缀（大小写不敏感）。例如样本名 <code>sampleA</code> 可匹配 <code>sampleA.sorted.bam</code>，但不能匹配 <code>mysampleA.bam</code>。</li>
  <li><b>基因组加载缓慢</b>：IGV 首次使用 hg19/hg38 会自动下载，建议提前在 IGV 中下载所需基因组，或使用本地 .fa/.genome 文件。</li>
  <li><b>手动输入模式下自动寻找轨道文件不可用</b>：因为没有表格文件路径，无法定位目录结构，请手动添加轨道文件。</li>
  <li><b>批次数设为 0 的含义</b>：0 = 全部，位置 0 表示所有位置一个批次，轨道 0 表示所有轨道一个批次。</li>
</ul>

<hr>
<p style="color:#888;">
  有问题请联系 中科苏州智能计算技术研究院 徐锡 <a href="mailto:xuxi@iict.ac.cn">xuxi@iict.ac.cn</a>
</p>
"""

        # ── 英文 HTML ──
        self._html_en = f"""
<h2>IGV Batch Navigator {VERSION}</h2>
<p>Developed by <strong>Institute of Intelligent Computing Technology, Suzhou, CAS (IICT)</strong>,
this tool switches IGV chromosome loci and track files in batches.
It supports TSV/CSV/XLSX table parsing, manual input, and sample-BAM smart matching (K-relation),
significantly accelerating manual review of genomic data.</p>

<h3>Preparation</h3>
<ol>
  <li>Open IGV and ensure the port is enabled: <b>View → Preferences → Advanced → Check "Enable port"</b>, default port is <b>60151</b> (can be customized in the "IGV Port" field at the bottom).</li>
  <li>Prepare a table file containing position information (TSV/CSV/XLSX), or organize a position list in advance.</li>
</ol>

<h3>Parameter Description</h3>

<h4>Locus Source (Choose One)</h4>
<ul>
  <li><b>Table File Mode (default)</b>: Select a table file in TSV, CSV, or XLSX format. TSV/CSV files have no extension restriction; the program auto-detects the delimiter (tab/comma). XLSX files read all sheets and concatenate results.</li>
  <li><b>Manual Input Mode</b>: Check "Enter positions manually" checkbox; the table file and column name rows are hidden, and positions are entered line by line in the text box.</li>
</ul>

<h4>Column Name Settings (Table File Mode, for TSV/CSV/XLSX)</h4>
<ul>
  <li><b>Chr:Pos Column Name</b>: The column name in the table that contains position information. The data in this column must be in <code>chr:position</code> format (e.g. <code>chr1:12345678</code>). Default value: <code>CHROM:POS</code>, supports persistence.</li>
  <li><b>Sample Column Name (optional)</b>: The column name in the table that contains sample names, used to establish K-relations with BAM track files (see below). Default value: <code>sample</code>, supports persistence. If left empty or the column does not exist in the table, the sample feature is disabled.</li>
</ul>

<h4>Manual Input Format</h4>
<ul>
  <li><b>Position only</b>: One <code>chr:position</code> per line, e.g. <code>chr1:12345678</code>.</li>
  <li><b>Position + Sample</b>: Separated by tab or comma, e.g. <code>chr1:12345678 sampleA</code> or <code>chr1:12345678,sampleA</code>.
  The program automatically determines whether a sample column is present based on the first line.</li>
  <li>Lines starting with <code>#</code> are treated as comments and skipped.</li>
</ul>

<h4>Genome / Additional Files</h4>
<ul>
  <li>On startup, the program automatically scans <code>%USERPROFILE%\\igv\\genomes\\*.genome</code> and lists all downloaded genomes.</li>
  <li>The <b>first checked item recognized as a genome</b> (built-in names such as hg38, hg19, or local .fa / .fasta / .genome files) will be used as the reference genome passed to IGV.</li>
  <li>Other checked files (.gtf, .gff, .bed, .vcf, .bw, .bigwig, etc.) are loaded into IGV as additional resources.</li>
  <li>Click <b>"Browse Local..."</b> to add local genome or additional files; <b>"Remove Selected"</b> to delete items from the list.</li>
  <li>Check states and list order are persisted and restored on next startup.</li>
</ul>

<h4>Track Files (BAM)</h4>
<ul>
  <li>Click <b>"Add Track Files"</b> to manually select .bam files (multi-select supported).</li>
  <li>Click <b>"Auto-Find Tracks for Table"</b>; the program searches upward from the table file path to locate the <code>final_out</code> directory, then scans its sibling <code>bam_out</code> directory for all .bam files and loads them automatically.
  This feature is not available in manual input mode.</li>
  <li><b>"Remove Selected"</b> deletes checked items from the track file list; <b>"Remove All"</b> clears all track files at once.</li>
</ul>

<h4>Batch Size Settings</h4>
<ul>
  <li><b>Position Batch Size</b>: How many loci per position batch. Set to <b>0</b> to put all positions in one batch.</li>
  <li><b>Track Batch Size</b>: How many BAM files per track batch. Set to <b>0</b> to put all tracks in one batch.</li>
  <li>Example: Position batch size=5, Track batch size=2 → each navigation grid cell contains 5 positions × 2 BAM tracks.</li>
</ul>

<h4>Filter Tracks Without Matching Samples (Checkbox)</h4>
<ul>
  <li>Located between <b>Track Batch Size</b> and "Hide tracks w/o matching locus in IGV", <b>checked by default</b>.</li>
  <li><b>When checked</b>: After K-relation computation, the program directly <b>discards</b> all track files without K-relations. Subsequent batch division, navigation grid, IGV loading, etc. are all based solely on tracks with K-relations. BAM files not matched by any sample are completely removed from the pipeline.</li>
  <li><b>When unchecked</b>: All added track files participate in downstream processing (same as legacy behavior).</li>
  <li>Difference from "Hide tracks w/o matching locus in IGV": the former removes irrelevant tracks at the <b>parsing stage</b> from the source; the latter filters display and loading by grid at the <b>navigation stage</b>.</li>
  <li>Use case: When there is a large number of track files but only a few are related to samples, this greatly simplifies the grid structure and IGV loading complexity.</li>
</ul>

<h4>Hide Tracks Without Matching Loci in IGV (Checkbox)</h4>
<ul>
  <li>Located to the right of the <b>Track Batch Size</b> input field, <b>checked by default</b>.</li>
  <li><b>When checked</b>: When navigating to a <b>relevant grid</b> (grid with a green "●"), IGV only loads and displays track files with K-relations in that grid; tracks without matching relationships are ignored. The <b>Track Batch Details</b> area below also only shows tracks with K-relations.</li>
  <li><b>When unchecked</b>: Restores original behavior — all track files in each grid are fully loaded into IGV, and the details area also shows all tracks (those with K-relations are highlighted in green, those without are shown in normal style).</li>
  <li>This setting <b>only affects relevant grids</b>; it has no effect on irrelevant grids (grids without K-relations).</li>
  <li>Use case: When there are many samples and complex track files, checking this option reduces interference from irrelevant tracks, keeping the IGV interface cleaner and focused on samples matching the current position.</li>
</ul>

<h4>Post-processing Commands (TCP)</h4>
<ul>
  <li>After track and position loading completes, send commands to IGV via raw TCP protocol.</li>
  <li>Default command: <code>sort base</code> (sorts all tracks by base). Multiple lines can contain multiple commands, sent one by one.</li>
  <li>Click <b>"Cmd Reference"</b> to view common IGV port command list.</li>
  <li>Command execution includes a retry mechanism (up to 6 attempts, 0.8-second intervals).</li>
</ul>

<h3>K-Relation (Sample-BAM Smart Matching)</h3>
<p>When sample column information is provided, the program performs prefix matching between the <b>sample name</b> in each position's row and the <b>filename (without extension)</b> of all BAM files:</p>
<ul>
  <li>Sample name <code>sampleA</code> can match BAM file <code>sampleA.sorted.markdup.bam</code>.</li>
  <li>Upon successful matching, a <b>K-relation</b> is established: locus ↔ BAM track file.</li>
</ul>
<p>K-relations are reflected in the following aspects:</p>
<ul>
  <li><b>Green circles</b>: In the navigation grid, cells containing at least one K-relation display a green "●" indicator, called <b>"relevant grids"</b>. Irrelevant grids do not show this indicator.</li>
  <li><b>Green highlighted details</b>: When a relevant grid is selected, positions and tracks with K-relations in the details area below are displayed in <b>green bold</b>, with global numbers (e.g. (1), (2)) and paired object names for quick identification.</li>
  <li><b>Relevant batch navigation</b>: The two green buttons "Prev Relevant Batch" / "Next Relevant Batch" jump only between relevant grids, automatically skipping irrelevant grids. Buttons are disabled when there is no sample column or no K-relations.</li>
</ul>

<h3>Navigation</h3>

<h4>Six-Button Navigation</h4>
<table border="1" cellpadding="4" cellspacing="0" style="border-collapse:collapse;">
<tr><th>Button</th><th>Shortcut</th><th>Function</th></tr>
<tr><td>◀ Prev Relevant Batch</td><td><b>Ctrl+,</b></td><td>Jump to previous grid with K-relation</td></tr>
<tr><td>Next Relevant Batch ▶</td><td><b>Ctrl+.</b></td><td>Jump to next grid with K-relation</td></tr>
<tr><td>◀ Prev Position Batch</td><td><b>Ctrl+4</b></td><td>Previous position batch (wraps with track batch at boundary)</td></tr>
<tr><td>Next Position Batch ▶</td><td><b>Ctrl+6</b></td><td>Next position batch (wraps with track batch at boundary)</td></tr>
<tr><td>◀ Prev Track Batch</td><td><b>Ctrl+8</b></td><td>Previous track batch (cycles)</td></tr>
<tr><td>Next Track Batch ▶</td><td><b>Ctrl+2</b></td><td>Next track batch (cycles)</td></tr>
</table>
<p>The six buttons work together with the original four button functions and can be used in any combination.</p>

<h4>Grid Interaction</h4>
<ul>
  <li><b>Mouse click</b> on a grid cell directly navigates to that batch position.</li>
  <li><b>Arrow keys</b> move the active cell (wrap at row end/start), <b>Enter</b> confirms navigation.</li>
  <li>Current position is highlighted with a blue background.</li>
</ul>

<h4>Other Shortcuts</h4>
<ul>
  <li><b>Ctrl+L</b> — Open the run log viewer to inspect program status and IGV communication logs.</li>
</ul>

<h3>Workflow (After Clicking "Parse")</h3>
<ol>
  <li>Check if IGV port is available (port can be set in "IGV Port" field; must match IGV setting).</li>
  <li>Parse locus information (table or manual input), extract sample info (if any).</li>
  <li>Compute K-relations and generate batch navigation grid.</li>
  <li><b>First-time batch load</b>: Generate IGV Session XML (reference genome + BAM tracks only), loaded via HTTP <code>/load</code>.</li>
  <li>Load additional files (.gtf/.bed/.vcf etc.) via individual HTTP <code>/load</code> commands.</li>
  <li>Navigate to the current batch position list via HTTP <code>/goto</code>.</li>
  <li>Execute post-processing TCP commands after delay (2.5-second delay on BAM switch, 0.8-second delay on position-only switch).</li>
</ol>

<h3>FAQ</h3>
<ul>
  <li><b>IGV not responding</b>: Check if IGV port is enabled (View → Preferences → Advanced → Enable port) and port matches "IGV Port" field.</li>
  <li><b>Parse failed</b>: Check column names match table headers exactly (case-sensitive), data format is <code>chr:position</code>. For TSV/CSV, check delimiter; for XLSX, check if data spans multiple sheets (all sheets are read automatically).</li>
  <li><b>Same track batch, switching positions</b>: BAM files are NOT reloaded, only goto position is refreshed, making it faster.</li>
  <li><b>Sample column exists but no K-relation</b>: Check if sample name is a prefix of BAM filename (case-insensitive). E.g., <code>sampleA</code> matches <code>sampleA.sorted.bam</code> but NOT <code>mysampleA.bam</code>.</li>
  <li><b>Slow genome loading</b>: IGV auto-downloads hg19/hg38 on first use; pre-download in IGV or use local .fa/.genome files.</li>
  <li><b>Auto-find tracks unavailable in manual input mode</b>: There is no table file path to locate the directory structure; please add track files manually.</li>
  <li><b>What batch size 0 means</b>: 0 = all; position 0 means all positions in one batch, track 0 means all tracks in one batch.</li>
</ul>

<hr>
<p style="color:#888;">
  For questions, contact Xu Xi, Institute of Intelligent Computing Technology, Suzhou, CAS (IICT) <a href="mailto:xuxi@iict.ac.cn">xuxi@iict.ac.cn</a>
</p>
"""

    def _build_html(self):
        """返回当前语言对应的 HTML"""
        if self._lang == 'en':
            return self._html_en
        return self._html_zh

    def set_lang(self, lang):
        """切换语言并刷新显示"""
        self._lang = lang
        self.setWindowTitle(T('help_title'))
        if self._browser is not None:
            self._browser.setHtml(self._build_html())

    def _init_ui(self):
        lay = QVBoxLayout(self)

        self._browser = QTextBrowser()
        self._browser.setOpenExternalLinks(True)
        self._browser.setHtml(self._build_html())
        lay.addWidget(self._browser)

        btns = QDialogButtonBox(QDialogButtonBox.Ok)
        btns.accepted.connect(self.accept)
        lay.addWidget(btns)