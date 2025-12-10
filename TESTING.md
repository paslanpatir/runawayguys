# Testing the Runaway Guys App Locally

This guide will help you test the refactored survey flow on your local machine.

## Prerequisites

1. **Python 3.10** (as specified in `pyproject.toml`)
2. **Virtual environment** (recommended)

## Setup Steps

### 1. Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Option 1: Install from requirements.txt (recommended)
pip install -r requirements.txt

# Option 2: Install core dependencies directly
pip install streamlit boto3 pandas numpy

# Note: You don't need to install the package in editable mode for local testing
```

### 3. Verify Data Files

Make sure you have the required CSV files in the `data/` directory:
- `GetToKnowQuestions.csv`
- `RedFlagCategories.csv`
- `RedFlagFilters.csv`
- `RedFlagQuestions.csv`
- `session_feedback.csv`
- `session_gtk_responses.csv`
- `session_responses.csv`
- `session_toxicity_rating.csv`
- `Summary_Sessions.csv`

### 4. Run the App

```bash
streamlit run app.py
```

The app will automatically:
- Open in your default web browser
- Use CSV files for data storage (no AWS credentials needed for local testing)
- Start at `http://localhost:8501`

## Testing the Flow

The survey flow consists of these steps:

1. **Language Selection** - Choose TR or EN
2. **User Details** - Enter name and email
3. **Boyfriend Name** - Enter boyfriend's name
4. **Welcome** - Welcome message
5. **Filter Questions** - Answer filter questions
6. **RedFlag Questions** - Answer toxicity questions
7. **GetToKnow Questions** - Answer additional questions
8. **Toxicity Opinion** - Rate toxicity level
9. **Results** - View results and comparison
10. **Feedback** - Provide feedback rating
11. **Goodbye** - Final message and data saving

## Local Testing Configuration

In `app.py`, the database flags are set to:
- `DB_READ = False` - Reads from CSV files in `data/` directory
- `DB_WRITE = False` - Writes to CSV files in `data/` directory

This means:
- ✅ No AWS credentials needed
- ✅ All data stored locally in CSV files
- ✅ Perfect for testing and development

## Troubleshooting

### Import Errors
If you get import errors, make sure you're running from the project root directory:
```bash
cd C:\Users\Pelin\Documents\Projects\runawayguys
streamlit run app.py
```

### Missing Data Files
If you get errors about missing CSV files, check that all required files exist in the `data/` directory.

### Port Already in Use
If port 8501 is already in use, Streamlit will automatically try the next available port.

### Clear Session State
To start fresh, you can:
- Click the "Clear cache" button in Streamlit's menu (☰)
- Or restart the Streamlit server

## Debugging

You can add debug output by checking `st.session_state` in your code or using Streamlit's built-in debugging features.

## Next Steps

Once local testing is successful, you can:
1. Test with AWS DynamoDB by setting `DB_READ = True` and `DB_WRITE = True` (requires AWS credentials)
2. Deploy to Streamlit Cloud or other hosting platforms
3. Continue development and add new features

