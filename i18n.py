"""
中英文国际化模块 (i18n)
用法:
    from i18n import T, LANG, toggle_lang
    label.setText(T('key'))
    btn.setText(T('key'))
"""

LANG = 'zh'  # 当前语言: 'zh' | 'en'


def toggle_lang():
    global LANG
    LANG = 'en' if LANG == 'zh' else 'zh'
    return LANG


# ── 所有 UI 字符串映射 ──
# 格式: key -> {'zh': 中文, 'en': English}

S = {
    # ── 窗口标题 ──
    'window_title':              {'zh': 'IGV 批量导航器 {version}',         'en': 'IGV Batch Navigator {version}'},

    # ── 标题行按钮 ──
    'btn_lang':                  {'zh': 'English',                          'en': '中文'},
    'btn_pin':                   {'zh': '📌 置顶',                           'en': '📌 Pin'},
    'btn_collapse':              {'zh': '收起 ▲',                           'en': 'Collapse ▲'},
    'btn_expand':                {'zh': '展开 ▼',                           'en': 'Expand ▼'},
    'btn_minimal':               {'zh': '极简',                             'en': 'Minimal'},
    'btn_minimal_on':            {'zh': '极简 ✓',                           'en': 'Minimal ✓'},
    'btn_help':                  {'zh': '? 帮  助',                         'en': '? Help'},
    'btn_settings':              {'zh': '⚙ 设  置',                       'en': '⚙ Settings'},

    # ── 文件组标签 ──
    'file_group_title':          {'zh': '文件与参数',                       'en': 'Files & Parameters'},
    'label_table_file':          {'zh': '表格文件:',                        'en': 'Table File:'},
    'btn_browse':                {'zh': '浏览',                             'en': 'Browse'},
    'label_locus_col':           {'zh': '染色体:位置列名:',                 'en': 'Chr:Pos Column:'},
    'label_sample_col':          {'zh': '样本列名(可选):',                  'en': 'Sample Col (opt):'},

    # ── 手动输入 ──
    'manual_checkbox':           {'zh': '手动输入位置信息（勾选后忽略表格文件，直接使用下方文本框内容）',
                                  'en': 'Enter positions manually (ignore table file, use text below)'},
    'manual_placeholder':        {'zh': '每行一个位置，格式：染色体名:位置[制表符或逗号样本名]\n'
                                        '样本列为可选，例如：\n'
                                        'chr1:12345678\n'
                                        'chr1:12345678\tsampleA （用Tab键分隔）\n'
                                        'chr2:87654321,sampleB （用逗号分隔）\n'
                                        'chrX:111222333',
                                  'en': 'One position per line, format: chr:pos[tab or comma sample]\n'
                                        'Sample column is optional, e.g.:\n'
                                        'chr1:12345678\n'
                                        'chr1:12345678\tsampleA (tab-separated)\n'
                                        'chr2:87654321,sampleB (comma-separated)\n'
                                        'chrX:111222333'},

    # ── 基因组/附加文件 ──
    'label_genome':              {'zh': '基因组/附加文件 (勾选需加载的项目):',
                                  'en': 'Genome / Extra Files (check to load):'},
    'btn_browse_local':          {'zh': '浏览本地...',                       'en': 'Browse Local...'},
    'btn_remove_selected':       {'zh': '移除选中',                         'en': 'Remove Selected'},

    # ── 轨道文件 ──
    'label_track_files':         {'zh': '轨道文件:',                        'en': 'Track Files:'},
    'btn_add_tracks':            {'zh': '添加轨道文件',                     'en': 'Add Track Files'},
    'btn_auto_find':             {'zh': '自动寻找表格文件对应的轨道文件',    'en': 'Auto-Find Tracks for Table'},
    'btn_remove_all':            {'zh': '移除所有',                         'en': 'Remove All'},

    # ── 批次数 & 过滤 ──
    'label_pos_batch':           {'zh': '位置批次数:',                      'en': 'Pos Batch Size:'},
    'label_bam_batch':           {'zh': '轨道批次数:',                      'en': 'Track Batch Size:'},
    'filter_no_k_bams':          {'zh': '过滤无样本对应的轨道',             'en': 'Filter tracks w/o matching sample'},
    'filter_k_tracks':           {'zh': 'IGV不展示无位置对应的轨道',        'en': 'Hide tracks w/o matching locus in IGV'},

    # ── 后处理命令 ──
    'label_post_cmds':           {'zh': '后处理命令 (TCP，每行一条，在轨道/位置加载后执行):',
                                  'en': 'Post-Process Cmds (TCP, one per line, after track/locus load):'},
    'btn_cmd_ref':               {'zh': '命令参考',                         'en': 'Cmd Reference'},
    'post_cmds_placeholder':     {'zh': 'sort base',                        'en': 'sort base'},

    # ── 端口 & 解析 ──
    'label_port':                {'zh': 'IGV 端口:',                        'en': 'IGV Port:'},
    'port_tooltip':              {'zh': 'IGV 通信端口，需与 IGV 中设置的端口一致',
                                  'en': 'IGV communication port; must match IGV port setting'},
    'btn_parse':                 {'zh': '解析',                             'en': 'Parse'},
    'btn_parsing':               {'zh': '解析中...',                        'en': 'Parsing...'},

    # ── 导航组 ──
    'nav_group_title':           {'zh': '批次导航',                         'en': 'Batch Navigation'},
    'pos_placeholder':           {'zh': '位置批次详情',                     'en': 'Position Batch Details'},
    'bam_placeholder':           {'zh': '轨道批次详情',                     'en': 'Track Batch Details'},
    'btn_prev_relevant':         {'zh': '◀ 上一个对应批次',                 'en': '◀ Prev Relevant Batch'},
    'btn_next_relevant':         {'zh': '下一个对应批次 ▶',                 'en': 'Next Relevant Batch ▶'},
    'btn_prev_pos':              {'zh': '◀ 上一个位置批次',                 'en': '◀ Prev Position Batch'},
    'btn_next_pos':              {'zh': '下一个位置批次 ▶',                 'en': 'Next Position Batch ▶'},
    'btn_prev_bam':              {'zh': '◀ 上一个轨道批次',                 'en': '◀ Prev Track Batch'},
    'btn_next_bam':              {'zh': '下一个轨道批次 ▶',                 'en': 'Next Track Batch ▶'},

    # ── 网格表头 ──
    'grid_pos_header':           {'zh': '位置批次 {i}',                     'en': 'Pos Batch {i}'},
    'grid_bam_header':           {'zh': '轨道批次 {i}',                     'en': 'Track Batch {i}'},

    # ── 内容展示区 HTML header ──
    'pos_html_header':           {'zh': '══ 位置批次 {col}/{total} ══',     'en': '══ Position Batch {col}/{total} ══'},
    'bam_html_header':           {'zh': '══ 轨道批次 {row}/{total} ══',     'en': '══ Track Batch {row}/{total} ══'},

    # ── 状态栏 ──
    'status_format':             {'zh': '轨道[{bam}/{bam_total}]  位置[{pos}/{pos_total}]',
                                  'en': 'Track[{bam}/{bam_total}]  Pos[{pos}/{pos_total}]'},

    # ── 文件对话框标题 ──
    'dlg_select_table':          {'zh': '选择表格文件',                     'en': 'Select Table File'},
    'dlg_select_local':          {'zh': '选择本地文件',                     'en': 'Select Local File'},
    'dlg_select_tracks':         {'zh': '选择轨道文件',                     'en': 'Select Track Files'},
    'dlg_select_python':         {'zh': '选择 Python 解释器',               'en': 'Select Python Interpreter'},

    # ── 文件过滤器 ──
    'filter_table':              {'zh': '所有文件 (*.*);;TSV 文件 (*.tsv *.txt);;CSV 文件 (*.csv);;Excel 文件 (*.xlsx)',
                                  'en': 'All Files (*.*);;TSV Files (*.tsv *.txt);;CSV Files (*.csv);;Excel Files (*.xlsx)'},
    'filter_local':              {'zh': '常见生信格式 (*.fa *.fasta *.genome *.gtf *.gff *.gff3 *.bed *.vcf *.bw *.bigwig *.txt);;所有文件 (*.*)',
                                  'en': 'Common Bioinfo Formats (*.fa *.fasta *.genome *.gtf *.gff *.gff3 *.bed *.vcf *.bw *.bigwig *.txt);;All Files (*.*)'},
    'filter_bam':                {'zh': 'BAM 文件 (*.bam);;所有文件 (*.*)',
                                  'en': 'BAM Files (*.bam);;All Files (*.*)'},
    'filter_python':             {'zh': 'Python 解释器 (python.exe);;所有文件 (*.*)',
                                  'en': 'Python Interpreter (python.exe);;All Files (*.*)'},

    # ── 消息框标题 ──
    'msg_title_notice':          {'zh': '提示',                             'en': 'Notice'},
    'msg_title_not_found':       {'zh': '未找到',                           'en': 'Not Found'},
    'msg_title_igv_not_conn':    {'zh': 'IGV 未连接',                       'en': 'IGV Not Connected'},
    'msg_title_error':           {'zh': '错误',                             'en': 'Error'},
    'msg_title_parse_fail':      {'zh': '解析失败',                         'en': 'Parse Failed'},
    'msg_title_igv_conn_fail':   {'zh': 'IGV 连接失败',                     'en': 'IGV Connection Failed'},
    'msg_title_settings_err':    {'zh': '设置异常',                         'en': 'Settings Error'},
    'msg_title_program_err':     {'zh': '程序异常',                         'en': 'Program Error'},

    # ── 消息框正文 ──
    'msg_need_table_first':      {'zh': '请先选择表格文件。',               'en': 'Please select a table file first.'},
    'msg_final_out_not_found':   {'zh': '未能从表格文件路径中定位到 final_out 目录，请确保表格文件位于路径中包含 final_out 的目录下。',
                                  'en': 'Could not locate "final_out" directory from table file path. Ensure the table file is under a path containing "final_out".'},
    'msg_bam_out_not_found':     {'zh': '未找到 bam_out 目录：\n{path}',
                                  'en': 'bam_out directory not found:\n{path}'},
    'msg_no_bam_in_bam_out':     {'zh': 'bam_out 目录下未找到 .bam 文件：\n{path}',
                                  'en': 'No .bam files found under bam_out:\n{path}'},
    'msg_port_unreachable':      {'zh': '无法连接 IGV 端口 {port}，请确认：\n'
                                        '1. IGV 已打开\n'
                                        '2. View → Preferences → Advanced → 勾选 Enable port 且端口号为 {port}',
                                  'en': 'Cannot connect to IGV port {port}. Please check:\n'
                                        '1. IGV is running\n'
                                        '2. View → Preferences → Advanced → Enable port is checked (port {port})'},
    'msg_need_at_least_one_bam': {'zh': '请添加至少一个轨道文件。',          'en': 'Please add at least one track file.'},
    'msg_manual_empty':          {'zh': '请先在手动输入框中输入位置信息。',  'en': 'Please enter positions in the manual input box first.'},
    'msg_manual_no_loci':        {'zh': '未能从手动输入中解析到任何有效位置。\n'
                                        '每行格式：染色体名:位置（例如 chr1:12345678）',
                                  'en': 'Could not parse any valid positions from manual input.\n'
                                        'Format per line: chr:pos (e.g. chr1:12345678)'},
    'msg_invalid_table':         {'zh': '请先选择有效的表格文件。',          'en': 'Please select a valid table file first.'},
    'msg_no_loci_from_col':      {'zh': "未能从列 '{col}' 解析到任何位置。",
                                  'en': "Could not parse any positions from column '{col}'."},
    'msg_igv_conn_fail':         {'zh': '无法连接 IGV，请确认：\n'
                                        '1. IGV 已打开\n'
                                        '2. View → Preferences → Advanced → Enable port 已勾选（端口 {port}）',
                                  'en': 'Cannot connect to IGV. Please check:\n'
                                        '1. IGV is running\n'
                                        '2. View → Preferences → Advanced → Enable port is checked (port {port})'},
    'msg_settings_error':        {'zh': '打开设置时出错：{error}',
                                  'en': 'Error opening settings: {error}'},
    'msg_program_error':         {'zh': '程序遇到未处理的错误，详细信息已写入：\n{log_path}\n\n{exc_info}',
                                  'en': 'Program encountered an unhandled error. Details written to:\n{log_path}\n\n{exc_info}'},
    'msg_unhandled_exception':   {'zh': '未处理的异常:\n{exc_info}',
                                  'en': 'Unhandled exception:\n{exc_info}'},

    # ── 自动寻找反馈 ──
    'status_auto_loaded':        {'zh': '已自动加载 {n} 个轨道文件',        'en': 'Auto-loaded {n} track file(s)'},

    # ── tsv_csv_parser 错误 ──
    'err_col_not_found':         {'zh': "未找到列 '{col}'。可用列: {available}",
                                  'en': "Column '{col}' not found. Available columns: {available}"},
    'err_no_openpyxl':           {'zh': '读取 xlsx 文件需要安装 openpyxl 库。请执行: pip install openpyxl',
                                  'en': 'openpyxl is required for reading XLSX files. Run: pip install openpyxl'},
    'err_no_col_in_xlsx':        {'zh': "在所有 sheet 中均未找到列 '{col}'。",
                                  'en': "Column '{col}' not found in any sheet."},

    # ── 设置对话框 ──
    'settings_title':            {'zh': '设置',                             'en': 'Settings'},
    'settings_group':            {'zh': 'Python 解释器路径',                'en': 'Python Interpreter Path'},
    'settings_desc':             {'zh': '用于执行 IGV 导航脚本的 Python 解释器路径（默认使用当前 Python）。',
                                  'en': 'Path to Python interpreter for running IGV nav script (defaults to current Python).'},

    # ── 命令参考对话框 ──
    'cmdref_title':              {'zh': 'IGV 命令参考',                      'en': 'IGV Command Reference'},
    'cmdref_desc':               {'zh': 'IGV 端口命令参考（可用于后处理命令输入框）',
                                  'en': 'IGV Port Command Reference (usable in post-processing input)'},
    'cmdref_th_cmd':             {'zh': '命令',                             'en': 'Command'},
    'cmdref_th_cat':             {'zh': '类别',                             'en': 'Category'},
    'cmdref_th_desc':            {'zh': '详细说明',                         'en': 'Description'},

    # ── 日志对话框 ──
    'log_title':                 {'zh': '运行日志 (Ctrl+L)',                 'en': 'Run Log (Ctrl+L)'},

    # ── 帮助对话框 ──
    'help_title':                {'zh': '帮助',                             'en': 'Help'},
}


def T(key: str, **kwargs) -> str:
    """获取当前语言的字符串。kwargs 用于 str.format() 填充占位符。"""
    entry = S.get(key)
    if entry is None:
        return f'??{key}??'
    text = entry.get(LANG, entry.get('zh', f'??{key}??'))
    if kwargs:
        return text.format(**kwargs)
    return text