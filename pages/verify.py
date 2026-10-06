import hashlib
import importlib.util

import streamlit as st

from core import analyze_job_text, extract_image_text, extract_job_page


st.markdown(
    """
    <section class="ms-page-heading ms-glass">
      <span class="ms-kicker">MULTI-SOURCE VERIFICATION · 多源验证</span>
      <h1>AI Recruitment Security Audit</h1>
      <p>提交招聘文字、职位链接或聊天截图。系统会先提取内容，再生成可解释的风险报告。</p>
    </section>
    """,
    unsafe_allow_html=True,
)

ocr_available = bool(
    importlib.util.find_spec("rapidocr") and importlib.util.find_spec("onnxruntime")
)
api_key_ready = bool(str(st.session_state.get("api_key", "")).strip())
status_columns = st.columns(3)
status_columns[0].markdown(
    '<div class="ms-status"><i class="green"></i> 中文 / English ready</div>',
    unsafe_allow_html=True,
)
status_columns[1].markdown(
    f'<div class="ms-status"><i class="{"green" if ocr_available else "amber"}"></i> '
    f'{"OCR engine ready" if ocr_available else "OCR install required"}</div>',
    unsafe_allow_html=True,
)
status_columns[2].markdown(
    f'<div class="ms-status"><i class="{"green" if api_key_ready else "amber"}"></i> '
    f'{"AI key ready" if api_key_ready else "AI key required"}</div>',
    unsafe_allow_html=True,
)

mode_options = ["📝 招聘文字", "🔗 职位链接", "📷 聊天截图 / 海报"]
preferred_input = st.session_state.pop("preferred_input", "")
if preferred_input:
    st.session_state["verify_mode"] = (
        mode_options[2] if preferred_input == "image" else mode_options[0]
    )
st.session_state.setdefault("verify_mode", mode_options[0])

mode = st.radio(
    "输入方式",
    mode_options,
    horizontal=True,
    label_visibility="collapsed",
    key="verify_mode",
)

source_text = ""
source_url = ""
source_type = mode

left, right = st.columns([1.45, 0.75], gap="large")

with left:
    st.markdown('<div class="ms-panel-title">AUDIT INPUT · 审查内容 <i></i></div>', unsafe_allow_html=True)

    if mode == "📝 招聘文字":
        source_text = st.text_area(
            "粘贴 Job Description、招聘广告或 HR 聊天记录",
            height=330,
            max_chars=20_000,
            placeholder=(
                "支持简体、繁體、English 和中英混合内容。\n\n"
                "例如：Graduate Management Trainee, no experience required, "
                "contact us on WhatsApp and pay a training deposit..."
            ),
            key="verify_text_content",
        )

    elif mode == "🔗 职位链接":
        url_input = st.text_input(
            "职位网页链接",
            placeholder="https://example.com/jobs/graduate-programme",
            key="verify_url_input",
        )
        current_url_input = url_input.strip()
        if st.session_state.get("_last_verify_url") != current_url_input:
            st.session_state["_last_verify_url"] = current_url_input
            st.session_state["job_url"] = ""
            st.session_state["url_content"] = ""
            st.session_state["url_extracted_digest"] = ""
            st.session_state["url_extract_notice"] = ""
            st.session_state["url_extract_error"] = ""

        if st.button("读取职位网页 / Extract Job Page", use_container_width=True):
            st.session_state["url_extract_notice"] = ""
            st.session_state["url_extract_error"] = ""
            try:
                with st.spinner("正在安全读取网页正文……"):
                    safe_url, content = extract_job_page(url_input)
                st.session_state["job_url"] = safe_url
                st.session_state["url_content"] = content
                st.session_state["url_extracted_digest"] = hashlib.sha256(
                    content.encode("utf-8")
                ).hexdigest()
                st.session_state["url_extract_notice"] = (
                    f"提取成功，共读取 {len(content):,} 个字符。请核对后再分析。"
                )
            except ValueError as error:
                # Do not erase text the user may already have pasted manually.
                st.session_state["url_extract_error"] = str(error)
            except RuntimeError as error:
                st.session_state["url_extract_error"] = str(error)
            except Exception as error:
                st.session_state["url_extract_error"] = (
                    f"网页读取程序出现异常（{type(error).__name__}）。"
                    "请直接粘贴职位文字，或上传截图。"
                )

        if st.session_state.get("url_extract_notice"):
            st.success(st.session_state["url_extract_notice"])
        if st.session_state.get("url_extract_error"):
            st.warning(st.session_state["url_extract_error"])
            st.info("你仍然可以把官网上的职位文字复制到下方，不会影响 AI 审查。")

        source_url = st.session_state.get("job_url") or current_url_input
        source_text = st.text_area(
            "职位正文（自动提取失败时，可直接粘贴到这里）",
            height=270,
            max_chars=20_000,
            key="url_content",
            placeholder=(
                "方法一：点击上方按钮自动读取；\n"
                "方法二：如果官网需要登录或动态加载，直接复制职位正文并粘贴到这里。"
            ),
        )
        current_digest = hashlib.sha256(source_text.encode("utf-8")).hexdigest() if source_text else ""
        auto_extracted = bool(
            source_text
            and current_digest == st.session_state.get("url_extracted_digest", "")
        )
        source_type = "职位链接（自动提取）" if auto_extracted else "职位链接（手工粘贴或已编辑）"
        origin_label = "自动提取" if auto_extracted else "手工粘贴 / 已编辑"
        if source_text:
            st.caption(
                f"内容来源：{origin_label} · 当前 {len(source_text):,}/20,000 字符"
                + (f" · 最终网址：{source_url}" if source_url else "")
            )
        else:
            st.caption(
                "支持大多数公开官网及其 JobPosting 数据。需要登录、安全验证或纯 JavaScript "
                "加载的页面无法强行绕过，请粘贴正文或上传截图。"
            )

    else:
        if not ocr_available:
            st.warning(
                "当前使用云端稳定版：为了避免部署时安装大型 OCR 组件失败，"
                "图片文字识别暂时关闭。你可以把截图中的文字复制到“招聘文字”模式分析。"
            )
        uploaded_file = st.file_uploader(
            "上传 PNG、JPG、JPEG 或 WEBP",
            type=["png", "jpg", "jpeg", "webp"],
            key="verify_image_upload",
        )
        image_digest = ""
        if uploaded_file is not None:
            image_digest = hashlib.sha256(uploaded_file.getvalue()).hexdigest()
        if st.session_state.get("_last_verify_image") != image_digest:
            st.session_state["_last_verify_image"] = image_digest
            st.session_state["ocr_content"] = ""

        if uploaded_file is not None:
            image_col, action_col = st.columns([1, 1])
            with image_col:
                st.image(uploaded_file, caption="待识别图片", use_container_width=True)
            with action_col:
                st.info("先识别文字，再检查公司名、金额、邮箱和网址。")
                if st.button(
                    "识别图片文字 / Run OCR",
                    use_container_width=True,
                    disabled=not ocr_available,
                ):
                    # A failed OCR attempt must not reuse a previous image's result.
                    st.session_state["ocr_content"] = ""
                    try:
                        with st.spinner("正在识别中英文文字，首次使用可能较慢……"):
                            st.session_state["ocr_content"] = extract_image_text(uploaded_file)
                        st.success("文字识别完成。")
                    except ValueError as error:
                        st.warning(str(error))
                    except Exception as error:
                        st.error(f"OCR 运行失败：{type(error).__name__}。请检查依赖安装。")

        source_text = st.text_area(
            "OCR 识别结果（可修改）",
            height=230,
            key="ocr_content",
            placeholder="点击“识别图片文字”后，文字会显示在这里。",
        )

