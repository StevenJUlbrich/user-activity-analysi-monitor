# User Guide - Client Activity Monitor

## Table of Contents
1. [Getting Started](#getting-started)
2. [Configuration](#configuration)
3. [Running Analysis](#running-analysis)
4. [Understanding Results](#understanding-results)
5. [Reporting Actions](#reporting-actions)
6. [Best Practices](#best-practices)

## Getting Started

### First-Time Setup

1. **Launch the Application**
   ```bash
   poetry run python src/client_activity_monitor/main.py
   ```

2. **Configure Oracle Client Settings**
   - Oracle Client Path: Browse to your Oracle Instant Client directory
   - KRB5 Config Path: Select your krb5.conf file
   - KRB5 Cache Path: Enter path where Kerberos stores tickets
   - User SID: Enter your employee ID (5-10 characters)

3. **Save Configuration**
   - Click "Save Config" to store settings
   - Settings are saved for future use

### Pre-Flight Checklist

Before running analysis:
- [ ] Obtain Kerberos ticket: `kinit username@DOMAIN`
- [ ] Verify ticket: `klist`
- [ ] Ensure network connectivity to databases
- [ ] Check VPN connection if required

## Configuration

### Understanding the Configuration Files

**configs/databases.yaml** (Admin-managed)
- Contains database connection details
- Defines which queries run on which database
- Not editable through UI

**configs/app_settings.yaml** (User settings)
- Stores your Oracle client paths
- Saves your SID for audit purposes
- Email recipients for reports

### Modifying Settings

To update your configuration:
1. Click "Edit Config" if settings are locked
2. Update the necessary fields
3. Click "Save Config"

## Running Analysis

### Steps to Run Analysis

1. **Verify Kerberos Authentication**
   - Check the "KINIT Executed?" checkbox
   - This confirms you have a valid Kerberos ticket

2. **Review Last Event Time**
   - This shows when the last report was run
   - Analysis looks for changes 24 hours before this time

3. **Click "Run Report"**
   - Button is only enabled when KINIT is checked
   - Analysis begins immediately

### What Happens During Analysis

1. **Connection Phase**
   - Connects to each configured database
   - Status shows "Connecting..."

2. **Query Execution**
   - Runs specific queries on each database
   - Shows "Running..." with live updates

3. **Data Processing**
   - Merges results from all databases
   - Filters for users meeting all criteria

4. **Report Generation**
   - Creates Excel report with results
   - Updates Last Event Time to current time

## Understanding Results

### Report Criteria

Users appear in the report if they have:
- Changed their password AND
- Changed their email AND
- Changed their phone number AND
- Changed their security token
- ALL within the same 24-hour window

### Reading the Excel Report

**User Activity Sheet**
- User ID: The user who made changes
- Change timestamps for each type
- Time window between first and last change
- Source database for each change

**Report Metadata Sheet**
- Who generated the report (your SID)
- When it was generated
- Analysis parameters used
- Summary statistics

### Database Status Panel

- **Green**: Query completed successfully
- **Blue**: Query currently running
- **Orange**: Connecting to database
- **Red**: Query or connection failed
- **Gray**: Pending or idle

## Reporting Actions

### Generate Email Report
1. Click "Generate Email Report"
2. Email client opens with:
   - Pre-filled recipients from configuration
   - Summary of findings in body
   - Instructions to attach Excel file
3. Manually attach the Excel report
4. Send to SOC team

### Copy Excel Path to Clipboard
- Copies full file path of report
- Use for manual file operations
- Helpful for email attachments

### OneNote Entry to Clipboard
- Copies summary line with:
  - Your SID
  - Report run time
  - Last event time  
  - Number of users found
- Paste into OneNote activity log

### Optional Save Report
- Exports data as CSV format
- Includes same data as Excel
- Useful for automated processing

## Best Practices

### Daily Workflow

1. **Morning Check**
   - Run `kinit` to get fresh ticket
   - Run analysis for overnight activity
   - Review any flagged users

2. **Investigation Process**
   - Note users in report
   - Check with identity management team
   - Document in incident tracking system

3. **Record Keeping**
   - Use OneNote entry for daily log
   - Save reports to shared drive
   - Email significant findings

### Performance Tips

- Run during off-peak hours for faster queries
- Close other database tools to free connections
- Monitor VPN connection stability
- Keep Kerberos ticket refreshed

### Security Reminders

- Never share your Kerberos credentials
- Lock workstation when away
- Review email recipients regularly
- Store reports in secure locations

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| "Run Report" disabled | Check KINIT checkbox |
| Connection failed | Run `kinit` again |
| No results found | Normal - no suspicious activity |
| Queries timing out | Check network/VPN connection |
| Excel won't open | Check default program associations |

## Need Help?

- Application issues: Contact IT Support
- Database access: Contact DBA team  
- Security questions: Contact SOC lead
- Report interpretation: See SOC procedures