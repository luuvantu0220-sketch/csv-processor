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

    # Lưu file tải lên vào thư mục tạm trên Render
    file.save(input_path)

    try:
        lines = []
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                lines = [line.rstrip('\r\n') for line in f]
        except Exception:
            try:
                with open(input_path, 'r', encoding='utf-16le') as f:
                    lines = [line.rstrip('\r\n') for line in f]
            except Exception as e:
                return {'error': f"Không thể đọc file '{filename}': {e}"}, 400

        if not lines or len(lines) < 3:
            return {'error': f"Bỏ qua '{filename}': File rỗng hoặc ít hơn 3 dòng."}, 400

        # Nhận diện dấu phân cách
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

        # 2. Tạo dòng thứ 4: Đếm từ 1 -> 81 bắt đầu từ ô C4 (col_idx = 2)
        sample_parts = lines[2].split(delimiter)
        row4 = [""] * (len(sample_parts) + 2)
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

        # 4. Ghi file kết quả xử lý
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            f.write('\n'.join(processed))

        # Trả file đã xử lý về cho n8n
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
