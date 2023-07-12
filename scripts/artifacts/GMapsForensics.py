import xml.etree.ElementTree as ET

from datetime import datetime
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_GMapsFirstUsed(files_found, report_folder, seeker, wrap_text):
    firstUsed = ''
    file_found = str(files_found[0])
    xmlTree = ET.parse(file_found)
    root = xmlTree.getroot()
    for child in root:
        if child.attrib['name'] == "first_open_time":
            print("First used date found: " + child.attrib['value'])
            firstUsed = child.attrib['value']

    firstUsedDatetime = firstUsed
    report = ArtifactHtmlReport('GMapsFirstUsed')
    report.start_artifact_report(report_folder, 'GMapsFirstUsed')
    report.add_script()
    data_headers = ('GMapsFirstUsed',)
    data_list = []
    data_list.append(('First used date', firstUsedDatetime))
    report.write_artifact_data_table(data_headers, data_list, file_found)
    report.end_artifact_report()
    tsvname = f'First used date'
    tsv(report_folder, data_headers, data_list, tsvname)

def get_GMapsLastUsed(files_found, report_folder, seeker, wrap_text):
    lastUsed = ''
    file_found = str(files_found[0])
    xmlTree = ET.parse(file_found)
    root = xmlTree.getroot()
    for child in root:
        if child.attrib['name'] == "last-used-date":
            print("Last used date found: " + child.text)
            lastUsed = child.text

    report = ArtifactHtmlReport('GMapsLastUsed')
    report.start_artifact_report(report_folder, 'GMapsLastUsed')
    report.add_script()
    data_headers = ('GMapsLastUsed',)
    data_list = []
    data_list.append(('Last used date', lastUsed))
    report.write_artifact_data_table(data_headers, data_list, file_found)
    report.end_artifact_report()
    tsvname = f'Last used date'
    tsv(report_folder, data_headers, data_list, tsvname)

def get_GMapsSettings(files_found, report_folder, seeker, wrap_text):
    voiceBundles = ''
    currentAccountId = ''
    satelite = ''
    locationSharing = ''
    appVersion = ''
    voicePref = ''
    file_found = str(files_found[0])
    xmlTree = ET.parse(file_found)
    root = xmlTree.getroot()
    for child in root:
        if child.attrib['name'] == "voice_bundles":
            print("Voice bundles found: " + child.text)
            voiceBundles = child.text
        if child.attrib['name'] == "current_account_id":
            print("Current account id found: " + child.text)
            currentAccountId = child.text
        if child.attrib['name'] == "satellite_on_at_startup":
            print("Satellite on at startup found: " + child.attrib['value'])
            satelite = child.attrib['value']
        if child.attrib['name'] == "location_sharing_diversion_criteria":
            print("Location sharing diversion criteria found: " + child.text)
            locationSharing = child.text
        if child.attrib['name'] == "app_version":
            print("App version found: " + child.text)
            appVersion = child.text
        if child.attrib['name'] == "voice_preference_locale":
            print("Voice preference locale found: " + child.text)
            voicePref = child.text

    report = ArtifactHtmlReport('GMapsSettings')
    report.start_artifact_report(report_folder, 'GMapsSettings')
    report.add_script()
    data_headers = ('GMapsSettings',)
    data_list = []
    data_list.append(('Current Account ID', currentAccountId))
    data_list.append(('Google Maps app version', appVersion))
    data_list.append(('Satellite on at startup', satelite))
    data_list.append(('Location sharing', locationSharing))
    data_list.append(('Voice preference locale', voicePref))
    data_list.append(('Voice Bundles', voiceBundles))
    report.write_artifact_data_table(data_headers, data_list, file_found)
    report.end_artifact_report()
    tsvname = f'GMaps Settings'
    tsv(report_folder, data_headers, data_list, tsvname)

__artifacts__ = {
        "GMapsFirstUsed": (
                "GMapsFirstUsed",
                ('*/com.google.android.apps.maps/shared_prefs/com.google.android.gms.measurement.prefs.xml'),
                get_GMapsFirstUsed),
        "GMapsLastUsed": (
                "GMapsLastUsed",
                ('*/com.google.android.apps.maps/shared_prefs/FirebaseHeartBeat*'),
                get_GMapsLastUsed),
        "GMapsSettings": (
                "GMapsSettings",
                ('*/com.google.android.apps.maps/shared_prefs/settings_preference.xml'),
                get_GMapsSettings),
}