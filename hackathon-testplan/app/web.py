from __future__ import annotations
import json
import sys
import os
from pathlib import Path
import streamlit as st
import re

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.models import ParsedEntities
from core.generator import generate_plan_offline
from nlp.llm_client import generate_plan_llm
from rules.validator import validate_entities, annotate_plan
from ingest.netlist_parser import parse_netlist
from ingest.pdf_parser import extract_pdf_hints
from ingest.bom_parser import parse_bom

# ---------- Page config & styling ----------
st.set_page_config(
    page_title="🛠️ Bring-Up / Test Plan Generator", 
    page_icon="🛠️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
PRIMARY_COLOR = "#7C5CFC"
st.markdown(f"""
<style>
    /* Main styling */
    .main .block-container {{ padding-top: 2rem; padding-bottom: 2rem; }}
    
    /* Custom pill badges */
    .pill {{ 
        display: inline-block; 
        padding: 4px 12px; 
        border-radius: 20px; 
        font-size: 0.8rem; 
        font-weight: 500;
        margin-left: 8px; 
    }}
    .pill-on {{ 
        background: {PRIMARY_COLOR}; 
        color: white; 
    }}
    .pill-off {{ 
        background: #333; 
        color: #bbb; 
    }}
    
    /* Status indicators */
    .status-box {{ 
        padding: 12px; 
        border-radius: 8px; 
        margin: 8px 0; 
    }}
    .status-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
    .status-info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
    .status-warning {{ background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }}
    
    /* File upload area */
    .upload-area {{ 
        border: 2px dashed #ccc; 
        border-radius: 10px; 
        padding: 20px; 
        text-align: center; 
        margin: 10px 0; 
    }}
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{ 
        height: 50px; 
        padding-left: 20px; 
        padding-right: 20px; 
        background: #f8f9fa; 
        border-radius: 8px 8px 0 0; 
    }}
    .stTabs [aria-selected="true"] {{ 
        background: {PRIMARY_COLOR}; 
        color: white; 
    }}
    
    /* Button styling */
    .stButton > button {{ 
        border-radius: 8px; 
        font-weight: 500; 
    }}
    
    /* Code blocks */
    .stCodeBlock {{ border-radius: 8px; }}
    
    /* Sidebar */
    .css-1d391kg {{ background: #f8f9fa; }}
</style>
""", unsafe_allow_html=True)

def _has_openai_key() -> bool:
    """Check if OpenAI API key is available"""
    return bool(os.getenv("OPENAI_API_KEY"))

def infer_entities_from_text(text: str, title: str = "Design") -> ParsedEntities:
    """Heuristically infer entities from text content"""
    T = text.upper()
    lines = text.split('\n')
    
    # Rails - look for voltage patterns
    rails = []
    voltage_patterns = [
        (r"\+?5V", 5.0), (r"\+?3V3", 3.3), (r"\+?3\.3V", 3.3),
        (r"VCC5", 5.0), (r"VCC3V3", 3.3), (r"PWR_JACK", 5.0)
    ]
    
    seen_voltages = set()
    for pattern, voltage in voltage_patterns:
        if re.search(pattern, T) and voltage not in seen_voltages:
            rails.append({
                "name": f"+{voltage:g}V" if voltage == 5.0 else f"+{voltage:g}V", 
                "voltage": voltage, 
                "tolerance_mv": 100
            })
            seen_voltages.add(voltage)
    
    # Oscillators - look for crystal references
    oscillators = []
    if "Y1" in T or "16MHZ" in T:
        oscillators.append({
            "ref": "Y1", 
            "frequency_hz": 16000000, 
            "tolerance_hz": 100000
        })
    
    if "Y2" in T or "32MHZ" in T:
        oscillators.append({
            "ref": "Y2", 
            "frequency_hz": 32000000, 
            "tolerance_hz": 100000
        })
    
    # Functional tests - infer from components
    functional_tests = []
    if "LORA" in T or "SX1276" in T:
        functional_tests.append({
            "name": "LoRa BIT", 
            "command": "bit.lora", 
            "expected": "PASS"
        })
    
    if "GPS" in T or "MAX-M10S" in T:
        functional_tests.append({
            "name": "GPS BIT", 
            "command": "bit.gps", 
            "expected": "PASS"
        })
    
    if "IMU" in T or "LSM6DSOX" in T:
        functional_tests.append({
            "name": "IMU BIT", 
            "command": "bit.imu", 
            "expected": "PASS"
        })
    
    if "I2C" in T:
        functional_tests.append({
            "name": "I2C BIT", 
            "command": "bit.i2c", 
            "expected": "PASS"
        })
    
    # Defaults if nothing found
    if not rails:
        rails = [{"name": "+5V", "voltage": 5.0, "tolerance_mv": 100},
                 {"name": "+3V3", "voltage": 3.3, "tolerance_mv": 100}]
    if not functional_tests:
        functional_tests.append({"name": "Full BIT", "command": "bit", "expected": "PASS"})
    
    return ParsedEntities.model_validate({
        "title": title,
        "rails": rails,
        "oscillators": oscillators,
        "functional_tests": functional_tests
    })

# ---------- Sidebar ----------
with st.sidebar:
    st.header("⚙️ Settings")
    
    # LLM toggle with status
    use_llm = st.toggle("🤖 Use LLM Enhancement", value=_has_openai_key())
    
    # Status indicators
    if use_llm and _has_openai_key():
        st.markdown('<div class="status-box status-success">✅ OpenAI API Key Found</div>', unsafe_allow_html=True)
    elif use_llm and not _has_openai_key():
        st.markdown('<div class="status-box status-warning">⚠️ No API Key - Using Offline Mode</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-box status-info">ℹ️ Offline Mode Active</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Reset button
    if st.button("🔄 Reset All", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ---------- Main Content ----------
st.title("🛠️ Bring-Up / Test Plan Generator")

# Status pill
llm_pill = '<span class="pill {}">LLM {}</span>'.format(
    "pill-on" if (use_llm and _has_openai_key()) else "pill-off",
    "ON" if (use_llm and _has_openai_key()) else "OFF",
)
st.markdown(f"**Status** {llm_pill}", unsafe_allow_html=True)

# Initialize session state
if "entities_text" not in st.session_state:
    placeholder = {
        "title": "LoRa Car Radio",
        "rails": [
            {"name": "+5V", "voltage": 5.0, "tolerance_mv": 100},
            {"name": "+3V3", "voltage": 3.3, "tolerance_mv": 100}
        ],
        "oscillators": [
            {"ref": "Y1", "frequency_hz": 16_000_000, "tolerance_hz": 100_000}
        ],
        "functional_tests": [
            {"name": "LoRa BIT", "command": "bit.lora", "expected": "PASS"},
            {"name": "GPS BIT", "command": "bit.gps", "expected": "PASS"}
        ]
    }
    st.session_state["entities_text"] = json.dumps(placeholder, indent=2)

if "plan_md" not in st.session_state:
    st.session_state["plan_md"] = ""

if "entities_obj" not in st.session_state:
    st.session_state["entities_obj"] = None

# ---------- Tabs ----------
tab_upload, tab_entities, tab_plan = st.tabs(["📁 Upload Files", "⚙️ Configure Entities", "📋 Generated Plan"])

# ---- Upload Tab ----
with tab_upload:
    st.subheader("📁 Upload Design Files")
    
    st.markdown("""
    <div class="upload-area">
        <h4>📄 Supported File Types</h4>
         <p><strong>JSON:</strong> Pre-defined entities • <strong>PDF:</strong> Design documents • <strong>BOM:</strong> Excel/CSV • <strong>Altium:</strong> .SchDoc/.PcbDoc • <strong>Netlist:</strong> .net/.ipc • <strong>ZIP:</strong> Archive files</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded = st.file_uploader(
        "Choose files...", 
        type=["json", "txt", "net", "ipc", "pdf", "xlsx", "xlsm", "csv", "schdoc", "pcbdoc", "prjpcb", "bomdoc", "zip"], 
        accept_multiple_files=True,
        help="Upload one or more design files to automatically extract entities"
    )
    
    if uploaded:
        st.success(f"✅ {len(uploaded)} file(s) uploaded: {', '.join([f.name for f in uploaded])}")
        
        if st.button("🔍 Parse Files → Extract Entities", type="primary", use_container_width=True):
            try:
                texts = []
                file_names = []
                processed_files = []  # Track individual files processed
                
                for f in uploaded:
                    # Save uploaded file temporarily
                    temp_path = f"/tmp/{f.name}"
                    with open(temp_path, "wb") as tmp_file:
                        tmp_file.write(f.getbuffer())
                    
                    file_ext = f.name.lower().split('.')[-1]
                    file_names.append(f.name)
                    
                    if file_ext in ['txt', 'net', 'ipc']:
                        # Parse netlist
                        ent = parse_netlist(temp_path)
                        processed_files.append(f.name)
                        st.success(f"✅ Parsed netlist {f.name}: {len(ent.rails)} rails, {len(ent.oscillators)} oscillators, {len(ent.functional_tests)} tests")
                        break  # Netlist is complete, no need to merge
                    
                    elif file_ext == 'json':
                        # Parse as JSON
                        data = json.loads(Path(temp_path).read_text())
                        ent = ParsedEntities.model_validate(data)
                        processed_files.append(f.name)
                        st.success(f"✅ Loaded JSON {f.name}: {len(ent.rails)} rails, {len(ent.oscillators)} oscillators, {len(ent.functional_tests)} tests")
                        break  # JSON is complete, no need to merge
                    
                    elif file_ext == 'pdf':
                        # Extract text from PDF
                        hints = extract_pdf_hints(temp_path)
                        text = "\n".join(hints)
                        texts.append(text)
                        processed_files.append(f.name)
                    
                    elif file_ext in ['xlsx', 'xlsm', 'csv']:
                        # Parse BOM
                        rows = parse_bom(temp_path)
                        text = "\n".join([f"{r} {v}" for r, v in rows])
                        texts.append(text)
                        processed_files.append(f.name)
                    
                    elif file_ext in ['schdoc', 'pcbdoc', 'prjpcb', 'bomdoc']:
                        # Parse Altium files
                        try:
                            text = Path(temp_path).read_text(encoding="utf-8", errors="ignore")
                        except:
                            text = Path(temp_path).read_bytes().decode("latin-1", errors="ignore")
                        texts.append(text)
                        processed_files.append(f.name)
                    
                    elif file_ext == 'zip':
                        # Extract and process zip files
                        from ingest.zip_loader import extract_zip
                        import tempfile
                        import os
                        
                        # Create temporary directory for extraction
                        with tempfile.TemporaryDirectory() as temp_dir:
                            extracted_files = extract_zip(temp_path, temp_dir)
                            
                            # Show what files were extracted
                            st.info(f"📦 Extracted {len(extracted_files)} files from {f.name}")
                            
                            # Process each extracted file
                            processed_count = 0
                            for extracted_file in extracted_files:
                                ext = Path(extracted_file).suffix.lower().lstrip('.')
                                file_name = Path(extracted_file).name
                                
                                if ext in ['txt', 'net', 'ipc']:
                                    # Parse netlist from zip
                                    ent = parse_netlist(extracted_file)
                                    processed_files.append(f"{f.name}/{file_name}")
                                    st.success(f"✅ Parsed netlist {file_name}: {len(ent.rails)} rails, {len(ent.oscillators)} oscillators, {len(ent.functional_tests)} tests")
                                    processed_count += 1
                                    break  # Netlist is complete, no need to merge
                                
                                elif ext == 'json':
                                    # Parse JSON from zip
                                    data = json.loads(Path(extracted_file).read_text())
                                    ent = ParsedEntities.model_validate(data)
                                    processed_files.append(f"{f.name}/{file_name}")
                                    st.success(f"✅ Loaded JSON {file_name}: {len(ent.rails)} rails, {len(ent.oscillators)} oscillators, {len(ent.functional_tests)} tests")
                                    processed_count += 1
                                    break  # JSON is complete, no need to merge
                                
                                elif ext == 'pdf':
                                    # Extract text from PDF in zip
                                    hints = extract_pdf_hints(extracted_file)
                                    text = "\n".join(hints)
                                    texts.append(text)
                                    processed_files.append(f"{f.name}/{file_name}")
                                    st.info(f"📄 Processed PDF {file_name}: {len(hints)} text hints")
                                    processed_count += 1
                                
                                elif ext in ['xlsx', 'xlsm', 'csv']:
                                    # Parse BOM from zip
                                    rows = parse_bom(extracted_file)
                                    text = "\n".join([f"{r} {v}" for r, v in rows])
                                    texts.append(text)
                                    processed_files.append(f"{f.name}/{file_name}")
                                    st.info(f"📊 Processed BOM {file_name}: {len(rows)} components")
                                    processed_count += 1
                                
                                elif ext in ['schdoc', 'pcbdoc', 'prjpcb', 'bomdoc']:
                                    # Parse Altium files from zip
                                    try:
                                        text = Path(extracted_file).read_text(encoding="utf-8", errors="ignore")
                                    except:
                                        text = Path(extracted_file).read_bytes().decode("latin-1", errors="ignore")
                                    texts.append(text)
                                    processed_files.append(f"{f.name}/{file_name}")
                                    st.info(f"🔧 Processed Altium {file_name}: {len(text)} characters")
                                    processed_count += 1
                            
                            # Show processing summary
                            if processed_count > 0:
                                st.success(f"🎯 Successfully processed {processed_count} files from {f.name}")
                            
                            # If we found a complete entity (JSON or netlist), break out of zip processing
                            if 'ent' in locals():
                                break
                
                # If we have multiple texts to merge
                if texts and not ('ent' in locals()):
                    blob = "\n".join(texts)
                    title = " | ".join(file_names)
                    ent = infer_entities_from_text(blob, title)
                    st.success(f"✅ Merged {len(processed_files)} files: {len(ent.rails)} rails, {len(ent.oscillators)} oscillators, {len(ent.functional_tests)} tests")
                
                # Update session state
                st.session_state["entities_text"] = ent.model_dump_json(indent=2)
                st.session_state["entities_obj"] = ent
                
                st.info("🎯 Entities extracted! Switch to 'Configure Entities' tab to review and edit.")
                
            except Exception as e:
                st.error(f"❌ Error processing files: {e}")
                st.exception(e)

# ---- Entities Tab ----
with tab_entities:
    st.subheader("⚙️ Configure Hardware Entities")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**📝 Edit Entities JSON**")
        sample_json = st.text_area(
            "entities.json", 
            value=st.session_state["entities_text"], 
            height=400,
            help="Modify the JSON structure to match your hardware design"
        )
    
    with col2:
        st.markdown("**🔧 Actions**")
        
        # Sample data buttons
        st.markdown("**📋 Load Samples**")
        col_arduino, col_lora = st.columns(2)
        with col_arduino:
            if st.button("Arduino", use_container_width=True):
                arduino_path = Path("examples/arduino_entities.json")
                if arduino_path.exists():
                    sample_json = arduino_path.read_text()
                    st.session_state["entities_text"] = sample_json
                    st.success("Arduino sample loaded!")
                    st.rerun()
                else:
                    st.error("Arduino sample not found")
        
        with col_lora:
            if st.button("LoRa", use_container_width=True):
                lora_path = Path("examples/lora_entities.json")
                if lora_path.exists():
                    sample_json = lora_path.read_text()
                    st.session_state["entities_text"] = sample_json
                    st.success("LoRa sample loaded!")
                    st.rerun()
                else:
                    st.error("LoRa sample not found")
        
        st.divider()
        
        # Validate button
        if st.button("✅ Validate JSON", use_container_width=True):
            try:
                data = json.loads(st.session_state["entities_text"])
                ent = ParsedEntities.model_validate(data)
                st.session_state["entities_obj"] = ent
                st.success("✅ Valid JSON structure!")
                
                # Show summary
                st.markdown("**📊 Summary:**")
                st.write(f"• **Title:** {ent.title}")
                st.write(f"• **Power Rails:** {len(ent.rails)}")
                st.write(f"• **Oscillators:** {len(ent.oscillators)}")
                st.write(f"• **Tests:** {len(ent.functional_tests)}")
                
            except Exception as e:
                st.error(f"❌ Invalid JSON: {e}")
        
        # Generate plan button
        if st.button("🚀 Generate Test Plan", type="primary", use_container_width=True):
            try:
                data = json.loads(st.session_state["entities_text"])
                ent = ParsedEntities.model_validate(data)
                
                # Show extracted entities
                st.subheader("📋 Extracted Entities")
                st.json(ent.model_dump(), expanded=False)
                
                # Generate plan
                issues = validate_entities(ent)
                plan = generate_plan_llm(ent) if use_llm else generate_plan_offline(ent)
                plan = annotate_plan(plan, issues)
                md = plan.to_markdown() if plan.steps else (plan.notes or "")
                
                # Update session state
                st.session_state["plan_md"] = md
                st.session_state["entities_obj"] = ent
                
                st.success("🎉 Test plan generated! Switch to 'Generated Plan' tab to view.")
                
            except Exception as e:
                st.error(f"❌ Error generating plan: {e}")
                st.exception(e)

# ---- Plan Tab ----
with tab_plan:
    st.subheader("📋 Generated Test Plan")
    
    if not st.session_state["plan_md"]:
        st.info("""
        📝 **No test plan yet!** 
        
        1. Go to **Upload Files** tab to upload design documents, OR
        2. Go to **Configure Entities** tab to edit the JSON and generate a plan
        """)
    else:
        # Display the plan
        st.markdown(st.session_state["plan_md"])
        
        st.divider()
        
        # Download section
        st.subheader("📥 Download Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📄 Download Test Plan (Markdown)",
                data=st.session_state["plan_md"],
                file_name="testplan.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        with col2:
            if st.session_state["entities_obj"]:
                st.download_button(
                    label="📋 Download Entities (JSON)",
                    data=st.session_state["entities_obj"].model_dump_json(indent=2),
                    file_name="entities.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        # Plan statistics
        if st.session_state["entities_obj"]:
            ent = st.session_state["entities_obj"]
            st.markdown("**📊 Plan Statistics:**")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Power Rails", len(ent.rails))
            with col2:
                st.metric("Oscillators", len(ent.oscillators))
            with col3:
                st.metric("Functional Tests", len(ent.functional_tests))
            with col4:
                total_steps = len([line for line in st.session_state["plan_md"].split('\n') if line.startswith('**') and '.' in line])
                st.metric("Test Steps", total_steps)