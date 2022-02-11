
import time
import datetime
import blackboxprotobuf
import json
import struct
#from bplist import *
import pprint
import nska_deserialize as nd
import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, kmlgen, tsv, is_platform_windows, open_sqlite_db_readonly


def get_duetExpertCenter(files_found, report_folder, seeker):
    data_list = []

    
    notification_typedef = json.loads(notificationTypeDef())

    

    for file_found in files_found:
        file_found = str(file_found)
        if "tombstone" in file_found:
            continue

        if os.path.isdir(file_found):
            print("directory")
            continue # Skip all other files
        else:
            print("matched")
        logfunc(file_found)
        with open(file_found, "rb") as file:
    
            file.seek(8)
            #print(struct.unpack('d',file.read(8)))
            headertime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(struct.unpack('d',file.read(8))[0] + 978307200))
            file.seek(56)
            while length := int.from_bytes(file.read(4), byteorder='little'):
                nextOffset = getNext8(file.tell()+length+28)
                datastart = file.tell()+32
                
                record_marker = int.from_bytes(file.read(4), byteorder='little')
                file.seek(24, 1)
                
                #timestamp1 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(struct.unpack('d',file.read(8))[0] + 978307200))
                #timestamp2 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(struct.unpack('d',file.read(8))[0] + 978307200))
                #unknown = format(bin(int(file.read(4).hex(), base=16))[2:], '032')
                #unknown = int(file.read(4).hex(), base=16)
                #identifier2 = int.from_bytes(file.read(4), byteorder='little')
                data = file.read(length)
                
                if record_marker == 1:

                    message, _ = blackboxprotobuf.decode_message(data, notification_typedef)
                    notification_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(message['1']['1'] + 978307200))
                    notification_date2 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(message['3'] + 978307200))

                    try:
                        title = message['1']['3']
                    except KeyError as e:
                        title = ''
                    try:
                        text = message['1']['5']
                    except KeyError as e:
                        text = ''
                    app = message['1']['8']
                    indicator = message['2']
                    indicator2 = message['5']
                    data_list.append((notification_date, notification_date2, title, text, app))
      
                file.seek(nextOffset)

    
    report = ArtifactHtmlReport('Duet Expert Center - Notifications')
    report.start_artifact_report(report_folder, 'Notifications')
    report.add_script()
    data_headers = ('Unknown Time 1', 'Unknown Time 2', 'Title', 'Text', 'App Identifier')
    report.write_artifact_data_table(data_headers, data_list, f'{os.path.dirname(file_found)}{os.sep}*')
    
    
    report.end_artifact_report()


def getNext8(num):
    while (remain := num % 8) != 0:
        num = num + 1
    return num

def notificationTypeDef():
    return """{"1": {"type": "message", "message_typedef": {"1": {"type": "double", "name": ""}, "2": {"type": "str", "name": ""}, "3": {"type": "str", "name": ""}, "5": {"type": "str", "name": ""}, "6": {"type": "int", "name": ""}, "8": {"type": "str", "name": ""}, "9": {"type": "message", "message_typedef": {}, "name": ""}, "10": {"type": "str", "name": ""}, "12": {"type": "str", "name": ""}, "14": {"type": "int", "name": ""}, "15": {"type": "int", "name": ""}, "16": {"type": "int", "name": ""}, "17": {"type": "int", "name": ""}, "19": {"type": "fixed64", "name": ""}}, "name": ""}, "2": {"type": "int", "name": ""}, "3": {"type": "double", "name": ""}, "5": {"type": "int", "name": ""}}"""

