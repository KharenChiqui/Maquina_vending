from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.uix.button import Button
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, NumericProperty, ListProperty, StringProperty
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
import requests # Asegúrate de tener requests instalado: pip install requests

def obtener_precio_dolar():
    try:
        response = requests.get("https://ve.dolarapi.com/v1/dolares/oficial", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return float(data.get("promedio", 1))
    except Exception as e:
        print("Error consultando API dólar:", e)
    return 1  # Valor por defecto si falla la API

PRECIO_DOLAR = obtener_precio_dolar()

Window.size = (1024, 600)

LabelBase.register(name='Intro', fn_regular='fonts/Intro.otf')

PRECIO_LITRO = 1000
SUPERUSER_PASSWORD = "aguaSegura24"

class Product:
    def __init__(self, litros, precio):
        self.litros = litros
        self.precio = precio


PRODUCTS = [
    Product(19, int(round(0.5 * PRECIO_DOLAR, 0))),
    Product(10, int(round(0.35 * PRECIO_DOLAR, 0))),
    Product(5, int(round(0.25 * PRECIO_DOLAR, 0))),
    Product(2, int(round(0.10 * PRECIO_DOLAR, 0))),
    Product(1, int(round(0.05 * PRECIO_DOLAR, 0)))
]

class BotonRecarga(ButtonBehavior, BoxLayout):
    img_src = StringProperty("")
    text_btn = StringProperty("")
    seleccionado = BooleanProperty(False)
    pantalla_recarga = ObjectProperty(None)

    def on_press(self):
        print(f"Presionado: {self.text_btn}")
        self.pantalla_recarga.deseleccionar_todos(self)
        self.seleccionado = True
        if self.text_btn == "Añadir":
            Clock.schedule_once(self.deseleccionar, 0.3)
        try:
            litros = int(self.text_btn.split()[0])
            self.pantalla_recarga.total_pagar = litros * PRECIO_LITRO
        except:
            self.pantalla_recarga.total_pagar = 0

    def deseleccionar(self, *args):
        self.seleccionado = False

class BotonOperacion(ButtonBehavior, RelativeLayout):
    color_fondo = ListProperty([1, 10, 10, 1])
    img_src = StringProperty("")
    icono = StringProperty("")

class PantallaInicio(Screen):
    tiempo_presionado = NumericProperty(0)

    def on_touch_down(self, touch):
        if self.ids.superusuario and self.ids.superusuario.collide_point(*touch.pos):
            self.ids.superusuario.opacity = 0
            Clock.schedule_interval(self.contar_tiempo, 0.1)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        Clock.unschedule(self.contar_tiempo)
        self.tiempo_presionado = 0
        return super().on_touch_up(touch)

    def contar_tiempo(self, dt):
        self.tiempo_presionado += dt
        if self.tiempo_presionado >= 3:
            self.ids.superusuario.opacity = 1
            Clock.schedule_once(self.ir_a_login, 1)
            Clock.unschedule(self.contar_tiempo)

    def ir_a_login(self, dt):
        self.manager.current = "login"
        self.ids.superusuario.opacity = 0

class CarritoItem(BoxLayout):
    cantidad = NumericProperty(1)
    costo_unitario = NumericProperty(5000)
    total = NumericProperty(5000)

    def actualizar_total(self):
        self.total = self.cantidad * self.costo_unitario
        self.ids.label_total.text = f"Bs {self.total}"
        app = App.get_running_app()
        app.root.ids.carrito_screen.actualizar_total_carrito()

    def aumentar(self):
        self.cantidad += 1
        self.ids.label_cantidad.text = str(self.cantidad)
        self.actualizar_total()

    def disminuir(self):
        if self.cantidad > 1:
            self.cantidad -= 1
            self.ids.label_cantidad.text = str(self.cantidad)
            self.actualizar_total()

class PantallaRecarga(Screen):
    total_pagar = NumericProperty(0)
    cantidad = NumericProperty(1)
    producto_seleccionado = NumericProperty(0)  # índice en PRODUCTS
    carrito = ListProperty([])  # lista de dicts: {'producto': Product, 'cantidad': int}

    def on_pre_enter(self):
        self.deseleccionar_todos()

    def deseleccionar_todos(self, seleccionado=None):
        for btn in self.ids.grid_botones.children:
            if btn != seleccionado:
                btn.seleccionado = False

    def seleccionar_producto(self, index):
        self.producto_seleccionado = index
        self.cantidad = 1  # reset cantidad al seleccionar producto

    def incrementar_cantidad(self):
        self.cantidad += 1

    def decrementar_cantidad(self):
        if self.cantidad > 1:
            self.cantidad -= 1

    def agregar_al_carrito(self):
        # Busca si ya existe el producto en el carrito
        for item in self.carrito:
            if item['producto'] == PRODUCTS[self.producto_seleccionado]:
                item['cantidad'] += self.cantidad
                item['monto_final'] = item['cantidad'] * item['producto'].precio
                break
        else:
            self.carrito.append({
                'producto': PRODUCTS[self.producto_seleccionado],
                'cantidad': self.cantidad,
                'precio': PRODUCTS[self.producto_seleccionado].precio,
                'monto_final': self.cantidad * PRODUCTS[self.producto_seleccionado].precio
            })
        print("Carrito actual:", [
            (item['producto'].litros, item['cantidad'], item['precio'], item['monto_final'])
            for item in self.carrito
        ])

    def continuar(self):
        total_general = 0
        print("Resumen del carrito:")
        for item in self.carrito:
            print(f"{item['cantidad']} x {item['producto'].litros}L - Bs {item['precio']} c/u = Bs {item['monto_final']}")
            total_general += item['monto_final']
        print(f"TOTAL A PAGAR: Bs {total_general}")

class PantallaInformacion(Screen):
    pass

class PantallaContacto(Screen):
    pass

class PantallaLogin(Screen):
    def verificar_contraseña(self):
        if self.ids.input_password.text == SUPERUSER_PASSWORD:
            print("Acceso concedido al modo administrador")
        else:
            self.ids.input_password.text = ""
            self.ids.etiqueta_status.text = "Contraseña incorrecta"

class PantallaCarrito(Screen):
    def on_enter(self):
        self.ids.contenedor_items.clear_widgets()
        # Cargar ejemplos
        self.agregar_item("Botellón 5L", 1, 5000)
        self.agregar_item("Botellón 10L", 1, 10000)
        self.actualizar_total_carrito()

    def agregar_item(self, descripcion, cantidad, precio):
        item = CarritoItem()
        item.ids.label_descripcion.text = descripcion
        item.cantidad = cantidad
        item.costo_unitario = precio
        item.ids.label_cantidad.text = str(cantidad)
        item.ids.label_total.text = f"Bs {precio * cantidad}"
        self.ids.contenedor_items.add_widget(item)

    def actualizar_total_carrito(self):
        total = 0
        for item in self.ids.contenedor_items.children:
            total += item.cantidad * item.costo_unitario
        self.ids.total_label.text = f"Total: Bs {total}"
        
class GestorPantallas(ScreenManager):
    pass

class ExpendedoraApp(App):
    azul_oscuro = get_color_from_hex("#1F3F60")
    PRODUCTS = PRODUCTS  # Esto hace accesible PRODUCTS como app.PRODUCTS
    def build(self):
        return GestorPantallas()


if __name__ == '__main__':
    ExpendedoraApp().run()
