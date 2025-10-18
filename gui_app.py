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

        # Theme
        self.style = ttk.Style()
        self.style.theme_use("clam") # "clam", "alt", "default", "classic"

        self.df = None
        self.visible_columns = []   # if empty => show all columns

        # Create a Notebook (tab container)
        notebook = ttk.Notebook(root)
        notebook.pack(expand=True, fill="both")

        # Create frames for each tab
        tab1 = ttk.Frame(notebook)
        tab2 = ttk.Frame(notebook)
        tab3 = ttk.Frame(notebook)

        # Add tabs
        notebook.add(tab1, text="Data")
        notebook.add(tab2, text="Analysis")
        notebook.add(tab3, text="Visualization")

        # region data tab --------------

        # Load file button
        self.load_button = ttk.Button(tab1, text="Load Data File", command=self.load_file)
        self.load_button.pack(pady=5)

        # Save CSV button
        self.save_button = ttk.Button(tab1, text="Save Filtered Data to CSV", command=self.save_to_csv)
        self.save_button.pack(pady=5)

        # Save h5 button
        self.save_h5_button = ttk.Button(tab1, text="Save Filtered Data to H5", command=self.save_to_h5)
        self.save_h5_button.pack(pady=5)

        # Save parquet (snappy) button
        self.save_parquet_button = ttk.Button(tab1, text="Save Filtered Data to Parquet", command=self.save_to_parquet)
        self.save_parquet_button.pack(pady=5)

        #endregion

        # region Analysis tab --------------

        # Row range controls
        range_bar = ttk.Frame(tab2)
        range_bar.pack(fill=tk.X, pady=(6, 4))

        ttk.Label(range_bar, text="Start row:").pack(side=tk.LEFT, padx=(0, 6))
        self.start_var = tk.IntVar(value=1)  # 1-based
        self.start_spin = tk.Spinbox(range_bar, from_=1, to=1, textvariable=self.start_var, width=8)
        self.start_spin.pack(side=tk.LEFT)

        ttk.Label(range_bar, text="End row:").pack(side=tk.LEFT, padx=(12, 6))
        self.end_var = tk.IntVar(value=1000)
        self.end_spin = tk.Spinbox(range_bar, from_=1, to=1, textvariable=self.end_var, width=8)
        self.end_spin.pack(side=tk.LEFT)

        apply_btn = ttk.Button(range_bar, text="Apply", command=self.apply_row_range)
        apply_btn.pack(side=tk.LEFT, padx=12)

        self.row_info = ttk.Label(range_bar, text="", foreground="#666")
        self.row_info.pack(side=tk.LEFT, padx=8)

        # Filter button opens a modal with checkboxes
        filter_btn = ttk.Button(range_bar, text="Filter", command=self.open_filter_dialog)
        filter_btn.pack(side=tk.LEFT, padx=4)

        # Table - Data Preview
        self.table_frame = ttk.Frame(tab2)
        self.table_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        # Use grid for better scroll integration
        self.table = ttk.Treeview(self.table_frame, columns=(), show="headings")

        y_scroll = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.table.yview)
        x_scroll = ttk.Scrollbar(self.table_frame, orient=tk.HORIZONTAL, command=self.table.xview)

        self.table.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        # Layout with grid
        self.table.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        # Make table expand
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        # Optional: Enter applies the range
        self.start_spin.bind("<Return>", lambda e: self.apply_row_range())
        self.end_spin.bind("<Return>", lambda e: self.apply_row_range())

        #endregion

        # region Visualization tab (single ncyc) --------------

        self.column_frame = ttk.Frame(tab3)
        self.column_frame.pack(fill=tk.X, pady=10)

        ttk.Label(self.column_frame, text="X-axis:").grid(row=0, column=0, padx=(0,4))
        ttk.Label(self.column_frame, text="Y-axis:").grid(row=0, column=2, padx=(12,4))

        self.x_column = ttk.Combobox(self.column_frame, width=30, state="readonly")
        self.y_column = ttk.Combobox(self.column_frame, width=30, state="readonly")
        self.x_column.grid(row=0, column=1, padx=(0,8))
        self.y_column.grid(row=0, column=3, padx=(0,8))

        self.ncyc_var = tk.StringVar()
        self.ncyc_entry = ttk.Entry(self.column_frame, width=12, textvariable=self.ncyc_var)
        self.ncyc_entry.grid(row=0, column=5, padx=(8, 4))
        ttk.Label(self.column_frame, text="ncyc:").grid(row=0, column=4, padx=(12, 0))

        self.plot_one_btn = ttk.Button(self.column_frame, text="Plot selected ncyc", command=self.plot_single_ncyc)
        self.plot_one_btn.grid(row=0, column=6, padx=(8, 0))

        self.split = ttk.PanedWindow(tab3, orient=tk.VERTICAL)
        self.split.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        self.top_pane = ttk.Frame(self.split)
        self.bot_pane = ttk.Frame(self.split)
        self.split.add(self.top_pane, weight=1)
        self.split.add(self.bot_pane, weight=1)

        # Set an initial 50/50 split after the widget is realized
        self._sash_inited = False
        def _on_split_configure(e):
            if not self._sash_inited and e.height > 0:
                try:
                    self.split.sashpos(0, e.height // 2)
                    self._sash_inited = True
                except Exception:
                    pass
        self.split.bind("<Configure>", _on_split_configure)

# endregion

    # region functions --------------
    def show_table(self, df, start=0, end=None, cols=None):
        """Render df rows [start:end] into the Treeview; show only 'cols' if provided."""
        n = len(df)
        if n == 0:
            # Clear rows and headings safely
            try:
                self.table.delete(*self.table.get_children())
            except Exception:
                pass
            self.table["columns"] = ()
            self.table["displaycolumns"] = ()
            self.row_info.config(text="No rows")
            return

        # sanitize row range
        start = max(0, min(start, n - 1))
        if end is None:
            end = n
        end = max(start + 1, min(end, n))

        # choose columns
        if cols is None or len(cols) == 0:
            cols = list(df.columns)
        else:
            cols = [c for c in cols if c in df.columns]
            if not cols:
                cols = list(df.columns)

        # ---- SAFE RESET SEQUENCE ----
        # 1) Clear all rows
        try:
            self.table.delete(*self.table.get_children())
        except Exception:
            pass

        # 2) Reset columns before touching headings (prevents 'Invalid column index')
        self.table["show"] = "headings"
        self.table["columns"] = cols
        self.table["displaycolumns"] = cols

        # 3) Now set headings/column options
        for col in cols:
            self.table.heading(col, text=col)
            self.table.column(col, width=100, minwidth=40, stretch=False, anchor="w")

        # Insert rows
        view = df.iloc[start:end][cols]
        for row in view.itertuples(index=False, name=None):
            self.table.insert("", tk.END, values=[("" if pd.isna(v) else v) for v in row])

        self.row_info.config(text=f"Showing rows {start+1}–{end} of {n}")

    def apply_row_range(self):
        if self.df is None:
            messagebox.showwarning("No Data", "Load data first.")
            return
        try:
            start_1b = int(self.start_var.get())
            end_1b = int(self.end_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Start/End must be integers.")
            return

        n = len(self.df)
        start_1b = max(1, min(start_1b, n))
        end_1b = max(1, min(end_1b, n))
        if start_1b > end_1b:
            start_1b, end_1b = end_1b, start_1b

        self.show_table(self.df, start=start_1b - 1, end=end_1b)

    def _populate_column_filter(self, columns):
        """Fill the listbox with column names and select all by default."""
        self.col_listbox.delete(0, tk.END)
        for c in columns:
            self.col_listbox.insert(tk.END, c)
        # select all
        self.col_listbox.select_set(0, tk.END)

    def _col_select_all(self):
        self.col_listbox.select_set(0, tk.END)

    def _col_clear(self):
        self.col_listbox.select_clear(0, tk.END)

    def _selected_columns(self):
        """Return list of selected column names; empty list means 'all'."""
        if self.df is None or self.col_listbox.size() == 0:
            return []
        idxs = self.col_listbox.curselection()
        if not idxs:
            return []
        return [self.col_listbox.get(i) for i in idxs]

    def apply_column_filter(self):
        """Re-render the table with only the chosen columns."""
        if self.df is None:
            messagebox.showwarning("No Data", "Load data first.")
            return
        sel = self._selected_columns()
        # Use all columns if none explicitly selected
        cols = sel if sel else list(self.df.columns)

        # Respect current start/end row range
        n = len(self.df)
        try:
            start_1b = max(1, min(int(self.start_var.get()), n))
            end_1b = max(1, min(int(self.end_var.get()), n))
            if start_1b > end_1b:
                start_1b, end_1b = end_1b, start_1b
        except Exception:
            start_1b, end_1b = 1, min(1000, n)

        start0, end0 = start_1b - 1, end_1b
        # Render only selected columns
        self.show_table(self.df.loc[self.df.index[start0:end0], cols], start=0, end=None)

    def _load_and_clean_files(self, all_files):
        """
        Load multiple files and:
        - coerce all columns to numeric (errors='coerce')
        - drop rows that are all-NaN across numeric columns
        - after the first file, drop ncyc==1 and ncyc==2 (to avoid repeats)
        - renumber ncyc to be continuous across files
        - make 'time' continuous if present
        Returns a single combined DataFrame.
        """
        import os

        combined = pd.DataFrame()
        current_max_ncyc = 0
        last_time_value = 0.0

        for i, file_path in enumerate(all_files):
            # Load
            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_csv(file_path, delim_whitespace=True)

            # Coerce all columns to numeric where possible
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            # Drop rows that are all-NaN across numeric columns
            # (keeps text columns if any, but typically everything is numeric in your files)
            numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
            if numeric_cols:
                df = df.dropna(how="all", subset=numeric_cols)

            # Ensure ncyc exists and numeric if present
            if "ncyc" in df.columns:
                # Remove first cycles from every file except the first, matching the notebook logic
                if i != 0:
                    df = df[~df["ncyc"].isin([1, 2])]

                # Renumber ncyc to continue across files
                # (convert to ints only at the end to avoid Int64/NaN fragility mid-pipeline)
                df["ncyc"] = pd.to_numeric(df["ncyc"], errors="coerce")
                # After filtering, drop any rows without ncyc
                df = df.dropna(subset=["ncyc"])
                df["ncyc"] = df["ncyc"].astype(int)

                k = 2 if i != 0 else 0

                df["ncyc"] = df["ncyc"].astype(int) + int(current_max_ncyc) - k
                if not df["ncyc"].empty:
                    current_max_ncyc = int(df["ncyc"].max())

            # Make time continuous if present
            if "time" in df.columns:
                df["time"] = pd.to_numeric(df["time"], errors="coerce")
                df = df.dropna(subset=["time"])
                df["time"] = df["time"] + last_time_value
                if not df["time"].empty:
                    last_time_value = float(df["time"].iloc[-1])

            combined = pd.concat([combined, df], ignore_index=True)

        # Optional: strict column cleanup (drop columns that are entirely NaN across the combined df)
        combined = combined.dropna(how="all", axis=1)

        # Make sure ncyc is Int64 (nullable) for GUI sorting but without floats
        if "ncyc" in combined.columns:
            combined["ncyc"] = pd.to_numeric(combined["ncyc"], errors="coerce").astype("Int64")

        return combined

    def load_file(self):
        choice = messagebox.askquestion(
            "Load Mode",
            "Do you want to select a directory?\nClick 'Yes' for directory, 'No' for multiple files."
        )

        all_files = []
        if choice == "yes":
            folder_path = filedialog.askdirectory()
            if folder_path:
                import os
                all_files = [
                    os.path.join(folder_path, f)
                    for f in os.listdir(folder_path)
                    if f.endswith((".txt", ".csv"))
                ]
        else:
            all_files = filedialog.askopenfilenames()

        if not all_files:
            return

        try:
            # >>> NEW: use the cleaner <<<
            combined_df = self._load_and_clean_files(all_files)
            if combined_df.empty:
                messagebox.showwarning("No Rows", "No valid rows after cleaning.")
                return

            self.df = combined_df

            # Update X/Y pickers
            columns = list(self.df.columns)

            # Exclude 'ncyc' from X/Y choices
            cols_no_ncyc = [c for c in columns if c.lower() != "ncyc"]

            self.x_column["values"] = cols_no_ncyc
            self.y_column["values"] = cols_no_ncyc

            # Set defaults (first two non-ncyc columns if available)
            if cols_no_ncyc:
                self.x_column.set(cols_no_ncyc[0])
                self.y_column.set(cols_no_ncyc[1] if len(cols_no_ncyc) > 1 else cols_no_ncyc[0])

            # Keep track of all columns for table rendering
            self.visible_columns = columns[:]

            # Row range controls + initial render
            n = len(self.df)
            self.start_spin.config(from_=1, to=max(1, n))
            self.end_spin.config(from_=1, to=max(1, n))
            self.start_var.set(1)
            self.end_var.set(min(1000, n))
            self.show_table(self.df, start=0, end=min(1000, n), cols=self.visible_columns)

            messagebox.showinfo(
                "Success",
                f"Loaded {len(all_files)} files. {len(self.df)} rows after cleaning & renumbering."
            )
        except Exception as e:
            messagebox.showerror("Error Loading Files", str(e))
    
    def save_to_h5(self):
        if self.df is None:
            messagebox.showwarning("No Data", "Load data before saving.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".h5",
                                             filetypes=[("H5 files", "*.h5")])
        if path:
            try:
                self.df.to_hdf(path, key='df', mode='w')
                messagebox.showinfo("Saved", f"Data saved to {path}")
            except Exception as e:
                messagebox.showerror("Save Error", str(e))
    
    def save_to_parquet(self):
        if self.df is None:
            messagebox.showwarning("No Data", "Load data before saving.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".parquet",
                                             filetypes=[("Parquet files", "*.parquet")])
        if path:
            try:
                self.df.to_parquet(path, index=False)
                messagebox.showinfo("Saved", f"Data saved to {path}")
            except Exception as e:
                messagebox.showerror("Save Error", str(e))

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
            # Clear previous content in both panes
            for pane in (self.top_pane, self.bot_pane):
                for w in pane.winfo_children():
                    w.destroy()

            def build_pane(parent, x_data, y_data, xlabel, ylabel, title, default_pdf, default_jpg):
                # Grid: row 0 = canvas (expands), row 1 = buttons (fixed)
                parent.grid_rowconfigure(0, weight=1)
                parent.grid_columnconfigure(0, weight=1)

                canvas_frame = ttk.Frame(parent)
                canvas_frame.grid(row=0, column=0, sticky="nsew")

                # Clean numeric conversion with pairwise drop of NaNs
                x = pd.to_numeric(x_data, errors="coerce")
                y = pd.to_numeric(y_data, errors="coerce")
                mask = ~(x.isna() | y.isna())
                x, y = x[mask], y[mask]
                if x.empty or y.empty:
                    raise ValueError("Selected columns contain no numeric data to plot.")

                # Responsive figure (no fixed figsize)
                fig, ax = plt.subplots()
                ax.plot(x, y, marker='o', linestyle='-')
                ax.set_xlabel(xlabel)
                ax.set_ylabel(ylabel)
                ax.set_title(title)

                canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
                cw = canvas.get_tk_widget()
                cw.pack(fill=tk.BOTH, expand=True)
                canvas.draw()

                # Redraw on pane resize so it always fits
                canvas_frame.bind("<Configure>", lambda e: canvas.draw())

                # Buttons row under the plot
                btns = ttk.Frame(parent)
                btns.grid(row=1, column=0, sticky="ew", pady=(4, 8))
                ttk.Button(btns, text="Save as PDF",
                        command=lambda: self._save_figure(fig, default_pdf)).pack(side=tk.LEFT, padx=4)
                ttk.Button(btns, text="Save as JPG",
                        command=lambda: self._save_figure(fig, default_jpg)).pack(side=tk.LEFT, padx=4)

            # Top: regular (Y vs X)
            build_pane(
                self.top_pane,
                self.df[x_col], self.df[y_col],
                x_col, y_col, f"{y_col} vs {x_col}",
                f"{y_col}_vs_{x_col}.pdf", f"{y_col}_vs_{x_col}.jpg"
            )

            # Bottom: flipped (X vs Y)
            build_pane(
                self.bot_pane,
                self.df[y_col], self.df[x_col],
                y_col, x_col, f"{x_col} vs {y_col} (Flipped)",
                f"{x_col}_vs_{y_col}_flipped.pdf", f"{x_col}_vs_{y_col}_flipped.jpg"
            )

        except Exception as e:
            messagebox.showerror("Plot Error", str(e))

    def _save_figure(self, fig, default_name):
        """Helper to save matplotlib figure as PDF or JPG."""
        path = filedialog.asksaveasfilename(initialfile=default_name,
                                            filetypes=[("PDF files", "*.pdf"),
                                                       ("JPEG files", "*.jpg")])
        if path:
            try:
                fig.savefig(path, bbox_inches='tight')
                messagebox.showinfo("Saved", f"Figure saved to {path}")
            except Exception as e:
                messagebox.showerror("Save Error", str(e))

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

    def open_filter_dialog(self):
        if self.df is None or self.df.empty:
            messagebox.showwarning("No Data", "Load data first.")
            return

        cols = list(self.df.columns)
        # Current selection (default = all)
        current = set(self.visible_columns) if self.visible_columns else set(cols)

        win = tk.Toplevel(self.root)
        win.title("Select columns")
        win.transient(self.root)
        win.grab_set()  # modal
        win.resizable(False, True)

        container = ttk.Frame(win, padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text="Choose columns to display:").pack(anchor="w", pady=(0, 6))

        # Scrollable area for many columns
        canvas = tk.Canvas(container, highlightthickness=0)
        inner = ttk.Frame(canvas)
        yscroll = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=yscroll.set)

        canvas.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")

        # Create a window inside canvas for checkboxes
        canvas.create_window((0, 0), window=inner, anchor="nw")

        # Checkbox vars per column
        vars_by_col = {}
        for c in cols:
            var = tk.BooleanVar(value=(c in current))
            cb = ttk.Checkbutton(inner, text=c, variable=var)
            cb.pack(anchor="w")
            vars_by_col[c] = var

        # Make scroll region update
        def _on_configure(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        inner.bind("<Configure>", _on_configure)

        # Buttons
        btns = ttk.Frame(container)
        btns.pack(fill="x", pady=(10, 0))
        def on_accept():
            selected = [c for c, v in vars_by_col.items() if v.get()]
            if not selected:
                messagebox.showerror("No Columns", "Please select at least one column.")
                return
            self.visible_columns = selected
            # Re-render table with current row range
            n = len(self.df)
            try:
                start_1b = max(1, min(int(self.start_var.get()), n))
                end_1b = max(1, min(int(self.end_var.get()), n))
                if start_1b > end_1b:
                    start_1b, end_1b = end_1b, start_1b
            except Exception:
                start_1b, end_1b = 1, min(1000, n)
            self.show_table(self.df, start=start_1b-1, end=end_1b, cols=self.visible_columns)
            win.destroy()

        def on_cancel():
            win.destroy()

        accept_btn = ttk.Button(btns, text="Accept", command=on_accept)
        cancel_btn = ttk.Button(btns, text="Cancel", command=on_cancel)
        cancel_btn.pack(side="right")
        accept_btn.pack(side="right", padx=(0, 8))

    def plot_single_ncyc(self):
        if self.df is None or self.df.empty:
            messagebox.showwarning("No Data", "Load data first.")
            return

        # Get and validate ncyc value
        raw = self.ncyc_var.get().strip()
        if not raw:
            messagebox.showwarning("ncyc required", "Please type an ncyc value.")
            return

        try:
            # allow floats/strings but cast to int (your data stores ncyc as ints)
            target_ncyc = int(float(raw))
        except Exception:
            messagebox.showerror("Invalid ncyc", f"'{raw}' is not a valid integer.")
            return

        # Ensure columns are selected and are not 'ncyc'
        xcol = self.x_column.get()
        ycol = self.y_column.get()
        if not xcol or not ycol:
            messagebox.showwarning("Pick columns", "Please select X and Y columns.")
            return
        if xcol.lower() == "ncyc" or ycol.lower() == "ncyc":
            messagebox.showwarning("Invalid column", "The X and Y columns cannot be 'ncyc'.")
            return
        if xcol not in self.df.columns or ycol not in self.df.columns:
            messagebox.showwarning("Missing columns", "Selected columns not found in DataFrame.")
            return

        # Filter the chosen ncyc
        if "ncyc" not in self.df.columns:
            messagebox.showerror("Missing 'ncyc'", "Column 'ncyc' is not in the data.")
            return

        # Handle nullable Int64 vs int
        subset = self.df[self.df["ncyc"].astype("Int64") == target_ncyc].copy()

        if subset.empty:
            messagebox.showinfo("No Rows", f"No rows found for ncyc = {target_ncyc}.")
            return

        # Keep numeric only for plotting and drop NaNs
        subset[xcol] = pd.to_numeric(subset[xcol], errors="coerce")
        subset[ycol] = pd.to_numeric(subset[ycol], errors="coerce")
        subset = subset.dropna(subset=[xcol, ycol])

        if subset.empty:
            messagebox.showinfo("No Plottable Data", f"ncyc {target_ncyc} has no valid numeric data for X='{xcol}', Y='{ycol}'.")
            return

        # Sort by X for nicer line plots
        subset = subset.sort_values(by=xcol)

        # Draw on the bottom pane canvas (reuse your existing Figure/Canvas if you have one)
        fig = plt.Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(subset[xcol].values, subset[ycol].values, linewidth=1.5)
        ax.set_xlabel(xcol)
        ax.set_ylabel(ycol)
        ax.set_title(f"{ycol} vs {xcol} — ncyc {target_ncyc}")
        ax.grid(True, alpha=0.3)

        # If you already have a canvas attribute, destroy and recreate; otherwise keep a handle
        if hasattr(self, "plot_canvas") and self.plot_canvas:
            try:
                self.plot_canvas.get_tk_widget().destroy()
            except Exception:
                pass

        self.plot_canvas = FigureCanvasTkAgg(fig, master=self.bot_pane)
        self.plot_canvas.draw()
        self.plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

#endregion

if __name__ == "__main__":
    root = tk.Tk()
    app = NovaAnalyzerGUI(root)
    root.mainloop()
