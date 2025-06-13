import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import json
import os 

# Setup credentials and access
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(os.environ["GOOGLE_CREDS"])
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_dict, scope)
client = gspread.authorize(creds)

# Global worksheet variables (optional, if you want to reuse without re-fetching)
# You can choose to always call getter functions instead
account_sheet_global = client.open("discord-bot").worksheet("accounts")
device_sheet_global = client.open("discord-bot").worksheet("device")
session_sheet_global = client.open("discord-bot").worksheet("session")


# Worksheet Getter Functions
def get_account_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("discord-bot").worksheet("accounts")
    return sheet

def get_device_sheet():
    return client.open("discord-bot").worksheet("device")

def get_session_sheet():
    return client.open("discord-bot").worksheet("session")


# ID Generators
def index():
    sheet_obj = get_account_sheet()
    return str(len(sheet_obj.get_all_values()) + 1)

def dindx():
    sheet_obj = get_device_sheet()
    return str(len(sheet_obj.get_all_values()) + 1)

def sess_id():
    sheet_obj = get_session_sheet()
    return str(len(sheet_obj.get_all_values()) + 1)


# Status Checkers
def astatus(account_id):
    try:
        sheet = get_account_sheet()  # Call the function to get the worksheet
        cell = sheet.find(str(account_id))  # Make sure ID is string for searching
        status = sheet.cell(cell.row,16).value  # Assuming status is in column 16
        print(status)
        return status
    except Exception as e:
        print(f"Error fetching status for account {account_id}: {e}")
        return None

def dstatus(device_id):
    sheet_obj = get_device_sheet()
    data = sheet_obj.get_all_values()
    for row in data:
        if row[0] == device_id:
            # Assuming Device_Free column is 3rd (index 2)
            return row[2].strip().lower() == "true"
    return False


# Update Device Sheet
def update_device_sheet(device_id):
    sheet_obj = get_device_sheet()
    data = sheet_obj.get_all_values()
    for i, row in enumerate(data):
        if row[0] == device_id:
            # Set Device_Free = FALSE (assuming col 3)
            sheet_obj.update_cell(i+1, 3, "FALSE")
            return True
    return False

def set_device_free(sheet_obj, device_id):
    data = sheet_obj.get_all_values()
    for i, row in enumerate(data):
        if row[0] == device_id:
            sheet_obj.update_cell(i+1, 3, "TRUE")
            return True
    return False


# Update Account Sheet
def update_account_sheet(account_id):
    sheet_obj = get_account_sheet()
    data = sheet_obj.get_all_values()
    for i, row in enumerate(data):
        if row[0] == account_id:
            # Last col assumed Status
            sheet_obj.update_cell(i+1,16, "INUSE")
            return True
    return False

def find_row_by_value(sheet_obj, col_index, value):
    all_values = sheet_obj.col_values(col_index)
    for i, val in enumerate(all_values, start=1):
        if str(val) == str(value):
            return i
    return None


# Set Cooldown on Account
def set_account_cooldown(sheet_obj, account_id):
    row = find_row_by_value(sheet_obj, 1, account_id)  # Column 1 = Account ID
    if not row:
        return False

    cooldown_until = datetime.now() + timedelta(hours=2)
    # Find cooldown and Status column indices by header
    headers = sheet_obj.row_values(1)
    try:
        col_cooldown = headers.index('cooldown') + 1
        col_status = headers.index('Status') + 1
    except ValueError:
        # Columns not found
        return False

    cd_time = cooldown_until.strftime('%Y-%m-%d %H:%M:%S')
    sheet_obj.update_cell(row, col_cooldown, cd_time)
    sheet_obj.update_cell(row, col_status, "CD")
    
    return True


# Session Info
def get_session_info(sheet_obj, session_id):
    rows = sheet_obj.get_all_values()
    headers = rows[0]
    for row in rows[1:]:
        if row[0] == session_id:
            return {
                "account_id": row[1],
                "device_id": row[2],
                "grind_type": row[3]
            }
    return None


# End Session
def update_session_end(sheet_obj, session_id):
    rows = sheet_obj.get_all_values()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for i, row in enumerate(rows):
        if row[0] == session_id:
            # Ensure at least 6 columns
            if len(row) < 6:
                # Fill missing columns if needed (optional)
                # But gspread won't append columns automatically here, so just update 6th col
                sheet_obj.update_cell(i+1, 6, now)  # 6th col = Grind Ended At
            else:
                sheet_obj.update_cell(i+1, 6, now)
            return True
    return False


# Account Value Update Based on Grind
def update_account_values(sheet_obj, account_id, new_values):
    rows = sheet_obj.get_all_values()
    header = rows[0]

    for i, row in enumerate(rows):
        if row[0] == account_id:
            for key, val in new_values.items():
                if key in header:
                    col = header.index(key)
                    cell_val = row[col]
                    
                    # Safely handle non-integer cells
                    try:
                        prev_val = int(cell_val)
                    except (ValueError, TypeError):
                        print(f"⚠️ Skipping column '{key}' - current value is not an integer: '{cell_val}'")
                        continue
                    
                    # Ensure val is also an int
                    if not isinstance(val, int):
                        print(f"⚠️ Skipping key '{key}' - update value is not an integer: {val}")
                        continue
                    
                    print(f"✅ Updating {key}: {prev_val} + {val}")
                    sheet_obj.update_cell(i + 1, col + 1, str(prev_val + val))
            return True
    return False
