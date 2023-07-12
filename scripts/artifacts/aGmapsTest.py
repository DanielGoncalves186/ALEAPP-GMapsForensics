import xml.etree.ElementTree as ET

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_aGmapsTest(files_found, report_folder, seeker, wrap_text):
    lastUsed = ''
    file_found = str(files_found[0])
    xmlTree = ET.parse(file_found)
    root = xmlTree.getroot()
    for child in root:
        if child.attrib['name'] == "last-used-date":
            print("Last used date found: " + child.text)
            lastUsed = child.text

    report = ArtifactHtmlReport('Last used date')
    report.start_artifact_report(report_folder, 'Last used date')
    report.add_script()
    data_headers = ('Last used date',)
    data_list = []
    data_list.append((lastUsed, ''))
    report.write_artifact_data_table(data_headers, data_list, file_found)
    report.end_artifact_report()
    tsvname = f'Last used date'
    tsv(report_folder, data_headers, data_list, tsvname)

__artifacts__ = {
        "A Gmaps Test": (
                "aGampsTest",
                ('*/com.google.android.apps.maps/shared_prefs/FirebaseHeartBeatQ0hJTUVfQU5EUk9JRF9TREs+MTo3NDc2NTQ1MjAyMjA6YW5kcm9pZDowMDAwMDAwMDAwMDAwMDAw.xml'),
                get_aGmapsTest)
}