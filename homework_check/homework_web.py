import streamlit as st
import pandas as pd
import os
import re
import io
import base64
from pathlib import Path
import streamlit.components.v1 as components

# 防止未安装 openpyxl 导致报错
try:
    from openpyxl.styles import Font
except ImportError:
    Font = None

st.markdown(
    """
    <style>
    .mouse-particle {
        position: fixed;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        pointer-events: none;
        z-index: 999999;
        animation: particle-move 0.6s ease-out forwards;
    }

    @keyframes particle-move {
        0% {
            opacity: 1;
            transform: translate(0, 0) scale(1);
        }
        100% {
            opacity: 0;
            transform: translate(var(--dx), var(--dy)) scale(0.2);
        }
    }
    </style>

    <script>
    document.addEventListener("mousemove", function(e) {
        const particle = document.createElement("div");
        particle.className = "mouse-particle";

        const size = Math.random() * 6 + 4;
        particle.style.width = size + "px";
        particle.style.height = size + "px";

        particle.style.left = e.clientX + "px";
        particle.style.top = e.clientY + "px";

        const colors = ["#FB7299", "#00E676", "#FFEB3B", "#FFFFFF"];
        const color = colors[Math.floor(Math.random() * colors.length)];
        particle.style.background = color;
        particle.style.boxShadow = `0 0 ${size * 2}px ${color}`;

        particle.style.setProperty("--dx", (Math.random() - 0.5) * 60 + "px");
        particle.style.setProperty("--dy", (Math.random() - 0.5) * 60 + "px");

        document.body.appendChild(particle);

        setTimeout(() => particle.remove(), 600);
    });
    </script>
    """,
    unsafe_allow_html=True
)

components.html(
    """
    <style>
    .mouse-particle {
        position: fixed;
        width: 6px;
        height: 6px;
        border-radius: 50%;
        pointer-events: none;
        z-index: 9999999;
        background: white;
        animation: fade 0.6s linear forwards;
    }

    @keyframes fade {
        from {
            opacity: 1;
            transform: translate(0,0) scale(1);
        }
        to {
            opacity: 0;
            transform: translate(var(--dx), var(--dy)) scale(0.2);
        }
    }
    </style>

    <script>
    const doc = window.parent.document;

    doc.addEventListener("mousemove", function(e) {
        const p = doc.createElement("div");
        p.className = "mouse-particle";

        const size = Math.random() * 4 + 4;
        p.style.width = size + "px";
        p.style.height = size + "px";

        p.style.left = e.clientX + "px";
        p.style.top = e.clientY + "px";

        const colors = ["#FB7299", "#00E676", "#FFEB3B", "#FFFFFF"];
        const color = colors[Math.floor(Math.random() * colors.length)];
        p.style.background = color;
        p.style.boxShadow = `0 0 10px ${color}`;

        p.style.setProperty("--dx", (Math.random() - 0.5) * 50 + "px");
        p.style.setProperty("--dy", (Math.random() - 0.5) * 50 + "px");

        doc.body.appendChild(p);
        setTimeout(() => p.remove(), 600);
    });
    </script>
    """,
    height=0,
)







# ==========================================
# 1. 页面配置
# ==========================================
st.set_page_config(
    page_title="作业检查系统",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed"  # 初始默认收起
)

# ==========================================
# 2. 状态初始化
# ==========================================
if 'nav_selection' not in st.session_state:
    st.session_state.nav_selection = "🏠 首页 (设置与上传)"
if 'results' not in st.session_state:
    st.session_state.results = None
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'collapsed'

# 定义页面常量
PAGE_HOME = "🏠 首页 (设置与上传)"
PAGE_RESULTS = "📊 结果看板"


# ==========================================
# 3. 视觉样式与背景
# ==========================================
@st.cache_data(show_spinner=False)
def get_video_base64(video_file):
    if not os.path.exists(video_file):
        return None
    with open(video_file, "rb") as f:
        video_bytes = f.read()
    return base64.b64encode(video_bytes).decode()


