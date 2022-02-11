
import time
import datetime
import blackboxprotobuf
import json
import struct
#from bplist import *
import pprint
import nska_deserialize as nd
import re
import os
import sys

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, kmlgen, tsv, is_platform_windows, open_sqlite_db_readonly


def get_intents(files_found, report_folder, seeker):
    message_data_list = []

    
    message_typedef = json.loads(messageTypeDef())
    sent_message_typedef = json.loads(sentMessageTypeDef())
    typedef = json.loads(typeDef())
    call_typedef = json.loads(callTypeDef())



    for file_found in files_found:
        #print(file_found)
        logfunc(file_found)
        if "tombstone" in file_found:
            continue
        if os.path.isdir(file_found):
            continue # Skip directory

        file_found = str(file_found)
        logfunc(file_found)

        with open(file_found, "rb") as file:
            file.seek(8)
            headertime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(struct.unpack('d',file.read(8))[0] + 978307200))
            file.seek(56)
            while length := int.from_bytes(file.read(4), byteorder='little'):
                nextOffset = getNext8(file.tell()+length+28)
                datastart = file.tell()+32
                record_marker = int.from_bytes(file.read(4), byteorder='little')

                #timestamp1 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(struct.unpack('d',file.read(8))[0] + 978307200))
                #timestamp2 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(struct.unpack('d',file.read(8))[0] + 978307200))
                #unknown = format(bin(int(file.read(4).hex(), base=16))[2:], '032')
                #unknown = int(file.read(4).hex(), base=16)
                #identifier2 = int.from_bytes(file.read(4), byteorder='little')
                file.seek(24,1)
                data = file.read(length)


                if record_marker == 1:
                    message, _ = blackboxprotobuf.decode_message(data, typedef)
                
                    dpl = nd.deserialize_plist_from_string(message['8'])

                    if (message['2'] == "com.apple.MobileSMS"):
                        if message['6'] != 3:
                            if dpl['direction'] == 1:
                                direction = "Sent"
                                intent, td = blackboxprotobuf.decode_message(dpl['intent']['backingStore']['bytes'], sent_message_typedef)
                                #print("SENT")
                                #print(intent)
                                #print(td)
                                #sys.exit()
                            elif dpl['direction'] == 2:
                                direction = "Received"
                                intent, td = blackboxprotobuf.decode_message(dpl['intent']['backingStore']['bytes'], message_typedef)

                            else:
                                direction = dpl['direction']    
                                
                            
                            #print(intent)
                            #print(td)
                            intent_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(message['1'] + 978307200))
                            try:
                                other_party_name = intent['10']['1']['4']
                            except:
                                #print(intent)
                                other_party_name = 'UNKNOWN'
                            try:
                                other_party_id = intent['10']['1']['7']['1']
                            except:
                                #print()
                                #print(intent)
                                other_party_id = 'UNKNOWN'
                                #sys.exit()
                            try:
                                content = intent['5']['1']['2']
                            except Exception as e:
                                print(file.tell())
                                print(e)
                                print(intent)
                                print(file_found)
                                print(dpl['intent']['backingStore']['bytes'])
                                sys.exit()
                            thread_id = intent['8']

                            print("APPENDED")
                            message_data_list.append((intent_time, content, direction, thread_id, other_party_id, other_party_name))

                            #print(datastart, identifier1, timestamp1, timestamp2, unknown, message['2'], intent_time, direction, other_party_name, other_party_id, content, thread_id)
                    elif message['2'] == "com.apple.InCallService":
                        #print(dpl)
                        #intent, _ = blackboxprotobuf.decode_message(dpl['intent']['backingStore']['bytes'], call_typedef)
                        #print(intent)
                        #duration = dpl['dateInterval']['NS.duration']
                        #startDate = dpl['dateInterval']['NS.startDate']
                        #endDate = dpl['dateInterval']['NS.endDate']
                        #otherParty = intent['5']['1']['4']
                        #otherPartyId = intent['5']['1']['7']['1']
                        pass
                    else:
                        pass
                        #print(message['2'])




                file.seek(nextOffset)
        print(len(message_data_list))
    description = "The Intents and IntentsUI frameworks drive interactions that start with \"Hey Siri\", Shortcuts actions, and widget configuration. The system also incorporates intents and user activities your app donates into contextual suggestions in Maps, Calendar, Watch complications, widgets, and search results. Use the standard intents that the system provides to empower actions users already ask Siri to do, such as playing music or sending a text message."
    report = ArtifactHtmlReport('Intents - Messages')
    report.start_artifact_report(report_folder, 'Messages', description)
    report.add_script()
    message_data_headers = ('Received Time', 'Message', 'Direction', 'Thread ID', 'Other Party', 'Other Party Name')
    report.write_artifact_data_table(message_data_headers, message_data_list, '\\'.join(file_found.split('\\')[0:-1]))
        
    
    
    report.end_artifact_report()


