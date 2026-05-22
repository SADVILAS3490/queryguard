# QueryGuard

AI-Powered Data Quality Validator and SQL Chat Agent

Built by Sadvilas Buddiga

## What It Does

- Data Quality Validation: runs YAML rules against any CSV and scores 0-100
- AI Explanation: explains issues in plain English
- SQL Chat Agent: ask questions in plain English, get SQL results instantly
- Live Dashboard: interactive Streamlit UI

## Tech Stack

- Python, pandas, SQLite, OpenAI, Streamlit, pyyaml, sentence-transformers

## Quick Start

    git clone https://github.com/SADVILAS3490/queryguard.git
    cd queryguard
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env
    python3 -m streamlit run src/queryguard/reporting/streamlit_app.py

## Works Without API Key

Runs in demo mode without OpenAI API key. All quality checks run fully locally.

## License

MIT
