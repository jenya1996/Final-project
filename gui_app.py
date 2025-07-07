import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class NovaAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Nova Simulation Analyzer")
        self.root.geometry("900x700")

        self.df = None

        # Load file
        self.load_button = tk.Button(root, text="Load Data File", command=self.load_file)
        self.load_button.pack(pady=5)

        # Column options
        self.column_frame = tk.Frame(root)
        self.column_frame.pack(pady=10)

        tk.Label(self.column_frame, text="X-axis:").grid(row=0, column=0)
        tk.Label(self.column_frame, text="Y-axis:").grid(row=0, column=2)

        self.x_column = ttk.Combobox(self.column_frame, width=30)
        self.y_column = ttk.Combobox(self.column_frame, width=30)
        self.x_column.grid(row=0, column=1, padx=5)
        self.y_column.grid(row=0, column=3, padx=5)

        # Plot button
        self.plot_button = tk.Button(root, text="Plot Graph", command=self.plot_data)
        self.plot_button.pack(pady=5)

        # Save CSV
        self.save_button = tk.Button(root, text="Save Filtered Data to CSV", command=self.save_to_csv)
        self.save_button.pack(pady=5)

        # Plot area
        self.plot_frame = tk.Frame(root)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)

    def load_file(self):  # ✅ Indented into the class
        choice = messagebox.askquestion("Load Mode", "Do you want to select a directory?\nClick 'Yes' for directory, 'No' for multiple files.")

        all_files = []

        if choice == "yes":
            folder_path = filedialog.askdirectory()
            if folder_path:
                import os
                all_files = [os.path.join(folder_path, f)
                             for f in os.listdir(folder_path)
                             if f.endswith((".txt", ".csv"))]
        else:
            all_files = filedialog.askopenfilenames()

        if not all_files:
            return

        try:
            combined_df = pd.DataFrame()
            for file_path in all_files:
                if file_path.endswith(".csv"):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_csv(file_path, delim_whitespace=True)
                combined_df = pd.concat([combined_df, df], ignore_index=True)

            combined_df = combined_df.dropna(how='all', axis=1)
            self.df = combined_df

            columns = list(self.df.columns)
            self.x_column["values"] = columns
            self.y_column["values"] = columns

            messagebox.showinfo("Success", f"Loaded {len(all_files)} files. {len(self.df)} rows total.")
        except Exception as e:
            messagebox.showerror("Error Loading Files", str(e))


    def plot_data(self):
        if self.df is None:
            messagebox.showwarning("No Data", "Please load a file first.")
            return

        x_col = self.x_column.get()
        y_col = self.y_column.get()
        if not x_col or not y_col:
            messagebox.showwarning("Select Columns", "Please select both X and Y columns.")
            return

        try:
            fig, ax = plt.subplots(figsize=(6, 4))
            x = self.df[x_col]
            y = self.df[y_col]
            ax.plot(x, y, marker='o', linestyle='-')
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(f"{y_col} vs {x_col}")

            for widget in self.plot_frame.winfo_children():
                widget.destroy()

            canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            messagebox.showerror("Plot Error", str(e))

    def save_to_csv(self):
        if self.df is None:
            messagebox.showwarning("No Data", "Load data before saving.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv")])
        if path:
            try:
                self.df.to_csv(path, index=False)
                messagebox.showinfo("Saved", f"Data saved to {path}")
            except Exception as e:
                messagebox.showerror("Save Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = NovaAnalyzerGUI(root)
    root.mainloop()