def getNext8(num):
    while (remain := num % 8) != 0:
        num = num + 1
    return num

def messageTypeDef():
    return """{"5": {"type": "message", "message_typedef": {"1": {"type": "message", "message_typedef": {"2": {"type": "str", "name": ""}}, "name": ""}}, "name": ""}, "8": {"type": "str", "name": ""}, "1": {"type": "message", "message_typedef": {"16": {"type": "str", "name": ""}, "11": {"type": "int", "name": ""}, "2": {"type": "str", "name": ""}}, "name": ""}, "2": {"type": "message", "message_typedef": {"1": {"type": "message", "message_typedef": {"7": {"type": "message", "message_typedef": {"4": {"type": "int", "name": ""}, "5": {"type": "int", "name": ""}, "2": {"type": "int", "name": ""}, "1": {"type": "str", "name": ""}}, "name": ""}, "2": {"type": "str", "name": ""}, "4": {"type": "str", "name": ""}, "10": {"type": "int", "name": ""}, "3": {"type": "message", "message_typedef": {}, "name": ""}, "15": {"type": "message", "message_typedef": {}, "name": ""}, "14": {"type": "message", "message_typedef": {}, "name": ""}, "16": {"type": "message", "message_typedef": {}, "name": ""}, "13": {"type": "message", "message_typedef": {}, "name": ""}, "18": {"type": "message", "message_typedef": {}, "name": ""}, "20": {"type": "message", "message_typedef": {}, "name": ""}, "19": {"type": "message", "message_typedef": {}, "name": ""}, "11": {"type": "int", "name": ""}, "1": {"type": "message", "message_typedef": {"2": {"type": "str", "name": ""}}, "name": ""}}, "name": ""}}, "name": ""}, "10": {"type": "message", "message_typedef": {"1": {"type": "message", "message_typedef": {"7": {"type": "message", "message_typedef": {"4": {"type": "int", "name": ""}, "5": {"type": "int", "name": ""}, "2": {"type": "int", "name": ""}, "1": {"type": "str", "name": ""}}, "name": ""}, "2": {"type": "str", "name": ""}, "4": {"type": "str", "name": ""}, "10": {"type": "int", "name": ""}, "3": {"type": "str", "name": ""}, "15": {"type": "message", "message_typedef": {}, "name": ""}, "14": {"type": "message", "message_typedef": {}, "name": ""}, "16": {"type": "message", "message_typedef": {}, "name": ""}, "13": {"type": "message", "message_typedef": {}, "name": ""}, "18": {"type": "message", "message_typedef": {}, "name": ""}, "20": {"type": "message", "message_typedef": {}, "name": ""}, "19": {"type": "message", "message_typedef": {}, "name": ""}, "11": {"type": "int", "name": ""}, "1": {"type": "message", "message_typedef": {"2": {"type": "str", "name": ""}}, "name": ""}}, "name": ""}}, "name": ""}, "9": {"type": "str", "name": ""}}"""

def typeDef():
     return '''{"1": {"type": "double", "name": ""}, "2": {"type": "str", "name": ""}, "4": {"type": "str", "name": ""}, "5": {"type": "str", "name": ""}, "6": {"type": "int", "name": ""}, "7": {"type": "int", "name": ""}, "8": {"type": "bytes", "name": ""}}'''

