import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# 1. إعدادات الصفحة والهوية البصرية
st.set_page_config(
    page_title="CPU Scheduler Simulator Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخصيص المظهر بألوان عصرية عبر CSS خفيف لحواف البطاقات
st.markdown("""
    <style>
    .kpi-card {
        background-color: #252538;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #00F0FF;
        text-align: center;
    }
    .kpi-card-purple {
        background-color: #252538;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #8A2BE2;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# 2. الشق الجانبي للتحكم والمدخلات (Sidebar)
st.sidebar.title("⚙️ Control Panel")
st.sidebar.markdown("---")

# اختيار الخوارزمية
algo_choice = st.sidebar.selectbox(
    "Choose Algorithm:",
    ["FCFS (First Come First Serve)", "SJF (Shortest Job First)"]
)

st.sidebar.markdown("### 📥 Processes Input")

# جدول العمليات الافتراضي القابل للتعديل مباشرة من الويب
default_data = pd.DataFrame([
    {"Process ID": "P1", "Arrival Time": 0, "Burst Time": 4},
    {"Process ID": "P2", "Arrival Time": 1, "Burst Time": 3},
    {"Process ID": "P3", "Arrival Time": 2, "Burst Time": 1},
    {"Process ID": "P4", "Arrival Time": 3, "Burst Time": 2},
    {"Process ID": "P5", "Arrival Time": 4, "Burst Time": 5},
    {"Process ID": "P6", "Arrival Time": 5, "Burst Time": 2},
    {"Process ID": "P7", "Arrival Time": 6, "Burst Time": 3},
    {"Process ID": "P8", "Arrival Time": 7, "Burst Time": 4},
    {"Process ID": "P9", "Arrival Time": 8, "Burst Time": 3},
    {"Process ID": "P10", "Arrival Time": 9, "Burst Time": 2},
    {"Process ID": "P11", "Arrival Time": 10, "Burst Time": 5},
    {"Process ID": "P12", "Arrival Time": 11, "Burst Time": 1},
    {"Process ID": "", "Arrival Time": None, "Burst Time": None},
    {"Process ID": "", "Arrival Time": None, "Burst Time": None},
    {"Process ID": "", "Arrival Time": None, "Burst Time": None},
])

# تمكين المستخدم من إضافة وتعديل العمليات عبر جدول تفاعلي
edited_df = st.sidebar.data_editor(
    default_data, 
    num_rows="dynamic", 
    use_container_width=True
)

run_button = st.sidebar.button("▶ RUN SIMULATION", use_container_width=True, type="primary")

# 3. الواجهة الرئيسية للويب (Main Panel)
st.title("⚡ CPU SCHEDULER SIMULATOR PRO")
st.write("A modern web-based simulation tool for operating system CPU scheduling algorithms.")
st.markdown("---")

if run_button:
    # تحويل البيانات إلى مصفوفة قواميس لمعالجتها
    processes = edited_df.to_dict(orient="records")

    # فلترة السطور الفارغة إن وجدت (بناءً على وجود Process ID)
    processes = [p for p in processes if pd.notna(p.get("Process ID"))]

    # تحقق من صحة قيم Arrival Time و Burst Time وحولها إلى أعداد صحيحة
    invalid = []
    for p in processes:
        pid = p.get("Process ID")
        # التحقق من Arrival Time
        at = p.get("Arrival Time")
        if pd.isna(at):
            invalid.append(str(pid))
            continue
        try:
            p["Arrival Time"] = int(at)
        except Exception:
            invalid.append(str(pid))
            continue

        # التحقق من Burst Time
        bt = p.get("Burst Time")
        if pd.isna(bt):
            invalid.append(str(pid))
            continue
        try:
            p["Burst Time"] = int(bt)
        except Exception:
            invalid.append(str(pid))
            continue

    if len(invalid) > 0:
        st.error("Please provide valid numeric Arrival Time and Burst Time for: " + ", ".join(sorted(set(invalid))))
        st.stop()

    if len(processes) == 0:
        st.error("Please add at least one process to simulate.")
    else:
        # منطق خوارزميات الجدولة
        if "FCFS" in algo_choice:
            ready_queue = sorted(processes, key=lambda x: x["Arrival Time"])
        else:
            ready_queue = sorted(processes, key=lambda x: (x["Arrival Time"], x["Burst Time"]))

        current_time = 0
        gantt_data = []
        waiting_times = {}
        turnaround_times = {}

        for p in ready_queue:
            pid = p["Process ID"]
            arr = p["Arrival Time"]
            burst = p["Burst Time"]
            
            if current_time < arr:
                current_time = arr
            
            start_time = current_time
            waiting_times[pid] = start_time - arr
            current_time += burst
            end_time = current_time
            turnaround_times[pid] = end_time - arr
            
            gantt_data.append((pid, start_time, burst))

        avg_wt = sum(waiting_times.values()) / len(processes)
        avg_tat = sum(turnaround_times.values()) / len(processes)

        # 4. عرض مؤشرات الأداء (KPI Cards) في أعمدة متناسقة
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                <div class="kpi-card">
                    <h3 style='color: #A0A0B8; margin:0;'>Avg Waiting Time</h3>
                    <h1 style='color: #00F0FF; margin:10px 0 0 0;'>{avg_wt:.2f} ms</h1>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
                <div class="kpi-card-purple">
                    <h3 style='color: #A0A0B8; margin:0;'>Avg Turnaround Time</h3>
                    <h1 style='color: #8A2BE2; margin:10px 0 0 0;'>{avg_tat:.2f} ms</h1>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("### 📊 Gantt Chart (Timeline)")
        
        # 5. رسم مخطط غانت بتنسيق متوافق مع ثيم الويب الداكن
        fig, ax = plt.subplots(figsize=(10, 2.5), facecolor='#1E1E2E')
        ax.set_facecolor('#252538')

        colors = ["#00F0FF", "#8A2BE2", "#FF007F", "#39FF14", "#FF9933"]

        for i, (pid, start, duration) in enumerate(gantt_data):
            color = colors[i % len(colors)]
            ax.barh(y="CPU", width=duration, left=start, color=color, edgecolor="#1E1E2E", height=0.4)
            ax.text(start + duration/2, 0, pid, ha='center', va='center', color='black', weight='bold', fontsize=11)

        ax.tick_params(colors='white', labelsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#A0A0B8')
        ax.spines['bottom'].set_color('#A0A0B8')
        ax.grid(axis='x', color='#32324D', linestyle='--', alpha=0.5)

        # عرض الرسم البياني داخل صفحة الويب تلقائياً
        st.pyplot(fig)
else:
    st.info("💡 Adjust processes in the sidebar table and click 'RUN SIMULATION' to start.")
 