def set_style_and_bg(video_file):
    b64_video = get_video_base64(video_file)

    video_html = ""
    if b64_video:
        video_html = f"""
<video autoplay muted loop id="myVideo" playsinline>
  <source src="https://raw.githubusercontent.com/regenschirm-jetzt/homework-checker/main/homework_check/a.mp4" type="video/mp4">
</video>

"""

    st.markdown(
        f"""
        <style>
        /* 1. 基础背景设置 */
        .stApp {{ background: transparent !important; }}
        #myVideo {{
            position: fixed; right: 0; bottom: 0;
            min-width: 100%; min-height: 100%;
            z-index: -1; object-fit: cover;
        }}

        /* 2. 顶栏深色化 */
        header[data-testid="stHeader"] {{
            background-color: #0E1117 !important;
            opacity: 0.95 !important;
        }}
        header[data-testid="stHeader"] * {{
            fill: #FFFFFF !important;
            color: #FFFFFF !important;
        }}

        /* 3. 主容器磨砂黑 */
        .main .block-container {{
            background-color: rgba(20, 20, 25, 0.85);
            padding: 3rem;
            border-radius: 12px;
            box-shadow: 0 4px 30px rgba(0,0,0,0.5);
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            max-width: 95%;
        }}

        /* 4. 全局文字颜色 */
        h1, h2, h3, h4, h5, h6 {{
            color: #FFFFFF !important;
            font-family: "HarmonyOS Sans", "Microsoft YaHei", sans-serif;
            text-shadow: 0 2px 4px rgba(0,0,0,0.8);
        }}
        h1 {{ text-align: center; padding-bottom: 20px; }}
        p, label, li, span, .stMarkdown, .stRadio label {{
            color: #E0E0E0 !important;
        }}

        /* 5. 指标数值亮白 */
        [data-testid="stMetricValue"] {{ color: #FFFFFF !important; }}
        [data-testid="stMetricValue"] div {{
            color: #FFFFFF !important; 
            text-shadow: 0 0 10px rgba(255,255,255,0.4);
        }}
        [data-testid="stMetricLabel"] label {{ color: #FB7299 !important; }}

        /* 6. 下载按钮白底黑字 */
        [data-testid="stDownloadButton"] button {{
            background-color: #FFFFFF !important;
            border: 1px solid #CCCCCC !important;
        }}
        [data-testid="stDownloadButton"] button * {{
            color: #000000 !important;
            font-weight: bold !important;
        }}
        [data-testid="stDownloadButton"] button:hover {{
            background-color: #F0F0F0 !important;
            border-color: #FB7299 !important;
        }}
        [data-testid="stDownloadButton"] button:hover p {{ color: #FB7299 !important; }}

        /* 7. 输入框 & 上传框 (白底黑字) */
        [data-testid="stFileUploader"] section {{
            background-color: #FFFFFF !important;
            border: 1px solid #CCCCCC !important;
        }}
        [data-testid="stFileUploader"] section * {{
            color: #000000 !important;
            text-shadow: none !important;
        }}
        [data-testid="stFileUploader"] button {{
            background-color: #F0F2F6 !important;
            color: #000000 !important;
            border-color: #999 !important;
        }}
        .stFileUploader > label, .stTextInput > label {{
            color: #FB7299 !important; 
            font-weight: bold;
            font-size: 1.1rem;
        }}
        .stTextInput > div > div > input {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border: 1px solid #CCCCCC;
        }}

        /* === B. 下面的框：已上传文件列表 (最终优化版) === */
        
        /* 0. 新增：全局滚动条样式 (小滑块) */
        /* 针对 Chrome/Edge/Safari 等浏览器 */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
            background-color: transparent;
        }}
        ::-webkit-scrollbar-thumb {{
            background-color: #FB7299 !important; /* 统一滑块颜色：主题粉 */
            border-radius: 10px;
        }}
        ::-webkit-scrollbar-track {{
            background: transparent;
        }}

        /* 1. 外层卡片主体：白底、圆角 */
        [data-testid="stFileUploaderFile"] {{
            background-color: #FFFFFF !important;
            border: 1px solid #E0E0E0 !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
            margin-bottom: 10px !important;
            padding: 8px 12px !important;
            align-items: center !important;
        }}

        /* 2. 消除方块背景：强制所有内部容器透明 */
        [data-testid="stFileUploaderFile"] div,
        [data-testid="stFileUploaderFile"] section {{
            background-color: transparent !important;
            background: transparent !important;
        }}

        /* 3. 文字颜色修复 */
        [data-testid="stFileUploaderFile"] span,
        [data-testid="stFileUploaderFile"] small,
        [data-testid="stFileUploaderFile"] div {{
            color: #333333 !important; /* 字体深灰，比纯黑柔和一点 */
            font-family: sans-serif !important;
            text-shadow: none !important;
        }}

        /* 4. 文件图标修复：平时显示为黑色剪影 */
        [data-testid="stFileUploaderFile"] svg {{
            background-color: transparent !important;
            filter: brightness(0) !important; 
            opacity: 0.6 !important; /* 平时颜色淡一点，不抢眼 */
        }}

        /* 5. 删除按钮 (X) 的特别处理 */
        /* A. 按钮容器平时样式 */
        [data-testid="stFileUploaderFile"] button {{
            border: none !important;
            background: transparent !important;
            transition: all 0.2s ease; /* 加个小动画 */
        }}
        
        /* B. 鼠标放上去时：背景变极淡的红色 */
        [data-testid="stFileUploaderFile"] button:hover {{
            background-color: rgba(255, 50, 50, 0.5) !important; /* 红色背景调淡 */
        }}
        
        /* C. 鼠标放上去时：叉号图标变红 */
        [data-testid="stFileUploaderFile"] button:hover svg {{
            filter: none !important; /* 取消黑色滤镜 */
            opacity: 1 !important;
            transform: scale(1.1); /* 稍微放大一点点 */
        }}
        
        /* === C. 其他输入框保持原样 === */
        .stFileUploader > label, .stTextInput > label {{
            color: #FB7299 !important; 
            font-weight: bold;
            font-size: 1.1rem;
        }}
        .stTextInput > div > div > input {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border: 1px solid #CCCCCC;
        }}
        /* 8. 侧边栏与按钮 */
        [data-testid="stSidebar"] {{
            background-color: rgba(18, 18, 24, 0.98);
            border-right: 1px solid rgba(255,255,255,0.1);
        }}
        .stButton > button {{
            background-color: #FB7299 !important;
            color: white !important;
            border: none;
            border-radius: 6px;
            font-weight: 600;
        }}
        .stButton > button:hover {{
            background-color: #FF8EB3 !important;
            transform: translateY(-2px);
        }}

        /* 9. 表格 */
        .stDataFrame {{ background-color: #2D2D2D; border-radius: 8px; padding: 5px; }}
        div[data-testid="stTable"] {{ color: #E0E0E0 !important; }}
        .stTabs [aria-selected="true"] {{
            color: #FB7299 !important;
            border-bottom-color: #FB7299 !important;
        }}
        </style>
        {video_html}
        """,
        unsafe_allow_html=True
    )


