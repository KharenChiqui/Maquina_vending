# ================= CONFIGURACIÓN =================
from kivy.config import Config
# Configuración de ventana
Config.set('graphics', 'width', '1024')
Config.set('graphics', 'height', '600')
Config.set('graphics', 'resizable', '0')  # Evita redimensionamiento
# Activar teclado virtual en Linux
Config.set('kivy', 'keyboard_mode', 'systemanddock')

# ================= MÓDULOS ESTÁNDAR =================
from datetime import datetime
import requests  # pip install requests
import subprocess

# ================= KIVY =================
from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown

from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, NumericProperty, ListProperty

from kivy.animation import Animation

# ================= MÓDULOS PROPIOS =================
from bd_funciones import insertar_usuario, insertar_maquina, registrar_pago_y_ventas


class CarritoItemPago(BoxLayout):
    pass


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

#def test_insercion():
    #print("Iniciando prueba de inserción...")
    
    # Datos de prueba
    #resultado = insertar_usuario(
       # "Juan", 
        #"Pérez", 
        #"juan@perez.com", 
        #"secreto123", 
        #"admin", 
        #"123456789", 
        #"Madrid", 
        #"male"
    #)

    #if resultado:
        #print("Prueba exitosa: Usuario insertado correctamente.")
    #else:
        #print("Error: No se pudo insertar el usuario.")

#def prueba_sistema():
    # Simulamos que el usuario que creamos tiene el ID 1
    #user_id_creado = 1 
    
    #resultado = insertar_maquina(
        #user_id=user_id_creado,
        #name='Máquina Central',
        #location='Plaza Principal',
        #status='available',
        #max_water=1000.0,
        #current_level=750.5,
        #price=0.50,
        #filter_ac=85.0,
        #filter_sg=90.0,
        #filter_zeo=78.0,
        #filter_rom=92.0,
        #filter_ml=88.0
    #)

    #if resultado:
     #   print("Sistema de máquina listo.")

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

class BotonOperacion2(ButtonBehavior, RelativeLayout):
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

class IconButton(ButtonBehavior, Image):
    pass

class CarritoItem(BoxLayout):
    cantidad = NumericProperty(1)
    producto = ObjectProperty(None)
    total = NumericProperty(0)

    def actualizar_total(self):
        app = App.get_running_app()
        pantalla_recarga = app.root.get_screen("recarga")

        for item_carrito in pantalla_recarga.carrito:
            if item_carrito['producto'] == self.producto:
                item_carrito['cantidad'] = self.cantidad
                item_carrito['monto_final'] = self.cantidad * self.producto.precio
                break

        self.ids.label_total.text = f"Bs {self.cantidad * self.producto.precio}"
        app.root.get_screen("carrito").actualizar_total_carrito()

    def aumentar_cantidad(self):
        self.cantidad += 1
        self.ids.label_cantidad.text = str(self.cantidad)
        self.actualizar_total()

    def decrementar_cantidad(self):
        if self.cantidad > 1:
            self.cantidad -= 1
            self.ids.label_cantidad.text = str(self.cantidad)
            self.actualizar_total()

    def eliminar_producto(self):
        app = App.get_running_app()
        pantalla_recarga = app.root.get_screen("recarga")

        #Elimina el producto de la lista
        pantalla_recarga.carrito = [
            item for item in pantalla_recarga.carrito if item['producto'] != self.producto
        ]

        #Elimina el widget de la tabla
        self.parent.remove_widget(self)
        app.root.get_screen("carrito").actualizar_total_carrito()


