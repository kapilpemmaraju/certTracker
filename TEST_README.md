# Quick Test Guide

## 🧪 Safe Testing - No Risk of Sending to Everyone!

### Quick Test (Recommended First Step)
```bash
python test_workflow.py
```
**Result:** Creates 3 email drafts in Outlook. No emails sent. Safe to test!

### Test with Your Email
```bash
python test_workflow.py --test-email your.email@ibm.com
```
**Result:** Creates 3 drafts addressed to YOUR email only. Original recipients won't receive anything.

### Test More Emails
```bash
python test_workflow.py --limit 10
```
**Result:** Creates 10 drafts instead of 3.

## 📋 What Gets Created

After running test:
1. **Email Drafts** in Outlook Drafts folder
2. **Test Report** in `output/Test_Report_*.txt`
3. **Log File** `test_workflow.log`

## ✅ Safety Features

- ✅ **Draft Mode by Default** - No emails sent automatically
- ✅ **Limited Emails** - Only 3 by default (not all 126)
- ✅ **Test Email Override** - Send to yourself instead of employees
- ✅ **No History Recording** - Test multiple times without affecting production

## 🚀 After Testing Successfully

When you're ready for production:
```bash
python certification_workflow_outlook.py
```
This creates drafts for all 126 employees.

## 📖 Full Documentation

See `TEST_MODE_GUIDE.md` for complete testing instructions.

## ⚠️ Important Notes

- Always test with drafts first
- Review drafts in Outlook before sending
- Use `--test-email` to send to yourself only
- Default limit is 3 emails (safe for testing)

## 🆘 Need Help?

1. Check `test_workflow.log` for errors
2. Review `output/Test_Report_*.txt` for results
3. See `TEST_MODE_GUIDE.md` for detailed instructions