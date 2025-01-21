import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from time import sleep


def create_directory(folder_name):
    """Tạo thư mục để lưu file PDF nếu chưa tồn tại"""
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


def download_file_with_progress(url, folder_name, progress, total, retries=3):
    """Tải file từ URL và hiển thị tiến độ tải từng file"""
    local_filename = os.path.join(folder_name, url.split("/")[-1])
    
    # Kiểm tra nếu file đã tồn tại
    if os.path.exists(local_filename):
        print(f"({progress}/{total}) Đã tồn tại: {local_filename}")
        return

    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(url, stream=True, timeout=10)
            if response.status_code != 200:
                print(f"({progress}/{total}) Không thể tải: {url} (HTTP {response.status_code})")
                return

            file_size = int(response.headers.get('Content-Length', 0))
            downloaded_size = 0
            with open(local_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:  # Lưu từng phần của file
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        percent_done = int((downloaded_size / file_size) * 100)
                        print(f"\r({progress}/{total}) Đang tải: {local_filename} - {percent_done}% hoàn thành", end="")

            print(f"\n({progress}/{total}) Đã tải: {local_filename}")
            return
        except requests.exceptions.RequestException as e:
            attempt += 1
            print(f"\n({progress}/{total}) Lỗi tải {url}. Thử lại ({attempt}/{retries})...")
            sleep(2)  # Đợi trước khi thử lại

    print(f"({progress}/{total}) Thất bại: Không thể tải {url} sau {retries} lần thử.")


def scrape_pdfs(base_url, folder_name):
    """Thu thập và tải xuống tất cả các file PDF từ trang web"""
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code != 200:
            print(f"Không thể truy cập {base_url} (HTTP {response.status_code})")
            return
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi truy cập {base_url}: {e}")
        return

    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.find_all("a", href=True)
    # Sử dụng set để loại bỏ các đường dẫn trùng lặp
    pdf_links = list(set(urljoin(base_url, link["href"]) for link in links if link["href"].endswith(".pdf")))

    if not pdf_links:
        print("Không tìm thấy file PDF nào.")
        return

    create_directory(folder_name)
    total_files = len(pdf_links)
    print(f"Tìm thấy {total_files} file PDF. Bắt đầu tải...")

    for idx, pdf_url in enumerate(pdf_links, start=1):
        download_file_with_progress(pdf_url, folder_name, idx, total_files)


if __name__ == "__main__":
    # URL của trang web cần thu thập file PDF
    base_url = "https://hayhay.work.gd/"
    # Tên thư mục lưu trữ file PDF
    folder_name = "downloaded_pdfs"

    scrape_pdfs(base_url, folder_name)
