# Runaway Guys - Toxic Boyfriend Detector

A Streamlit-based survey application that helps users assess the toxicity level of their relationships through a comprehensive questionnaire.

## Overview

This application guides users through a multi-step survey to evaluate relationship red flags and toxicity indicators. It collects responses, calculates toxicity scores, generates AI-powered insights, and provides detailed reports via email.

## Application Flow

The survey consists of the following steps:

1. **Language Selection** - Choose between Turkish (TR) or English (EN)
2. **User Details** - Enter name and optional email
3. **Boyfriend Name** - Enter the name of the person being evaluated
4. **Welcome & GTK Questions** - Welcome message and GetToKnow questions
5. **Filter Questions** - Initial screening questions (F1-F15)
6. **RedFlag Questions** - Main toxicity assessment questions (Q1-Q75)
7. **Toxicity Opinion** - User's subjective toxicity rating
8. **Results** - Display toxicity score, AI insights, and category-based analysis
9. **Feedback** - Collect user feedback on the survey
10. **Report** - Send email report (if email provided) and show goodbye message

## Project Structure

```
├── app.py                 <- Local entry point (for development)
├── streamlit_app.py       <- Production entry point (for Streamlit Cloud)
├── requirements.txt       <- Python dependencies
├── README.md              <- This file
│
├── src/                   <- Main source code
│   ├── main.py            <- Application entry point and step orchestration
│   │
│   ├── application/       <- Application layer
│   │   ├── steps/         <- Survey step implementations
│   │   │   ├── ask_language.py
│   │   │   ├── ask_user_details.py
│   │   │   ├── ask_boyfriend_name.py
│   │   │   ├── welcome.py              <- Welcome + GTK questions
│   │   │   ├── ask_filter_questions.py
│   │   │   ├── redflag_questions_step.py
│   │   │   ├── toxicity_opinion_step.py
│   │   │   ├── results_step.py
│   │   │   ├── feedback_step.py
│   │   │   └── report_step.py
│   │   ├── base_step.py
│   │   ├── messages.py
│   │   ├── session_manager.py
│   │   └── survey_controller.py
│   │
│   ├── domain/            <- Domain layer (value objects, mappers)
│   │   ├── value_objects.py
│   │   └── mappers.py
│   │
│   ├── adapters/          <- Adapters for external services
│   │   ├── database/      <- CSV and DynamoDB adapters
│   │   ├── email/         <- Email sending adapter
│   │   └── llm/           <- LLM adapters (Hugging Face, Groq)
│   │
│   ├── services/          <- Business logic services
│   │   ├── insight_service.py
│   │   └── insight_prompt_builder.py
│   │
│   ├── utils/             <- Utility functions
│   │   ├── constants.py
│   │   ├── session_id_generator.py
│   │   ├── summary_updater.py
│   │   └── ...
│   │
│   └── ports/             <- Port interfaces
│       ├── database_port.py
│       ├── email_port.py
│       └── llm_port.py
│
├── data/                  <- CSV data files (when using CSV mode)
│   ├── RedFlagQuestions.csv
│   ├── RedFlagFilters.csv
│   ├── GetToKnowQuestions.csv
│   ├── session_responses.csv
│   └── ...
│
├── notebooks/             <- Jupyter notebooks for data management
│   └── cold_start/        <- Data initialization and management utilities
│       ├── 03_initialize_tables.ipynb
│       ├── 04_delete_session.ipynb
│       ├── 07_reassign_session_ids.ipynb
│       └── 08_clear_all_data.ipynb
│
├── config/                <- Configuration files
│   ├── aws_credentials.txt    <- AWS credentials for DynamoDB
│   ├── email_credentials.txt  <- Email credentials for SMTP
│   └── llm_credentials.txt   <- LLM API credentials
│
└── documentation/         <- Additional documentation
    ├── CONFIG_SETUP.md
    ├── EMAIL_SETUP.md
    └── ...
```

## Getting Started

### Prerequisites

- Python 3.8+
- Streamlit
- AWS credentials (if using DynamoDB)
- Email credentials (if sending email reports)
- LLM API credentials (if using AI insights)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. **Database**: Set `DB_READ` and `DB_WRITE` flags in `app.py` or `streamlit_app.py`
   - `False`: Use CSV files in `data/` folder
   - `True`: Use DynamoDB (requires AWS credentials in `config/aws_credentials.txt`)

2. **Email**: Configure SMTP settings in `config/email_credentials.txt` (optional)

3. **LLM**: Configure LLM API credentials in `config/llm_credentials.txt` (optional)

### Running Locally

```bash
streamlit run app.py
```

### Deployment to Streamlit Cloud

The application is configured to run on Streamlit Cloud using `streamlit_app.py`. Make sure to:
- Set up secrets in Streamlit Cloud dashboard
- Configure AWS credentials, email credentials, and LLM credentials as secrets

## Features

- **Multi-language Support**: Turkish and English
- **Flexible Data Storage**: CSV files or DynamoDB
- **AI-Powered Insights**: LLM-generated personalized insights
- **Email Reports**: Detailed reports sent via email
- **Category-Based Analysis**: Toxicity scores per category
- **Filter Question Detection**: Identifies violated filter questions

## Data Management

Use the notebooks in `notebooks/cold_start/` for:
- Initializing tables with default values
- Managing session records
- Reassigning session IDs
- Clearing data

See `notebooks/cold_start/README.md` for detailed instructions.

## License

See LICENSE file for details.

--------

