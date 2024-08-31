import azure.functions as func
from .excel_processor import process_excel_file

def main(myblob: func.InputStream):
    process_excel_file(myblob)