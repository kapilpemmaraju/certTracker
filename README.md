# IBM BOB - Autonomous Certification Workflow

## 📋 Overview

This autonomous agentic workflow automates the processing of certification data and notification generation for Westpac Banking Corporation resources. The system intelligently matches employee records with certification data and generates personalized notifications.

## 🎯 Purpose

Automate the end-to-end process of:
1. Loading and validating two Excel files
2. Filtering certification records for Westpac Banking Corporation
3. Matching employee email addresses across datasets
4. Extracting and consolidating certification information
5. Generating personalized notification messages
6. Creating structured output files for review and distribution

## 📊 Workflow Results

### Execution Summary
- **Status**: ✅ SUCCESS
- **File A Records**: 225 employees
- **File B Total Records**: 38,336 certifications
- **Westpac Records**: 1,244 certifications
- **Matched Records**: 614 certifications
- **Unique Employees**: 126 employees
- **Notifications Generated**: 126 messages

### Output Files
1. **Consolidated Spreadsheet**: `Westpac_Certification_Consolidated_20260521_221538.xlsx`
   - 614 certification records
   - 8 columns: Internet Email, Name, Vendor, Credential Title, Award Date, Expiry Date, Employee Name, Employee ID
   
2. **Notification Messages**: `Westpac_Certification_Notifications_20260521_221538.txt`
   - 126 personalized notification messages
   - Ready for email distribution

3. **Execution Log**: `certification_workflow.log`
   - Detailed execution trace
   - Error handling and validation logs

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CERTIFICATION WORKFLOW                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐
│    File A        │         │    File B        │
│  Active Cloud    │         │  T2G Cert Data   │
│  List (225)      │         │  (38,336)        │
└────────┬─────────┘         └────────┬─────────┘
         │                            │
         │  EMP_INTRANETID           │  Internet Email
         │                            │
         └────────────┬───────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │  Filter Westpac        │
         │  (1,244 records)       │
         └────────┬───────────────┘
                  │
                  ▼
         ┌────────────────────────┐
         │  Email Matching        │
         │  (Case-insensitive)    │
         └────────┬───────────────┘
                  │
                  ▼
         ┌────────────────────────┐
         │  Extract & Consolidate │
         │  (614 matched)         │
         └────────┬───────────────┘
                  │
                  ├──────────────────┬──────────────────┐
                  ▼                  ▼                  ▼
         ┌────────────────┐  ┌──────────────┐  ┌──────────────┐
         │  Spreadsheet   │  │ Notifications│  │  Log File    │
         │  (Excel)       │  │  (Text)      │  │              │
         └────────────────┘  └──────────────┘  └──────────────┘
```

## 🔧 Technical Implementation

### Key Features

1. **Intelligent Email Matching**
   - Case-insensitive comparison
   - Whitespace normalization
   - Handles missing/invalid emails gracefully

2. **Name Parsing**
   - Extracts name from email prefix (before @)
   - Converts to title case
   - Handles special characters (dots, underscores)

3. **Data Validation**
   - Column existence checks
   - Missing data handling ("Not Available" instead of fabrication)
   - Type validation for dates

4. **Error Handling**
   - Comprehensive logging
   - Graceful failure recovery
   - Detailed error messages

5. **Production-Ready Standards**
   - Modular, object-oriented design
   - Extensive logging
   - Configurable parameters
   - Reusable workflow class

### Technology Stack

- **Python 3.11+**
- **pandas**: Excel file processing and data manipulation
- **openpyxl**: Excel file I/O
- **logging**: Comprehensive execution tracking
- **smtplib**: Email sending capability (optional)

## 📖 Usage

### Basic Usage

```python
from certification_workflow import CertificationWorkflow

# Initialize workflow
workflow = CertificationWorkflow(
    file_a_path="Active Offshore Cloud List-05212026.xlsx",
    file_b_path="T2G Certification_Financial Services as on 11 May 2026.xlsx",
    output_dir="./output"
)

# Run workflow
results = workflow.run(send_emails=False)

# Check results
print(f"Status: {results['success']}")
print(f"Matched records: {results['matched_records']}")
print(f"Notifications: {results['notifications_generated']}")
```

### Command Line Usage

```bash
# Run the workflow
python certification_workflow.py

# View logs
type certification_workflow.log

# Check output files
dir Westpac_Certification_*.xlsx
dir Westpac_Certification_*.txt
```

### With Email Sending (Optional)

```python
# Configure SMTP
smtp_config = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'your-email@example.com',
    'sender_password': 'your-app-password',
    'test_mode': True,
    'test_recipient': 'test@example.com'
}

