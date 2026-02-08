import csv
import tkinter as tk
from tkinter import messagebox, filedialog
from model import ProductModel

class ProductService:
    def __init__(self, view):
        self.model = ProductModel()
        self.view = view

    def _get_vat_percent(self):
        try:
            if not self.view or not hasattr(self.view, "tva_entry"):
                return 20.0

            raw = self.view.tva_entry.get().strip()
            if not raw or raw == "TVA 20%":
                return 20.0

            val = float(raw)
            if val < 0:
                val = 0.0
            if val > 100:
                val = 100.0
            return val
        except Exception:
            return 20.0

    def load_products(self):
        products = self.model.get_products()
        if hasattr(self.view, "clear_table"):
            self.view.clear_table()

        for product in products:
            self.view.update_table(product)

        self.refresh_totals()

    def refresh_totals(self):
        subtotal, vat, total = self.model.get_totals(self._get_vat_percent())
        self.view.update_totals(subtotal, vat, total)

    def add_product(self):
        try:
            name = self.view.name_entry.get().strip()
            price_str = self.view.price_entry.get().strip()
            qty_str = self.view.qty_entry.get().strip()

            if name == "Product name" or not name:
                raise ValueError("Name cannot be empty")
            if price_str == "Price" or not price_str:
                raise ValueError("Price cannot be empty")
            if qty_str == "Quantity" or not qty_str:
                raise ValueError("Quantity cannot be empty")

            price = float(price_str)
            qty = int(qty_str)

            product = self.model.add_product(name, price, qty)
            self.view.update_table(product)

            self.refresh_totals()

            if hasattr(self.view, "reset_inputs"):
                self.view.reset_inputs()
            else:
                self.view.name_entry.delete(0, tk.END)
                self.view.price_entry.delete(0, tk.END)
                self.view.qty_entry.delete(0, tk.END)
                
                self.view.name_entry.insert(0, "Product name")
                self.view.price_entry.insert(0, "Price")
                self.view.qty_entry.insert(0, "Quantity")

        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def export_csv(self):
        products = self.model.get_products()
        if not products:
            messagebox.showwarning("Warning", "No products to export")
            return

        try:
            default_name = f"example{len(products) + 1}.csv"
        except Exception:
            default_name = "example1.csv"

        file_path = filedialog.asksaveasfilename(
            initialfile=default_name,
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )

        if file_path:
            try:
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Name", "Price", "Quantity", "Total"])
                    writer.writerows(products)

                    vat_percent = self._get_vat_percent()
                    subtotal, vat, total = self.model.get_totals(vat_percent)
                    writer.writerow([])
                    writer.writerow(["", "", "Subtotal", f"{subtotal:.2f}"])
                    writer.writerow(["", "", f"VAT ({vat_percent:.2f}%)", f"{vat:.2f}"])
                    writer.writerow(["", "", "Total", f"{total:.2f}"])

                messagebox.showinfo("Success", "Invoice exported successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")

    def delete_selected_product(self):
        item_id, values = self.view.get_selected_product()
        if not item_id or not values:
            messagebox.showwarning("Warning", "Select a product first")
            return

        name, price, qty, _total = values
        if not messagebox.askyesno("Delete", f"Delete '{name}'?"):
            return

        try:
            self.model.delete_product(name, price, qty)
            self.view.delete_row(item_id)
            self.refresh_totals()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete product: {e}")

    def edit_selected_product(self):
        item_id, values = self.view.get_selected_product()
        if not item_id or not values:
            messagebox.showwarning("Warning", "Select a product first")
            return
        self.view.open_edit_window(item_id, values)

    def apply_product_edit(self, item_id, old_values, new_name, new_price_str, new_qty_str):
        try:
            old_name, old_price, old_qty, _old_total = old_values

            new_name = new_name.strip()
            if not new_name:
                raise ValueError("Name cannot be empty")

            new_price = float(new_price_str)
            new_qty = int(new_qty_str)

            updated = self.model.update_product(
                old_name, old_price, old_qty,
                new_name, new_price, new_qty
            )
            self.view.update_row(item_id, updated)

            self.refresh_totals()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update product: {e}")
