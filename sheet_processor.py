import pandas as pd
import openpyxl

def process_and_fill_template(datasource_path, template_path, output_path):
    # 1. Đọc và xử lý dữ liệu từ file datasheet (giữ nguyên logic bạn đã làm ở các bước trước)
    # Ví dụ đọc datasheet:
    df_source = pd.read_excel(datasource_path)
    
    # 2. Mở file mẫu (file đo) chứa sheet 'Ket qua do' và 'Xu ly du lieu do'
    wb_template = openpyxl.load_workbook(template_path)
    
    # Kiểm tra hoặc tạo sheet kết quả nếu chưa có
    if 'Ket qua do' in wb_template.sheetnames:
        ws_result = wb_template['Ket qua do']
    else:
        ws_result = wb_template.create_sheet('Ket qua do')
        
    # 3. Thực hiện logic copy/ghi dữ liệu đã xử lý sang sheet kết quả của file mẫu
    # (Tùy chỉnh logic gán giá trị vào các ô/dòng cụ thể tại đây)
    # Ví dụ ghi dữ liệu mẫu:
    # ws_result['A1'] = "Kết quả đo sau xử lý"
    
    # 4. Lưu lại file mẫu đã được điền dữ liệu thành file mới riêng biệt cho từng thiết bị/lần đo
    wb_template.save(output_path)
    return output_path
