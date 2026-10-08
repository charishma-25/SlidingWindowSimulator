
import streamlit as st
import pandas as pd
from protocols import simulate_protocol

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
        linear-gradient(120deg, rgba(24, 48, 77, .96), rgba(25, 29, 61, .96) 68%, rgba(35, 38, 79, .96));
    border: 1px solid rgba(128, 153, 205, .34);
    border-radius: 24px;
    padding: clamp(2rem, 5vw, 3.5rem);
    margin-bottom: 2rem;
    box-shadow: 0 20px 60px rgba(0, 0, 0, .22);
}

.hero::after {
    content: "01";
    position: absolute;
    right: 2.5rem;
    bottom: -1rem;
    color: rgba(133, 157, 255, .1);
    font: 700 clamp(5rem, 14vw, 10rem)/1 'Space Grotesk', sans-serif;
}

.hero-label {
    display: inline-block;
    background: rgba(32, 59, 77, .84);
    color: #75f0e8;
    border: 1px solid rgba(94, 213, 217, .42);
    border-radius: 30px;
    padding: 7px 13px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
}

.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(30px, 3.5vw, 46px);
    font-weight: 700;
    line-height: 1.2;
    margin: 18px 0 12px;
    color: white;
}

.hero-desc {
    position: relative;
    z-index: 1;
    max-width: 720px;
    color: #b9c8dc;
    font-size: 15px;
    line-height: 1.8;
}

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
    st.markdown("## 🌐 FrameFlow")
    st.caption("COMPUTER NETWORKS LAB")
    st.divider()

    st.markdown("### ⚙️ Configuration")

    protocol = st.selectbox(
        "Select ARQ Protocol",
        ["Go-Back-N", "Selective Repeat"]
    )

    total_frames = st.slider(
        "Number of frames", 5, 20, 10
    )

    window_size = st.slider(
        "Window size", 1, min(10, total_frames),
        min(4, total_frames)
    )

    st.markdown("### 📡 Channel Conditions")

    simulate_loss = st.toggle(
        "Simulate frame loss", value=False
    )

    lost_frame = None

    if simulate_loss:
        lost_frame = st.slider(
            "Frame to lose",
            1, total_frames, min(3, total_frames)
        )

    st.divider()

    run = st.button("▶ RUN SIMULATION", use_container_width=True)

    st.divider()
    st.caption("PROJECT TEAM: 3 STUDENTS")
    st.caption("MENTOR: DR. P. RAMESH BABU")


# ==================== HERO ====================
st.markdown("""
<div class="hero">
    <span class="hero-label">COMPUTER NETWORKS · CASE STUDY</span>
    <div class="hero-title">
        🌐 Sliding Window<br>Protocol Simulator
    </div>
    <div class="hero-desc">
        Explore reliable data transmission, flow control,
        acknowledgements, and error recovery through an
        interactive simulation of Go-Back-N and Selective Repeat ARQ.
    </div>
</div>
""", unsafe_allow_html=True)


# ==================== COLLEGE AND TEAM ====================
with st.container(border=True):
    st.caption("INSTITUTIONAL PROJECT SUBMISSION")
    st.markdown("## 🎓 Chaitanya Bharathi Institute of Technology")
    st.markdown("### 👥 Project Team")

    team1, team2 = st.columns(2)

    with team1:
        st.markdown("**Battula Anjali**")
        st.caption("Roll Number: 160124737004")
        st.divider()

        st.markdown("**Chithuluri Charishma**")
        st.caption("Roll Number: 160124737006")

    with team2:
        st.markdown("**Kulsum Abid**")
        st.caption("Roll Number: 160124737014")

        st.divider()
        st.markdown("### 👨‍🏫 Project Mentor")
        st.markdown("**Dr. P. Ramesh Babu**")
        st.write("Associate Professor")


# ==================== SIMULATION ====================
if run:
    try:
        result = simulate_protocol(
            total_frames=total_frames,
            window_size=window_size,
            protocol=protocol,
            lost_frame=lost_frame
        )

        st.session_state["result"] = result
        st.session_state["settings"] = {
            "protocol": protocol,
            "total_frames": total_frames,
            "window_size": window_size,
            "lost_frame": lost_frame
        }

    except Exception as exc:
        st.error(f"Simulation error: {exc}")


# ==================== INITIAL SCREEN ====================
if "result" not in st.session_state:
    st.markdown("## ✨ Welcome to FrameFlow")

    c1, c2, c3 = st.columns(3)

    with c1:
        with st.container(border=True):
            st.markdown("### 📦 Frame Transmission")
            st.write(
                "Observe how frames move from sender to receiver "
                "within the configured window."
            )

    with c2:
        with st.container(border=True):
            st.markdown("### 🔄 Error Recovery")
            st.write(
                "Simulate frame loss and observe the selected "
                "protocol's retransmission behavior."
            )

    with c3:
        with st.container(border=True):
            st.markdown("### 📊 Performance Analysis")
            st.write(
                "Review transmission attempts, delivered frames, "
                "retransmissions, and delivery efficiency."
            )

    st.info(
        "Configure the simulation in the sidebar and click "
        "**RUN SIMULATION** to view the results."
    )


# ==================== RESULTS ====================
else:
    result = st.session_state["result"]
    cfg = st.session_state["settings"]

    st.markdown("## 📊 Simulation Overview")

    st.caption(
        f"Protocol: {cfg['protocol']}  |  "
        f"Frames: {cfg['total_frames']}  |  "
        f"Window size: {cfg['window_size']}"
    )

    if cfg["lost_frame"] is not None:
        st.warning(
            f"Configured frame loss: Frame {cfg['lost_frame']}"
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

            if cfg["lost_frame"] == frame and attempts == 1:
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

            chart_data = pd.DataFrame(frame_status).set_index("Frame")[
                ["Transmission Attempts"]
            ]

            st.bar_chart(chart_data)

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

# ==================== FOOTER ====================
st.markdown("""
<div class="small-footer">
    FRAMEFLOW · SLIDING WINDOW PROTOCOL SIMULATOR<br>
    Chaitanya Bharathi Institute of Technology<br>
    Mentor: Dr. P. Ramesh Babu · Associate Professor
</div>
""", unsafe_allow_html=True)
