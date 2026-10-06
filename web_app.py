import streamlit as st
from markitdown import MarkItDown
from openai import OpenAI
import pdfplumber
import os
import zipfile
import io
import time

# 1. 全局配置
st.set_page_config(page_title="文献解析舱 2.0 | DeepSeek 驱动", page_icon="⚡", layout="wide")

# 2. 侧边栏：API Key 防蹭额度设置 (核心升级)
with st.sidebar:
    st.markdown("### ⚙ 核心引擎设置")
    user_api_key = st.text_input("🔑 请输入 DeepSeek API Key (用于 PDF 深度解析)", type="password")
    if user_api_key:
        st.success("✅ 密钥已就绪，文本重构引擎已激活")
    st.markdown("---")
    st.markdown("💡 **没有 Key 怎么办？**\n前往 DeepSeek 开放平台 (platform.deepseek.com) 注册，1分钟即可获取。")
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
    <h1 style="margin:0; font-weight:800;">⚡ 智能文献解析舱 <span style="color:#F59E0B;">2.0 终极版</span></h1>
    <p style="opacity:0.9; margin-top:10px;">搭载 DeepSeek 大语言模型引擎，彻底攻克排版错位与文本提取难题</p>
</div>
""", unsafe_allow_html=True)


# 4. 混合双擎解析函数
def parse_document(file_path, file_name, api_key):
    # 【引擎 A】针对 PDF 启用 DeepSeek 大模型进行学术重构
    if file_name.lower().endswith('.pdf'):
        if not api_key:
            st.warning(f"⚠️ 解析 {file_name} 需要大模型支持，请先在左侧侧边栏输入你的 API Key！")
            return None

        st.info(f"📄 检测到 PDF 文献，已启动 DeepSeek 解析引擎...")

        # 4.1 提取 PDF 纯文本内容
        text_content = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text_content += extracted + "\n"
        except Exception as e:
            raise Exception(f"PDF 文本读取失败: {str(e)}")

        if len(text_content.strip()) < 10:
            raise Exception("未能从文档中提取到有效文字，请确保它不是纯图片扫描件。")

        # 4.2 调用 DeepSeek 进行学术级洗稿与表格重构
        try:
            client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system",
                     "content": "你是一个专业的学术文档排版助手。请将用户提供的未格式化文本，重新整理成结构清晰、排版整洁的 Markdown 格式。请重点修正乱码错别字，并理顺跨页表格的数据对应关系。"},
                    {"role": "user", "content": f"请重构以下提取自《{file_name}》的文本：\n\n{text_content}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"DeepSeek 接口调用异常: {str(e)}")

    # 【引擎 B】针对结构化数据回退使用 MarkItDown
    else:
        st.info(f"📊 检测到结构化数据，使用 MarkItDown 高速提取...")
        md = MarkItDown()
        result = md.convert(file_path)
        return result.text_content


# 5. 核心交互区
uploaded_files = st.file_uploader(
    "拖拽文件至此开启混合解析 (支持批量上传 PDF / XLSX / DOCX 等)",
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
                    # 输出真实系统报错，方便排查
                    st.error(f"❌ 解析 {file.name} 失败，系统底层报错为: {str(e)}")
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
            file_name="DeepSeek_学术深度解析包.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True
        )