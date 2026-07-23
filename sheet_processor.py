import os
import pandas as pd
import openpyxl

def process_with_embedded_template(datasource_path, output_path):
    """
    - Đọc file datasheet sau xử lý (được truyền vào).
    - Tự động lấy file mẫu 'Xu ly du lieu file do.xlsx' đã có sẵn trong thư mục dự án trên Render/GitHub.
    - Copy dữ liệu sang sheet 'Ket qua do' và lưu ra file kết quả.
    """
    # 1. Đọc dữ liệu từ file datasheet sau xử lý
    df_source = pd.read_excel(datasource_path, sheet_name=0)
    
    # 2. Đường dẫn tới file mẫu đã được đưa lên GitHub (nằm cùng thư mục với script)
    template_path = 'Xu ly du lieu file do.xlsx'
    
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Không tìm thấy file mẫu tại: {template_path}")
        
    # 3. Mở file mẫu bằng openpyxl
    wb_template = openpyxl.load_workbook(template_path)
    
    # 4. Chọn hoặc tạo sheet 'Ket qua do'
    if 'Ket qua do' in wb_template.sheetnames:
        ws_result = wb_template['Ket qua do']
    else:
        ws_result = wb_template.create_sheet('Ket qua do')
        
    # Xóa dữ liệu cũ trong sheet kết quả nếu cần thiết (đảm bảo sạch sẽ trước khi ghi mới)
    # ws_result.delete_rows(1, ws_result.max_row)
        
    # 5. Ghi dữ liệu từ datasheet vào sheet kết quả
    for row_idx, row_data in enumerate(df_source.itertuples(index=False), start=1):
        for col_idx, value in enumerate(row_data, start=1):
            ws_result.cell(row=row_idx, column=col_idx, value=value)
            
    # 6. Lưu lại thành file kết quả mới
    wb_template.save(output_path)
    return output_path