set_style_and_bg('a.mp4')


# ==========================================
# 4. 逻辑函数
# ==========================================

def render_progress_bar(normal, risky, missing):
    """绘制进度条 (HTML)"""
    total = normal + risky + missing
    if total == 0:
        return "<div style='color:#888; margin-bottom:15px;'>暂无数据</div>"

    # 颜色定义
    c_norm = "#00E676"  # 绿色
    c_risk = "#FFEB3B"  # 黄色
    c_miss = "#FF5252"  # 红色

    p_norm = (normal / total) * 100
    p_risk = (risky / total) * 100
    p_miss = (missing / total) * 100

    html_parts = []
    # 容器开始
    html_parts.append(
        f'<div style="width:100%; height:24px; background-color:rgba(255,255,255,0.2); border-radius:12px; overflow:hidden; display:flex; margin-bottom:10px;">')

    if p_norm > 0:
        label = f"{p_norm:.0f}%" if p_norm >= 5 else ""
        html_parts.append(
            f'<div style="width:{p_norm}%; background-color:{c_norm}; height:100%; display:flex; align-items:center; justify-content:center; color:black; font-weight:bold; font-size:12px;" title="正常提交: {normal}人">{label}</div>')
    if p_risk > 0:
        label = f"{p_risk:.0f}%" if p_risk >= 5 else ""
        html_parts.append(
            f'<div style="width:{p_risk}%; background-color:{c_risk}; height:100%; display:flex; align-items:center; justify-content:center; color:black; font-weight:bold; font-size:12px;" title="风险提交: {risky}人">{label}</div>')
    if p_miss > 0:
        label = f"{p_miss:.0f}%" if p_miss >= 5 else ""
        html_parts.append(
            f'<div style="width:{p_miss}%; background-color:{c_miss}; height:100%; display:flex; align-items:center; justify-content:center; color:black; font-weight:bold; font-size:12px;" title="未交作业: {missing}人">{label}</div>')

    html_parts.append('</div>')

    # 图例
    legend_parts = []
    legend_parts.append('<div style="display:flex; gap:20px; font-size:13px; color:#ddd; margin-bottom:20px;">')
    if normal > 0:
        legend_parts.append(
            f'<div style="display:flex; align-items:center;"><div style="width:10px; height:10px; background-color:{c_norm}; border-radius:50%; margin-right:6px;"></div>正常: {normal}</div>')
    if risky > 0:
        legend_parts.append(
            f'<div style="display:flex; align-items:center;"><div style="width:10px; height:10px; background-color:{c_risk}; border-radius:50%; margin-right:6px;"></div>风险: {risky}</div>')
    if missing > 0:
        legend_parts.append(
            f'<div style="display:flex; align-items:center;"><div style="width:10px; height:10px; background-color:{c_miss}; border-radius:50%; margin-right:6px;"></div>未交: {missing}</div>')
    legend_parts.append('</div>')

    return "".join(html_parts + legend_parts)


