# Email Setup Guide

This guide explains how to configure automatic email sending for survey results.

## Configuration Options

### Option 1: Environment Variables (Recommended)

Set these environment variables before running the app:

**Windows (PowerShell):**
```powershell
$env:SMTP_SERVER="smtp.gmail.com"
$env:SMTP_PORT="587"
$env:SENDER_EMAIL="your-email@gmail.com"
$env:SENDER_PASSWORD="your-app-password"
```

**Windows (Command Prompt):**
```cmd
set SMTP_SERVER=smtp.gmail.com
set SMTP_PORT=587
set SENDER_EMAIL=your-email@gmail.com
set SENDER_PASSWORD=your-app-password
```

**Linux/Mac:**
```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="your-app-password"
```

### Option 2: .env File

Create a `.env` file in the project root:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

Then install python-dotenv (already in requirements.txt) and the app will automatically load it.

### Option 3: Modify Code Directly

Edit `src/email_sender.py` and set the values directly in the `EmailSender.__init__()` method (not recommended for production).

## Gmail Setup

If using Gmail, you need to:

1. **Enable 2-Step Verification** on your Google account
2. **Create an App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
   - Use this 16-character password (not your regular Gmail password)

## Other Email Providers

### Outlook/Hotmail
```
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

### Yahoo
```
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

### Custom SMTP Server
Use your email provider's SMTP settings. Common ports:
- 587 (TLS/STARTTLS - recommended)
- 465 (SSL)
- 25 (usually blocked by ISPs)

## Testing

To test email sending:

1. Set up your environment variables
2. Run the app: `streamlit run app.py`
3. Complete the survey and check "Would you like to receive the results via email?"
4. Enter your email address
5. Complete the survey - you should receive an email at the Report step

## Troubleshooting

### "Email credentials not configured"
- Make sure environment variables are set correctly
- Check that variable names match exactly (case-sensitive)

### "Authentication failed"
- For Gmail: Make sure you're using an App Password, not your regular password
- Check that 2-Step Verification is enabled
- Verify SMTP server and port are correct

### "Connection timeout"
- Check your internet connection
- Verify SMTP server address is correct
- Some networks block SMTP ports - try a different network or use port 465 with SSL

### Email not received
- Check spam/junk folder
- Verify recipient email address is correct
- Check sender email configuration
- Look at console output for error messages

## Security Notes

⚠️ **Never commit email credentials to version control!**

- Use environment variables or `.env` file
- Add `.env` to `.gitignore`
- For production, use secure secret management (AWS Secrets Manager, Azure Key Vault, etc.)

## Customizing Email Content

Edit the `_create_email_body()` method in `src/email_sender.py` to customize:
- Email template
- Styling
- Additional information
- Language-specific content