def callTypeDef():
    return '''{"8": {"type": "int", "name": ""}, "5": {"type": "message", "message_typedef": {"1": {"type": "message", "message_typedef": {"7": {"type": "message", "message_typedef": {"4": {"type": "int", "name": ""}, "5": {"type": "int", "name": ""}, "2": {"type": "int", "name": ""}, "1": {"type": "str", "name": ""}}, "name": ""}, "4": {"type": "str", "name": ""}, "10": {"type": "int", "name": ""}, "11": {"type": "int", "name": ""}}, "name": ""}}, "name": ""}, "3": {"type": "int", "name": ""}, "1": {"type": "message", "message_typedef": {"16": {"type": "str", "name": ""}, "11": {"type": "int", "name": ""}, "2": {"type": "str", "name": ""}, "7": {"type": "str", "name": ""}}, "name": ""}, "4": {"type": "int", "name": ""}, "7": {"type": "int", "name": ""}}'''

def messageTypeDef3():
    return '''{"5": {"type": "message", "message_typedef": {"1": {"type": "message", "message_typedef": {"2": {"type": "bytes", "name": ""}}, "name": ""}}, "name": ""}, "8": {"type": "bytes", "name": ""}, "1": {"type": "message", "message_typedef": {"16": {"type": "bytes", "name": ""}, "11": {"type": "int", "name": ""}, "2": {"type": "bytes", "name": ""}}, "name": ""}, "15": {"type": "bytes", "name": ""}, "2": {"type": "message", "message_typedef": {"1": {"type": "message", "message_typedef": {"7": {"type": "message", "message_typedef": {"4": {"type": "int", "name": ""}, "5": {"type": "int", "name": ""}, "2": {"type": "int", "name": ""}, "1": {"type": "bytes", "name": ""}}, "name": ""}, "4": {"type": "bytes", "name": ""}, "23": {"type": "int", "name": ""}, "10": {"type": "int", "name": ""}, "11": {"type": "int", "name": ""}}, "name": ""}}, "name": ""}, "10": {"type": "bytes", "name": ""}, "9": {"type": "bytes", "name": ""}}'''

def messageTypeDef2():
    return'''{"5": {"type": "message", "message_typedef": {"1": {"type": "message", "message_typedef": {"2": {"type": "bytes", "name": ""}}, "name": ""}}, "name": ""}, "8": {"type": "bytes", "name": ""}, "1": {"type": "message", "message_typedef": {"16": {"type": "bytes", "name": ""}, "11": {"type": "int", "name": ""}, "2": {"type": "bytes", "name": ""}}, "name": ""}, "2": {"type": "message", "message_typedef": {"1": {"type": "message", "message_typedef": {"7": {"type": "message", "message_typedef": {"4": {"type": "int", "name": ""}, "3": {"type": "bytes", "name": ""}, "5": {"type": "int", "name": ""}, "2": {"type": "int", "name": ""}, "1": {"type": "bytes", "name": ""}}, "name": ""}, "2": {"type": "bytes", "name": ""}, "4": {"type": "bytes", "name": ""}, "23": {"type": "int", "name": ""}, "10": {"type": "int", "name": ""}, "3": {"type": "message", "message_typedef": {}, "name": ""}, "15": {"type": "message", "message_typedef": {}, "name": ""}, "14": {"type": "message", "message_typedef": {}, "name": ""}, "16": {"type": "message", "message_typedef": {}, "name": ""}, "13": {"type": "message", "message_typedef": {}, "name": ""}, "18": {"type": "message", "message_typedef": {}, "name": ""}, "20": {"type": "message", "message_typedef": {}, "name": ""}, "19": {"type": "message", "message_typedef": {}, "name": ""}, "11": {"type": "int", "name": ""}, "1": {"type": "message", "message_typedef": {"2": {"type": "bytes", "name": ""}}, "name": ""}}, "name": ""}}, "name": ""}, "10": {"type": "message", "message_typedef": {"1": {"type": "message", "message_typedef": {"7": {"type": "message", "message_typedef": {"4": {"type": "int", "name": ""}, "5": {"type": "int", "name": ""}, "2": {"type": "int", "name": ""}, "1": {"type": "bytes", "name": ""}}, "name": ""}, "2": {"type": "bytes", "name": ""}, "4": {"type": "bytes", "name": ""}, "23": {"type": "int", "name": ""}, "10": {"type": "int", "name": ""}, "3": {"type": "message", "message_typedef": {}, "name": ""}, "15": {"type": "message", "message_typedef": {}, "name": ""}, "14": {"type": "message", "message_typedef": {}, "name": ""}, "16": {"type": "message", "message_typedef": {}, "name": ""}, "13": {"type": "bytes", "name": ""}, "18": {"type": "message", "message_typedef": {}, "name": ""}, "20": {"type": "message", "message_typedef": {}, "name": ""}, "19": {"type": "message", "message_typedef": {}, "name": ""}, "11": {"type": "int", "name": ""}, "1": {"type": "message", "message_typedef": {"2": {"type": "bytes", "name": ""}}, "name": ""}}, "name": ""}}, "name": ""}, "9": {"type": "bytes", "name": ""}}'''

