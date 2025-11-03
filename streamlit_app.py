import streamlit as st
import requests
import json

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="AI Career Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== STYLING ====================
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        padding: 10px;
        font-size: 16px;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== API CONFIG ====================
API_BASE_URL = "http://192.168.1.25:8000"

# ==================== SESSION STATE INITIALIZATION ====================
if "user_skills" not in st.session_state:
    st.session_state.user_skills = []

if "results" not in st.session_state:
    st.session_state.results = None

if "selected_job" not in st.session_state:
    st.session_state.selected_job = None

if "jobs_list" not in st.session_state:
    st.session_state.jobs_list = []

if "parsed" not in st.session_state:
    st.session_state.parsed = False

# ==================== TITLE & HEADER ====================
st.title("🚀 AI Career Platform")
st.markdown("Upload your resume, analyze skill gaps, and get personalized career recommendations!")

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("📋 Navigation")
    page = st.radio(
        "Select a page:",
        ["Resume Parser", "Skill Gap Analyzer", "Analysis Results"]
    )

# ==================== PAGE: RESUME PARSER ====================
if page == "Resume Parser":
    st.header("📄 Resume Parser")
    st.markdown("Upload your resume (PDF or DOCX) to extract skills and information.")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload your resume",
        type=["pdf", "docx"],
        key="resume_uploader"
    )
    
    if uploaded_file is not None:
        st.success(f"✓ File selected: {uploaded_file.name}")
        st.info(f"File size: {uploaded_file.size / 1024:.2f} KB")
        
        if st.button("🔍 Parse Resume", key="parse_button"):
            with st.spinner("Parsing your resume..."):
                try:
                    # Prepare file for upload
                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file,
                            uploaded_file.type
                        )
                    }
                    
                    # Call backend API
                    response = requests.post(
                        f"{API_BASE_URL}/parse-resume",
                        files=files,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        parsed_data = data.get("data", {})
                        
                        # Update session state
                        st.session_state.user_skills = [
                            skill["name"] for skill in parsed_data.get("skills", [])
                        ]
                        st.session_state.parsed = True
                        
                        # Display parsed information
                        st.success("✓ Resume parsed successfully!")
                        
                        # Show personal info
                        if parsed_data.get("personal_info"):
                            with st.expander("👤 Personal Information"):
                                for key, value in parsed_data["personal_info"].items():
                                    st.write(f"**{key}:** {value}")
                        
                        # Show experience
                        if parsed_data.get("experience"):
                            with st.expander("💼 Experience"):
                                for exp in parsed_data["experience"]:
                                    st.write(f"**{exp.get('title', 'N/A')}** at {exp.get('company', 'N/A')}")
                                    st.write(f"Duration: {exp.get('duration', 'N/A')}")
                        
                        # Show education
                        if parsed_data.get("education"):
                            with st.expander("🎓 Education"):
                                for edu in parsed_data["education"]:
                                    st.write(f"**{edu.get('degree', 'N/A')}** from {edu.get('institution', 'N/A')}")
                        
                        # Show extracted skills
                        with st.expander("🔧 Extracted Skills", expanded=True):
                            st.info(f"Total skills extracted: {len(st.session_state.user_skills)}")
                            
                            # Display skills in columns
                            cols = st.columns(3)
                            for idx, skill in enumerate(st.session_state.user_skills):
                                with cols[idx % 3]:
                                    st.write(f"✓ {skill}")
                        
                        # Prompt to next step
                        st.markdown("---")
                        st.success("Ready for skill gap analysis! Go to **Skill Gap Analyzer** tab.")
                    
                    else:
                        st.error(f"Error parsing resume: {response.text}")
                
                except requests.exceptions.Timeout:
                    st.error("Request timed out. Please try again.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# ==================== PAGE: SKILL GAP ANALYZER ====================
elif page == "Skill Gap Analyzer":
    st.header("🎯 Skill Gap Analyzer")
    
    if not st.session_state.parsed or not st.session_state.user_skills:
        st.warning("⚠️ Please parse your resume first on the **Resume Parser** page!")
    else:
        st.success(f"✓ Skills loaded: {len(st.session_state.user_skills)} skills detected")
        
        # Display current skills
        with st.expander("🔧 Your Current Skills"):
            st.write(", ".join(st.session_state.user_skills))
        
        # Load available jobs
        if not st.session_state.jobs_list:
            with st.spinner("Loading available jobs..."):
                try:
                    jobs_resp = requests.get(
                        f"{API_BASE_URL}/jobs",
                        timeout=10
                    )
                    
                    if jobs_resp.status_code == 200:
                        st.session_state.jobs_list = jobs_resp.json().get("jobs", [])
                    else:
                        st.error("Failed to load jobs")
                except Exception as e:
                    st.error(f"Error loading jobs: {str(e)}")
        
        # Job selection dropdown
        if st.session_state.jobs_list:
            st.session_state.selected_job = st.selectbox(
                "Select your target job:",
                options=st.session_state.jobs_list,
                index=(
                    st.session_state.jobs_list.index(st.session_state.selected_job)
                    if st.session_state.selected_job in st.session_state.jobs_list
                    else 0
                ),
                key="job_selector"
            )
            
            # Analyze button
            if st.button("📊 Analyze Skill Gap", key="analyze_button"):
                with st.spinner("Analyzing skill gaps..."):
                    try:
                        payload = {
                            "user_skills": st.session_state.user_skills,
                            "target_job": st.session_state.selected_job
                        }
                        
                        # Log the request
                        st.write(f"📤 Request payload: {json.dumps(payload, indent=2)}")
                        
                        # Call backend API
                        analyze_resp = requests.post(
                            f"{API_BASE_URL}/analyze-gap",
                            json=payload,
                            timeout=30
                        )
                        
                        st.write(f"📥 Response status: {analyze_resp.status_code}")
                        
                        if analyze_resp.status_code == 200:
                            st.session_state.results = analyze_resp.json()
                            st.success("✓ Skill gap analysis complete!")
                            st.info("Go to **Analysis Results** tab to view detailed results.")
                        else:
                            st.error(f"Error: {analyze_resp.text}")
                    
                    except requests.exceptions.Timeout:
                        st.error("Request timed out. Please try again.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        else:
            st.warning("No jobs available. Please check backend connection.")

# ==================== PAGE: ANALYSIS RESULTS ====================
elif page == "Analysis Results":
    st.header("📈 Analysis Results")
    
    if st.session_state.results is None:
        st.warning("⚠️ No analysis results yet. Please run the analysis first!")
    else:
        analysis = st.session_state.results.get("data", {})
        
        # ========== TOP LEVEL METRICS ==========
        st.subheader(f"Position: {analysis.get('job_title', 'N/A')}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Match %",
                f"{analysis.get('match_percentage', 0)}%",
                delta=None
            )
        
        with col2:
            st.metric(
                "Learning Hours",
                analysis.get('total_learning_hours', 0),
                delta=None
            )
        
        with col3:
            st.metric(
                "Weeks Needed",
                f"{analysis.get('estimated_weeks', 0):.1f}",
                delta=None
            )
        
        with col4:
            st.metric(
                "Salary Impact",
                f"${analysis.get('potential_salary_increase', 0):,.0f}",
                delta=None
            )
        
        # ========== RECOMMENDATION ==========
        st.markdown("---")
        st.subheader("💡 Recommendation")
        st.info(analysis.get("recommendation", "No recommendation available"))
        
        # ========== MATCHED SKILLS ==========
        st.markdown("---")
        st.subheader("✅ Matched Skills")
        
        matched = analysis.get("matched_skills", [])
        if matched:
            for skill in matched:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"🎯 **{skill.get('skill_name', 'N/A')}**")
                with col2:
                    st.write(f"Your Level: {skill.get('proficiency_level', 'N/A')}")
                with col3:
                    st.write(f"Required: {skill.get('required_level', 'N/A')}")
        else:
            st.info("No matched skills found.")
        
        # ========== SKILL GAPS ==========
        st.markdown("---")
        st.subheader("❌ Skill Gaps (Sorted by ROI)")
        
        gaps = analysis.get("skill_gaps", [])
        if gaps:
            for idx, gap in enumerate(gaps, 1):
                with st.expander(f"{idx}. {gap.get('skill_name', 'N/A')} (Priority: {gap.get('priority', 'N/A').upper()})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Learning Hours:** {gap.get('learning_hours', 0)}")
                        st.write(f"**Difficulty:** {gap.get('difficulty', 0)}/10")
                        st.write(f"**Market Demand:** {gap.get('market_demand', 0):.0%}")
                    
                    with col2:
                        st.write(f"**Salary Impact:** ${gap.get('salary_impact', 0):,.0f}")
                        st.write(f"**ROI:** ${gap.get('roi', 0):.2f}/hour")
                        st.write(f"**Weeks:** {gap.get('weeks_to_proficiency', 0):.1f}")
        else:
            st.success("🎉 No skill gaps! You're well-prepared for this role.")
        
        # ========== LEARNING ROADMAP ==========
        st.markdown("---")
        st.subheader("📚 Learning Roadmap")
        
        roadmap = analysis.get("learning_roadmap", [])
        if roadmap:
            for step in roadmap:
                st.write(f"→ {step}")
        else:
            st.info("No learning roadmap available.")
        
        # ========== ADDITIONAL METRICS ==========
        st.markdown("---")
        st.subheader("📊 Additional Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Average Difficulty:** {analysis.get('average_difficulty', 0):.1f}/10")
            st.write(f"**Market Demand Score:** {analysis.get('market_demand_score', 0):.2f}")
        
        with col2:
            st.write(f"**User Skills Count:** {analysis.get('user_skill_count', 0)}")
            st.write(f"**Required Skills Count:** {analysis.get('required_skill_count', 0)}")
        
        # ========== EXPORT RESULTS ==========
        st.markdown("---")
        st.subheader("💾 Export Results")
        
        results_json = json.dumps(st.session_state.results, indent=2)
        
        st.download_button(
            label="📥 Download Results (JSON)",
            data=results_json,
            file_name="skill_gap_analysis.json",
            mime="application/json"
        )

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 12px;">
    <p>AI Career Platform © 2025 | Powered by FastAPI + Streamlit</p>
</div>
""", unsafe_allow_html=True)
