import customtkinter as ctk
from interface import InterfaceGrafica

if __name__ == "__main__":
    # Define o tema (System = segue o Windows, Dark = Escuro, Light = Claro)
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    raiz = ctk.CTk()
    raiz.title("Guardião da Planilha")
    app = InterfaceGrafica(raiz)
    raiz.mainloop()
    
    