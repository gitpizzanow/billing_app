import csv
from db import get_connection

class ProductModel:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def add_product(self, name, price, qty):
        total = price * qty

        query = """
        INSERT INTO products (name, price, quantity, total)
        VALUES (%s, %s, %s, %s)
        """
        self.cursor.execute(query, (name, price, qty, total))
        self.conn.commit()

        return name, price, qty, total

    def get_products(self):
        self.cursor.execute("SELECT name, price, quantity, total FROM products")
        return self.cursor.fetchall()

    def get_totals(self, vat_percent=20.0):
        self.cursor.execute("SELECT SUM(total) FROM products")
        subtotal = self.cursor.fetchone()[0] or 0
        subtotal = float(subtotal)

        vat_rate = float(vat_percent) / 100.0
        vat = subtotal * vat_rate
        total = subtotal + vat
        return subtotal, vat, total

    def update_product(self, old_name, old_price, old_qty, new_name, new_price, new_qty):
        new_total = float(new_price) * int(new_qty)

        query = """
        UPDATE products
        SET name = %s, price = %s, quantity = %s, total = %s
        WHERE name = %s AND price = %s AND quantity = %s
        LIMIT 1
        """
        self.cursor.execute(
            query,
            (new_name, float(new_price), int(new_qty), new_total, old_name, float(old_price), int(old_qty))
        )
        self.conn.commit()
        return new_name, float(new_price), int(new_qty), new_total

    def delete_product(self, name, price, qty):
        query = """
        DELETE FROM products
        WHERE name = %s AND price = %s AND quantity = %s
        LIMIT 1
        """
        self.cursor.execute(query, (name, float(price), int(qty)))
        self.conn.commit()

    def export_csv(self, file_path):
        products = self.get_products()

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Price", "Quantity", "Total"])
            writer.writerows(products)