def to_excel_download(df, filename="output.xlsx", highlight_red=False):
    output = io.BytesIO()
    try:
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
            if highlight_red and Font:
                try:
                    ws = writer.sheets['Sheet1']
                    red_font = Font(color="FF0000", bold=True)
                    for row in ws.iter_rows(min_row=2):
                        for cell in row:
                            cell.font = red_font
                except Exception:
                    pass
    except Exception:
        output = io.BytesIO()
        try:
            with pd.ExcelWriter(output) as writer:
                df.to_excel(writer, index=False)
        except Exception:
            return None
    return output.getvalue()


def extract_student_id_from_filename(filename, name_to_id):
    match_digit = re.search(r'\d{9}', filename)
    if match_digit:
        return match_digit.group(), False
    for name, s_id in name_to_id.items():
        if name in filename:
            return s_id, True
    return None, False


def get_student_info_from_roster(file_obj):
    try:
        df = pd.read_excel(file_obj)
        student_id_col = None
        for col in df.columns:
            if '学号' in str(col):
                student_id_col = col
                break
        if student_id_col is None:
            for col in df.columns:
                sample = df[col].dropna().head(5)
                if len(sample) > 0 and any(re.search(r'\d{9}', str(v)) for v in sample):
                    student_id_col = col
                    break
        if student_id_col is None: student_id_col = df.columns[0]

        name_col = None
        for col in df.columns:
            if '姓名' in str(col):
                name_col = col
                break
        if name_col is None and len(df.columns) > 1:
            try:
                idx = list(df.columns).index(student_id_col)
                if idx + 1 < len(df.columns): name_col = df.columns[idx + 1]
            except:
                name_col = df.columns[1]

        student_id_to_name = {}
        roster_ids = set()
        for _, row in df.iterrows():
            id_val = row[student_id_col]
            if pd.isna(id_val): continue
            str_val = str(id_val).strip()
            sid = None
            if str_val.isdigit() and len(str_val) >= 9:
                sid = str_val[:9]
            else:
                match = re.search(r'\d{9}', str_val)
                if match: sid = match.group()
            if sid:
                roster_ids.add(sid)
                name = "未知"
                if name_col and not pd.isna(row[name_col]): name = str(row[name_col]).strip()
                student_id_to_name[sid] = name
        return roster_ids, student_id_to_name
    except Exception as e:
        st.error(f"读取花名册失败: {e}")
        return set(), {}