class PantallaRecarga(Screen):
    total_pagar = NumericProperty(0)
    cantidad = NumericProperty(1)
    producto_seleccionado = NumericProperty(0)
    carrito = ListProperty([])

    def on_pre_enter(self):
        self.deseleccionar_todos()

    def deseleccionar_todos(self, seleccionado=None):
        for btn in self.ids.grid_botones.children:
            if btn != seleccionado:
                btn.seleccionado = False

    def seleccionar_producto(self, index):
        self.producto_seleccionado = index
        self.cantidad = 1

    def incrementar_cantidad(self):
        self.cantidad += 1

    def decrementar_cantidad(self):
        if self.cantidad > 1:
            self.cantidad -= 1

    def agregar_al_carrito(self):
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

        self.mostrar_popup()

    def mostrar_popup(self):
        popup = self.ids.popup_label
        popup.opacity = 1
        anim = Animation(opacity=0, duration=1)  
        Clock.schedule_once(lambda dt: anim.start(popup), 1)  

    def continuar(self):
        total_general = 0
        print("Resumen del carrito:")
        for item in self.carrito:
            print(f"{item['cantidad']} x {item['producto'].litros}L - Bs {item['precio']} c/u = Bs {item['monto_final']}")
            total_general += item['monto_final']
        print(f"Bs {total_general}")

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

    def on_pre_enter(self):
        self.actualizar_carrito()

    def imprimir_carrito(self):
        app = App.get_running_app()
        pantalla_recarga = app.root.get_screen("recarga")
        total_general = 0
        print("Resumen del carrito ")
        for item in pantalla_recarga.carrito:
            print(f"{item['cantidad']} x {item['producto'].litros}L - Bs {item['precio']} c/u = Bs {item['monto_final']}")
            total_general += item['monto_final']
        print(f"Total: Bs {total_general}")

    #Limpia y recorre el carrito de PantallaRecarga para llenar la tabla
    def actualizar_carrito(self):
        self.ids.contenedor_items.clear_widgets()

        app = App.get_running_app()
        pantalla_recarga = app.root.get_screen("recarga")
        carrito = pantalla_recarga.carrito

        for item in carrito:
            descripcion = f"Botellón {item['producto'].litros}L"
            cantidad = item['cantidad']
            monto_total = item['monto_final']
            self.agregar_item(item['producto'], descripcion, cantidad, monto_total)

        self.actualizar_total_carrito() #AQUI ES, REVISAR

    def agregar_item(self, producto, descripcion, cantidad, monto_total):
        item = CarritoItem()
        item.producto = producto  
        item.ids.label_descripcion.text = descripcion
        item.cantidad = cantidad
        item.ids.label_cantidad.text = str(cantidad)
        item.ids.label_total.text = f"{monto_total} Bs"
        self.ids.contenedor_items.add_widget(item)

    def actualizar_total_carrito(self):
        app = App.get_running_app()
        pantalla_recarga = app.root.get_screen("recarga")
        total = sum([item['monto_final'] for item in pantalla_recarga.carrito])
        self.ids.total_label.text = f" {total} Bs"


        
class GestorPantallas(ScreenManager):
    pass

class ExpendedoraApp(App):
    azul_oscuro = get_color_from_hex("#1F3F60")
    PRODUCTS = PRODUCTS  #Esto hace accesible PRODUCTS como app.PRODUCTS
    def build(self):
        return GestorPantallas()
    def open_ticket(self):
        ModalTicketPago().open()

from kivy.factory import Factory

class ModalTicketPago(ModalView):

    def on_open(self):
        self.cargar_ticket()

    def cargar_ticket(self):
        self.ids.contenedor_items.clear_widgets()
        app = App.get_running_app()
        carrito = app.root.get_screen("recarga").carrito

        total = 0
        for item in carrito:
            widget = Factory.CarritoItemPago()
            widget.ids.label_descripcion.text = f"Botellón {item['producto'].litros}L"
            widget.ids.label_cantidad.text = str(item['cantidad'])
            widget.ids.label_total.text = f"{item['monto_final']} Bs"
            self.ids.contenedor_items.add_widget(widget)
            total += item['monto_final']

        self.ids.total_label.text = f"{total} Bs"

    def ir_a_pago(self):
        total = sum(
            item['monto_final']
            for item in App.get_running_app().root.get_screen("recarga").carrito
        )
        self.dismiss()
        modal = ModalConfirmarPago()
        modal.total = total
        modal.open()
    
