import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from PIL import Image, ImageTk

local_app_data = os.getenv("LocalAppData")
app_data = os.getenv("appdata")
user_profile = os.getenv("USERPROFILE")
source_dirs = {
    "Zalo": os.path.join(local_app_data, "Programs", "Zalo"),
    "ZaloPC": os.path.join(local_app_data,"ZaloPC"),
    "ZaloData": os.path.join(app_data,"ZaloData"),
    "Zalo Received Files": os.path.join(user_profile, "Documents", "Zalo Received Files"),
    "zalo-updater": os.path.join(app_data,"zalo-updater"),
}


def copy_directory(source, target, progress_callback):
    try:
        total_size = get_dir_size(source)  
        copied_size = [0]  

        def copy_tree_with_progress(source_dir, target_dir):
            os.makedirs(target_dir, exist_ok=True)
            for item in os.listdir(source_dir):
                source_item = os.path.join(source_dir, item)
                target_item = os.path.join(target_dir, item)
                if os.path.isdir(source_item):
                     copy_tree_with_progress(source_item, target_item)
                else:
                    shutil.copy2(source_item, target_item)
                    copied_size[0] += os.path.getsize(source_item)
                    if total_size > 0:
                         progress_callback(copied_size[0] / total_size)
                    else :
                        progress_callback(0)
        copy_tree_with_progress(source, target)
    except Exception as e:
        raise e
def get_dir_size(path):

    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    return total_size
def create_link_copy_thread(path_z, progress_callback):

    try:
        for dir_name, source_path in source_dirs.items():
            if var_dict[dir_name].get():
                if not os.path.exists(source_path):
                    messagebox.showwarning("Cảnh báo", f"Thư mục {source_path} không tồn tại, bỏ qua thư mục này.")
                    var_dict[dir_name].set(False)
                    continue
                target_path = os.path.join(path_z, dir_name)
                messagebox.showinfo("Thông báo", f"Đang sao chép {source_path} đến {target_path}")

                copy_directory(source_path, target_path, progress_callback)

                old_source_path = source_path + "_old"
                os.rename(source_path, old_source_path)
                os.system(f'mklink /J "{source_path}" "{target_path}"')

        messagebox.showinfo("Thành công", "Sao chép và tạo liên kết hoàn tất. Vui lòng kiểm tra lại thư mục.- có thể bấm xóa file_old ở dưới")
        btn_delete_backup.config(state="normal")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")
    finally:
         progress_callback(1.0) 

def start_create_link_copy():
    """Hàm khởi tạo thread để thực hiện sao chép và tạo liên kết."""
    path_z = entry_path_z.get()
    
    if not path_z:
        messagebox.showwarning("Cảnh báo", "Vui lòng chọn đường dẫn đích trước.")
        return
    progress_bar.grid(row=len(source_dirs) + 3, column=1, sticky="ew", pady=10)
    progress_bar['value'] = 0
    progress_label.grid(row=len(source_dirs) + 4, column=1, pady=10)
    progress_label.config(text="Tiến trình: 0%")


    threading.Thread(target=create_link_copy_thread, args=(path_z,update_progress_bar), daemon=True).start()
    btn_start.config(state="disabled")
def mklink_backup_thread(path_z):
    """Hàm tạo liên kết và sao chép thư mục trong thread."""
    try:
        for dir_name, source_path in source_dirs.items():
            if var_dict[dir_name].get():
                target_path = os.path.join(path_z, dir_name)
                old_source_path = source_path + "_old"
                os.rename(source_path, old_source_path)
                os.system(f'mklink /J "{source_path}" "{target_path}"')

        messagebox.showinfo("Thành công", "tạo liên kết hoàn tất. Vui lòng kiểm tra lại thư mục.- có thể bấm xóa file_backup ở dưới")
        btn_delete_backup.config(state="normal")
    except Exception as e:
         messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")
def start_mklink_backup():
    path_z = entry_path_z.get()
    if not path_z:
        messagebox.showwarning("Cảnh báo", "Vui lòng chọn đường dẫn đích trước.")
        return
    threading.Thread(target=mklink_backup_thread, args=(path_z,), daemon=True).start()
    btn_mklink.config(state="disabled")
def delete_backup():
    try:
        for dir_name, source_path in source_dirs.items():
            if var_dict[dir_name].get():
                backup_path = source_path + "_old"
                if os.path.exists(backup_path):
                    shutil.rmtree(backup_path)
        messagebox.showinfo("Xóa thành công", "Các thư mục _old đã được xóa.")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi xóa backup: {e}")

def select_path_z():
    entry_path_z.delete(0, tk.END)
    entry_path_z.insert(0, filedialog.askdirectory())

def update_progress_bar(progress):
    progress_bar['value'] = int(progress * 100)
    progress_label.config(text=f"Tiến trình: {int(progress * 100)}%")
    if progress >= 1:
         btn_start.config(state="normal") 
         btn_mklink.config(state="normal")
         progress_bar.grid_forget()
         progress_label.grid_forget()
root = tk.Tk()
root.title("Công cụ chuyển thư mục mặc định zalo sang bộ nhớ khác")

try:
    image = Image.open("Dungtb.net.ico")
    photo = ImageTk.PhotoImage(image)
    root.iconphoto(False, photo)
except:
    pass
tk.Label(root, text="Đường dẫn thư mục zalo bạn chọn:").grid(row=0, column=0, padx=5, pady=5)
entry_path_z = tk.Entry(root, width=50)
entry_path_z.grid(row=0, column=1)
tk.Button(root, text="Chọn", command=select_path_z).grid(row=0, column=2, padx=5)

var_dict = {}
for i, dir_name in enumerate(source_dirs.keys(), start=1):
    var_dict[dir_name] = tk.BooleanVar()
    tk.Checkbutton(root, text=f"Thư mục {dir_name}", variable=var_dict[dir_name]).grid(row=i, column=1, sticky="w")

btn_start = tk.Button(root, text="Bắt đầu", command=start_create_link_copy)
btn_start.grid(row=len(source_dirs) + 1, column=1, pady=20)
btn_mklink = tk.Button(root, text="mklink lại thư mục đã sao chép", command=start_mklink_backup)
btn_mklink.grid(row=len(source_dirs) + 2, column=1, pady=20)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_label = tk.Label(root, text="Tiến trình: 0%")

btn_delete_backup = tk.Button(root, text="Xóa các file backup", command=delete_backup, state="disabled")
btn_delete_backup.grid(row=len(source_dirs) + 4, column=1, pady=20)


tk.Label(root, text="Ứng dụng được viết bởi dungtb.net", font=("Arial", 10, "italic")).grid(row=len(source_dirs) + 5, column=1, pady=10)

root.mainloop()
