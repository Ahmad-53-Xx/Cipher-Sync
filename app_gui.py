import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os

from CipherSync_Engine.cipher_sync import CipherSyncVault

# --- UI OVERHAUL: Sleek Dark/Green Cyber Aesthetic ---
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("green")  

class CipherSyncApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Cipher-Sync: Zero-Knowledge Steganographic Vault")
        self.geometry("750x600")
        self.resizable(True, True)

        # --- SIGNATURE LOGO INJECTION ---
        try:
            icon_img = tk.PhotoImage(file="./logo/53_logo.png")
            self.wm_iconphoto(False, icon_img)
        except Exception:
            pass 

        # --- MAIN HEADER ---
        self.header = ctk.CTkLabel(self, text="CIPHER-SYNC CORE ENGINE", font=("Courier New", 24, "bold"), text_color="#1DB954")
        self.header.pack(pady=(20, 5))
        self.sub_header = ctk.CTkLabel(self, text="Phase 3: DCT & Shamir's Distributed Vault", font=("Arial", 12), text_color="gray")
        self.sub_header.pack(pady=(0, 15))

        # Main Layout: 2 Tabs with stylized borders
        self.tabview = ctk.CTkTabview(self, width=680, height=450, corner_radius=10, border_width=1, border_color="#333333")
        self.tabview.pack(padx=20, pady=10)

        self.tab_hide = self.tabview.add("  [ LOCK DATA ]  ")
        self.tab_extract = self.tabview.add("  [ RECOVER DATA ]  ")

        self.build_hide_tab()
        self.build_extract_tab()

    def build_hide_tab(self):
        self.target_file_path = ctk.StringVar()
        self.carrier_image_path = ctk.StringVar()

        # --- FRAME 1: File Selection ---
        file_frame = ctk.CTkFrame(self.tab_hide, corner_radius=8, fg_color="#2b2b2b")
        file_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(file_frame, text="1. TARGET PAYLOAD:", font=("Courier New", 14, "bold")).pack(pady=(15,0))
        self.lbl_target = ctk.CTkLabel(file_frame, textvariable=self.target_file_path, text_color="#aaaaaa", font=("Arial", 11))
        self.lbl_target.pack(pady=(0,5))
        ctk.CTkButton(file_frame, text="Browse Target", command=self.browse_target, width=150, corner_radius=20).pack(pady=(0,15))

        ctk.CTkLabel(file_frame, text="2. CARRIER MATRIX (JPEG):", font=("Courier New", 14, "bold")).pack(pady=(5,0))
        self.lbl_carrier = ctk.CTkLabel(file_frame, textvariable=self.carrier_image_path, text_color="#aaaaaa", font=("Arial", 11))
        self.lbl_carrier.pack(pady=(0,5))
        ctk.CTkButton(file_frame, text="Browse Carrier", command=self.browse_carrier, width=150, corner_radius=20).pack(pady=(0,15))

        # --- FRAME 2: Security & Execution ---
        sec_frame = ctk.CTkFrame(self.tab_hide, corner_radius=8, fg_color="#1a1a1a", border_width=1, border_color="#8B0000")
        sec_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(sec_frame, text="3. MASTER ENCRYPTION KEY:", font=("Courier New", 14, "bold"), text_color="#ff4d4d").pack(pady=(15,5))
        self.entry_password_hide = ctk.CTkEntry(sec_frame, show="*", width=350, placeholder_text="Awaiting AES-256 key...", justify="center")
        self.entry_password_hide.pack(pady=5)

        self.btn_execute_hide = ctk.CTkButton(sec_frame, text="INITIALIZE VAULT INJECTION", font=("Courier New", 14, "bold"), 
                                              command=self.run_hide_pipeline, fg_color="#8B0000", hover_color="#5c0000", height=40, corner_radius=8)
        self.btn_execute_hide.pack(pady=(15, 20))


    def build_extract_tab(self):
        self.stego_image_path = ctk.StringVar()

        # --- FRAME 1: File Selection ---
        file_frame = ctk.CTkFrame(self.tab_extract, corner_radius=8, fg_color="#2b2b2b")
        file_frame.pack(fill="x", padx=20, pady=25)

        ctk.CTkLabel(file_frame, text="1. SECURED CARRIER IMAGE:", font=("Courier New", 14, "bold")).pack(pady=(20,0))
        self.lbl_stego = ctk.CTkLabel(file_frame, textvariable=self.stego_image_path, text_color="#aaaaaa", font=("Arial", 11))
        self.lbl_stego.pack(pady=(0,5))
        ctk.CTkButton(file_frame, text="Browse Secured Image", command=self.browse_stego, width=200, corner_radius=20).pack(pady=(0,20))

        # --- FRAME 2: Security & Execution ---
        sec_frame = ctk.CTkFrame(self.tab_extract, corner_radius=8, fg_color="#1a1a1a", border_width=1, border_color="#1DB954")
        sec_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(sec_frame, text="2. DECRYPTION KEY:", font=("Courier New", 14, "bold"), text_color="#1DB954").pack(pady=(20,5))
        self.entry_password_extract = ctk.CTkEntry(sec_frame, show="*", width=350, placeholder_text="Awaiting AES-256 key...", justify="center")
        self.entry_password_extract.pack(pady=5)

        self.btn_execute_extract = ctk.CTkButton(sec_frame, text="DECRYPT & RECOVER PAYLOAD", font=("Courier New", 14, "bold"), 
                                                 command=self.run_extract_pipeline, fg_color="#1DB954", text_color="black", hover_color="#14833b", height=40, corner_radius=8)
        self.btn_execute_extract.pack(pady=(15, 25))

    # --- Button Logic ---
    def browse_target(self):
        filename = filedialog.askopenfilename()
        if filename: self.target_file_path.set(filename)

    def browse_carrier(self):
        filename = filedialog.askopenfilename(filetypes=[("JPEG Images", "*.jpg *.jpeg"), ("All Files", "*.*")])
        if filename: self.carrier_image_path.set(filename)

    def browse_stego(self):
        filename = filedialog.askopenfilename(filetypes=[("JPEG Images", "*.jpg *.jpeg"), ("All Files", "*.*")])
        if filename: self.stego_image_path.set(filename)

    def run_hide_pipeline(self):
        target = self.target_file_path.get()
        carrier = self.carrier_image_path.get()
        password = self.entry_password_hide.get()

        if not target or not carrier or not password:
            messagebox.showerror("Error", "Missing required parameters.")
            return

        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vault_output")
        os.makedirs(output_dir, exist_ok=True)
        carrier_filename = os.path.basename(carrier)
        output_path = os.path.join(output_dir, f"SECURED_{carrier_filename}")

        try:
            vault = CipherSyncVault(master_password=password)
            vault.hide_file(target_filepath=target, carrier_image_path=carrier, output_image_path=output_path)
            messagebox.showinfo("Vault Locked", f"Payload secured in matrix.\n\nOutput:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Engine Failure", str(e))

    def run_extract_pipeline(self):
        stego = self.stego_image_path.get()
        password = self.entry_password_extract.get()

        if not stego or not password:
            messagebox.showerror("Error", "Missing required parameters.")
            return

        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vault_output")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "RECOVERED_SECRET_DATA.bin")

        try:
            vault = CipherSyncVault(master_password=password)
            vault.extract_file(stego_image_path=stego, output_filepath=output_path)
            messagebox.showinfo("Extraction Complete", f"Payload mathematically recovered.\n\nSaved to:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Security Lockout", f"Access Denied: Hash mismatch or corrupted matrix.\n\n{str(e)}")

if __name__ == "__main__":
    app = CipherSyncApp()
    app.mainloop()