def check_folder_logic(folder_path, roster_ids, name_to_id):
    path_obj = Path(folder_path)
    if not path_obj.exists(): return set(), roster_ids, {}, set()

    student_files_map = {}
    extensions = ['.py', '.docx', '.pdf', '.zip', '.rar', '.c', '.cpp', '.txt']

    for file_path in path_obj.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in extensions:
            sid, is_risky = extract_student_id_from_filename(file_path.name, name_to_id)
            if sid:
                if sid not in student_files_map:
                    student_files_map[sid] = []
                student_files_map[sid].append((is_risky, file_path.name))

    submitted_ids = set()
    normal_ids = set()
    risky_files_map = {}

    for sid, files in student_files_map.items():
        submitted_ids.add(sid)
        has_normal_file = any(not f[0] for f in files)
        if has_normal_file:
            normal_ids.add(sid)
        else:
            risky_files_map[sid] = files[0][1]

    missing_ids = roster_ids - submitted_ids
    return submitted_ids, missing_ids, risky_files_map, normal_ids


# ==========================================
# 5. 主程序逻辑 (Home / Results)
# ==========================================

# 兼容性 Rerun
def safe_rerun():
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()


# 侧边栏重置函数 (用于 callback)
def reset_callback():
    st.session_state.results = None
    st.session_state.nav_selection = PAGE_HOME
    st.session_state.sidebar_state = 'collapsed'


# >>>>> 页面 1: 首页 <<<<<
if st.session_state.nav_selection == PAGE_HOME:
    st.title("自动化作业检查系统")
    st.markdown("<p style='text-align:center;'>基于 Python 自动化处理 · 支持 Excel 花名册与本地文件扫描</p>",
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.5], gap="large")
    with col1:
        st.markdown("### 📂 第一步：上传花名册")
        uploaded_roster = st.file_uploader("请选择 Excel 文件 (.xlsx/.xls/.csv)", type=['xlsx', 'xls', 'csv'],
                                           key="uploader")

    with col2:
        st.markdown("### 📂 第二步：指定作业目录")
        st.markdown("请输入包含 `学生作业` 文件夹的**完整路径**：")
        root_folder_input = st.text_input("本地路径地址", value=str(Path.cwd()), key="path_input")
        st.caption("提示：系统将扫描该路径下所有以“学生作业”开头的子文件夹。")

    st.markdown("---")
    _, c_btn, _ = st.columns([1, 2, 1])
    with c_btn:
        start_check = st.button("🚀 启动检查引擎", type="primary", use_container_width=True)

    # 检查逻辑
    if start_check:
        if not uploaded_roster:
            st.error("请先上传花名册文件！")
        else:
            with st.spinner("正在扫描文件并匹配学号..."):
                try:
                    roster_ids, id_to_name = get_student_info_from_roster(uploaded_roster)
                    name_to_id = {v: k for k, v in id_to_name.items() if v != "未知"}
                    root_path = Path(root_folder_input)

                    if not root_path.exists():
                        st.error("❌ 路径不存在，请检查输入！")
                    else:
                        try:
                            homework_folders = [d for d in root_path.iterdir() if d.is_dir() and "学生作业" in d.name]
                        except Exception as e:
                            homework_folders = []
                            st.error(f"目录读取错误: {e}")

                        if not homework_folders:
                            st.warning("⚠️ 未找到包含“学生作业”字样的文件夹。")
                        else:
                            all_results = []
                            for folder in sorted(homework_folders):
                                sub, miss, risky_map, normal_ids = check_folder_logic(folder, roster_ids, name_to_id)

                                missing_data = [{"学号": sid, "姓名": id_to_name.get(sid, "未知")} for sid in
                                                sorted(miss)]
                                risky_data = [{"学号": sid, "姓名": id_to_name.get(sid, "未知"), "文件名": fn,
                                               "备注": "找到姓名，学号异常"} for sid, fn in risky_map.items()]

                                all_results.append({
                                    "folder_name": folder.name,
                                    "submitted_count": len(sub),
                                    "missing_count": len(miss),
                                    "risky_count": len(risky_map),
                                    "normal_count": len(normal_ids),
                                    "missing_df": pd.DataFrame(missing_data),
                                    "risky_df": pd.DataFrame(risky_data)
                                })

                            st.session_state.results = all_results

                            # 关键：更新状态并重新运行，触发跳转
                            st.session_state.nav_selection = PAGE_RESULTS
                            safe_rerun()
                except Exception as e:
                    st.error(f"发生未知错误: {e}")

