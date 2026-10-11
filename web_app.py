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

    with st.expander("👉 点击查看 API Key 免费获取保姆级教程"):
        st.markdown("""
        **1. 访问官网**
        打开浏览器访问 `platform.deepseek.com`，使用手机号或微信登录。

        **2. 创建密钥**
        点击左侧菜单的 **API Keys**，点击 **创建 API Key**，随意起个名字（如“文献解析”）。

        **3. 复制保存（非常重要）**
        系统会生成一串以 `sk-` 开头的代码。**务必立刻点击复制并保存到备忘录**。一旦关闭窗口，这串完整代码将永远隐藏！

        **4. 填入系统**
        将这串 `sk-` 开头的代码粘贴到上方输入框，即可解锁解析引擎！新用户自动获赠的免费额度，足够解析上百篇论文。
        """)

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
# 4. 全格式 AI 深度解析引擎
def parse_document(file_path, file_name, api_key):
    if not api_key:
        raise Exception("⚠️ 请先在左侧侧边栏输入 DeepSeek API Key！全格式 AI 分析需要大模型支持。")

    text_content = ""

    # 【第一步：底层文本提取】根据文件类型采取不同提取策略
    if file_name.lower().endswith('.pdf'):
        st.info(f"📄 正在提取 PDF 文本...")
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text_content += extracted + "\n"
        except Exception as e:
            raise Exception(f"PDF 文本读取失败: {str(e)}")
    else:
        st.info(f"📊 正在提取 {file_name} 的结构化数据...")
        try:
            md = MarkItDown()
            result = md.convert(file_path)
            text_content = result.text_content
        except Exception as e:
            raise Exception(f"文档底层数据提取失败: {str(e)}")

    if not text_content or len(text_content.strip()) < 10:
        raise Exception("未能从文档中提取到有效文字，请确保它不是纯图片。")

    # 【第二步：统一移交 DeepSeek 进行 AI 深度洗稿与重构】
    st.info(f"🤖 提取成功！已移交 DeepSeek 引擎进行 AI 深度重构与排版...")
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system",
                 "content": "你是一个专业的学术文档与数据排版分析助手。请将用户提供的未格式化文本或粗糙的表格数据，重新整理成结构清晰、排版整洁的 Markdown 格式。要求：1. 修正乱码与错别字；2. 完美理顺表格行数与列数的数据对应关系；3. 保持学术严谨性，不遗漏关键数据。"},
                {"role": "user", "content": f"请重构并优化以下提取自《{file_name}》的文本数据：\n\n{text_content}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"DeepSeek AI 分析异常: {str(e)}")

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