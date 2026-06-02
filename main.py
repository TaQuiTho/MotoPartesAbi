import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Moto Partes Abi")
app.geometry("1200x700")

sidebar = ctk.CTkFrame(app, width=200, fg_color="#1C1C1E")
sidebar.pack(side="left", fill="y")

logo_label = ctk.CTkLabel(sidebar, text="Moto Partes Abi", font=ctk.CTkFont(size=14, weight="bold"), text_color="#FFFFFF")
logo_label.pack(pady=20, padx=10)

main_frame = ctk.CTkFrame(app, fg_color="#1a1a2e")
main_frame.pack(side="left", fill="both", expand=True)

app.mainloop()