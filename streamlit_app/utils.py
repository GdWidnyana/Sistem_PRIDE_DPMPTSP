import bcrypt
import os

FILE_PATH = 'akun.txt'

def create_usertable():
    # Membuat file userstable.txt jika belum ada
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'w') as f:
            f.write('')  # Membuat file kosong

def add_userdata(username, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Mengecek apakah username sudah ada
    with open(FILE_PATH, 'r') as f:
        for line in f.readlines():
            stored_username, _ = line.strip().split(',')
            if stored_username == username:
                print(f"Username '{username}' sudah ada. Gunakan username lain.")
                return False
    
    # Menambahkan pengguna baru
    with open(FILE_PATH, 'a') as f:
        f.write(f"{username},{hashed_password}\n")
    print(f"User '{username}' berhasil ditambahkan dengan password hash: {hashed_password}")
    return True

def login_user(username, password):
    with open(FILE_PATH, 'r') as f:
        for line in f.readlines():
            stored_username, stored_password = line.strip().split(',')
            # Tambahkan debug print untuk memastikan data yang dibaca benar
            print(f"Checking username: '{stored_username}' with hash: '{stored_password}'")
            if stored_username == username:
                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    print("Password cocok, login berhasil!")
                    return True
                else:
                    print("Password tidak cocok.")
                    return False
    print("Username tidak ditemukan.")
    return False