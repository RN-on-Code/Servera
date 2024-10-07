import subprocess
import re
import time
def process_onroad():
    onroad_messages = []
    phonenos = []
    _, onroad_messages, _, _, = read_recent_sms()
    for i in range(len(onroad_messages)):
        phonenos.append(extract_onroad_phone_number(onroad_messages[i]))
    print(phonenos)
    return phonenos
def extract_onroad_phone_number(onroad_message):
    if onroad_message:
        match = re.search(r"Onroad &(.+) #(\d+)", onroad_message)
        if match:
            phone_number = match.group(2).strip()
            return "+91" + phone_number
    return None
def read_recent_sms():
    adb_command = 'adb shell content query --uri content://sms/inbox --projection address,date_sent,body --sort date_sent'

    result = subprocess.run(adb_command, shell=True, capture_output=True, text=True, encoding='utf-8')

    if result.returncode == 0:
        if result.stdout:
            sms_messages = result.stdout.strip().split('\n')

            # Regex patterns for matching Byroad and Onroad messages
            byroad_pattern1 = re.compile(r"Byroad @(.+) @(.+)(?: #(\d+))?")
            byroad_pattern2 = re.compile(r"Byroad @(.+) @(.+)")
            onroad_pattern = re.compile(r"Onroad &(.+) #(\d+)")
            response_pattern = re.compile(r"Yeah @(.+)", re.IGNORECASE)
            response_pattern2 = re.compile(r"(Yeah)",re.IGNORECASE)


            # Extract valid Byroad and Onroad messages
            valid_byroad_messages = [msg for msg in sms_messages if byroad_pattern1.search(msg) or byroad_pattern2.search(msg)] 
            valid_onroad_messages = [msg for msg in sms_messages if onroad_pattern.search(msg)]
            valid_response_messages = [msg for msg in sms_messages if response_pattern.search(msg)]
            valid_response_messages2 = [msg for msg in sms_messages if response_pattern2.search(msg)]
            # Find the most recent Byroad, Onroad, and response messages
            most_recent_byroad_message = valid_byroad_messages[-1] if valid_byroad_messages else None
            most_recent_onroad_message = valid_onroad_messages[-1] if valid_onroad_messages else None
            most_recent_response_message = valid_response_messages[-1] if valid_response_messages else None
            most_recent_response_message2 = valid_response_messages2[-1] if valid_response_messages2 else None

            # Open a file in exclusive creation mode ('x')
# This will create a new file, but if the file already exists, it will raise a FileExistsError.
            


            return most_recent_byroad_message, valid_onroad_messages, most_recent_response_message, most_recent_response_message2
        else:
            return None, None, None  # No SMS messages found
    else:
        print(f"Error executing ADB command. Return code: {result.returncode}")
        print(f"Error details: {result.stderr}")
        return None, None, None
    

process_onroad()