"""Convert a .docx to .pdf with Microsoft Word (COM) and print the page count.

Usage: python scripts/to_pdf.py <file.docx>
"""
import sys
from pathlib import Path

import win32com.client


def convert(docx_path: Path) -> int:
    pdf_path = docx_path.with_suffix(".pdf")
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        doc = word.Documents.Open(str(docx_path), ReadOnly=True)
        pages = doc.ComputeStatistics(2)  # wdStatisticPages
        doc.ExportAsFixedFormat(str(pdf_path), 17)  # wdExportFormatPDF
        doc.Close(False)
    finally:
        word.Quit()
    print(f"saved {pdf_path} ({pages} pages)")
    return pages


if __name__ == "__main__":
    convert(Path(sys.argv[1]).resolve())
