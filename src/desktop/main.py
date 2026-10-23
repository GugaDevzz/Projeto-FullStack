import customtkinter as ctk

from paginas.pagina_login import CatatauLogin


def main():

    ctk.set_appearance_mode("blue")

    app = CatatauLogin()

    app.mainloop()


if __name__ == "__main__":
    main()  