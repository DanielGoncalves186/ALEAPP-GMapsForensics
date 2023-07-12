import sqlite3
import io
import json
import os
import shutil
import magic

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, is_platform_windows, open_sqlite_db_readonly, media_to_html

def get_googlePhotos(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_name = str(file_found)
        
        if file_name.lower().endswith(('-shm','-wal')):
            continue
        
        if file_name.lower().endswith('.db') and os.path.basename(file_name).startswith('gphotos'):
            
            report_title = ''
            if file_name.endswith('gphotos0.db'):
                report_title = ' (gphotos0) '
            elif file_name.endswith('gphotos-1.db'):
                report_title = ' (gphotos-1) '
            
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            
            columns = [i[1] for i in cursor.execute('PRAGMA table_info(local_media)')]
            
            if 'purge_timestamp' not in columns:
                cursor.execute('''
                select
                datetime(utc_timestamp/1000, 'unixepoch'),
                filename,
                filepath,
                datetime(capture_timestamp/1000, 'unixepoch'),
                timezone_offset/3600000,
                width,
                height,
                size_bytes,
                case duration
                    when 0 then ''
                    else strftime('%H:%M:%S', duration/1000, 'unixepoch')
                end,
                latitude,
                longitude,
                folder_name,
                media_store_id,
                case trash_timestamp
                    when NULL then ''
                    else datetime(trash_timestamp/1000, 'unixepoch')
                end
                from local_media
                ''')
            
                all_rows = cursor.fetchall()
                usageentries = len(all_rows)
                if usageentries > 0:
                    report = ArtifactHtmlReport('Google Photos' + report_title + '- Local Media')
                    report.start_artifact_report(report_folder, 'Google Photos' + report_title + '- Local Media')
                    report.add_script()
                    data_headers = ('Timestamp','File Name','File Path','Captured Timestamp (Local)','Timezone Offset','Width','Height','Size','Duration','Latitude','Longitude','Folder Name','Media Store ID','Trashed Timestamp')
                    data_list = []
                    for row in all_rows:
                        data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13]))

                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    
                    tsvname = f'Google Photos' + report_title + '- Local Media'
                    tsv(report_folder, data_headers, data_list, tsvname, file_found)
                    
                    tlactivity = f'Google Photos' + report_title + '- Local Media'
                    timeline(report_folder, tlactivity, data_list, data_headers)
                    
                    kmlactivity = 'Google Photos' + report_title + '- Local Media'
                    kmlgen(report_folder, kmlactivity, data_list, data_headers)
                    
                else:
                    logfunc('No Google Photos' + report_title + '- Local Media data available')
            
            else:
                cursor.execute('''
                select
                datetime(utc_timestamp/1000, 'unixepoch'),
                filename,
                filepath,
                datetime(capture_timestamp/1000, 'unixepoch'),
                timezone_offset/3600000,
                width,
                height,
                size_bytes,
                case duration
                    when 0 then ''
                    else strftime('%H:%M:%S', duration/1000, 'unixepoch')
                end,
                latitude,
                longitude,
                folder_name,
                media_store_id,
                case trash_timestamp
                    when NULL then ''
                    else datetime(trash_timestamp/1000, 'unixepoch')
                end,
                case purge_timestamp
                    when NULL then ''
                    else datetime(purge_timestamp/1000, 'unixepoch')
                end
                from local_media
                ''')

                all_rows = cursor.fetchall()
                usageentries = len(all_rows)
                if usageentries > 0:
                    report = ArtifactHtmlReport('Google Photos' + report_title + '- Local Media')
                    report.start_artifact_report(report_folder, 'Google Photos' + report_title + '- Local Media')
                    report.add_script()
                    data_headers = ('Timestamp','File Name','File Path','Captured Timestamp (Local)','Timezone Offset','Width','Height','Size','Duration','Latitude','Longitude','Folder Name','Media Store ID','Trashed Timestamp','Purge Timestamp') 
                    data_list = []
                    for row in all_rows:
                        data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14]))

                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    
                    tsvname = f'Google Photos' + report_title + '- Local Media'
                    tsv(report_folder, data_headers, data_list, tsvname, file_found)
                    
                    tlactivity = f'Google Photos' + report_title + '- Local Media'
                    timeline(report_folder, tlactivity, data_list, data_headers)
                    
                    kmlactivity = 'Google Photos' + report_title + '- Local Media'
                    kmlgen(report_folder, kmlactivity, data_list, data_headers)
                    
                else:
                    logfunc('No Google Photos' + report_title + '- Local Media data available')
               
            columns2 = [i[1] for i in cursor.execute('PRAGMA table_info(remote_media)')]
            
            if 'inferred_latitude' not in columns2:
                cursor.execute('''
                select
                datetime(utc_timestamp/1000, 'unixepoch'),
                filename,
                replace(remote_url,'=s0-d',''),
                datetime(capture_timestamp/1000, 'unixepoch'),
                timezone_offset/3600000,
                strftime('%H:%M:%S', duration/1000, 'unixepoch'),
                latitude,
                longitude,
                upload_status
                from remote_media
                ''')

                all_rows = cursor.fetchall()
                usageentries = len(all_rows)
                if usageentries > 0:
                    report = ArtifactHtmlReport('Google Photos' + report_title + '- Remote Media')
                    report.start_artifact_report(report_folder, 'Google Photos' + report_title + '- Remote Media')
                    report.add_script()
                    data_headers = ('Timestamp','File Name','Remote URL','Captured Timestamp (Local)','Timezone Offset','Duration','Latitude','Longitude','Upload Status %') 
                    data_list = []
                    for row in all_rows:
                        data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))

                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    
                    tsvname = f'Google Photos' + report_title + '- Remote Media'
                    tsv(report_folder, data_headers, data_list, tsvname, file_found)
                    
                    tlactivity = f'Google Photos' + report_title + '- Remote Media'
                    timeline(report_folder, tlactivity, data_list, data_headers)
                    
                    kmlactivity = 'Google Photos' + report_title + '- Remote Media'
                    kmlgen(report_folder, kmlactivity, data_list, data_headers)
                    
                else:
                    logfunc('No Google Photos' + report_title + '- Remote Media data available')
                 
            else:
                cursor.execute('''
                select
                datetime(utc_timestamp/1000, 'unixepoch'),
                filename,
                replace(remote_url,'=s0-d',''),
                datetime(capture_timestamp/1000, 'unixepoch'),
                timezone_offset/3600000,
                strftime('%H:%M:%S', duration/1000, 'unixepoch'),
                latitude,
                longitude,
                inferred_latitude,
                inferred_longitude,
                upload_status
                from remote_media
                ''')

                all_rows = cursor.fetchall()
                usageentries = len(all_rows)
                if usageentries > 0:
                    report = ArtifactHtmlReport('Google Photos' + report_title + '- Remote Media')
                    report.start_artifact_report(report_folder, 'Google Photos' + report_title + '- Remote Media')
                    report.add_script()
                    data_headers = ('Timestamp','File Name','Remote URL','Captured Timestamp (Local)','Timezone Offset','Duration','Latitude','Longitude','Inferred Latitude','Inferred Longitude','Upload Status %') 
                    data_list = []
                    for row in all_rows:
                        data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]))

                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    
                    tsvname = f'Google Photos' + report_title + '- Remote Media'
                    tsv(report_folder, data_headers, data_list, tsvname, file_found)
                    
                    tlactivity = f'Google Photos' + report_title + '- Remote Media'
                    timeline(report_folder, tlactivity, data_list, data_headers)
                    
                    kmlactivity = 'Google Photos' + report_title + '- Remote Media'
                    kmlgen(report_folder, kmlactivity, data_list, data_headers)
                    
                else:
                    logfunc('No Google Photos' + report_title + '- Remote Media data available')
            
            cursor.execute('''
            select
            datetime(utc_timestamp/1000, 'unixepoch') as "Timestamp (UTC)",
            filename,
            replace(remote_url,'=s0-d',''),
            size_bytes,
            datetime(capture_timestamp/1000, 'unixepoch') as "Capture Local Timestamp",
            timezone_offset/3600000,
            upload_status
            from shared_media
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Google Photos' + report_title + '- Shared Media')
                report.start_artifact_report(report_folder, 'Google Photos' + report_title + '- Shared Media')
                report.add_script()
                data_headers = ('Timestamp','File Name','Remote URL','Size','Captured Timestamp (Local)','Timezone Offset','Upload Status %')
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Google Photos' + report_title + '- Shared Media'
                tsv(report_folder, data_headers, data_list, tsvname, file_found)
                
                tlactivity = f'Google Photos' + report_title + '- Shared Media'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Google Photos' + report_title + '- Shared Media data available')
            
            cursor.execute('''
            select 
            DISTINCT(local_media.bucket_id),
            local_media.folder_name,
            rtrim(local_media.filepath, replace(local_media.filepath, '/', ''))
            from local_media, backup_folders
            where local_media.bucket_id = backup_folders.bucket_id
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Google Photos' + report_title + '- Backed Up Folders')
                report.start_artifact_report(report_folder, 'Google Photos' + report_title + '- Backed Up Folders')
                report.add_script()
                data_headers = ('Bucket ID','Backed Up Folder Name','Backed Up Folder Path',)
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Google Photos' + report_title + '- Backed Up Folders'
                tsv(report_folder, data_headers, data_list, tsvname, file_found)
                
                tlactivity = f'Google Photos' + report_title + '- Backed Up Folders'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Google Photos' + report_title + '- Backed Up Folders data available')
            
            db.close()

        if file_name.lower().endswith('disk_cache'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            
            cursor.execute('''
            select
            datetime(last_modified_time/1000, 'unixepoch'),
            key,
            size,
            case pending_delete
                when 0 then ''
                when 1 then 'Yes'
            end
            from journal
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            data_list = []
            
            if usageentries > 0:
                for row in all_rows:
                    fileNameKey = row[1]
                    
                    for match in files_found:
                        if fileNameKey in match:
                            mimetype = magic.from_file(match, mime = True)
                            ext = (mimetype.split('/')[1])
                            newname = os.path.join(report_folder, f'{fileNameKey}.{ext}')
                            shutil.copy2(match, newname)
                    
                    thumb = media_to_html(fileNameKey, files_found, report_folder)
                        
                    data_list.append((row[0],row[1],thumb,row[2],row[3]))
            
                report = ArtifactHtmlReport('Google Photos' + report_title + '- Cache')
                report.start_artifact_report(report_folder, 'Google Photos' + report_title + '- Cache')
                report.add_script()
                data_headers = ('Timestamp','Key','Image','Size','Pending Deletion')
                
                report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Image'])
                report.end_artifact_report()
                
                tsvname = f'Google Photos' + report_title + '- Cache'
                tsv(report_folder, data_headers, data_list, tsvname, file_found)
                
                tlactivity = f'Google Photos' + report_title + '- Cache'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Google Photos' + report_title + '- Cache data available')
            
            db.close()
                   
        if file_name.lower().endswith('local_trash.db'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            
            cursor.execute('''
            select
            datetime(deleted_time/1000, 'unixepoch'),
            local_path,
            content_uri,
            trash_file_name,
            case is_video
                when 0 then ''
                when 1 then 'Yes'
            end,
            media_store_id
            from local
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            data_list = []
            
            if usageentries > 0:
                for row in all_rows:
                
                    fileNameKey = row[3]
                    thumb = ''
                    
                    for match in files_found:
                        if fileNameKey in match:
                            mimetype = magic.from_file(match, mime = True)
                            ext = (mimetype.split('/')[1])
                            newname = os.path.join(report_folder, f'{fileNameKey}.{ext}')
                            shutil.copy2(match, newname)
                            
                    thumb = media_to_html(fileNameKey, files_found, report_folder)
                        
                    data_list.append((row[0],row[1],row[2],row[3],thumb,row[4],row[5]))
            
                report = ArtifactHtmlReport('Google Photos' + report_title + '- Local Trash')
                report.start_artifact_report(report_folder, 'Google Photos' + report_title + '- Local Trash')
                report.add_script()
                data_headers = ('Timestamp','Original Path','Content URI','File Name','Image','Is Video','Media Store ID')
                
                report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Image'])
                report.end_artifact_report()
                
                tsvname = f'Google Photos' + report_title + '- Local Trash'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Google Photos' + report_title + '- Local Trash'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Google Photos' + report_title + '- Local Trash data available')
            
            db.close()
            
        else:
            continue

__artifacts__ = {
        "GooglePhotos": (
                "Google Photos",
                ('*/com.google.android.apps.photos/databases/gphotos*.db*','*/com.google.android.apps.photos/databases/disk_cache*','*/com.google.android.apps.photos/cache/glide_cache/*','*/com.google.android.apps.photos/databases/local_trash.db*','*/com.google.android.apps.photos/files/trash_files/*'),
                get_googlePhotos)
}