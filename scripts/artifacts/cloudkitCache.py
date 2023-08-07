# Cloudkit Cache Snapshots
# Author:  John Hyla
# Version: 1.0.0
#
#   Description:
#   Parses cloudkit cache snapshots and their manifests/files
#
import plistlib

import nska_deserialize as nd

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, kmlgen, timeline, is_platform_windows, generate_thumbnail, \
    open_sqlite_db_readonly
from scripts.builds_ids import OS_build


def get_cloudkitCache(files_found, report_folder, seeker, wrap_text):
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.db'):
            break
      

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()

    cursor.execute("""
        SELECT 
            Snapshots.snapshotID,
            Snapshots.committed,
            DateTime(Snapshots.created, 'UNIXEPOCH') as snapshotCreated,
            Snapshots.snapshot as snapshotData,
            Manifests.manifestID,
            Manifests.domain,
            Files.fileID,
            Files.domain,
            DateTime(Files.modified, 'UNIXEPOCH') as fileModified,
            Files.relativePath,
            Files.deleted,
            Files.fileType,
            Files.size,
            Files.signature,
            Snapshots.snapshot
        FROM Snapshots
        LEFT JOIN Manifests ON Manifests.snapshotID = Snapshots.snapshotID
        LEFT JOIN Files ON Manifests.manifestID = Files.manifestID
    """)
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    logfunc(str(usageentries))
    data_list = []
    counter = 0
    snapshot_grouped_data = {}
    snapshot_summary_plist = {}
    if usageentries > 0:
        data_headers = ('File Modified', 'ManifestID', 'Domain', 'FileID', 'File Path', 'File Deleted', 'File Type', 'File Size', 'File Signature')
        summary_data_headers = ('Key', 'Value')
        for row in all_rows:
            snapshot_id = row[0]
            if snapshot_id not in snapshot_grouped_data:
                snapshot_grouped_data[snapshot_id] = []
            if snapshot_id not in snapshot_summary_plist:
                snapshot_summary_plist[snapshot_id] = row[14]
            snapshot_grouped_data[snapshot_id].append(row[:14])


        logfunc('Snapshot grouped data length: ' + str(len(snapshot_grouped_data)))

        for (key, snapshot_data) in snapshot_grouped_data.items():
            report = ArtifactHtmlReport(f'Snapshot')
            description = ''
            report.start_artifact_report(report_folder, f'SnapshotID - {key}', description)
            report.add_section_heading("Snapshot Summary")
            # Get summary data from first row
            snapshot_summary_data = snapshot_data[0]
            summary_data_list = []
            summary_data_list.append(('SnapshotID', key))
            summary_data_list.append(('Snapshot Committed', snapshot_summary_data[1]))
            summary_data_list.append(('Snapshot Created', snapshot_summary_data[2]))

            # read Snapshot NSKA
            deserialized_plist = nd.deserialize_plist_from_string(snapshot_summary_plist[key])
            summary_data_list.append(('DeviceName', deserialized_plist['DeviceName']))
            summary_data_list.append(('BackupReason', deserialized_plist['BackupReason']))

            # read backup properties plist
            backup_properties = deserialized_plist['BackupProperties']
            backup_properties_plist = plistlib.loads(backup_properties)
            summary_data_list.append(('Active Apple ID', backup_properties_plist['ActiveAppleID']))
            summary_data_list.append(('Backup Date', backup_properties_plist['Date'].strftime("%Y-%m-%d %H:%M:%S")))

            report.write_artifact_data_table(summary_data_headers, summary_data_list, file_found)

            report.add_section_heading("Snapshot Records")
            data_list = []
            for row in snapshot_data:
                data_list.append(( row[8], row[4], row[5], row[6],row[9], row[10], row[11], row[12], row[13]))

            report.write_artifact_data_table(data_headers, data_list, file_found)

            report.add_script()
            report.end_artifact_report()



        # tsvname = 'Photos-sqlite Migrations'
        # tsv(report_folder, data_headers, data_list, tsvname)
        #
        # tlactivity = 'Photos-sqlite Migrations'
        # timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No data available for Cloudkit Cache')

    db.close()
    return



__artifacts__ = {
    "cloudkitCache": (
        "CloudKit Cache",
        ('**/cloudkit_cache.db*'),
        get_cloudkitCache)
}