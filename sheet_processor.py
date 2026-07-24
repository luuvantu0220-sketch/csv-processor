import os
import pandas as pd
import openpyxl

def process_with_embedded_template(datasource_path, output_path):
    """
    - Đọc file datasheet sau xử lý (hỗ trợ cả CSV và Excel).
    - Tự động lấy file mẫu 'Xu ly du lieu file do.xlsx' đã có sẵn trong thư mục dự án trên Render.
    - Copy dữ liệu sang sheet 'Ket qua do' và lưu ra file kết quả.
    """
    # Tự động nhận diện đọc file CSV hay Excel dựa vào phần mở rộng
    if datasource_path.endswith('.csv'):
        # Thử đọc file CSV với các encoding phổ biến
        try:
            df_source = pd.read_csv(datasource_path, encoding='utf-8-sig')
        except Exception:
            df_source = pd.read_csv(datasource_path, encoding='latin-1', errors='ignore')
    else:
        df_source = pd.read_excel(datasource_path, sheet_name=0)
    
    template_path = 'Xu ly du lieu file do.xlsx'
    
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Không tìm thấy file mẫu tại: {template_path}")
        
    wb_template = openpyxl.load_workbook(template_path)
    
    if 'Ket qua do' in wb_template.sheetnames:
        ws_result = wb_template['Ket qua do']
    else:
        ws_result = wb_template.create_sheet('Ket qua do')
        
    for row_idx, row_data in enumerate(df_source.itertuples(index=False), start=1):
        for col_idx, value in enumerate(row_data, start=1):
            ws_result.cell(row=row_idx, column=col_idx, value=value)
            
    wb_template.save(output_path)
    return output_path
