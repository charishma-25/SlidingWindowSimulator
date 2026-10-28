import streamlit as st
import pandas as pd
import altair as alt
from analytics import (
    comparison_summary,
    run_comparison,
    selected_loss_sweep,
    window_sweep,
)

from protocols import parse_lost_frames, simulate_protocol

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="FrameFlow | Sliding Window Simulator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

.stApp {
    background:
        radial-gradient(circle at 82% -8%, rgba(88, 112, 255, .22), transparent 34rem),
        radial-gradient(circle at 8% 18%, rgba(39, 211, 195, .08), transparent 28rem),
        #080d19;
    color: #f1f5f9;
    font-family: 'DM Sans', sans-serif;
}

:root { --primary-color:#62dfd1; }

[data-testid="stHeader"] {
    background: rgba(8, 13, 25, .72);
    backdrop-filter: blur(14px);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1a2e 0%, #0b1322 100%);
    border-right: 1px solid rgba(121, 145, 185, .2);
    box-shadow: 12px 0 40px rgba(0, 0, 0, .16);
}

[data-testid="stSidebar"] * { color: #e6eefb; }
[data-testid="stSidebar"] { position:relative; }
[data-testid="stSidebar"] .block-container { padding:1.35rem 1.2rem 2rem; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#91a3bd; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color:#bdcbe0!important;font-size:12px;font-weight:600; }
[data-testid="stSidebar"] hr { border-color:rgba(135,158,194,.17);margin:1.1rem 0; }
.sidebar-brand { display:flex;align-items:center;gap:11px;padding:7px 0 15px; }
.sidebar-brand-mark { width:38px;height:38px;display:grid;place-items:center;border:1px solid rgba(102,224,215,.25);border-radius:12px;background:linear-gradient(145deg,rgba(30,97,111,.38),rgba(30,48,82,.55));color:#70e7de;font:700 18px 'Space Grotesk',sans-serif;box-shadow:0 5px 18px rgba(0,0,0,.16); }
.sidebar-brand-name { color:#edf3ff;font:700 17px 'Space Grotesk',sans-serif;letter-spacing:-.4px; }
.sidebar-brand-sub { color:#7f92ae;font-size:9px;font-weight:700;letter-spacing:1.4px;margin-top:3px; }
.sidebar-section { color:#91a7c5;font-size:9px;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;margin:15px 0 9px; }
.sidebar-note { padding:10px 11px;border:1px solid rgba(119,147,191,.14);border-radius:9px;background:rgba(18,33,54,.7);color:#94a8c3;font-size:10px;line-height:1.55;margin:4px 0 11px; }
[data-testid="stSidebar"] .stButton>button,
[data-testid="stSidebar"] .stButton>button * { position:relative;color:#fff!important;-webkit-text-fill-color:#fff!important; }
[data-testid="stSidebar"] .stButton>button { min-height:50px;border-radius:12px;background:linear-gradient(105deg,#168b91 0%,#4d63c6 100%);border:1px solid rgba(183,207,255,.38);font-size:12px;font-weight:800;letter-spacing:.9px;box-shadow:0 9px 24px rgba(61,117,204,.3),inset 0 1px rgba(255,255,255,.2);transition:transform .16s ease,filter .16s ease,box-shadow .16s ease; }
[data-testid="stSidebar"] .stButton>button::before { content:"▶";display:inline-block;margin-right:10px;font-size:11px; }
[data-testid="stSidebar"] .stButton>button:hover { filter:brightness(1.08);transform:translateY(-2px);box-shadow:0 13px 28px rgba(61,173,204,.34),inset 0 1px rgba(255,255,255,.48); }
[data-testid="stSidebar"] .stButton>button:active { transform:translateY(0) scale(.985); }
[data-testid="stSidebar"] .stButton>button:focus-visible { outline:2px solid #a9c4ff;outline-offset:3px; }
[data-testid="stSidebar"] div[data-baseweb="select"]>div { background:#111e31;border-color:#334761; }
[data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] { background:#62dfd1!important;border:2px solid #62dfd1!important;box-shadow:0 0 0 4px rgba(98,223,209,.14)!important; }
[data-testid="stSidebar"] input[type="range"] { accent-color:#62dfd1; }

.block-container {
    max-width: 1440px;
    padding: 3rem 2.5rem 4rem;
}

[data-testid="stSidebar"] .block-container {
    padding: 2rem 1.35rem 2.5rem;
}

[data-testid="stSidebar"] hr {
    border-color: rgba(121, 145, 185, .2);
}

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #f5f8ff !important;
    letter-spacing: -.025em;
}

h2 {
    margin-top: 2.2rem !important;
    margin-bottom: 1rem !important;
}

h3 {
    margin-top: .4rem !important;
}

.hero {
    position: relative;
    overflow: hidden;
    background:
        radial-gradient(circle at 78% 48%, rgba(65, 104, 203, .24), transparent 19rem),
        linear-gradient(115deg, #102d43 0%, #18223f 55%, #25254d 100%);
    border: 1px solid rgba(131, 159, 220, .3);
    border-radius: 22px;
    padding: clamp(2rem, 5vw, 3.35rem);
    margin-bottom: 1.7rem;
    min-height: 286px;
    display: flex;
    align-items: center;
    box-shadow: 0 24px 65px rgba(0, 0, 0, .28), inset 0 1px rgba(255,255,255,.06);
}

.hero::after {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    opacity: .16;
    background-image: linear-gradient(rgba(176,199,255,.12) 1px, transparent 1px), linear-gradient(90deg, rgba(176,199,255,.12) 1px, transparent 1px);
    background-size: 36px 36px;
    mask-image: linear-gradient(90deg, transparent 38%, #000 100%);
}

.hero-copy { position:relative; z-index:2; max-width:700px; }
.hero-kicker { color:#72e9df; font-size:10px; font-weight:800; letter-spacing:1.7px; text-transform:uppercase; margin:0 0 17px; }
.hero-heading { color:#f7f9ff; font:700 clamp(32px,4.1vw,52px)/1.12 'Space Grotesk',sans-serif; letter-spacing:-1.7px; margin:0 0 14px; }
.hero-heading span { color:#8ea6ff; }
.hero-visual { position:absolute; z-index:1; right:5%; top:50%; transform:translateY(-50%); width:min(34%,330px); opacity:.95; }
.hero-visual svg { width:100%; overflow:visible; filter:drop-shadow(0 12px 30px rgba(7,15,35,.25)); }
.hero-desc { max-width:590px; color:#b8c8dd; font-size:14px; line-height:1.8; }
.hero-meta { display:flex; gap:8px; margin-top:20px; flex-wrap:wrap; }
.hero-chip { color:#c3d2e8; border:1px solid rgba(156,180,223,.22); background:rgba(7,17,35,.24); border-radius:7px; padding:6px 10px; font-size:10px; font-weight:600; }
@media (max-width: 760px) {
    .hero { min-height:0; padding:2rem 1.5rem; }
    .hero-visual { opacity:.16; right:-4%; width:55%; }
    .hero-heading { font-size:clamp(32px,8vw,44px); }
}

.project-profile { position:relative; overflow:hidden; padding:clamp(22px,3vw,34px); margin:8px 0 24px; border:1px solid rgba(125,155,210,.25); border-radius:20px; background:radial-gradient(ellipse at 100% 0%,rgba(92,111,207,.16),transparent 38%),linear-gradient(140deg,#111d31,#11182a 62%,#171a35); box-shadow:0 18px 46px rgba(0,0,0,.2),inset 0 1px rgba(255,255,255,.035); }
.profile-head { display:flex; justify-content:space-between; align-items:flex-start; gap:18px; padding-bottom:24px; border-bottom:1px solid rgba(146,165,197,.16); }
.profile-eyebrow { color:#72e3d5; font-size:10px; font-weight:800; letter-spacing:1.6px; text-transform:uppercase; margin-bottom:12px; }
.profile-title { color:#f4f7ff; font:700 clamp(22px,3vw,32px)/1.2 'Space Grotesk',sans-serif; letter-spacing:-.8px; }
.profile-subtitle { color:#9eafc7; font-size:12px; margin-top:8px; }
.profile-mark { width:58px;height:58px; flex:none; display:grid;place-items:center;border:1px solid rgba(118,150,226,.32);border-radius:17px;background:linear-gradient(145deg,rgba(78,111,190,.25),rgba(37,55,92,.3));color:#c0d0ff;font:700 17px 'Space Grotesk',sans-serif;letter-spacing:.5px;box-shadow:inset 0 1px rgba(255,255,255,.06); }
.profile-section-label { color:#8397b3;font-size:10px;font-weight:800;letter-spacing:1.25px;text-transform:uppercase;margin:23px 0 11px; }
.member-grid { display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:11px; }
.member-card { min-width:0;padding:15px 15px 14px;border:1px solid rgba(136,158,194,.16);border-radius:12px;background:linear-gradient(145deg,rgba(25,39,62,.9),rgba(18,29,47,.92)); }
.member-top { display:flex;align-items:center;gap:11px; }
.member-avatar { width:34px;height:34px;flex:none;display:grid;place-items:center;border-radius:10px;background:#203757;color:#9fc0ff;font:700 11px 'Space Grotesk',sans-serif; }
.member-name { color:#e8eef9;font-size:13px;font-weight:700;line-height:1.35; }
.member-role { color:#8397b3;font-size:10px;margin-top:3px; }
.member-id { color:#95a8c2;font:500 10px 'DM Sans',sans-serif;margin-top:13px;padding-top:10px;border-top:1px solid rgba(136,158,194,.12); }
.mentor-row { display:flex;align-items:center;gap:16px;margin-top:15px;padding:20px 24px;min-height:86px;border:1px solid rgba(114,227,213,.22);border-radius:14px;background:linear-gradient(100deg,rgba(20,51,59,.62),rgba(21,34,53,.78));box-shadow:inset 0 1px rgba(255,255,255,.025); }
.mentor-avatar { width:46px;height:46px;flex:none;display:grid;place-items:center;border-radius:13px;background:rgba(64,157,148,.16);border:1px solid rgba(114,227,213,.24);color:#8ce6db;font:700 10px 'Space Grotesk',sans-serif; }
.mentor-name { color:#eef6ff;font-size:13px;font-weight:700; }
.mentor-role { color:#9aafc3;font-size:11px;margin-top:4px; }
.profile-footer { margin-left:auto;color:#7186a4;font-size:9px;font-weight:700;letter-spacing:1px;text-transform:uppercase; }
@media(max-width:700px) { .member-grid{grid-template-columns:1fr}.profile-mark{width:46px;height:46px}.profile-footer{display:none} }

.welcome { position:relative;overflow:hidden;margin:26px 0 18px;padding:4px 0 12px; }
.welcome-kicker { color:#73e2d7;font-size:10px;font-weight:800;letter-spacing:1.6px;text-transform:uppercase;margin-bottom:10px; }
.welcome-title { color:#f3f6ff;font:700 clamp(26px,3.4vw,38px)/1.16 'Space Grotesk',sans-serif;letter-spacing:-1px; }
.welcome-title span { color:#91a8ff; }
.welcome-copy { color:#9aacc5;font-size:13px;line-height:1.7;max-width:700px;margin-top:9px; }
.welcome-grid { display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:22px 0 14px; }
.welcome-card { position:relative;overflow:hidden;min-height:178px;padding:21px 20px 18px;border:1px solid rgba(128,153,205,.22);border-radius:15px;background:linear-gradient(145deg,rgba(19,35,57,.96),rgba(15,23,40,.98));box-shadow:0 10px 28px rgba(0,0,0,.14);transition:transform .2s ease,border-color .2s ease; }
.welcome-card:hover { transform:translateY(-3px);border-color:rgba(111,143,238,.55); }
.welcome-card::after { content:attr(data-step);position:absolute;right:15px;top:8px;color:rgba(142,166,255,.09);font:700 48px 'Space Grotesk',sans-serif; }
.welcome-card-top { display:flex;align-items:center;gap:12px;margin-bottom:16px; }
.welcome-icon { width:39px;height:39px;flex:none;display:grid;place-items:center;border-radius:12px;background:rgba(76,111,191,.17);border:1px solid rgba(129,158,235,.18);color:#a9bcff;font-size:17px; }
.welcome-card:nth-child(2) .welcome-icon { background:rgba(81,179,160,.12);border-color:rgba(92,208,180,.2);color:#77e3c9; }
.welcome-card:nth-child(3) .welcome-icon { background:rgba(155,124,232,.14);border-color:rgba(177,146,246,.2);color:#c1a7ff; }
.welcome-card-title { color:#eef3ff;font:600 15px 'Space Grotesk',sans-serif; }
.welcome-card-copy { color:#9aacc5;font-size:12px;line-height:1.7; }
.welcome-cta { display:flex;align-items:center;gap:14px;margin:16px 0 4px;padding:17px 20px;border:1px solid rgba(91,151,218,.28);border-radius:13px;background:linear-gradient(100deg,rgba(28,67,101,.6),rgba(27,43,78,.72)); }
.welcome-cta-mark { width:34px;height:34px;flex:none;display:grid;place-items:center;border-radius:10px;background:rgba(91,172,232,.14);color:#80c7ff;font-size:16px; }
.welcome-cta-title { color:#e8f2ff;font-size:13px;font-weight:700; }
.welcome-cta-copy { color:#9ab2ce;font-size:11px;margin-top:3px; }
@media(max-width:760px) { .welcome-grid{grid-template-columns:1fr}.welcome-card{min-height:0}.welcome-card::after{font-size:38px} }


div[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(135deg, rgba(20, 41, 67, .94), rgba(23, 29, 56, .94));
    border-color: rgba(128, 153, 205, .28) !important;
    border-radius: 18px;
    box-shadow: 0 12px 30px rgba(0, 0, 0, .12);
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: rgba(103, 232, 216, .4) !important;
    transform: translateY(-1px);
    transition: border-color .2s ease, transform .2s ease;
}

.metric-card {
    background: linear-gradient(145deg, rgba(21, 35, 58, .98), rgba(16, 24, 39, .98));
    border: 1px solid rgba(102, 132, 175, .34);
    border-radius: 17px;
    padding: 1.1rem 1.15rem;
    min-height: 120px;
    margin-bottom: .6rem;
    box-shadow: inset 0 1px rgba(255, 255, 255, .04);
}

.metric-label {
    color: #9eb0c9;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .6px;
}

.metric-value {
    color: #ffffff;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 29px;
    font-weight: 700;
    margin: 9px 0 4px;
}

.metric-note {
    color: #67e8d8;
    font-size: 11px;
}

.run-confirmation { display:flex;align-items:center;gap:13px;margin:16px 0 15px;padding:14px 17px;border:1px solid rgba(96,218,190,.3);border-radius:13px;background:linear-gradient(100deg,rgba(20,71,66,.62),rgba(23,48,72,.72));box-shadow:0 8px 26px rgba(0,0,0,.12),inset 0 1px rgba(255,255,255,.035);animation:result-arrive .45s ease-out both; }
.run-check { width:34px;height:34px;flex:none;display:grid;place-items:center;border-radius:11px;background:rgba(73,211,173,.15);border:1px solid rgba(105,230,190,.26);color:#7af0c7;font-size:18px;font-weight:800; }
.run-title { color:#eafff8;font-size:13px;font-weight:800; }
.run-detail { color:#a7c8c3;font-size:11px;margin-top:3px; }
.run-badge { margin-left:auto;color:#81e8c7;border:1px solid rgba(111,223,186,.22);border-radius:20px;padding:6px 9px;font-size:9px;font-weight:800;letter-spacing:1px;white-space:nowrap; }
@keyframes result-arrive { from { opacity:0;transform:translateY(8px); } to { opacity:1;transform:translateY(0); } }

.frame {
    text-align: center;
    border-radius: 11px;
    padding: 13px 3px;
    margin-bottom: 9px;
    border: 1px solid #334762;
    background: #17263c;
}

.frame-number {
    font-size: 17px;
    font-weight: 700;
    color: white;
}

.frame-label {
    font-size: 9px;
    margin-top: 6px;
    font-weight: 700;
}

.delivered {
    background: #103b37;
    border-color: #247f70;
}

.delivered .frame-label { color: #66f0c5; }

.lost {
    background: #4b202c;
    border-color: #a33c58;
}

.lost .frame-label { color: #ff9bb0; }

.transmitted {
    background: #25264e;
    border-color: #6961c9;
}

.transmitted .frame-label { color: #c4b5fd; }

.panel {
    background: #101a2c;
    border: 1px solid #263750;
    border-radius: 15px;
    padding: 18px;
    margin-bottom: 15px;
}

.stCaption {
    color: #91a3bd !important;
}

.stAlert {
    border-radius: 12px;
    border: 1px solid rgba(130, 157, 204, .28);
}

.stDataFrame {
    border: 1px solid rgba(128, 153, 205, .2);
    border-radius: 12px;
    overflow: hidden;
}

.log-row {
    background: #121f32;
    border-left: 3px solid #55e6e0;
    border-radius: 5px;
    padding: 10px 13px;
    margin: 6px 0;
    font-size: 13px;
    color: #dbe7f7;
    overflow-wrap: anywhere;
}

.log-row.warning { border-left-color: #f6ad55; }
.log-row.error { border-left-color: #fb7185; }
.log-row.ack { border-left-color: #5ee6b0; }

.stButton > button,
.stDownloadButton > button {
    background: linear-gradient(100deg, #55e6e0, #8b9dff);
    color: #081321 !important;
    font-weight: 700;
    border: none;
    border-radius: 10px;
    min-height: 44px;
    box-shadow: 0 8px 18px rgba(85, 230, 224, .12);
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    filter: brightness(1.08);
    border: none;
}

div[data-baseweb="select"] > div {
    background: #152239;
    border-color: #354863;
    border-radius: 9px;
}

div[data-baseweb="select"] > div:focus-within {
    border-color: #67e8d8;
    box-shadow: 0 0 0 1px #67e8d8;
}

.stSlider > div[data-baseweb="slider"] {
    padding-top: .35rem;
}

.small-footer {
    text-align: center;
    color: #91a3bd;
    font-size: 12px;
    padding: 25px 0 5px;
    line-height: 1.9;
}

@media (max-width: 900px) {
    .block-container {
        padding: 2rem 1rem 3rem;
    }

    .hero {
        padding: 2rem 1.35rem;
    }

    .hero::after {
        right: 1rem;
        opacity: .55;
    }
}
</style>
""", unsafe_allow_html=True)


# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
      <div class="sidebar-brand-mark">F</div>
      <div><div class="sidebar-brand-name">FrameFlow</div><div class="sidebar-brand-sub">COMPUTER NETWORKS LAB</div></div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    workspace = st.radio(
        "Workspace",
        ["Single Simulation", "Protocol Comparison", "Performance Analytics"],
        index=0,
        help="Choose the simulator view to open.",
    )
    st.divider()

    if workspace == "Single Simulation":
        st.markdown('<div class="sidebar-section">01 &nbsp; / &nbsp; Simulation setup</div>', unsafe_allow_html=True)
        protocol = st.selectbox("ARQ protocol", ["Go-Back-N", "Selective Repeat"])
        total_frames = st.slider("Number of frames", 5, 20, 10)
        window_size = st.slider("Sender window size", 1, min(10, total_frames), min(4, total_frames))
        st.markdown('<div class="sidebar-note">The sender can transmit up to the window size before waiting for acknowledgements.</div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section">02 &nbsp; / &nbsp; Channel conditions</div>', unsafe_allow_html=True)
        lost_frames_text = st.text_input(
            "Frames to Lose",
            placeholder="Example: 2, 5, 7",
            help="Enter the frame numbers whose original transmissions should be lost. Leave empty for no frame loss.",
            key="single_lost_frames_text",
        )
        st.caption("Enter the frame numbers whose original transmissions should be lost. Leave empty for no frame loss.")
        try:
            lost_frames = parse_lost_frames(lost_frames_text, total_frames)
            if lost_frames:
                st.info("Original transmissions lost: " + ", ".join(map(str, lost_frames)))
        except ValueError as error:
            lost_frames = None
            st.error(str(error))
            st.session_state.pop("result", None)
            st.session_state.pop("settings", None)

        st.divider()
        run = st.button("RUN SIMULATION", use_container_width=True, type="primary")
        st.caption("Set your parameters above, then run the experiment.")


def render_comparison_cards(results, total_frames):
    card_cols = st.columns(2)
    for col, protocol_name, color in zip(
        card_cols, ("Go-Back-N", "Selective Repeat"), ("#68a6ff", "#63e0c1")
    ):
        result = results[protocol_name]
        with col:
            with st.container(border=True):
                st.markdown(f"### <span style='color:{color}'>{protocol_name} ARQ</span>", unsafe_allow_html=True)
                st.caption(f"{total_frames} requested data frames")
                metrics = st.columns(3)
                metrics[0].metric("Delivered", f"{result['frames_delivered']}/{total_frames}")
                metrics[1].metric("Total transmissions", result["frames_sent"])
                metrics[2].metric("Retransmissions", result["retransmissions"])
                metrics = st.columns(3)
                metrics[0].metric("ACKs sent", result["ack_count"])
                metrics[1].metric("Channel failures", result["failure_count"])
                metrics[2].metric("Success rate", f"{result['success_rate']:.1f}%")
                st.progress(min(result["efficiency"] / 100, 1.0), text=f"Transmission efficiency · {result['efficiency']:.1f}%")
                st.caption("Retransmissions are additional data-frame attempts; retransmitted copies do not increase unique frames delivered.")


def comparison_charts(results):
    rows = []
    for protocol_name, result in results.items():
        rows.extend([
            {"Protocol": protocol_name, "Transmission type": "Original", "Count": result["original_transmissions"]},
            {"Protocol": protocol_name, "Transmission type": "Retransmission", "Count": result["retransmissions"]},
            {"Protocol": protocol_name, "Transmission type": "Total", "Count": result["frames_sent"]},
        ])
    data = pd.DataFrame(rows)
    colors = alt.Scale(domain=["Go-Back-N", "Selective Repeat"], range=["#68a6ff", "#63e0c1"])
    transmission_chart = alt.Chart(data).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X("Transmission type:N", title="Data-frame attempt type"),
        xOffset=alt.XOffset("Protocol:N"),
        y=alt.Y("Count:Q", title="Data-frame transmissions", scale=alt.Scale(domainMin=0)),
        color=alt.Color("Protocol:N", scale=colors),
        tooltip=["Protocol", "Transmission type", "Count"],
    ).properties(height=280)
    a, b = st.columns(2)
    with a:
        st.markdown("#### Transmission breakdown")
        st.altair_chart(transmission_chart, use_container_width=True)
    metric_rows = pd.DataFrame([
        {"Protocol": name, "Retransmissions": result["retransmissions"]}
        for name, result in results.items()
    ])
    with b:
        st.markdown("#### Recovery transmissions")
        retrans_chart = alt.Chart(metric_rows).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
            x=alt.X("Protocol:N", title=None, sort=None),
            y=alt.Y("Retransmissions:Q", title="Retransmitted data frames", scale=alt.Scale(domainMin=0)),
            color=alt.Color("Protocol:N", scale=colors, legend=None),
            tooltip=["Protocol", "Retransmissions"],
        ).properties(height=280)
        st.altair_chart(retrans_chart, use_container_width=True)
    efficiency_data = pd.DataFrame([
        {"Protocol": name, "Transmission efficiency": result["efficiency"]}
        for name, result in results.items()
    ])
    efficiency_chart = alt.Chart(efficiency_data).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
        x=alt.X("Protocol:N", title=None, sort=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Transmission efficiency:Q", title="Unique deliveries per data-frame attempt (%)", scale=alt.Scale(domain=[0, 100])),
        color=alt.Color("Protocol:N", scale=colors, legend=None),
        tooltip=["Protocol", alt.Tooltip("Transmission efficiency:Q", format=".1f")],
    ).properties(height=220)
    st.markdown("#### Transmission efficiency")
    st.altair_chart(efficiency_chart, use_container_width=True)
    st.caption("Delivery success remains in the result cards. Since selected losses recover on retransmission, success rate is normally 100%; transmission efficiency shows the extra-attempt cost.")


if workspace == "Protocol Comparison":
    st.markdown("# Protocol Comparison")
    st.markdown("Compare Go-Back-N and Selective Repeat using the same deterministic selected frame losses.")
    with st.form("comparison_form", border=True):
        st.markdown("### Shared experiment settings")
        c1, c2, c3 = st.columns(3)
        cmp_frames = c1.number_input("Total frames", 1, 200, 20, key="cmp_frames")
        cmp_window = c2.number_input("Window size", 1, int(cmp_frames), min(4, int(cmp_frames)), key="cmp_window")
        cmp_losses_text = c3.text_input(
            "Frames to Lose", placeholder="Example: 2, 5, 7", key="cmp_losses_text",
            help="Enter the frame numbers whose original transmissions should be lost. Leave empty for no frame loss.",
        )
        st.caption("Enter the frame numbers whose original transmissions should be lost. Leave empty for no frame loss.")
        run_comparison_button = st.form_submit_button("RUN COMPARISON", type="primary", use_container_width=True)
    if run_comparison_button:
        st.session_state.pop("comparison_results", None)
        st.session_state.pop("comparison_settings", None)
        try:
            cmp_losses = parse_lost_frames(cmp_losses_text, int(cmp_frames))
            st.session_state["comparison_results"] = run_comparison(
                int(cmp_frames), int(cmp_window), cmp_losses
            )
            st.session_state["comparison_settings"] = (int(cmp_frames), int(cmp_window), cmp_losses)
        except ValueError as error:
            st.error(str(error))
    if "comparison_results" in st.session_state:
        saved_frames, saved_window, saved_losses = st.session_state["comparison_settings"]
        results = st.session_state["comparison_results"]
        losses_label = ", ".join(map(str, saved_losses)) if saved_losses else "None"
        st.caption(f"Shared settings · {saved_frames} frames · window {saved_window} · frames to lose: {losses_label}")
        render_comparison_cards(results, saved_frames)
        st.markdown("### Measured comparison")
        st.info(comparison_summary(results))
        comparison_charts(results)
        with st.expander("How are metrics calculated?"):
            st.markdown(
                "- **Delivery success rate:** unique frames delivered ÷ requested frames × 100.\n"
                "- **Transmission efficiency:** unique frames delivered ÷ all data-frame attempts × 100.\n"
                "- **Retransmissions:** data-frame attempts beyond the first attempt for each requested frame.\n"
                "- **Retransmission overhead:** retransmissions ÷ all data-frame attempts × 100.\n"
                "- ACK count is the number of ACK events emitted by the simulation; channel failures count dropped transmission attempts.\n\n"
                "The simulator has no elapsed-time model, so throughput is not calculated. The same selected original frame attempts are lost for both protocols."
            )
    st.markdown("#### Protocol behavior")
    st.caption("Go-Back-N may resend later outstanding frames after a gap; Selective Repeat retries only missing frames. The measured result depends on the loss pattern and window size.")
    st.stop()


if workspace == "Performance Analytics":
    st.markdown("# Performance Analytics")
    st.markdown("Explore measured protocol performance. Each chart point comes from fresh protocol simulations.")
    with st.form("analytics_form", border=True):
        st.markdown("### Experiment settings")
        a1, a2, a3 = st.columns(3)
        analytics_frames = a1.number_input("Total frames", 1, 100, 20, key="analytics_frames")
        analytics_window = a2.number_input("Window size", 1, int(analytics_frames), min(4, int(analytics_frames)), key="analytics_window")
        analytics_losses_text = a3.text_input(
            "Frames to Lose", placeholder="Example: 2, 5, 7", key="analytics_losses_text",
            help="Enter the frame numbers whose original transmissions should be lost. Leave empty for no frame loss.",
        )
        st.caption("Enter the frame numbers whose original transmissions should be lost. Leave empty for no frame loss.")
        run_analytics_button = st.form_submit_button("RUN ANALYTICS", type="primary", use_container_width=True)
    if run_analytics_button:
        st.session_state.pop("analytics_results", None)
        try:
            analytics_losses = parse_lost_frames(analytics_losses_text, int(analytics_frames))
            base_results = run_comparison(int(analytics_frames), int(analytics_window), analytics_losses)
            ws_rows = window_sweep(int(analytics_frames), int(analytics_frames), analytics_losses)
            loss_rows = selected_loss_sweep(int(analytics_frames), int(analytics_window), analytics_losses)
            st.session_state["analytics_results"] = {
                "base": base_results, "window": ws_rows, "loss": loss_rows,
                "frames": int(analytics_frames), "window_size": int(analytics_window),
                "lost_frames": analytics_losses,
            }
        except ValueError as error:
            st.error(str(error))
    if "analytics_results" in st.session_state:
        analytics = st.session_state["analytics_results"]
        results = analytics["base"]
        selected_label = ", ".join(map(str, analytics["lost_frames"])) or "None"
        st.caption(
            f"Base run · {analytics['frames']} frames · window {analytics['window_size']} · "
            f"frames to lose: {selected_label}"
        )
        kpis = st.columns(5)
        labels = [
            ("Frames delivered", sum(r["frames_delivered"] for r in results.values())),
            ("Frame transmissions", sum(r["frames_sent"] for r in results.values())),
            ("Retransmissions", sum(r["retransmissions"] for r in results.values())),
            ("Delivery success", f"{sum(r['success_rate'] for r in results.values()) / 2:.1f}%"),
            ("Transmission efficiency", f"{sum(r['efficiency'] for r in results.values()) / 2:.1f}%"),
        ]
        for col, (label, value) in zip(kpis, labels):
            col.metric(label, value)
        st.caption("KPI totals combine both protocol runs; rates are the arithmetic mean of the two measured protocol rates.")
        comparison_charts(results)
        window_data = pd.DataFrame(analytics["window"])
        st.markdown("### Window size vs. transmission cost")
        window_chart = alt.Chart(window_data).mark_line(point=True).encode(
            x=alt.X("Window size:Q", title="Window size", scale=alt.Scale(domainMin=1)),
            y=alt.Y("Total transmissions:Q", title="Total data-frame transmissions"),
            color=alt.Color("Protocol:N", scale=alt.Scale(domain=["Go-Back-N", "Selective Repeat"], range=["#68a6ff", "#63e0c1"])),
            tooltip=["Window size", "Protocol", "Total transmissions", "Retransmissions"],
        ).properties(height=300)
        st.altair_chart(window_chart, use_container_width=True)
        st.caption("A fresh paired simulation was run at each window size. This implementation uses absolute frame numbers and does not model finite sequence-number wraparound, so window sizes 1 through the frame count are valid here.")
        st.markdown("### Number of Selected Lost Frames vs. Retransmissions")
        loss_data = pd.DataFrame(analytics["loss"])
        loss_chart = alt.Chart(loss_data).mark_line(point=True).encode(
            x=alt.X("Number of selected lost frames:Q", title="Number of original frames deliberately lost", scale=alt.Scale(domainMin=0)),
            y=alt.Y("Retransmissions:Q", title="Retransmitted data-frame attempts"),
            color=alt.Color("Protocol:N", scale=alt.Scale(domain=["Go-Back-N", "Selective Repeat"], range=["#68a6ff", "#63e0c1"])),
            tooltip=["Number of selected lost frames", "Selected frames", "Protocol", "Retransmissions"],
        ).properties(height=300)
        st.altair_chart(loss_chart, use_container_width=True)
        st.caption("Each point is a fresh deterministic simulation. The selected frame numbers are used first in ascending order; additional losses use the remaining frame numbers in ascending order. Both protocols receive the same selected list at each point.")
        st.markdown("### Interpretation")
        st.info(comparison_summary(results))
        st.caption("Generally, Go-Back-N can retransmit multiple outstanding frames following a loss, while Selective Repeat can retry individual missing frames. In real networks, a larger window can improve utilization but also expose more outstanding frames to recovery after a loss; this simulator does not model elapsed time. These are protocol behaviors; observed results above come from the selected simulations.")
        with st.expander("How are metrics calculated?"):
            st.markdown(
                "- **Delivery success rate:** unique frames successfully delivered ÷ total requested × 100.\n"
                "- **Transmission efficiency:** unique frames delivered ÷ total data-frame transmissions × 100.\n"
                "- **Retransmission count:** additional attempts beyond one original attempt per frame.\n"
                "- **Retransmission overhead:** retransmitted data-frame attempts ÷ total data-frame attempts × 100.\n"
                "- **Throughput:** N/A because the simulator does not model elapsed time; it reports logical frame-attempt counts."
            )
    st.stop()


# ==================== HERO ====================
if "result" not in st.session_state:
    st.markdown("""
    <div class="hero">
        <div class="hero-copy">
            <div class="hero-kicker">COMPUTER NETWORKS &nbsp;&middot;&nbsp; INTERACTIVE CASE STUDY</div>
            <div class="hero-heading">Sliding window<br><span>protocol simulator</span></div>
            <div class="hero-desc">Explore reliable data transmission, flow control, acknowledgements, and error recovery<br>with Go-Back-N and Selective Repeat ARQ.</div>
            <div class="hero-meta"><span class="hero-chip">FLOW CONTROL</span><span class="hero-chip">ERROR RECOVERY</span><span class="hero-chip">ARQ PROTOCOLS</span></div>
        </div>
        <div class="hero-visual" aria-hidden="true">
          <svg viewBox="0 0 330 210" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M49 57H272M49 105H272M49 153H272" stroke="#8FA9FF" stroke-opacity=".28" stroke-width="2" stroke-dasharray="5 7"/>
            <path d="M82 57H243M82 105H195M82 153H243" stroke="#62E1D3" stroke-opacity=".75" stroke-width="2.5" stroke-linecap="round"/>
            <path d="M236 49L245 57L236 65M188 97L197 105L188 113M236 145L245 153L236 161" stroke="#62E1D3" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <rect x="20" y="76" width="39" height="58" rx="11" fill="#172C4C" stroke="#91A8FF" stroke-opacity=".65"/>
            <rect x="271" y="76" width="39" height="58" rx="11" fill="#172C4C" stroke="#91A8FF" stroke-opacity=".65"/>
            <path d="M31 94H48M31 102H48M31 110H43M282 94H299M282 102H299M282 110H294" stroke="#B8C9FF" stroke-width="2" stroke-linecap="round"/>
            <rect x="88" y="39" width="33" height="35" rx="7" fill="#1D3B55" stroke="#62E1D3" stroke-opacity=".75"/><rect x="130" y="39" width="33" height="35" rx="7" fill="#1D3B55" stroke="#62E1D3" stroke-opacity=".75"/><rect x="172" y="39" width="33" height="35" rx="7" fill="#1D3B55" stroke="#62E1D3" stroke-opacity=".75"/>
            <text x="98" y="61" fill="#E9F7FF" font-family="sans-serif" font-size="12" font-weight="700">01</text><text x="140" y="61" fill="#E9F7FF" font-family="sans-serif" font-size="12" font-weight="700">02</text><text x="182" y="61" fill="#E9F7FF" font-family="sans-serif" font-size="12" font-weight="700">03</text>
            <rect x="88" y="136" width="33" height="35" rx="7" fill="#262951" stroke="#9B91FF" stroke-opacity=".8"/><rect x="130" y="136" width="33" height="35" rx="7" fill="#262951" stroke="#9B91FF" stroke-opacity=".8"/><rect x="172" y="136" width="33" height="35" rx="7" fill="#262951" stroke="#9B91FF" stroke-opacity=".8"/>
            <text x="104.5" y="158" text-anchor="middle" fill="#D5D0FF" font-family="sans-serif" font-size="9" font-weight="700">ACK</text><text x="146.5" y="158" text-anchor="middle" fill="#D5D0FF" font-family="sans-serif" font-size="9" font-weight="700">ACK</text><text x="188.5" y="158" text-anchor="middle" fill="#D5D0FF" font-family="sans-serif" font-size="9" font-weight="700">ACK</text>
            <circle cx="165" cy="105" r="85" stroke="#7895FF" stroke-opacity=".09"/>
          </svg>
        </div>
    </div>
    """, unsafe_allow_html=True)



# ==================== SIMULATION ====================
if run and lost_frames is not None:
    try:
        result = simulate_protocol(
            total_frames=total_frames,
            window_size=window_size,
            protocol=protocol,
            lost_frames=lost_frames,
        )

        st.session_state["result"] = result
        st.session_state["settings"] = {
            "protocol": protocol,
            "total_frames": total_frames,
            "window_size": window_size,
            "lost_frames": lost_frames
        }
        st.session_state["run_count"] = st.session_state.get("run_count", 0) + 1
        st.toast("Simulation complete. Dashboard updated below.")

    except Exception as exc:
        st.error(f"Simulation error: {exc}")


# ==================== INITIAL SCREEN ====================
if "result" not in st.session_state:
    st.markdown("""
    <section class="welcome">
      <div class="welcome-kicker">Your computer networks workspace</div>
      <div class="welcome-title">Welcome to <span>FrameFlow</span></div>
      <div class="welcome-copy">Run a transmission experiment and see how sliding window ARQ keeps data moving when frames are delayed or lost.</div>
    </section>
    <div class="welcome-grid">
      <article class="welcome-card" data-step="01">
        <div class="welcome-card-top"><div class="welcome-icon">&#9638;</div><div class="welcome-card-title">Frame transmission</div></div>
        <div class="welcome-card-copy">Follow frames as the sender releases them in a window and the receiver confirms delivery.</div>
      </article>
      <article class="welcome-card" data-step="02">
        <div class="welcome-card-top"><div class="welcome-icon">&#8635;</div><div class="welcome-card-title">Error recovery</div></div>
        <div class="welcome-card-copy">Introduce a frame loss and compare how Go-Back-N and Selective Repeat recover.</div>
      </article>
      <article class="welcome-card" data-step="03">
        <div class="welcome-card-top"><div class="welcome-icon">&#8599;</div><div class="welcome-card-title">Performance analysis</div></div>
        <div class="welcome-card-copy">Inspect attempts, retransmissions, delivery results, and the full event timeline.</div>
      </article>
    </div>
    <div class="welcome-cta">
      <div class="welcome-cta-mark">&#8594;</div>
      <div><div class="welcome-cta-title">Ready to run your first scenario?</div><div class="welcome-cta-copy">Choose a protocol and frame settings in the setup panel, then select Run simulation.</div></div>
    </div>
    """, unsafe_allow_html=True)


# ==================== RESULTS ====================
else:
    result = st.session_state["result"]
    cfg = st.session_state["settings"]

    loss_detail = (
        "Frames " + ", ".join(map(str, cfg["lost_frames"])) + " lost on original attempts"
        if cfg["lost_frames"]
        else "No frame loss"
    )
    st.markdown(f"""
    <div class="run-confirmation">
      <div class="run-check">&#10003;</div>
      <div><div class="run-title">Run #{st.session_state.get('run_count', 1)} complete &mdash; dashboard refreshed</div>
      <div class="run-detail">{cfg['protocol']} &nbsp;&middot;&nbsp; {cfg['total_frames']} frames &nbsp;&middot;&nbsp; window size {cfg['window_size']} &nbsp;&middot;&nbsp; {loss_detail}</div></div>
      <div class="run-badge">LATEST RUN</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 📊 Simulation Overview")

    st.caption(
        f"Protocol: {cfg['protocol']}  |  "
        f"Frames: {cfg['total_frames']}  |  "
        f"Window size: {cfg['window_size']}"
    )

    if cfg["lost_frames"]:
        st.warning(
            "Configured original frame losses: " + ", ".join(map(str, cfg["lost_frames"]))
        )
    else:
        st.success("No frame loss was configured.")

    metrics = [
        ("TOTAL TRANSMISSIONS", result["frames_sent"],
         "All transmission attempts"),
        ("FRAMES DELIVERED",
         f'{result["frames_delivered"]}/{cfg["total_frames"]}',
         "Successfully delivered"),
        ("RETRANSMISSIONS", result["retransmissions"],
         "Recovery attempts"),
        ("DELIVERY EFFICIENCY", f'{result["efficiency"]:.1f}%',
         "Frames delivered per transmission")
    ]

    cols = st.columns(4)

    for col, (label, value, note) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-note">{note}</div>
            </div>
            """, unsafe_allow_html=True)

    # ==================== SENDER → RECEIVER ====================
    st.markdown("## 🔄 Sender → Receiver")

    st.markdown("""
    <style>
    .sender-receiver-card {
        background: #142239;
        border: 1px solid #2b405b;
        border-radius: 14px;
        min-height: 130px;
        padding: 20px 12px;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .sr-icon { font-size: 27px; margin-bottom: 7px; }
    .sr-title {
        color: #f5f7ff;
        font-size: 14px;
        font-weight: 800;
        margin-bottom: 9px;
    }
    .sr-desc { color: #9eafc7; font-size: 11px; }
    .arrow-line {
        color: #55e6e0;
        font-size: 25px;
        font-weight: 700;
        line-height: 1;
    }
    .arrow-label {
        color: #91a6c2;
        font-size: 9px;
        margin-top: 9px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    diagram_left, diagram_mid, diagram_right = st.columns([1, .48, 1])

    with diagram_left:
        st.markdown("""
        <div class="sender-receiver-card">
            <div class="sr-icon">💻</div>
            <div class="sr-title">SENDER</div>
            <div class="sr-desc">Transmits frames within the window</div>
        </div>
        """, unsafe_allow_html=True)

    with diagram_mid:
        st.markdown("""
        <div style="text-align:center;padding:22px 0 5px;">
            <div class="arrow-line">⟶</div>
            <div class="arrow-label">DATA FRAMES</div>
            <div class="arrow-line" style="margin-top:18px;">⟵</div>
            <div class="arrow-label">ACKNOWLEDGEMENTS</div>
        </div>
        """, unsafe_allow_html=True)

    with diagram_right:
        st.markdown("""
        <div class="sender-receiver-card">
            <div class="sr-icon">🖥️</div>
            <div class="sr-title">RECEIVER</div>
            <div class="sr-desc">Receives frames and sends ACKs</div>
        </div>
        """, unsafe_allow_html=True)

    # ==================== FRAME MAP ====================
    st.markdown("## 🧩 Frame Transmission Map")
    st.markdown("🟢 Delivered  |  🔴 Initially lost  |  🟣 Retransmitted")

    frame_status = result["frame_status"]

    for start in range(1, cfg["total_frames"] + 1, cfg["window_size"]):
        end = min(start + cfg["window_size"] - 1, cfg["total_frames"])
        st.caption(f"SENDER WINDOW · Frames {start}–{end}")
        frame_cols = st.columns(end - start + 1)

        for col, frame in zip(frame_cols, range(start, end + 1)):
            row = frame_status[frame - 1]
            attempts = row["Transmission Attempts"]

            if frame in cfg["lost_frames"] and attempts == 1:
                css = "lost"
                label = "LOST"
            elif attempts > 1:
                css = "transmitted"
                label = "RETRIED"
            else:
                css = "delivered"
                label = "DELIVERED"

            with col:
                st.markdown(f"""
                <div class="frame {css}">
                    <div class="frame-number">F{frame:02d}</div>
                    <div class="frame-label">{label}</div>
                    <div style="font-size:10px;color:#a7b8d0;margin-top:5px">
                        {attempts} attempt(s)
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Analysis
    st.markdown("## 📈 Transmission Analysis")

    chart_col, table_col = st.columns([1, 1])

    with chart_col:
        with st.container(border=True):
            st.markdown("### Attempts per Frame")

            chart_data = pd.DataFrame(frame_status)
            chart_data["Outcome"] = chart_data.apply(
                lambda row: (
                    "Retransmitted" if row["Transmission Attempts"] > 1
                    else row["Status"]
                ),
                axis=1,
            )
            attempts_chart = alt.Chart(chart_data).encode(
                x=alt.X(
                    "Frame:O",
                    title="Frame number",
                    sort=None,
                    axis=alt.Axis(labelAngle=-45, labelFontSize=10, titlePadding=10),
                ),
                y=alt.Y(
                    "Transmission Attempts:Q",
                    title="Transmission attempts",
                    scale=alt.Scale(domainMin=0),
                    axis=alt.Axis(tickMinStep=1, grid=True),
                ),
                color=alt.Color(
                    "Outcome:N",
                    title="Frame outcome",
                    scale=alt.Scale(
                        domain=["Delivered", "Retransmitted", "Pending"],
                        range=["#62dfd1", "#f6ad55", "#fb7185"],
                    ),
                    legend=alt.Legend(orient="top", direction="horizontal"),
                ),
                tooltip=[
                    alt.Tooltip("Frame:Q", title="Frame"),
                    alt.Tooltip("Status:N", title="Delivery status"),
                    alt.Tooltip("Transmission Attempts:Q", title="Attempts"),
                ],
            )
            bars = attempts_chart.mark_bar(size=14, cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
            value_labels = attempts_chart.mark_text(
                dy=-8, color="#e6eefb", fontSize=10, fontWeight=700
            ).encode(text=alt.Text("Transmission Attempts:Q"))
            attempts_chart = (
                (bars + value_labels)
                .properties(height=280)
                .configure_view(stroke=None)
                .configure_axis(
                    labelColor="#aebed5",
                    titleColor="#d7e2f2",
                    domainColor="#42516b",
                    tickColor="#42516b",
                    gridColor="#25334a",
                )
                .configure_legend(labelColor="#c4d1e3", titleColor="#d7e2f2")
            )
            st.altair_chart(attempts_chart, use_container_width=True)
            st.caption("Retransmitted frames are highlighted. Hover over a bar to inspect its status and exact attempt count.")

    with table_col:
        with st.container(border=True):
            st.markdown("### Frame Delivery Details")

            st.dataframe(
                pd.DataFrame(frame_status),
                hide_index=True,
                use_container_width=True,
                height=330
            )

    # Event log
    st.markdown("## 📜 Transmission Event Log")

    events = result["events"]

    with st.expander("View complete transmission log", expanded=True):
        for i, event in enumerate(events, 1):
            event_text = str(event)

            if "LOST" in event_text.upper() or "DISCARD" in event_text.upper():
                css = "error"
            elif "TIMEOUT" in event_text.upper():
                css = "warning"
            elif "ACK" in event_text.upper():
                css = "ack"
            else:
                css = ""

            st.markdown(
                f'<div class="log-row {css}">'
                f'<span style="color:#8296b3">#{i:03d}</span> '
                f'{event_text}</div>',
                unsafe_allow_html=True
            )

    st.download_button(
        "⬇ Download Transmission Log",
        data="\n".join(str(event) for event in events),
        file_name="FrameFlow_transmission_log.txt",
        mime="text/plain"
    )

# ==================== PROJECT PROFILE ====================
st.markdown("""
<section class="project-profile">
  <div class="profile-head">
    <div>
      <div class="profile-eyebrow">Institutional project submission</div>
      <div class="profile-title">Chaitanya Bharathi Institute<br>of Technology</div>
      <div class="profile-subtitle">Computer Networks &nbsp;&middot;&nbsp; Sliding Window Protocol Simulator</div>
    </div>
    <div class="profile-mark">CBIT</div>
  </div>
  <div class="profile-section-label">Project team &nbsp; / &nbsp; 03 contributors</div>
  <div class="member-grid">
    <div class="member-card"><div class="member-top"><div class="member-avatar">BA</div><div><div class="member-name">Battula Anjali</div><div class="member-role">Project contributor</div></div></div><div class="member-id">ROLL NUMBER &nbsp; 160124737004</div></div>
    <div class="member-card"><div class="member-top"><div class="member-avatar">CC</div><div><div class="member-name">Chithuluri Charishma</div><div class="member-role">Project contributor</div></div></div><div class="member-id">ROLL NUMBER &nbsp; 160124737006</div></div>
    <div class="member-card"><div class="member-top"><div class="member-avatar">KA</div><div><div class="member-name">Kulsum Abid</div><div class="member-role">Project contributor</div></div></div><div class="member-id">ROLL NUMBER &nbsp; 160124737014</div></div>
  </div>
  <div class="mentor-row"><div class="mentor-avatar">MENTOR</div><div><div class="mentor-name">Dr. P. Ramesh Babu</div><div class="mentor-role">Project mentor &nbsp;&middot;&nbsp; Associate Professor</div></div><div class="profile-footer">Faculty guidance</div></div>
</section>
""", unsafe_allow_html=True)



# ==================== FOOTER ====================
st.markdown("""
<div class="small-footer">
    FRAMEFLOW · SLIDING WINDOW PROTOCOL SIMULATOR<br>
    Chaitanya Bharathi Institute of Technology<br>
    Mentor: Dr. P. Ramesh Babu · Associate Professor
</div>
""", unsafe_allow_html=True)
