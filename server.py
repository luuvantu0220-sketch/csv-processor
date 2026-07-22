import os
from flask import Flask, request, send_file
import pandas as pd

app = Flask(__name__)

@app.route('/upload-and-process', methods=['POST'])
def upload_and_process():
    if 'file' not in request.files:
        return {'error': 'Không tìm thấy file gửi lên'}, 400
    
    file = request.files['file']
    if file.filename == '':
        return {'error': 'Chưa chọn file'}, 400

    input_path = os.path.join('/tmp', file.filename)
    file.save(input_path)
    
    output_path = os.path.join('/tmp', 'processed_' + file.filename)

    try:
        chunk_size = 10000  # Đọc mỗi lần 10,000 dòng để tiết kiệm RAM nhưng vẫn quét đủ 100% dữ liệu
        all_chunks = []

        for chunk in pd.read_csv(input_path, chunksize=chunk_size):
            # --- VIẾT LOGIC XỬ LÝ / TÍNH TOÁN CỦA BẠN VÀO ĐÂY ---
            processed_chunk = chunk
            # -----------------------------------------------------
            all_chunks.append(processed_chunk)

        final_df = pd.concat(all_chunks, ignore_index=True)
        final_df.to_csv(output_path, index=False)

        return send_file(output_path, as_attachment=True, download_name=file.filename)

    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
