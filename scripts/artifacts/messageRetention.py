from datetime import datetime
import os
import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 

def get_messageRetention(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    
    for file_found in files_found:
        with open(file_found, "rb") as fp:
            pl = plistlib.load(fp)
            indicator = 0
            for key, val in pl.items():
                
                if key == 'KeepMessageForDays':
                    data_list.append(('Keep Message for Days',val,file_found))
                    logdevinfo(f"<b>Keep Message for Days: </b>{val}")
                    indicator = 1
                
            if indicator == 0:
                data_list.append(('Keep Message for Days','Forever',file_found))
                logdevinfo(f"<b>Keep Message for Days: </b>Forever")
            
    if len(data_list) > 0:
        report = ArtifactHtmlReport('iOS Message Retention')
        report.start_artifact_report(report_folder, 'iOS Message Retention')
        report.add_script()
        data_headers = ('Key','Values','Path')
        report.write_artifact_data_table(data_headers, data_list, 'File path in the report below')
        report.end_artifact_report()
        
        tsvname = 'iOS Message Retention'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No iOS Message Retention data')
            
__artifacts__ = {
    "messageRetention": (
        "Identifiers",
        ('*/mobile/Library/Preferences/com.apple.MobileSMS.plist','*//mobile/Library/Preferences/com.apple.mobileSMS.plist'),
        get_messageRetention)
}
