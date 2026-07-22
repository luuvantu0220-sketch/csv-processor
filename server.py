import os
from flask import Flask, request, send_file

app = Flask(__name__)

@app.route('/upload-and-process', methods=['POST'])
def upload_and_process():
    if 'file' not in request.files:
        return {'error': 'Không tìm thấy file gửi lên'}, 400
    
    file = request.files['file']
    if file.filename == '':
        return {'error': 'Chưa chọn file'}, 400

    filename = file.filename
    name, ext = os.path.splitext(filename)
    input_path = os.path.join('/tmp', filename)
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
            return {'error': 'File rỗng hoặc ít hơn 3 dòng.'}, 400

        delimiter = ','
        if '\t' in lines[2]: 
            delimiter = '\t'
        elif ';' in lines[2]: 
            delimiter = ';'

        # Tìm vị trí cột UN dựa vào dòng tiêu đề (lines[2])
        header_parts = lines[2].split(delimiter)
        un_idx = 6  # Mặc định là cột G (index 6) nếu không tìm thấy tên
        for idx, val in enumerate(header_parts):
            if val.strip().upper() == 'UN':
                un_idx = idx
                break

        # --- BƯỚC 1: CHÈN CÔNG THỨC THẲNG VÀO CỘT UN TRƯỚC KHI THÊM HÀNG/CỘT ---
        modified_lines = []
        for i, line in enumerate(lines):
            if not line.strip():
                modified_lines.append(line)
                continue
            parts = line.split(delimiter)
            # Chỉ chèn công thức cho các dòng dữ liệu (từ dòng 4 Excel trở đi, tức index >= 3)
            if i >= 3:
                if len(parts) > un_idx:
                    row_num = i + 1  # Số dòng trong Excel (index 3 là dòng 4)
                    formula = f"=MAX(ABS(C{row_num}-F{row_num}), ABS(D{row_num}-F{row_num}), ABS(E{row_num}-F{row_num}))/F{row_num}*100"
                    parts[un_idx] = formula
            modified_lines.append(delimiter.join(parts))

        processed = []

        # --- BƯỚC 2: Giữ 3 dòng tiêu đề đầu tiên và chèn 2 cột rỗng trước/sau cột B ---
        for i in range(min(3, len(modified_lines))):
            parts = modified_lines[i].split(delimiter)
            parts.insert(1, "")
            parts.insert(3, "")
            processed.append(delimiter.join(parts))

        # --- BƯỚC 3: Tạo dòng thứ 4: Đếm từ 1 -> 81 bắt đầu từ ô C4 ---
        sample_parts = modified_lines[2].split(delimiter)
        total_cols = len(sample_parts) + 2
        row4 = [""] * total_cols
        count = 1
        for col_idx in range(2, len(row4)):
            if count <= 81:
                row4[col_idx] = str(count)
                count += 1
        processed.append(delimiter.join(row4))

        # --- BƯỚC 4: Xử lý các dòng dữ liệu từ dòng 5 trở đi (thêm STT) ---
        stt = 1
        for i in range(3, len(modified_lines)):
            if not modified_lines[i].strip():
                continue
            parts = modified_lines[i].split(delimiter)
            parts.insert(1, str(stt))
            parts.insert(3, str(stt))
            processed.append(delimiter.join(parts))
            stt += 1

        # --- BƯỚC 5: Ghi file kết quả ---
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            f.write('\n'.join(processed))

        return send_file(
            output_path, 
            as_attachment=True, 
            download_name=output_filename,
            mimetype='text/csv'
        )

    except Exception as e:
        return {'error': f"Lỗi xử lý file: {str(e)}"}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
