import tkinter as tk
import tkinter.messagebox
import customtkinter as ctk
import os
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"
outputPath = "./output.txt"

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
            
        self.x = tk.StringVar(self)
        self.y = tk.StringVar(self)
        self.z = tk.StringVar(self)
        self.storedValues = {
            "X coordinate:" : self.x,
            "Y coordinate:" : self.y,
            "Z coordinate:" : self.z,
        }

        # Configure window
        self.title("Primitive GUI")
        self.geometry(f"{1000}x{625}")

        # Give weight to window container - allows for better window size adjustment
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        self.xFrame = ctk.CTkFrame(self)
        self.xFrame.grid(
            row=0,
            column=0,
            rowspan=1,
            columnspan=1,
            sticky='ew',
        )
        self.xFrame.grid_rowconfigure((0,1), weight=1)
        self.xFrame.grid_columnconfigure(0, weight=1)
        self.xLabel = ctk.CTkLabel(self.xFrame, text="Input the X coordinate of the particle")
        self.xLabel.grid(
            row=0,
            column=0
        )
        self.xEntry = ctk.CTkEntry(self.xFrame, textvariable=self.x, placeholder_text="Ex: 83.1")
        self.xEntry.grid(
            row=1,
            column=0
        )


        self.yFrame = ctk.CTkFrame(self)
        self.yFrame.grid(
            row=1,
            column=0,
            rowspan=1,
            columnspan=1,
            sticky='ew',
        )
        self.yFrame.grid_rowconfigure((0,1), weight=1)
        self.yFrame.grid_columnconfigure(0, weight=1)
        self.yLabel = ctk.CTkLabel(self.yFrame, text="Input the Y coordinate of the particle")
        self.yLabel.grid(
            row=0,
            column=0
        )
        self.yEntry = ctk.CTkEntry(self.yFrame, textvariable=self.y, placeholder_text="Ex: 83.1")
        self.yEntry.grid(
            row=1,
            column=0
        )


        self.zFrame = ctk.CTkFrame(self)
        self.zFrame.grid(
            row=2,
            column=0,
            rowspan=1,
            columnspan=1,
            sticky='ew',
        )
        self.zFrame.grid_rowconfigure((0,1), weight=1)
        self.zFrame.grid_columnconfigure(0, weight=1)
        self.zLabel = ctk.CTkLabel(self.zFrame, text="Input the Z coordinate of the particle")
        self.zLabel.grid(
            row=0,
            column=0
        )
        self.zEntry = ctk.CTkEntry(self.zFrame, textvariable=self.z, placeholder_text="Ex: 83.1")
        self.zEntry.grid(
            row=1,
            column=0
        )

        self.writeButtonFrame = ctk.CTkFrame(self)
        self.writeButtonFrame.grid(
            row=3,
            column=0,
            rowspan=1,
            columnspan=1,
            sticky='ew',
        )
        self.writeButtonFrame.grid_rowconfigure(0, weight=1)
        self.writeButtonFrame.grid_columnconfigure(0, weight=1)
        self.writeButton = ctk.CTkButton(self.writeButtonFrame, text="Submit", command=self.storeData)
        self.writeButton.grid(
            row=0,
            column=0
        )

    def storeData(self):
        with open(outputPath, 'w') as file:
            for key in self.storedValues.keys():
                file.write(key)
                file.write('\n')
                file.write(self.storedValues[key].get())
                self.storedValues[key].set("")
                file.write('\n')
            file.close()




if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()