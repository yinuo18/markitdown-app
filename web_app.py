import streamlit as st
from markitdown import MarkItDown
import google.generativeai as genai
import os
import zipfile
import io
import time

# 1. 全局配置
st.set_page_config(page_title="文献解析舱 2.0 | 视觉大模型驱动", page_icon="⚡", layout="wide")

# 2. 侧边栏：API Key 防蹭额度设置 (核心升级)
with st.sidebar:
    st.markdown("### ⚙️️ 核心引擎设置")
    user_api_key = st.text_input("🔑 请输入 Gemini API Key (用于 PDF 深度解析)", type="password")

    st.markdown("---")
    st.markdown("💡 **没有 Key 怎么办？**\nGemini 接口目前完全免费，只需 2 分钟即可申请。")
    # 留出你的小红书教程占位符
    st.markdown("[👉 点击查看主理人的免费获取教程](#)")
    st.markdown("---")
    st.markdown("*(注：处理 Excel / Word / PPT 时直接调用本地轻量引擎，无需输入 Key)*")

# 3. 注入现代化 SaaS 风格的 CSS 样式
st.markdown("""
<style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .hero-banner {
        background: linear-gradient(135deg, #0F2027 0%, #203A43 50%, #2C5364 100%);
        padding: 3rem 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
</style>
<div class="hero-banner">
    <h1 style="margin:0; font-weight:800;">⚡ 智能文献解析舱 <span style="color:#F59E0B;">2.0 视觉终极版</span></h1>
    <p style="opacity:0.9; margin-top:10px;">搭载多模态视觉大模型引擎，彻底攻克顶刊公式乱码与跨页表格错位难题</p>
</div>
""", unsafe_allow_html=True)


# 4. 混合双擎解析函数
def parse_document(file_path, file_name, api_key):
    # 【引擎 A】针对 PDF 启用视觉大模型进行降维打击
    if file_name.lower().endswith('.pdf'):
        if not api_key:
            st.warning(f"⚠️ 解析 {file_name} 需要视觉大模型支持，请先在左侧侧边栏输入你的 API Key！")
            return None

        st.info(f"📄 检测到 PDF 文献，已启动 VLM 视觉解析引擎...")
        genai.configure(api_key=api_key)
        uploaded_pdf = genai.upload_file(path=file_path)

        # 这里默认调用最新的 pro 模型以应对复杂的数理推导和多维表格
        model = genai.GenerativeModel('gemini-1.5-pro')

        prompt = """
        你现在是一个顶级的学术文献排版解析器。请仔细阅读这份 PDF 文献，并将其内容转化为纯净的 Markdown 格式输出。
        严格遵守以下规则：
        1. 保持所有正文段落的连贯性，忽略页眉、页脚和页码的干扰。
        2. 将所有化学反应式、物理公式和带有上下标的变量转化为标准的 LaTeX 格式（例如 $H_2$ 或 $$X_{e,N}$$）。
        3. 遇到实验数据表时，必须通过 Markdown 表格语法严格对齐行列，不得将列平铺或丢失空白单元格。
        """
        response = model.generate_content([uploaded_pdf, prompt])
        genai.delete_file(uploaded_pdf.name)
        return response.text

    # 【引擎 B】针对结构化数据回退使用 MarkItDown
    else:
        st.info(f"📊 检测到结构化数据，使用 MarkItDown 高速提取...")
        md = MarkItDown()
        result = md.convert(file_path)
        return result.text_content


# 5. 核心交互区
uploaded_files = st.file_uploader(
    "拖拽文件至此开启 VLM 混合解析 (支持批量上传 PDF / XLSX / DOCX 等)",
    type=["pdf", "docx", "pptx", "xlsx", "csv", "html"],
    accept_multiple_files=True
)

if uploaded_files:
    zip_buffer = io.BytesIO()
    processed_count = 0

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file in uploaded_files:
            temp_path = file.name
            with open(temp_path, "wb") as f:
                f.write(file.getbuffer())

            with st.spinner(f"⏳ 引擎全开，正在高精度重构 {file.name}..."):
                try:
                    markdown_text = parse_document(temp_path, file.name, user_api_key)
                    if markdown_text:
                        zip_file.writestr(f"Parsed_{file.name}.md", markdown_text)
                        processed_count += 1

                        with st.expander(f"✅ {file.name} (解析成功)", expanded=False):
                            st.download_button("⬇️ 单独下载", data=markdown_text, file_name=f"Parsed_{file.name}.md",
                                               mime="text/markdown", key=f"btn_{file.name}")
                            st.text_area("高精度文本预览：", markdown_text, height=150, key=f"txt_{file.name}")
                except Exception as e:
                    st.error(f"❌ 解析 {file.name} 失败: 请检查网络连接或 API Key 是否有效。")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

            # API 频率保护
            time.sleep(2)

    if processed_count > 0:
        st.success(f"🎉 任务完成！共成功处理 {processed_count} 个文件。")
        st.download_button(
            label="📦 一键打包下载全部高精度 Markdown (.zip)",
            data=zip_buffer.getvalue(),
            file_name="VLM_学术深度解析包.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True
        )
        try:
                    # ...上面是你原本正确的解析代码...
                    markdown_text = parse_document(temp_path, file.name, user_api_key)
                    # ...中间的代码省略...
                    
        except Exception as e:
                    # 👇 注意下面这行的缩进，并且去掉了 file_name，换成了真实错误 e
                    st.error(f"❌ 解析失败，系统底层报错为: {str(e)}")
