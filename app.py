from flask import Flask, render_template, request, send_file
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import pandas as pd
import os
import time
import dropbox

app = Flask(__name__)

# 🔹 Dropbox Access Token (Replace with your actual token)
DROPBOX_ACCESS_TOKEN = "sl.u.AFlZdR-SRjN-O3txhZmLTNWfn459AoK5MAyesvE7J0q0IUDShBkF0RPKJOndvj313BoirPLMHsWLM0F4VbDVlmeU4hzY2l1iL0O_WupFllUEy8qqB1wJmf51f-28HLU_2zJwgXQ18fwXj9RB-KPBlLTUjBVzW0a38a4E7l4x604m-vLwLlLzTKUOOmnEZHA4wbLph9VWl_xJ1hjyJCGx3rKpGOLX9rF1HRNbqeA10pvGaU_AnERUE3cW24o_hRqBGwTVU_ZSHMPILMEK3WuwPwTk6NXJeFCWy4Wa6rNTtrnIj7l2KcS2iU5yzbu8T0jMUFoaxvasqI-uyvXhjT310LOPh4Hx3buBcDGZrRoGvCycU0bkRfpqgK53xb_b61xEKl4GZhEP88Xv2pBjMDhDV3zfx7UdWVqfHAVgVKaVmakl9F0IMFGqm9s5riU6gx1KalcFkY0bDF2Nt90p0j3-W2_s5IFdo1r02nqW1I6oZTEbdSj9XpnivlFF2nlnETCpFD-YbQzGEmenJkNfkXiHhVVUQQqw_lmrIZ7MFJxy_-OLsfiQUavXzzBTVQy41OjZmrDgUmS7LsQi5zI5FgPcFt3iMhl-coFguIyg6EdwA7snoJlgPavSS4NTcorEcB3nao71yt_y8jgv9gRwa4wMU_J9I53KHVCwW503F-bvr5DODBhH4q9wHOAP6d6OGfFhVo6PFi0m1HMYEVUBjMwtf55L7G6xhNv3ZJFQrGO2fKcX78XR5UEdkuNEyEz2fsiJJtWXhPJdr5wGLGAf_KjSYp6FGeIYSR1jxMs_tVoce6Vd2yjsDqj5aMx4jSrFnFOep_zmOpIbqGU-19YBeOziKOJImkQwFMwy_RO0YZq4I__v39rE66icCe2STCV-BJe96lnrZNWaXSnaTu4SNxXPxX8yU709oPMTm4_pyaGv66IvtQ26GhqeOs4VgO1Tu4yzwnJYwqnKw_DSUW3CvBztRHWDggFDPhFfme3GxwgqWkxE4ZTOPXL2W4WT2GFz7pCUDycPBWhOx_xqUg1bVkh9VdmTSmycGswW3dHbnUshNBjOkWHEO8XFeNI8Sf4dGxa3NUkw4BDFXtsuAIJkX8-bC3YfNE5abryfSQJO8MitBOMRzDtNZJHfSvWunPPwEYc-fYIlRMGgfaC3dhfF51amEMtdN3uR0Ixj9oTf1jnfMx1HtOkhl15UVGzd0s8vCcTeI-jeKu9odmtEeuTFkRrMsotKf2qZiO3CyR3JgpOiclW2g0lB-0lAS5BqakSG8Iu3hDXrmzio32IagJkoPKUY1Saix4nsyr7zruJMiF2gNZFvGiNCbLhIrOJjNjPvLJ_X4tvXpD9moi566xot2qlTXFtznjWkFC7q4abIOmVdBeXdkg-4YEA4a4brrPSn7bUbyiL2L1CxAv5YiaAxfjXcNWkmaqeUymRQ71H6KvyG6F8CtvlatvsJgRZxST-LYW93EVc"
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

UPLOAD_FOLDER = "uploads"
ENCRYPTED_FOLDER = "encrypted_files"
DECRYPTED_FOLDER = "decrypted_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)
os.makedirs(DECRYPTED_FOLDER, exist_ok=True)

# 🔹 AES Key (16 bytes)
KEY = b'Sixteen byte key'

# 🔹 Encrypt Data
def encrypt_data(data, key):
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    return ciphertext.hex(), cipher.iv.hex()

# 🔹 Decrypt Data
def decrypt_data(ciphertext, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, bytes.fromhex(iv))
    decrypted_data = unpad(cipher.decrypt(bytes.fromhex(ciphertext)), AES.block_size)
    return decrypted_data.decode('utf-8')

# 🔹 Upload File to Dropbox
def upload_to_dropbox(file_path, dropbox_path):
    with open(file_path, "rb") as f:
        dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))
    print(f"✅ Uploaded {file_path} to Dropbox at {dropbox_path}")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            
            # 🔹 Load Dataset
            df = pd.read_csv(file_path, encoding="latin-1")
            
            # 🔹 Encrypt Email Column
            start_time = time.time()
            df['encrypted_email'], df['iv'] = zip(*df['email'].apply(lambda x: encrypt_data(x, KEY)))
            encryption_time = time.time() - start_time
            print(f"🔒 Encryption Time: {encryption_time:.4f} seconds")

            # 🔹 Save Encrypted Dataset
            encrypted_file_path = os.path.join(ENCRYPTED_FOLDER, "encrypted_" + file.filename)
            df.to_csv(encrypted_file_path, index=False)

            # 🔹 Upload to Dropbox
            upload_to_dropbox(encrypted_file_path, "/encrypted_" + file.filename)

            # 🔹 Decrypt Data
            start_time = time.time()
            df["decrypted_email"] = df.apply(lambda row: decrypt_data(row["encrypted_email"], KEY, row["iv"]), axis=1)
            decryption_time = time.time() - start_time
            print(f"🔓 Decryption Time: {decryption_time:.4f} seconds")

            # 🔹 Save Decrypted Dataset
            decrypted_file_path = os.path.join(DECRYPTED_FOLDER, "decrypted_" + file.filename)
            df.to_csv(decrypted_file_path, index=False)

            # 🔹 Upload Decrypted File to Dropbox
            upload_to_dropbox(decrypted_file_path, "/decrypted_" + file.filename)

            return render_template("index.html", encrypted=True, decrypted=True, 
                                   enc_file="encrypted_" + file.filename,
                                   dec_file="decrypted_" + file.filename)
    
    return render_template("index.html", encrypted=False, decrypted=False)

@app.route("/download/<filename>")
def download(filename):
    if "encrypted_" in filename:
        path = os.path.join(ENCRYPTED_FOLDER, filename)
    elif "decrypted_" in filename:
        path = os.path.join(DECRYPTED_FOLDER, filename)
    else:
        return "File not found", 404
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
