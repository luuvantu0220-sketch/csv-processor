import os
import zipfile
from flask import Flask, request, send_file

app = Flask(__name__)

@app.route('/upload-and-process', methods=['POST'])
def upload_and_process():
    if not request.files:
        return {'error': 'Không tìm thấy file gửi lên'}, 400
    
    processed_files = []
    
    # Lặp qua tất cả các file được gửi lên từ n8n (bất kể tên file_0, file_1,...)
    for key, file in request.files.items():
        if file.filename == '':
            continue
            
        filename = file.filename
        name, ext = os.path.splitext(filename)
        input_path = os.path.join('/tmp', f"{key}_{filename}")
        output_filename = f"{name}_Da_Xu_Ly.csv"
        output_path = os.path.join('/tmp', output_filename)

        file.save(input_path)

        try:
            lines = []
            for enc in ['utf-8', 'utf-16le', 'utf-16', 'latin-1']:
                try:
                    with open(input_path, 'r', encoding=enc) as f:
                        lines = [line.rstrip('\r\n') for line in f]
                    break
                except Exception:
                    continue

            if not lines or len(lines) < 3:
                continue

            delimiter = ','
            if '\t' in lines[2]: 
                delimiter = '\t'
            elif ';' in lines[2]: 
                delimiter = ';'

            processed = []

            # 1. Giữ 3 dòng tiêu đề đầu tiên và chèn 2 cột rỗng trước/sau cột B
            for i in range(min(3, len(lines))):
                parts = lines[i].split(delimiter)
                parts.insert(1, "")
                parts.insert(3, "")
                processed.append(delimiter.join(parts))

            # 2. Tạo dòng thứ 4: Đếm từ 1 -> 81 bắt đầu từ ô C4
            sample_parts = lines[2].split(delimiter)
            total_cols = len(sample_parts) + 2
            row4 = [""] * total_cols
            count = 1
            for col_idx in range(2, len(row4)):
                if count <= 81:
                    row4[col_idx] = str(count)
                    count += 1
            processed.append(delimiter.join(row4))

            # 3. Xử lý các dòng dữ liệu từ dòng 5 trở đi
            stt = 1
            for i in range(3, len(lines)):
                if not lines[i].strip():
                    continue
                parts = lines[i].split(delimiter)
                parts.insert(1, str(stt))
                parts.insert(3, str(stt))
                processed.append(delimiter.join(parts))
                stt += 1

            # 4. Ghi file kết quả
            with open(output_path, 'w', encoding='utf-8-sig') as f:
                f.write('\n'.join(processed))
                
            processed_files.append(output_path)

        except Exception as e:
            continue

    if not processed_files:
        return {'error': 'Không có file nào được xử lý thành công'}, 500

    # Nếu chỉ có 1 file, trả về trực tiếp file đó
    if len(processed_files) == 1:
        return send_file(
            processed_files[0], 
            as_attachment=True, 
            download_name=os.path.basename(processed_files[0]),
            mimetype='text/csv'
        )
    
    # Nếu có nhiều file được xử lý, nén lại thành 1 file ZIP trả về để n8n nhận trọn gói gọn gàng
    zip_path = os.path.join('/tmp', 'Tat_Ca_File_Da_Xu_Ly.zip')
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path in processed_files:
            zipf.write(file_path, os.path.basename(file_path))
            
    return send_file(
        zip_path,
        as_attachment=True,
        download_name='Tat_Ca_File_Da_Xu_Ly.zip',
        mimetype='application/zip'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