class ModalConfirmarPago(ModalView):
    total = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Clock.schedule_once(lambda dt: self.on_metodo_pago(), 0)
        Clock.schedule_once(lambda dt: self.bind_teclado_virtual(), 0)
        Clock.schedule_once(lambda dt: self.init_spinner_tipo_cuenta(), 0)
        Clock.schedule_once(lambda dt: self.bind_spinner_tipo_cuenta(), 0)

    # ----------------TECLADO VIRTUAL----------------
    def bind_teclado_virtual(self):
        """Enlaza los TextInput al evento focus para abrir teclado virtual."""
        if hasattr(self.ids, 'input_cedula_tarjeta'):
            self.ids.input_cedula_tarjeta.bind(focus=self.show_keyboard)
        if hasattr(self.ids, 'input_contrasena'):
            self.ids.input_contrasena.bind(focus=self.show_keyboard)

    def show_keyboard(self, instance, value):
        """Abre teclado virtual cuando el TextInput gana foco, lo cierra al perderlo."""
        if value:  # gana foco
            try:
                subprocess.Popen(['onboard'])  # lanzar teclado virtual
            except FileNotFoundError:
                print("No se encontró el teclado virtual 'onboard'. Instala con: sudo apt install onboard")
        else:  # pierde foco
            subprocess.Popen(['pkill', 'onboard'])  # cerrar teclado virtual

    # ----------------SPINNER DINÁMICO----------------
    def init_spinner_tipo_cuenta(self):
        """Inicializa el spinner con valor por defecto y opciones restantes."""
        spinner = self.ids.spinner_tipo_cuenta
        spinner.text = "Corriente"  
        spinner.values = ["Ahorro"]  

    def bind_spinner_tipo_cuenta(self):
        """Enlaza el evento de selección del spinner para actualizar dinámicamente las opciones."""
        spinner = self.ids.spinner_tipo_cuenta
        spinner.bind(text=self.on_spinner_tipo_cuenta_select)

    def on_spinner_tipo_cuenta_select(self, spinner, text):
        """Actualiza las opciones del spinner para que la seleccionada no se duplique."""
        todas_opciones = ["Corriente", "Ahorro"]
        spinner.values = [v for v in todas_opciones if v != text]

    # ----------------MÉTODO DE PAGO----------------
    def abrir_dropdown(self):
        # No se necesita dropdown de momento
        pass

    def on_metodo_pago(self, metodo=None):
        if hasattr(self.ids, 'box_tarjeta'):
            self.ids.box_tarjeta.opacity = 1
            self.ids.box_tarjeta.disabled = False
            self.ids.box_tarjeta.height = self.ids.box_tarjeta.minimum_height

    # ---------------- CONFIRMAR PAGO ----------------
    def confirmar_pago(self):
        print("CONFIRMAR PAGO EJECUTADO")

        cedula = self.ids.input_cedula_tarjeta.text.strip()
        contrasena = self.ids.input_contrasena.text.strip()
        tipo_cuenta = self.ids.spinner_tipo_cuenta.text.strip()

        if not cedula or not contrasena:
            print("Debe ingresar cédula y contraseña")
            return

        # ================= CREAR CADENA POS =================
        # Formato: "POS|<monto>|<cedula>|<tipo_cuenta>|<clave>"
        cadena_pos = f"POS|{self.total:.2f}|{cedula}|{tipo_cuenta}|{contrasena}"
        print("Cadena POS generada:", cadena_pos)
        # =====================================================

        payment_method = "card"

        app = App.get_running_app()
        pantalla_recarga = app.root.get_screen("recarga")
        carrito = pantalla_recarga.carrito

        exito = registrar_pago_y_ventas(
            remote_payment_id=f"PAGO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            payment_method=payment_method,
            bank="",
            reference_code=cedula,
            amount=self.total,
            receipt="",
            recharge=0,
            carrito=carrito,
            user_id=1,
            machine_id=1
        )

        if exito:
            pantalla_recarga.carrito.clear()
            self.dismiss()
            app.root.current = "inicio"

if __name__ == '__main__':
    ExpendedoraApp().run()
    #test_insercion()
    #prueba_sistema()