import os
import csv
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
        # Tự động nhận diện ký tự phân cách (delimiter)
        with open(input_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
            sample_text = f.read(2048)
        
        delimiter = ','
        if '\t' in sample_text:
            delimiter = '\t'
        elif ';' in sample_text:
            delimiter = ';'

        # Đọc toàn bộ file CSV bằng csv.reader
        rows = []
        encodings = ['utf-8-sig', 'utf-16le', 'utf-16', 'latin-1']
        success = False
        for enc in encodings:
            try:
                with open(input_path, 'r', encoding=enc) as f:
                    reader = csv.reader(f, delimiter=delimiter)
                    rows = list(reader)
                if rows:
                    success = True
                    break
            except Exception:
                continue

        if not success or len(rows) < 3:
            return {'error': 'File rỗng hoặc ít hơn 3 dòng.'}, 400

        # Tìm vị trí cột UN dựa vào dòng tiêu đề (rows[2])
        header = rows[2] if len(rows) > 2 else []
        un_idx = 6  # Mặc định cột G nếu không tìm thấy
        for idx, val in enumerate(header):
            if val.strip().upper() == 'UN':
                un_idx = idx
                break

        # --- BƯỚC 1: CHÈN CÔNG THỨC THẲNG VÀO CỘT UN (Dùng dấu ngoặc kép để Excel không tách cột) ---
        for i in range(3, len(rows)):
            if not rows[i] or not any(rows[i]):
                continue
            if len(rows[i]) > un_idx:
                row_num = i + 1  # Số dòng trong Excel
                formula = f"=MAX(ABS(C{row_num}-F{row_num}), ABS(D{row_num}-F{row_num}), ABS(E{row_num}-F{row_num}))/F{row_num}*100"
                rows[i][un_idx] = formula

        processed_rows = []

        # --- BƯỚC 2: Giữ 3 dòng tiêu đề đầu tiên và chèn 2 cột rỗng trước/sau cột B ---
        for i in range(min(3, len(rows))):
            r = list(rows[i])
            while len(r) <= 1:
                r.append("")
            r.insert(1, "")
            r.insert(3, "")
            processed_rows.append(r)

        # --- BƯỚC 3: Tạo dòng thứ 4: Đếm từ 1 -> 81 bắt đầu từ ô C4 ---
        sample_r = list(rows[2]) if len(rows) > 2 else []
        total_cols = len(sample_r) + 2
        row4 = [""] * total_cols
        count = 1
        for col_idx in range(2, len(row4)):
            if count <= 81:
                row4[col_idx] = str(count)
                count += 1
        processed_rows.append(row4)

        # --- BƯỚC 4: Xử lý các dòng dữ liệu từ dòng 5 trở đi (thêm STT vào trước cột B và trước cột D) ---
        stt = 1
        for i in range(3, len(rows)):
            if not rows[i] or not any(rows[i]):
                continue
            r = list(rows[i])
            r.insert(1, str(stt))
            r.insert(3, str(stt))
            processed_rows.append(r)
            stt += 1

        # --- BƯỚC 5: Ghi file kết quả bằng csv.writer (tự động wrap ngoặc kép các trường chứa dấu phẩy) ---
        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
            writer.writerows(processed_rows)

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
