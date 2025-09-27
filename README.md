Aeronix Ignite Hackathon at UF
Hackathon Test Plan Generator
A complete hardware bring-up/test plan generator with CLI and web interface, developed for the Aeronix Ignite Hackathon at University of Florida.

Features
CLI interface for batch processing
Streamlit web UI for interactive use
Netlist parser (IPC-D-356A format)
JSON entity support
Offline deterministic templates
Optional LLM enhancement
Professional test plan generation
Quick Start
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m app.cli examples/lora_entities.json --out out/testplan.md
streamlit run app/web.py
Project Structure
hackathon-testplan/
├── app/           # CLI and web interfaces
├── core/          # Core models and generators
├── ingest/        # File parsers (PDF, BOM, netlist)
├── nlp/           # LLM integration
├── rules/         # Validation and annotation
├── examples/      # Sample data files
├── tests/         # Test suite
└── out/           # Generated test plans
Git Repo Link: https://github.com/Deepika-muchukota/Aeronix_Hackathon_PCB_Analyzer

License
MIT
