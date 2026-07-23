import os
import pandas as pd
import openpyxl

def process_and_fill_template(datasource_path, template_path, output_path):
    """
    1. Đọc dữ liệu từ file datasheet sau xử lý.
    2. Mở file mẫu (template_path) chứa các sheet như 'Ket qua do', 'Xu ly du lieu do'...
    3. Copy/ghi dữ liệu vào sheet 'Ket qua do' của file mẫu.
    4. Lưu ra file kết quả mới (output_path).
    """
    # 1. Đọc dữ liệu từ datasheet (chọn sheet chứa dữ liệu đã xử lý, mặc định sheet đầu tiên hoặc chỉ định tên sheet)
    df_source = pd.read_excel(datasource_path, sheet_name=0)
    
    # 2. Mở file mẫu bằng openpyxl để giữ nguyên định dạng (format, style, formula nếu có)
    wb_template = openpyxl.load_workbook(template_path)
    
    # 3. Chọn sheet 'Ket qua do' (hoặc tạo mới nếu chưa tồn tại)
    if 'Ket qua do' in wb_template.sheetnames:
        ws_result = wb_template['Ket qua do']
    else:
        ws_result = wb_template.create_sheet('Ket qua do')
        
    # 4. Ghi dữ liệu từ dataframe vào sheet kết quả
    # Ghi tiêu đề cột (header) ở dòng 1
    for col_idx, col_name in enumerate(df_source.columns, start=1):
        ws_result.cell(row=1, column=col_idx, value=col_name)
        
    # Ghi các dòng dữ liệu từ dòng 2 trở đi
    for row_idx, row_data in enumerate(df_source.itertuples(index=False), start=2):
        for col_idx, value in enumerate(row_data, start=1):
            ws_result.cell(row=row_idx, column=col_idx, value=value)
            
    # 5. Lưu file kết quả hoàn chỉnh
    wb_template.save(output_path)
    return output_path
