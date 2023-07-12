import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, open_sqlite_db_readonly

def get_pSettings(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('googlesettings.db'):
            break# Skip all other files
        
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select 
    name,
    value
    from partner
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Partner Settings')
        report.start_artifact_report(report_folder, 'Partner Settings')
        report.add_script()
        data_headers = ('Name','Value' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'partner settings'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No Partner Settings data available')
    
    db.close()

__artifacts__ = {
        "pSettings": (
                "Device Info",
                ('*/com.google.android.gsf/databases/googlesettings.db*'),
                get_pSettings)
}
