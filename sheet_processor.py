import os
import pandas as pd
import openpyxl

def process_with_embedded_template(datasource_path, output_path):
    """
    - Đọc file datasheet sau xử lý với dtype=str để bảo toàn 100% dữ liệu gốc.
    - Sử dụng phương pháp ghi mảng hàng loạt (append) giúp tăng tốc độ xử lý gấp nhiều lần, 
      tránh gây nghẽn server và lỗi 502 trên Render.
    """
    # Đọc file nguồn với dtype=str để giữ nguyên vẹn cấu trúc và chống tràn RAM
    if datasource_path.endswith('.csv'):
        try:
            df_source = pd.read_csv(datasource_path, encoding='utf-8-sig', dtype=str, low_memory=False)
        except Exception:
            df_source = pd.read_csv(datasource_path, encoding='latin-1', errors='ignore', dtype=str, low_memory=False)
    else:
        df_source = pd.read_excel(datasource_path, sheet_name=0, dtype=str)
    
    template_path = 'Xu ly du lieu file do.xlsx'
    
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Không tìm thấy file mẫu tại: {template_path}")
        
    wb_template = openpyxl.load_workbook(template_path)
    
    if 'Ket qua do' in wb_template.sheetnames:
        ws_result = wb_template['Ket qua do']
    else:
        ws_result = wb_template.create_sheet('Ket qua do')
        
    # --- TỐI ƯU TỐC ĐỘ: Ghi hàng loạt thay vì dùng 2 vòng lặp for duyệt từng ô ---
    # Chuyển DataFrame thành danh sách các dòng và dùng append vào sheet
    rows_data = df_source.values.tolist()
    for row in rows_data:
        ws_result.append(row)
            
    wb_template.save(output_path)
    return output_path
