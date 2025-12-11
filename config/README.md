# Configuration Files

This directory contains credential files and configuration files for the application.

## Configuration Files

- `dynamodb_tables.yaml` - DynamoDB table configurations (safe to commit to git)

## Setup Instructions

### AWS Credentials

1. Copy `aws_credentials.example.txt` to `aws_credentials.txt`
2. Fill in your AWS credentials:
   - Line 1: AWS Access Key ID
   - Line 2: AWS Secret Access Key
   - Line 3: AWS Region

**Example:**
```
AKIAIOSFODNN7EXAMPLE
wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
us-east-1
```

### Email Credentials

1. Copy `email_credentials.example.txt` to `email_credentials.txt`
2. Fill in your email credentials:
   - Line 1: SMTP Server
   - Line 2: SMTP Port
   - Line 3: Sender Email
   - Line 4: Sender Password (for Gmail, use App Password)

**Example:**
```
smtp.gmail.com
587
your-email@gmail.com
your-16-char-app-password
```

### LLM Credentials (Optional - for AI Insights)

1. Copy `llm_credentials.example.txt` to `llm_credentials.txt`
2. Choose a provider and fill in credentials:

**Option A: Hugging Face (Recommended)**
```
huggingface
hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
mistralai/Mistral-7B-Instruct-v0.2
```

**Option B: Groq (Very Fast)**
```
groq
gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
llama-3.1-8b-instant
```

**Setup:**
- **Hugging Face**: Get free token from https://huggingface.co/settings/tokens
- **Groq**: Get free API key from https://console.groq.com/

See `AVAILABLE_LLM_OPTIONS.md` for more details.

## Security Notes

⚠️ **IMPORTANT:**
- Never commit actual credential files (`*.txt`) to version control
- Only commit example/template files (`*.example.txt`)
- Use environment variables in production when possible
- Keep credentials secure and never share them

## Alternative: Environment Variables

Instead of using files, you can set environment variables:

**AWS:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`

**Email:**
- `SMTP_SERVER`
- `SMTP_PORT`
- `SENDER_EMAIL`
- `SENDER_PASSWORD`

**LLM:**
- `HF_API_TOKEN` (for Hugging Face)
- `GROQ_API_KEY` (for Groq)

Environment variables take precedence over config files.

