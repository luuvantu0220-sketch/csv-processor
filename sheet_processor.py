import os
import pandas as pd
import openpyxl

def full_process_pipeline(datasource_path, template_path, output_path):
    """
    Hàm này chạy hoàn toàn tự động trên Render:
    - Đọc file datasheet đã xử lý.
    - Mở file mẫu (template).
    - Copy dữ liệu sang sheet 'Ket qua do'.
    - Lưu ra file hoàn chỉnh.
    """
    # 1. Đọc datasheet đã xử lý
    df_source = pd.read_excel(datasource_path, sheet_name=0)
    
    # 2. Mở file mẫu
    wb_template = openpyxl.load_workbook(template_path)
    
    # 3. Chọn hoặc tạo sheet 'Ket qua do'
    if 'Ket qua do' in wb_template.sheetnames:
        ws_result = wb_template['Ket qua do']
    else:
        ws_result = wb_template.create_sheet('Ket qua do')
        
    # 4. Ghi dữ liệu vào sheet kết quả
    for row_idx, row_data in enumerate(df_source.itertuples(index=False), start=1):
        for col_idx, value in enumerate(row_data, start=1):
            ws_result.cell(row=row_idx, column=col_idx, value=value)
            
    # 5. Lưu lại
    wb_template.save(output_path)
    return output_path
