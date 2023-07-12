# Get GPS data from the table 'activity_polyline' and activity_details
# The script uses polyline to decode the GPS data and folium to plot the GPS data on a map
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-02-24
# Version: 1.0
# Requirements: Python 3.7 or higher, folium and polyline, datetime
import datetime
import os

import folium
import polyline

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_garmin_polyline(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Garmin Polyline")

    #Generate title for map file
    title = 'Garmin_Polyline_Map_' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)

    # Get the GPS data from the table 'activity_polyline' for the activities in the table 'activity_details'
    cursor = db.cursor()
    cursor.execute('''
        SELECT 
        activity_details.activityId, 
        datetime(lastUpdated/1000,'unixepoch'),
        activityName, 
        startTimeGMT, 
        activityTypeKey, 
        round(distance, 0), 
        round(duration/60, 0), 
        steps, 
        encodedLevels, 
        encodedSamples, 
        round(startLat, 2), 
        round(endLat, 2), 
        round(startLon, 2), 
        round(endLon, 2)
        from activity_details
        left join activity_polyline ap on activity_details.activityId = ap.activityId
        where activity_details.activityId = ap.activityId
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f'Found {usageentries} activity_polyline entries')
        report = ArtifactHtmlReport('Polyline')
        report.start_artifact_report(report_folder, 'Polyline')
        report.add_script()
        data_headers = ('Activity ID', 'Start Time GMT', 'Last Updated', 'Activity Name', 'Activity Type Key', 'Distance', 'Duration', 'Steps', 'Coordinates File', 'Start Latitude', 'End Latitude', 'Start Longitude', 'End Longitude', 'Button')
        data_list = []
        html_map = []
        for row in all_rows:
            activity_id = row[0]
            place_lat = []
            place_lon = []

            #convert polyline to lat/long
            coordinates = polyline.decode(row[9])

            for coordinate in coordinates:
                coordinate = str(coordinate)
                # remove the parenthesis
                coordinate = coordinate.replace("(", "")
                coordinate.replace(")", "")

            m = folium.Map(location=[row[10], row[12]], zoom_start=10, max_zoom=19)

            for coordinate in coordinates:
                #if points are to close, skip
                if len(place_lat) > 0 and abs(place_lat[-1] - coordinate[0]) < 0.0001 and abs(place_lon[-1] - coordinate[1]) < 0.0001:
                    continue
                else:
                    place_lat.append(coordinate[0])
                    place_lon.append(coordinate[1])

            points = []
            for i in range(len(place_lat)):
                points.append([place_lat[i], place_lon[i]])

            # Add points to map
            for index, lat in enumerate(place_lat):
                # Start point
                if index == 0:
                    folium.Marker([lat, place_lon[index]],popup=(('Start Location\nActivity ID \n' + str(row[0])).format(index)),icon=folium.Icon(color='blue', icon='flag', prefix='fa')).add_to(m)
                # last point
                elif index == len(place_lat) - 1:
                    folium.Marker([lat, place_lon[index]],popup=(('End Location\nActivity ID \n' + str(row[0])).format(index)),icon=folium.Icon(color='red', icon='flag', prefix='fa')).add_to(m)
                # middle points


            # Create polyline
            folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(m)
            # Save the map to an HTML file
            title = 'Garmin_Polyline_Map_' + str(activity_id)
            if os.name == 'nt':
                m.save(report_folder + '\\' + title + '.html')
            else:
                m.save(report_folder + '/' + title + '.html')
            html_map.append('<iframe id="' + str(activity_id) + '" src="Garmin-Cache/' + title + '.html" width="100%" height="500" class="map" hidden></iframe>')
            # save coords to a kml file
            kml = """
                                <?xml version="1.0" encoding="UTF-8"?>
                                <kml xmlns="http://www.opengis.net/kml/2.2">
                                <Document>
                                <name>Coordinates</name>
                                <description>Coordinates</description>
                                <Style id="yellowLineGreenPoly">
                                    <LineStyle>
                                        <color>7f00ffff</color>
                                        <width>4</width>
                                    </LineStyle>
                                    <PolyStyle>
                                        <color>7f00ff00</color>
                                    </PolyStyle>
                                </Style>
                                <Placemark>
                                    <name>Absolute Extruded</name>
                                    <description>Transparent green wall with yellow outlines</description>
                                    <styleUrl>#yellowLineGreenPoly</styleUrl>
                                    <LineString>
                                        <extrude>1</extrude>
                                        <tessellate>1</tessellate>
                                        <altitudeMode>clampedToGround</altitudeMode>
                                        <coordinates>
                                        """
            for i in range(len(place_lat)):
                kml += str(place_lon[i]) + ',' + str(place_lat[i]) + ',0 '
            kml = kml[:-1]
            kml += """
                                        </coordinates>
                                    </LineString>
                                </Placemark>
                                </Document>
                                </kml>
                                """
            # remove the first space
            kml = kml[1:]
            # remove last line
            kml = kml[:-1]
            # remove extra indentation
            kml = kml.replace("    ", "")
            if os.name == 'nt':
                with open(report_folder + '\\' + str(row[0]) + '.kml', 'w') as f:
                    f.write(kml)
                    f.close()
            else:
                with open(report_folder + '/' + str(row[0]) + '.kml', 'w') as f:
                    f.write(kml)
                    f.close()
            # Store the map in the report
            data_list.append((row[0], row[3], row[1], row[2], row[4], row[5], row[6], row[7], '<a href=Garmin-Cache/'+str(row[0])+'.kml class="badge badge-light" target="_blank">'+str(row[0])+'.kml</a>', row[10], row[11], row[12], row[13], '<button type="button" class="btn btn-light btn-sm" onclick="openMap(\''+str(activity_id)+'\')">Show Map</button>'))

        # Added feature to allow the user to sort the data by the selected collumns and with the ID of the table
        table_id = 'Garmin_Polyline'
        report.filter_by_date(table_id, 1)

        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False, table_id='GarminCache')

        # Add the map to the report
        report.add_section_heading('Garmin Polyline Map')
        for htmlMap in html_map:
            report.add_map(htmlMap)
        report.end_artifact_report()

        tsvname = f'Garmin - Polyline'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Garmin - Polyline'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Garmin Polyline data available')

    db.close()


__artifacts__ = {
    "GarminPolyline": (
        "Garmin-Cache",
        ('*/com.garmin.android.apps.connectmobile/databases/cache-database*'),
        get_garmin_polyline)
}
