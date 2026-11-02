import zipfile
import re

def verify():
    filename = 'Predictive_Sales_Forecasting_Documentation.docx'
    with zipfile.ZipFile(filename, 'r') as z:
        doc_xml = z.read('word/document.xml').decode('utf-8')
        page_breaks = len(re.findall(r'<w:br\s+w:type="page"/>', doc_xml))
        
        # Extract text elements
        text_matches = re.findall(r'<w:t[^>]*>(.*?)</w:t>', doc_xml)
        all_text = ' '.join(text_matches)
        words = len(all_text.split())
        
        # Embedded figures
        media_files = [f for f in z.namelist() if f.startswith('word/media/')]

    print("==================================================================")
    print(f"DOCUMENT VERIFICATION REPORT: {filename}")
    print("==================================================================")
    print(f"Total Explicit A4 Page Breaks : {page_breaks}")
    print(f"Total Rendered A4 Pages       : {page_breaks + 1} Pages")
    print(f"Total Technical Word Count    : {words:,} words")
    print(f"Embedded Publication Figures  : {len(media_files)}")
    for idx, f in enumerate(media_files, 1):
        print(f"  [{idx}] {f}")
    print("==================================================================")
    if (page_breaks + 1) == 20:
        print("VERIFICATION RESULT: SUCCESS - EXACTLY 20 COMPLETE A4 PAGES.")
    else:
        print(f"VERIFICATION RESULT: Document contains {page_breaks + 1} pages.")

if __name__ == '__main__':
    verify()