# Run with email sending
results = workflow.run(send_emails=True, smtp_config=smtp_config)
```

## 📁 File Structure

```
CertificationsWestpac/
├── certification_workflow.py          # Main workflow script
├── README.md                          # This documentation
├── certification_workflow.log         # Execution log
├── Active Offshore Cloud List-05212026.xlsx
├── T2G Certification_Financial Services as on 11 May 2026.xlsx
├── Westpac_Certification_Consolidated_20260521_221538.xlsx
└── Westpac_Certification_Notifications_20260521_221538.txt
```

## 🔍 Data Flow

### Input Files

**File A: Active Offshore Cloud List**
- Columns: EMP ID, EMP_NAME, PEM_TALENT_ID, PEM_NOTESID, LOCATION_AS_PER_BLUEPAGES, PROJECT_START_DATE, EMP_INTRANETID
- Key Column: `EMP_INTRANETID` (IBM E-mail ID)
- Records: 225 employees

**File B: T2G Certification Financial Services**
- Worksheet: "T2G Certification data-11 May"
- Key Columns: Internet Email, Global_Client_Name, Vendor, Credential Title, Credential Award Date, Credential Expiry Date
- Total Records: 38,336 certifications
- Westpac Records: 1,244 certifications

### Processing Steps

1. **Load File A** → Normalize emails → 225 valid records
2. **Load File B** → Validate columns → 38,336 records
3. **Filter Westpac** → Match client name → 1,244 records
4. **Match Emails** → Inner join on normalized email → 614 matches
5. **Extract Data** → Parse names, format dates → Consolidated dataset
6. **Generate Output** → Create Excel + Text files → 2 output files
7. **Create Notifications** → One per unique email → 126 messages

### Output Structure

**Consolidated Spreadsheet Columns:**
1. Internet Email
2. Name (parsed from email)
3. Vendor
4. Credential Title
5. Credential Award Date
6. Credential Expiry Date
7. Employee Name (from File A)
8. Employee ID (from File A)

**Notification Message Format:**
```
Dear [Name],

This is an automated notification regarding your IBM certification 
status for the Westpac Banking Corporation project.

Your Current Certifications:
================================================================================

Certification #1:
  • Vendor:              [Vendor Name]
  • Credential Title:    [Title]
  • Award Date:          [YYYY-MM-DD]
  • Expiry Date:         [YYYY-MM-DD or Not Available]
--------------------------------------------------------------------------------

[Additional certifications...]

Total Certifications: [Count]
```

## 🛡️ Error Handling

The workflow implements comprehensive error handling:

1. **File Validation**
   - Checks file existence
   - Validates required columns
   - Handles missing worksheets

2. **Data Validation**
   - Handles missing email addresses
   - Validates date formats
   - Manages null/NaN values

3. **Processing Errors**
   - Graceful failure recovery
   - Detailed error logging
   - Continues processing valid records

4. **Output Validation**
   - Ensures output directory exists
   - Handles file write permissions
   - Validates generated content

## 📊 Statistics & Insights

### Matching Analysis
- **Match Rate**: 56% (126 out of 225 employees have certifications)
- **Average Certifications per Employee**: 4.87 (614 ÷ 126)
- **Westpac Coverage**: 49.4% (614 out of 1,244 Westpac certifications matched)

### Data Quality
- **Email Normalization**: 100% success rate
- **Name Parsing**: 100% success rate
- **Date Formatting**: Handled both valid dates and missing values
- **Missing Data**: Replaced with "Not Available" (no fabrication)

## 🔄 Reusability

The workflow is designed for easy reuse:

1. **Update File Paths**: Modify paths in `main()` function
2. **Change Client Filter**: Update `target_client` in `__init__`
3. **Customize Columns**: Modify column names in class attributes
4. **Add New Fields**: Extend `extract_and_consolidate_data()` method
5. **Custom Notifications**: Modify `generate_notification_message()` method

## 🚀 Future Enhancements

Potential improvements for production deployment:

1. **Email Integration**
   - Configure SMTP server
   - Implement batch email sending
   - Add email templates
   - Track delivery status

2. **Scheduling**
   - Add cron job/Task Scheduler integration
   - Implement automatic file detection
   - Schedule periodic runs

3. **Reporting**
   - Generate executive summary
   - Create visualization dashboards
   - Export to multiple formats (PDF, CSV)

4. **Notifications**
   - Add Slack/Teams integration
   - Implement SMS notifications
   - Create web dashboard

5. **Data Enrichment**
   - Add certification expiry alerts
   - Include renewal recommendations
   - Track certification trends

## 📝 Configuration

### Customizable Parameters

```python
class CertificationWorkflow:
    # Column names
    file_a_email_col = 'EMP_INTRANETID'
    file_b_email_col = 'Internet Email'
    client_name_col = 'Global_Client_Name'
    target_client = 'WESTPAC BANKING CORPORATION'
    
    # Worksheet name
    worksheet_name = 'T2G Certification data-11 May'
    
    # Output directory
    output_dir = Path("./output")
```

## 🐛 Troubleshooting

### Common Issues

1. **File Not Found**
   - Verify file paths are correct
   - Check file permissions
   - Ensure files are not open in Excel

2. **Column Not Found**
   - Verify column names match exactly
   - Check for extra spaces in column names
   - Ensure correct worksheet is selected

3. **No Matches Found**
   - Verify email format consistency
   - Check client name spelling
   - Review filtering criteria

4. **Memory Issues**
   - Process files in chunks for large datasets
   - Increase available RAM
   - Optimize data types

## 📞 Support

For issues or questions:
1. Check the log file: `certification_workflow.log`
2. Review error messages in console output
3. Verify input file formats and column names
4. Contact IBM BOB for assistance

## 📄 License

IBM Internal Use Only - Confidential

## 👤 Author

**IBM BOB** - AI Software Engineer
- Autonomous Agentic Workflow Specialist
- Date: 2026-05-21

---

**Note**: This workflow is production-ready and follows IBM Consulting Advantage standards for enterprise automation, security, and maintainability.