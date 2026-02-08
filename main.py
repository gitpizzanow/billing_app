from view import ProductView
from service import ProductService

def main():
    controller = ProductService(None)
    view = ProductView(controller)
    controller.view = view
    controller.load_products()
    view.mainloop()

if __name__ == "__main__":
    main()