def sentMessageTypeDef():
    return '''{"5": {"type": "message", "message_typedef": {"1": {"type": "message", "message_typedef": {"2": {"type": "str", "name": ""}}, "name": ""}}, "name": ""}, "8": {"type": "str", "name": ""}, "1": {"type": "message", "message_typedef": {"16": {"type": "bytes", "name": ""}, "11": {"type": "int", "name": ""}, "2": {"type": "bytes", "name": ""}}, "name": ""}, "2": {"type": "message", "message_typedef": {"1": {"type": "message", "message_typedef": {"7": {"type": "message", "message_typedef": {"4": {"type": "int", "name": ""}, "3": {"type": "bytes", "name": ""}, "5": {"type": "int", "name": ""}, "2": {"type": "int", "name": ""}, "1": {"type": "bytes", "name": ""}}, "name": ""}, "2": {"type": "bytes", "name": ""}, "4": {"type": "bytes", "name": ""}, "23": {"type": "int", "name": ""}, "10": {"type": "int", "name": ""}, "3": {"type": "message", "message_typedef": {}, "name": ""}, "15": {"type": "message", "message_typedef": {}, "name": ""}, "14": {"type": "message", "message_typedef": {}, "name": ""}, "16": {"type": "message", "message_typedef": {}, "name": ""}, "13": {"type": "message", "message_typedef": {}, "name": ""}, "18": {"type": "message", "message_typedef": {}, "name": ""}, "20": {"type": "message", "message_typedef": {}, "name": ""}, "19": {"type": "message", "message_typedef": {}, "name": ""}, "11": {"type": "int", "name": ""}, "1": {"type": "message", "message_typedef": {"2": {"type": "bytes", "name": ""}}, "name": ""}}, "name": ""}}, "name": ""}, "10": {"type": "message", "message_typedef": {"1": {"type": "message", "message_typedef": {"7": {"type": "message", "message_typedef": {"4": {"type": "int", "name": ""}, "5": {"type": "int", "name": ""}, "2": {"type": "int", "name": ""}, "1": {"type": "bytes", "name": ""}}, "name": ""}, "2": {"type": "bytes", "name": ""}, "4": {"type": "bytes", "name": ""}, "23": {"type": "int", "name": ""}, "10": {"type": "int", "name": ""}, "3": {"type": "message", "message_typedef": {}, "name": ""}, "15": {"type": "message", "message_typedef": {}, "name": ""}, "14": {"type": "message", "message_typedef": {}, "name": ""}, "16": {"type": "message", "message_typedef": {}, "name": ""}, "13": {"type": "bytes", "name": ""}, "18": {"type": "message", "message_typedef": {}, "name": ""}, "20": {"type": "message", "message_typedef": {}, "name": ""}, "19": {"type": "message", "message_typedef": {}, "name": ""}, "11": {"type": "int", "name": ""}, "1": {"type": "message", "message_typedef": {"2": {"type": "bytes", "name": ""}}, "name": ""}}, "name": ""}}, "name": ""}, "9": {"type": "bytes", "name": ""}}'''