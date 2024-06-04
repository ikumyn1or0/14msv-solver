import customtkinter


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("14 minesweeper variants solver")
        self.geometry("500x500")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.button = customtkinter.CTkButton(self, text="ボタン")
        self.button.grid(row=0, column=0, padx=20, pady=20, sticky="ew")


if __name__ == "__main__":
    app = App()
    app.mainloop()