# >>>>> 页面 2: 结果看板 <<<<<
elif st.session_state.nav_selection == PAGE_RESULTS:
    # 修复：如果没有数据，不强制自动跳转，而是显示手动返回按钮
    if not st.session_state.results:
        st.warning("⚠️ 暂无检查结果，请先返回首页进行操作。")
        if st.button("⬅️ 返回首页"):
            st.session_state.nav_selection = PAGE_HOME
            safe_rerun()
    else:
        st.title("📊 检查结果看板")

        # 汇总数据
        total_folders = len(st.session_state.results)
        total_missing = sum(r['missing_count'] for r in st.session_state.results)
        grand_normal = sum(r['normal_count'] for r in st.session_state.results)
        grand_risky = sum(r['risky_count'] for r in st.session_state.results)

        m1, m2, m3 = st.columns(3)
        m1.metric("📂 作业次数", f"{total_folders} 次")
        m2.metric("❌ 累计未交", f"{total_missing} 人次", delta_color="inverse")
        m3.metric("✨ 状态", "检查完毕")

        st.markdown("##### 📈 总体进度概览")
        st.markdown(render_progress_bar(grand_normal, grand_risky, total_missing), unsafe_allow_html=True)

        st.markdown("---")
        tabs = st.tabs([f"📄 {res['folder_name']}" for res in st.session_state.results])

        for i, res in enumerate(st.session_state.results):
            with tabs[i]:
                st.subheader(f"详情：{res['folder_name']}")

                st.markdown(render_progress_bar(res['normal_count'], res['risky_count'], res['missing_count']),
                            unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                c1.info(f"✅ 已提交: {res['submitted_count']} 人")
                c2.error(f"❌ 未提交: {res['missing_count']} 人")
                c3.warning(f"⚠️ 风险文件: {res['risky_count']} 个")

                col_miss, col_risk = st.columns(2)
                with col_miss:
                    st.markdown("#### 🚫 未交名单")
                    if not res['missing_df'].empty:
                        st.dataframe(res['missing_df'], hide_index=True, use_container_width=True)
                        data = to_excel_download(res['missing_df'])
                        if data:
                            st.download_button(
                                label="📥 导出未交名单",
                                data=data,
                                file_name=f"未交_{res['folder_name']}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                    else:
                        st.success("🎉 全员已提交！")

                with col_risk:
                    st.markdown("#### ⚠️ 风险名单 (仅匹配姓名)")
                    if not res['risky_df'].empty:
                        st.dataframe(res['risky_df'], hide_index=True, use_container_width=True)
                        data = to_excel_download(res['risky_df'], highlight_red=True)
                        if data:
                            st.download_button(
                                label="📥 导出风险名单",
                                data=data,
                                file_name=f"风险名单_{res['folder_name']}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                    else:
                        st.info("✅ 文件名格式均正常")

# ==========================================
# 6. 侧边栏 (最后渲染，防止 modify error)
# ==========================================
st.sidebar.title("📺 检查系统导航")
st.sidebar.markdown("---")

# 侧边栏 Radio
st.sidebar.radio(
    "跳转至：",
    options=[PAGE_HOME, PAGE_RESULTS],
    key="nav_selection"
)

st.sidebar.markdown("---")
st.sidebar.button("🔄 重置系统", on_click=reset_callback)