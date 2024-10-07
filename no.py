import subprocess
import re

def get_contact_number(message_body):
    # Run ADB command to get SMS details
    adb_command = f"adb shell am broadcast -a android.provider.Telephony.SMS_RECEIVED"
    output = subprocess.check_output(adb_command, shell=True).decode('utf-8')

    # Parse the output to extract contact number based on the message body
    contact_number = None
    lines = output.split('\n')
    for line in lines:
        if "android.provider.Telephony.SMS_RECEIVED" in line and message_body in line:
            match = re.search(r'(?<=address=\")(.*?)(?=\")', line)
            if match:
                contact_number = match.group(0)
                break

    return contact_number

# Replace "yeah" with your desired message body
message_body = "yeah"
contact_number = get_contact_number(message_body)

if contact_number:
    print(f"The contact number for the message '{message_body}' is: {contact_number}")
else:
    print(f"No contact number found for the message '{message_body}'")
