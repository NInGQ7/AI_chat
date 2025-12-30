# app/core/file_parser.py
import os
import pdfplumber
from docx import Document
import pandas as pd

def parse_file_content(file_path: str) -> str:
    """
    全能文件解析器 (修复了 Excel 文件占用问题)
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        # 1. Excel -> Markdown
        if ext in ['.xlsx', '.xls', '.csv']:
            text_output = ""
            try:
                if ext == '.csv':
                    # CSV 也可以直接用 with 或者是简单的读取，pandas read_csv 通常会自动关闭
                    df_dict = {'CSV': pd.read_csv(file_path)}
                else:
                    # 【核心修复】使用 context manager (with) 确保读取后自动关闭文件
                    with pd.ExcelFile(file_path) as xls:
                        df_dict = {sheet: pd.read_excel(xls, sheet_name=sheet).fillna('') for sheet in xls.sheet_names}
                
                for sheet_name, df in df_dict.items():
                    # 限制行数/列数防止 token 爆炸 (可选)
                    table_md = df.to_markdown(index=False)
                    text_output += f"\n--- Sheet: {sheet_name} ---\n{table_md}\n"
                return text_output
            except Exception as e:
                return f"Error reading Excel: {str(e)}"

        # 2. PDF
        elif ext == '.pdf':
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    txt = page.extract_text()
                    if txt: text += txt + "\n"
            return text
            
        # 3. Word
        elif ext in ['.docx', '.doc']:
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
            
        # 4. Text
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
            
    except Exception as e:
        print(f"❌ Parse Error: {e}")
        return f"Error parsing file: {str(e)}"