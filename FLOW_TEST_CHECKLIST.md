# Survey Flow Test Checklist

Use this checklist to test the complete refactored survey flow.

## Pre-Test Setup

- [ ] App is running: `streamlit run app.py`
- [ ] Browser opened to `http://localhost:8501` (or the port shown)
- [ ] Email credentials configured (if testing email sending):
  - Option 1: Set environment variables
  - Option 2: Create `config/email_credentials.txt`

## Flow Steps to Test

### 1. Language Selection ✅
- [ ] Page shows language selection (TR/EN)
- [ ] Can select language
- [ ] Progress bar appears
- [ ] Clicking "Continue" advances to next step

### 2. User Details ✅
- [ ] Name field is required
- [ ] Email field is optional (labeled "Optional")
- [ ] Can proceed with just name (no email)
- [ ] If email provided, it's validated
- [ ] Invalid email shows error message
- [ ] Valid email allows proceeding

### 3. Boyfriend Name ✅
- [ ] Shows input field for boyfriend's name
- [ ] Can enter name and continue
- [ ] Name is required

### 4. Welcome ✅
- [ ] Shows welcome message with user's name
- [ ] Shows description and instructions
- [ ] Continue button advances

### 5. Filter Questions ✅
- [ ] Questions load from CSV/DynamoDB
- [ ] Questions are randomized
- [ ] Can answer questions (slider/radio based on type)
- [ ] Continue button saves responses
- [ ] Progress bar updates

### 6. RedFlag Questions ✅
- [ ] Questions load correctly
- [ ] "Not Applicable" checkbox works
- [ ] Can answer applicable questions
- [ ] Scoring works correctly
- [ ] Continue button saves responses

### 7. GetToKnow Questions ✅
- [ ] Questions load correctly
- [ ] Different question types work (Range, YES/NO)
- [ ] Continue button saves responses

### 8. Toxicity Opinion ✅
- [ ] Shows slider with toxicity options
- [ ] Can select toxicity level
- [ ] "See Results" button advances

### 9. Results ✅
- [ ] Balloons animation appears
- [ ] Shows toxicity score
- [ ] Shows comparison messages (pass/fail)
- [ ] Shows filter violations info
- [ ] Graph displays (if data available)
- [ ] "Finish" button advances

### 10. Feedback ✅
- [ ] Shows star rating feedback
- [ ] Can select rating
- [ ] Continue button saves feedback

### 11. Report (Email) ✅
- [ ] If email was provided:
  - [ ] Shows "Report sent" message
  - [ ] Email is actually sent (check inbox)
- [ ] If no email:
  - [ ] Shows "Email sending skipped" message
- [ ] Step completes successfully

### 12. Goodbye ✅
- [ ] Shows goodbye message
- [ ] Balloons animation
- [ ] Data is saved to CSV/DynamoDB
- [ ] Survey completes

## Data Verification

After completing a survey:

- [ ] Check `data/session_responses.csv` - new record added
- [ ] Check `data/session_gtk_responses.csv` - new record added
- [ ] Check `data/session_toxicity_rating.csv` - new record added
- [ ] Check `data/session_feedback.csv` - new record added
- [ ] All records have correct data
- [ ] IDs are auto-incremented correctly

## Email Testing

If email was provided:

- [ ] Email received in inbox
- [ ] Email has correct subject
- [ ] Email contains user name
- [ ] Email contains boyfriend name
- [ ] Email shows toxicity score
- [ ] Email shows filter violations
- [ ] Email formatting looks good (HTML)

## Error Scenarios

- [ ] Missing name - shows error
- [ ] Invalid email format - shows error
- [ ] Missing email credentials - shows warning (doesn't crash)
- [ ] Missing data files - handles gracefully

## Notes

- Progress bar should update at each step
- Session state should persist between reruns
- All steps should be accessible in order
- No steps should be skipped unexpectedly

