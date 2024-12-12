__artifacts_v2__ = {
    "netEventData": {
        "name": "Net Event Data",
        "description": "Extracts Net Event Data - Research Needed",
        "author": "@jfhyla",
        "version": "0.1",
        "date": "2024-12-12",
        "requirements": "none",
        "category": "Data Usage",
        "notes": "",
        "paths": ('*/var/mobile/Library/Caches/com.apple.geod/Vault/AnalyticNetworkEvent/neteventdata-*',),
        "output_types": "standard"
    }
}

from scripts.ilapfuncs import artifact_processor, convert_cocoa_core_data_ts_to_utc
import blackboxprotobuf
import struct

@artifact_processor
def netEventData(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    db_file = ''

    type_def = {'1': {'type': 'message',
                      'message_typedef': {'2': {'type': 'message',
                                                'message_typedef': {'1': {'type': 'int', 'name': ''},
                                                                    '2': {'type': 'str', 'name': ''},
                                                                    '20': {'type': 'double', 'name': ''},
                                                                    '21': {'type': 'double', 'name': ''},
                                                                    '22': {'type': 'int', 'name': ''},
                                                                    '23': {'type': 'message',
                                                                           'message_typedef': {
                                                                               '1': {'type': 'fixed64', 'name': ''},
                                                                               '2': {'type': 'double', 'name': ''},
                                                                               '3': {'type': 'double', 'name': ''},
                                                                               '4': {'type': 'double', 'name': ''},
                                                                               '5': {'type': 'double', 'name': ''},
                                                                               '6': {'type': 'double', 'name': ''},
                                                                               '7': {'type': 'double', 'name': ''},
                                                                               '8': {'type': 'double', 'name': ''},
                                                                               '9': {'type': 'double', 'name': ''},
                                                                               '10': {'type': 'double', 'name': ''},
                                                                               '11': {'type': 'double', 'name': ''},
                                                                               '12': {'type': 'int', 'name': ''},
                                                                               '13': {'type': 'int', 'name': ''},
                                                                               '14': {'type': 'int', 'name': ''},
                                                                               '15': {'type': 'int', 'name': ''},
                                                                               '16': {'type': 'int', 'name': ''},
                                                                               '18': {'type': 'int', 'name': ''}},
                                                                           'name': ''}},
                                                'name': ''}},
                      'name': ''},
                '2': {'type': 'int', 'name': ''},
                '3': {'type': 'int', 'name': ''},
                '4': {'type': 'int', 'name': ''},
                '6': {'type': 'str', 'name': ''},
                '12': {'type': 'double', 'name': ''},
                '13': {'type': 'bytes', 'name': ''},
                '14': {'type': 'int', 'name': ''},
                '15': {'type': 'message',
                       'message_typedef': {'12': {'type': 'fixed32', 'name': ''}},
                       'name': ''},
                '16': {'type': 'int', 'name': ''},
                '17': {'type': 'bytes', 'name': ''},
                '18': {'type': 'bytes', 'name': ''}}

    for file_found in files_found:

        with open(file_found, 'rb') as file:
            file.seek(0, 2)
            file_size = file.tell()
            file.seek(0)
            file.seek(4, 1)
            while file.tell() < file_size:
                length = struct.unpack('<I', file.read(4))[0]
                raw_pb = file.read(length)
                decoded_pb, typess = blackboxprotobuf.decode_message(raw_pb, type_def)
                dt = convert_cocoa_core_data_ts_to_utc(decoded_pb['12'])
                data_list.append((dt, decoded_pb.get('6'), decoded_pb['1']['2'].get('2'), decoded_pb['1']['2'].get('1')))

                file.seek(4, 1)

    data_headers = ['unknown time', 'service', 'ip', 'http response']

    return data_headers, data_list, file_found
