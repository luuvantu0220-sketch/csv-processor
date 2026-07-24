# Route 2: Xử lý và copy dữ liệu vào file mẫu Excel
@app.route('/api/process-and-copy', methods=['POST'])
def api_process_and_copy():
    try:
        # Linh hoạt chấp nhận cả key 'datasheet' hoặc 'file' từ n8n gửi lên
        file_key = None
        if 'datasheet' in request.files:
            file_key = 'datasheet'
        elif 'file' in request.files:
            file_key = 'file'
        else:
            return {"error": "Thiếu file datasheet hoặc file gửi lên"}, 400
            
        datasheet_file = request.files[file_key]
        
        ds_path = os.path.join('/tmp', datasheet_file.filename)
        output_filename = f"Ket_qua_{datasheet_file.filename}.xlsx"
        out_path = os.path.join('/tmp', output_filename)
        
        datasheet_file.save(ds_path)
        
        # Gọi hàm xử lý và copy vào file mẫu Excel
        process_with_embedded_template(ds_path, out_path)
        
        return send_file(
            out_path, 
            as_attachment=True, 
            download_name=output_filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return {"error": str(e)}, 500
