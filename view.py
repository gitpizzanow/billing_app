import tkinter as tk
from tkinter import ttk, PhotoImage
import os

class ProductView(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.title("Simple Billing System")
        self.geometry("800x550")
        
        if os.path.exists("assets/logo.png"):
            self._app_icon = PhotoImage(file="assets/logo.png")
            self.iconphoto(True, self._app_icon)

        self._style = ttk.Style(self)
        try:
            self._style.theme_use("clam")
        except Exception:
            pass

        self._style.configure(
            "Green.TButton",
            background="#4CAF50",
            foreground="white",
            padding=(12, 8),
            font=("Arial", 10, "bold"),
            borderwidth=0,
            focusthickness=0
        )
        self._style.map(
            "Green.TButton",
            background=[("active", "#43A047"), ("pressed", "#388E3C")],
            foreground=[("disabled", "#eaeaea")]
        )

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.LabelFrame(self, text="Add Product")
        frame.pack(fill="x", padx=15, pady=10)

        frame.columnconfigure(0, weight=3)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        frame.columnconfigure(3, weight=1)
        frame.columnconfigure(4, weight=0)

        self.name_entry = ttk.Entry(frame, width=25)
        self.price_entry = ttk.Entry(frame, width=15)
        self.qty_entry = ttk.Entry(frame, width=15)
        self.tva_entry = ttk.Entry(frame, width=10)

        self.name_entry.insert(0, "Product name")
        self.name_entry.config(foreground="gray")
        self.price_entry.insert(0, "Price")
        self.price_entry.config(foreground="gray")
        self.qty_entry.insert(0, "Quantity")
        self.qty_entry.config(foreground="gray")
        
        self.name_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(e, "Product name"))
        self.name_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(e, "Product name"))
        self.price_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(e, "Price"))
        self.price_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(e, "Price"))
        self.qty_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(e, "Quantity"))
        self.qty_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(e, "Quantity"))

        vcmd_price = (self.register(self._validate_decimal), "%P")
        vcmd_int = (self.register(self._validate_int), "%P")
        vcmd_vat = (self.register(self._validate_percent), "%P")
        self.price_entry.configure(validate="key", validatecommand=vcmd_price)
        self.qty_entry.configure(validate="key", validatecommand=vcmd_int)
        self.tva_entry.configure(validate="key", validatecommand=vcmd_vat)
        
        self.name_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.price_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.qty_entry.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.tva_entry.insert(0, "TVA %")
        self.tva_entry.config(foreground="gray")
        self.tva_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(e, "TVA %"))
        self.tva_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(e, "TVA %"))
        self.tva_entry.bind("<KeyRelease>", lambda e: self.controller.refresh_totals())
        self.tva_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        ttk.Button(
            frame,
            text="Add Product",
            command=self.controller.add_product
        ).grid(row=0, column=4, padx=(10, 5), pady=5, sticky="e")

        self.table = ttk.Treeview(
            self, columns=("Name", "Price", "Qty", "Total"), show="headings"
        )

        for col in self.table["columns"]:
            self.table.heading(col, text=col)

        self.table.bind("<Double-1>", lambda e: self.controller.edit_selected_product())
        self.bind("<F10>", lambda e: self.controller.edit_selected_product())
        self.bind("<Delete>", lambda e: self.controller.delete_selected_product())
        self.table.bind("<KeyPress-minus>", lambda e: self.controller.delete_selected_product())
        self.table.bind("<KeyPress-KP_Subtract>", lambda e: self.controller.delete_selected_product())

        self.table.pack(fill="both", expand=True, padx=15, pady=10)

        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.total_label = ttk.Label(bottom_frame, text="Total: 0.00")
        self.total_label.pack(side="right", padx=(10, 0))
        
        if os.path.exists("assets/csv.png"):
            csv_icon_raw = PhotoImage(file="assets/csv.png")
            w, h = csv_icon_raw.width(), csv_icon_raw.height()
            scale = max(w // 24, h // 24, 1)
            csv_icon = csv_icon_raw.subsample(scale, scale)
            export_btn = ttk.Button(
                bottom_frame,
                text="Export CSV",
                image=csv_icon,
                compound="left",
                command=self.controller.export_csv,
                style="Green.TButton"
            )
            export_btn.image = csv_icon  
            export_btn.pack(side="right")
        else:
            export_btn = ttk.Button(
                bottom_frame,
                text="Export CSV",
                command=self.controller.export_csv,
                style="Green.TButton"
            )
            export_btn.pack(side="right")

    def update_table(self, product):
        self.table.insert("", "end", values=product)

    def clear_table(self):
        for row in self.table.get_children():
            self.table.delete(row)

    def delete_row(self, item_id):
        self.table.delete(item_id)

    def get_selected_product(self):
        selection = self.table.selection()
        if not selection:
            return None, None
        item_id = selection[0]
        values = self.table.item(item_id, "values")
        if not values:
            return None, None
        name, price, qty, total = values
        return item_id, (name, float(price), int(qty), float(total))

    def update_row(self, item_id, product):
        self.table.item(item_id, values=product)

    def open_edit_window(self, item_id, values):
        old_values = values
        name, price, qty, _total = values

        win = tk.Toplevel(self)
        win.title("Edit Product")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        frm = ttk.Frame(win)
        frm.pack(padx=12, pady=12, fill="both", expand=True)

        ttk.Label(frm, text="Name").grid(row=0, column=0, sticky="w", pady=(0, 6))
        name_entry = ttk.Entry(frm, width=30)
        name_entry.insert(0, str(name))
        name_entry.grid(row=0, column=1, sticky="ew", pady=(0, 6))

        ttk.Label(frm, text="Price").grid(row=1, column=0, sticky="w", pady=(0, 6))
        price_entry = ttk.Entry(frm, width=15)
        price_entry.insert(0, str(price))
        price_entry.configure(validate="key", validatecommand=(self.register(self._validate_decimal), "%P"))
        price_entry.grid(row=1, column=1, sticky="w", pady=(0, 6))

        ttk.Label(frm, text="Quantity").grid(row=2, column=0, sticky="w", pady=(0, 6))
        qty_entry = ttk.Entry(frm, width=15)
        qty_entry.insert(0, str(qty))
        qty_entry.configure(validate="key", validatecommand=(self.register(self._validate_int), "%P"))
        qty_entry.grid(row=2, column=1, sticky="w", pady=(0, 6))

        btns = ttk.Frame(frm)
        btns.grid(row=3, column=0, columnspan=2, sticky="e", pady=(8, 0))

        def on_save():
            self.controller.apply_product_edit(
                item_id,
                old_values,
                name_entry.get(),
                price_entry.get(),
                qty_entry.get()
            )
            win.destroy()

        ttk.Button(btns, text="Cancel", command=win.destroy).pack(side="right")
        ttk.Button(btns, text="Save", command=on_save).pack(side="right", padx=(0, 8))

        frm.columnconfigure(1, weight=1)
        name_entry.focus_set()

    def _validate_int(self, proposed):
        if proposed == "":
            return True
        return proposed.isdigit()

    def _validate_decimal(self, proposed):
        if proposed == "":
            return True
        if proposed.count(".") > 1:
            return False
        if proposed == ".":
            return True
        try:
            float(proposed)
            return True
        except Exception:
            return False

    def _validate_percent(self, proposed):
        if proposed == "TVA %":
            return True
        if proposed == "":
            return True
        if proposed.count(".") > 1:
            return False
        if proposed == ".":
            return True
        try:
            val = float(proposed)
            return 0.0 <= val <= 100.0
        except Exception:
            return False

    def update_totals(self, subtotal, vat, total):
        self.total_label.config(
            text=f"Subtotal: {subtotal:.2f} | VAT: {vat:.2f} | Total: {total:.2f}"
        )
    
    def clear_placeholder(self, event, placeholder_text):
        entry = event.widget
        if entry.get() == placeholder_text:
            entry.delete(0, tk.END)
            entry.config(foreground="black")
    
    def restore_placeholder(self, event, placeholder_text):
        entry = event.widget
        if not entry.get():
            entry.insert(0, placeholder_text)
            entry.config(foreground="gray")