with right:
    st.markdown('<div class="ms-panel-title">AUDIT FOCUS · 审查重点 <i></i></div>', unsafe_allow_html=True)
    focus_items = [
        ("💳", "付款与培训贷", "押金、垫资、设备费、培训费"),
        ("🪪", "身份与隐私", "护照、银行卡、验证码、住址"),
        ("🏢", "公司真实性", "企业名称、邮箱域名、合同主体"),
        ("✈️", "跨境与签证", "IANG、工作签证、境外培训"),
        ("💬", "招聘流程", "私聊、无面试录用、时间压力"),
        ("🔗", "链接与域名", "短链接、仿冒域名、异常跳转"),
    ]
    for icon, title, description in focus_items:
        st.markdown(
            f'<div class="ms-mini-card"><b>{icon} {title}</b><span>{description}</span></div>',
            unsafe_allow_html=True,
        )

st.markdown("<div class='ms-rule'></div>", unsafe_allow_html=True)
if st.button("🛡️ RUN AI AUDIT · 开始 AI 安全审查", type="primary", use_container_width=True):
    api_key = str(st.session_state.get("api_key", "")).strip()
    cleaned_text = source_text.strip()

    if not api_key:
        st.error("请打开左侧设置，先输入 DeepSeek API Key。")
    elif not cleaned_text:
        st.warning("请先输入招聘文字、读取网页或在职位正文框手工粘贴内容，也可以完成图片 OCR。")
    else:
        try:
            with st.spinner("AI 正在核对原文证据、跨境风险与 Offer 合规事项……"):
                result = analyze_job_text(
                    api_key=api_key,
                    model_name=st.session_state.get("model_name", "deepseek-flash"),
                    content=cleaned_text,
                    output_language=st.session_state.get("report_language", "简体中文"),
                    source_type=source_type,
                    source_url=source_url,
                )
            st.session_state["latest_analysis"] = result
            st.session_state["analysis_source_text"] = cleaned_text
            st.session_state["analysis_source_url"] = source_url
            st.session_state["analysis_source_type"] = source_type
            st.switch_page("pages/report.py")
        except Exception as error:
            error_name = type(error).__name__
            if error_name == "AuthenticationError":
                st.error("API Key 无效，请检查 DeepSeek 密钥。")
            elif error_name == "RateLimitError":
                st.error("请求过于频繁或余额不足，请稍后再试。")
            elif error_name == "APIConnectionError":
                st.error("无法连接 DeepSeek，请检查网络。")
            else:
                st.error(f"分析失败：{error_name}。请重试；如持续出现，请检查模型名称与网络。")

st.caption("Mindshield 只做风险筛查，不会替代警方、学校就业中心、招聘平台或专业法律意见。")
