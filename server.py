from flask import Flask, request, jsonify, send_file
import os
import process

app = Flask(__name__)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/upload-and-process', methods=['POST'])
def handle_upload():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Không tìm thấy file gửi lên!"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "Tên file rỗng!"}), 400

    # 1. Lưu file tạm thời lên Server Cloud
    input_path = os.path.join(CURRENT_DIR, file.filename)
    file.save(input_path)

    # Đường dẫn file kết quả
    name, ext = os.path.splitext(file.filename)
    output_filename = f"{name}_Da_Xu_Ly.csv"
    output_path = os.path.join(CURRENT_DIR, output_filename)

    # 2. Xử lý file bằng process.py
    try:
        process.process_single_file(input_path)
        
        # 3. Trả file CSV đã xử lý về lại cho n8n
        if os.path.exists(output_path):
            return send_file(
                output_path, 
                as_attachment=True, 
                download_name=output_filename, 
                mimetype='text/csv'
            )
        else:
            return jsonify({"status": "error", "message": "Không tìm thấy file kết quả!"}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Đọc cổng do Render tự động cấp phát
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)