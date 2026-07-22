import os
import glob

def process_single_file(file_path):
    folder, filename = os.path.split(file_path)
    name, ext = os.path.splitext(filename)
    output_path = os.path.join(folder, f"{name}_Da_Xu_Ly.csv")

    lines = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.rstrip('\r\n') for line in f]
    except Exception:
        try:
            with open(file_path, 'r', encoding='utf-16le') as f:
                lines = [line.rstrip('\r\n') for line in f]
        except Exception as e:
            print(f"❌ Không thể đọc file '{filename}': {e}")
            return

    if not lines or len(lines) < 3:
        print(f"⚠️ Bỏ qua '{filename}': File rỗng hoặc ít hơn 3 dòng.")
        return

    delimiter = ','
    if '\t' in lines[2]: delimiter = '\t'
    elif ';' in lines[2]: delimiter = ';'

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

    # 4. Ghi file kết quả (Có bắt lỗi nếu file đang mở trong Excel)
    try:
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            f.write('\n'.join(processed))
        print(f"✅ Đã xử lý xong '{filename}' -> Tạo file '{name}_Da_Xu_Ly.csv' ({len(processed)} dòng)")
    except PermissionError:
        print(f"❌ LỖI: Không thể ghi file '{name}_Da_Xu_Ly.csv'!")
        print("👉 Vui lòng ĐÓNG FILE EXCEL đó lại rồi chạy lại lệnh 'python process.py'.")

def main():
    all_csvs = glob.glob("*.csv")
    input_files = [f for f in all_csvs if not f.endswith("_Da_Xu_Ly.csv")]

    if not input_files:
        print("❌ Không tìm thấy file CSV mới nào trong thư mục!")
        return

    print(f"🚀 Tìm thấy {len(input_files)} file CSV cần xử lý...")
    for file_path in input_files:
        process_single_file(file_path)
    print("🎉 Tất cả đã hoàn tất!")

if __name__ == "__main__":
    main()