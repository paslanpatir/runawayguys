# Configuration Setup Guide

This guide explains how to set up credentials for AWS and Email services.

## Quick Setup

### 1. AWS Credentials

**Option A: Using Config File (Recommended for Local Development)**

1. Copy the example file:
   ```bash
   cp config/aws_credentials.example.txt config/aws_credentials.txt
   ```

2. Edit `config/aws_credentials.txt` and add your credentials:
   ```
   YOUR_AWS_ACCESS_KEY_ID
   YOUR_AWS_SECRET_ACCESS_KEY
   YOUR_AWS_REGION
   ```

**Option B: Using Environment Variables (Recommended for Production)**

Set these environment variables:
```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=your_region
```

### 2. Email Credentials

**Option A: Using Config File (Recommended for Local Development)**

1. Copy the example file:
   ```bash
   cp config/email_credentials.example.txt config/email_credentials.txt
   ```

2. Edit `config/email_credentials.txt` and add your credentials:
   ```
   smtp.gmail.com
   587
   your-email@gmail.com
   your-app-password
   ```

**Option B: Using Environment Variables (Recommended for Production)**

Set these environment variables:
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

**Option C: Using .env File**

Create a `.env` file in the project root:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

## Priority Order

Credentials are loaded in this order (first found wins):

1. **Direct parameters** (if passed to constructor)
2. **Environment variables**
3. **Config files** (`config/aws_credentials.txt` or `config/email_credentials.txt`)
4. **Default values** (for SMTP server/port only)

## Security

✅ **DO:**
- Use environment variables in production
- Keep credential files local only
- Use App Passwords for Gmail (not your regular password)
- Review `.gitignore` to ensure secrets are excluded

❌ **DON'T:**
- Commit actual credential files to git
- Share credentials in chat/email
- Use production credentials in development
- Store credentials in code

## File Structure

```
config/
├── README.md                          # This guide
├── aws_credentials.example.txt        # Template (safe to commit)
├── email_credentials.example.txt       # Template (safe to commit)
├── aws_credentials.txt                # Your credentials (gitignored)
└── email_credentials.txt              # Your credentials (gitignored)
```

## Gmail App Password Setup

For Gmail, you need to create an App Password:

1. Go to https://myaccount.google.com/
2. Security → 2-Step Verification (enable if not already)
3. App passwords → Generate new password
4. Select "Mail" and your device
5. Copy the 16-character password
6. Use this password (not your regular Gmail password)

## Troubleshooting

### "File not found" errors
- Make sure you copied the example files
- Check file paths are correct
- Verify files are in the `config/` directory

### "Credentials not configured" warnings
- Check environment variables are set correctly
- Verify config files exist and have correct format
- Check file permissions (should be readable)

### Authentication failures
- For Gmail: Make sure you're using an App Password
- Verify SMTP server and port are correct
- Check credentials don't have extra spaces/newlines

