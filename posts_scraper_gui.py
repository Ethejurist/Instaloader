import subprocess
import streamlit as st
import tempfile
import os
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

def run_instaloader(username, password, hashtag, post_limit, output_dir):
    with tempfile.TemporaryDirectory() as tmpdirname:
        cmd = [
            "instaloader",
            f"--login={username}",
            f"--dirname-pattern={output_dir}",
            f"--count={post_limit}",
            f"#{hashtag}"
        ]
        try:
            result = subprocess.run(
                cmd,
                input=password.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(".json.xz"):
                        time.sleep(3)
            return result.stdout.decode() + "\n" + result.stderr.decode()
        except Exception as e:
            return str(e)

def launch_streamlit():
    st.set_page_config(
        page_title="Téléchargement Instagram par Hashtag",
        layout="centered"
    )

    st.markdown(
        """
        <style>
        body {
            background-color: #f7f7f9;
        }
        .stButton > button {
            background-color: #0f62fe;
            color: white;
            font-weight: 500;
            padding: 0.6rem 1.2rem;
            border-radius: 6px;
            border: none;
        }
        .stTextInput > div > div > input {
            background-color: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("Téléchargeur Instagram par Hashtag")
    st.write("Téléchargez des publications Instagram en utilisant vos identifiants.")

    username = st.text_input("Nom d'utilisateur Instagram")
    password = st.text_input("Mot de passe Instagram", type="password")
    hashtag = st.text_input("Hashtag (sans #)", value="nature")
    post_limit = st.number_input("Nombre de publications à télécharger", value=10, min_value=1)
    output_folder = st.text_input("Dossier de sauvegarde", value=str(Path.cwd() / "telechargements"))

    if st.button("Lancer le téléchargement"):
        if not username or not password or not hashtag:
            st.warning("Veuillez remplir tous les champs.")
        else:
            os.makedirs(output_folder, exist_ok=True)
            with st.spinner("Téléchargement en cours..."):
                result = run_instaloader(username, password, hashtag, post_limit, output_folder)
            st.success("Téléchargement terminé.")
            st.text_area("Résultat de la commande", result, height=250)
            st.markdown(f"Fichiers enregistrés dans : `{output_folder}`")

def launch_tkinter():
    def start_download():
        username = entry_username.get()
        password = entry_password.get()
        hashtag = entry_hashtag.get()
        limit = int(entry_limit.get())
        folder = entry_folder.get()

        if not username or not password or not hashtag or not folder:
            messagebox.showwarning("Champs manquants", "Veuillez remplir tous les champs.")
            return

        os.makedirs(folder, exist_ok=True)
        result = run_instaloader(username, password, hashtag, limit, folder)
        text_output.delete(1.0, tk.END)
        text_output.insert(tk.END, result)
        messagebox.showinfo("Succès", "Téléchargement terminé.")

    def browse_folder():
        folder = filedialog.askdirectory()
        if folder:
            entry_folder.delete(0, tk.END)
            entry_folder.insert(0, folder)

    root = tk.Tk()
    root.title("Téléchargeur Instagram")
    root.geometry("600x500")
    root.configure(bg="#f0f2f5")

    style = ttk.Style()
    style.configure("TLabel", font=("Helvetica", 11), background="#f0f2f5")
    style.configure("TEntry", font=("Helvetica", 11))
    style.configure("TButton", font=("Helvetica", 11), padding=6)

    frm = ttk.Frame(root, padding=20)
    frm.pack(fill="both", expand=True)

    ttk.Label(frm, text="Nom d'utilisateur Instagram :").grid(row=0, column=0, sticky="w", pady=5)
    entry_username = ttk.Entry(frm, width=40)
    entry_username.grid(row=0, column=1, pady=5)

    ttk.Label(frm, text="Mot de passe :").grid(row=1, column=0, sticky="w", pady=5)
    entry_password = ttk.Entry(frm, show="*", width=40)
    entry_password.grid(row=1, column=1, pady=5)

    ttk.Label(frm, text="Hashtag (sans #) :").grid(row=2, column=0, sticky="w", pady=5)
    entry_hashtag = ttk.Entry(frm, width=40)
    entry_hashtag.grid(row=2, column=1, pady=5)

    ttk.Label(frm, text="Nombre de publications :").grid(row=3, column=0, sticky="w", pady=5)
    entry_limit = ttk.Entry(frm, width=40)
    entry_limit.insert(0, "10")
    entry_limit.grid(row=3, column=1, pady=5)

    ttk.Label(frm, text="Dossier de sauvegarde :").grid(row=4, column=0, sticky="w", pady=5)
    entry_folder = ttk.Entry(frm, width=40)
    entry_folder.grid(row=4, column=1, pady=5)
    ttk.Button(frm, text="Parcourir...", command=browse_folder).grid(row=4, column=2, padx=5)

    ttk.Button(frm, text="Lancer le téléchargement", command=start_download).grid(row=5, column=0, columnspan=3, pady=15)

    text_output = tk.Text(frm, height=10, font=("Courier", 10))
    text_output.grid(row=6, column=0, columnspan=3, pady=10, sticky="nsew")

    frm.rowconfigure(6, weight=1)
    frm.columnconfigure(1, weight=1)

    root.mainloop()

if __name__ == "__main__":
    import sys
    if "streamlit" in sys.argv[0].lower():
        launch_streamlit()
    else:
        launch_tkinter()
