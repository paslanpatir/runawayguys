# Configuration Files

This directory contains credential files for the application.

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

Environment variables take precedence over config files.

