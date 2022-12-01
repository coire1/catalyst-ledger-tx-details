import io
import os
import pandas as pd
import numpy as np

import gspread
from gspread_formatting import *

from time import sleep
from config import settings

class GSheet():
    def __init__(self):
        self.service = gspread.service_account(
            filename=f"{settings.gdrive_auth_path}service_account.json"
        )

    def get_doc(self, file_id):
        file_id = self.extract_file_id(file_id)
        try:
            doc = self.service.open_by_key(file_id)
            return doc
        except gspread.exceptions.APIError as e:
            print(e)
        except Exception as e:
            print(e)
        return False

    def get_df(self, file_id, sheet_id=False, return_sheet=False):
        file_id = self.extract_file_id(file_id)
        try:
            doc = self.service.open_by_key(file_id)
            sheet = False
            if sheet_id:
                sheets = [s.title for s in doc.worksheets()]
                if sheet_id in sheets:
                    sheet = doc.worksheet(sheet_id)
            if not sheet:
                sheet = doc.get_worksheet(0)
            records = sheet.get_values()
            original_headers = records[0]
            if (len(original_headers) != len(set(original_headers))):
                headers = [f"{col}" for i, col in enumerate(original_headers)]
            else:
                headers = original_headers
            records.pop(0)
            df = pd.DataFrame(records, columns=headers)
            df.fillna('', inplace=True)
            if return_sheet:
                return df, sheet
            else:
                return df
        except gspread.exceptions.APIError as e:
            print(e)
            dict_error = e.response.json()
            if dict_error['error']['status'] == 'RESOURCE_EXHAUSTED':
                print("Rate limit exceeded. Sleep for 30s...")
                sleep(30)
                print("Retry download...")
                return self.get_df(file_id, sheet_id)
            else:
                print("GSheet error downloading: {}".format(file_id))
                print(e)
                return pd.DataFrame([])
        except Exception as e:
            print(e)
            print("Generic error downloading: {}".format(file_id))
            return pd.DataFrame([])

    def extract_file_id(self, url):
        file_id = re.findall("[-\w]{25,}", url)
        if len(file_id) == 1:
            return file_id[0]
        else:
            print("Not valid Google doc/sheet link found.")
            return False
