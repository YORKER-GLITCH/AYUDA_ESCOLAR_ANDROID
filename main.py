import json
import os
from datetime import date, datetime

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

APP_NAME = "AYUDA ESCOLAR"

LIGHT = {
    "bg": (0.956, 0.965, 0.973, 1),
    "card": (1, 1, 1, 1),
    "text": (0.09, 0.13, 0.16, 1),
    "muted": (0.42, 0.45, 0.50, 1),
    "primary": (0.145, 0.388, 0.922, 1),
}
DARK = {
    "bg": (0.059, 0.09, 0.165, 1),
    "card": (0.118, 0.16, 0.22, 1),
    "text": (0.97, 0.98, 0.99, 1),
    "muted": (0.58, 0.64, 0.72, 1),
    "primary": (0.23, 0.51, 0.95, 1),
}

class AyudaEscolar(App):
    def build(self):
        self.theme = LIGHT
        self.dark = False
        self.data_dir = self.user_data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.files = {
            "tasks": "tareas.json", "subjects": "materias.json",
            "grades": "calificaciones.json", "exams": "examenes.json",
            "projects": "proyectos.json", "memory": "memoria_ia.json",
            "config": "config.json"
        }
        self.tasks = self.load("tasks", [])
        self.subjects = self.load("subjects", [])
        self.grades = self.load("grades", [])
        self.exams = self.load("exams", [])
        self.projects = self.load("projects", [])
        self.memory = self.load("memory", [])
        self.config = self.load("config", {"nombre": "", "carrera": "", "grupo": "", "semestre": "", "ciclo": ""})
        self.root = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        self.show_home()
        return self.root

    def path(self, key):
        return os.path.join(self.data_dir, self.files[key])

    def load(self, key, default):
        try:
            with open(self.path(key), "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default

    def save(self, key, value):
        try:
            with open(self.path(key), "w", encoding="utf-8") as f:
                json.dump(value, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def label(self, text, size=16, bold=False):
        return Label(text=text, color=self.theme["text"], font_size=dp(size),
                     bold=bold, halign="left", valign="middle", size_hint_y=None,
                     height=dp(max(35, size*2.1)))

    def button(self, text, fn, primary=False):
        b = Button(text=text, size_hint_y=None, height=dp(48),
                   background_normal="", background_color=self.theme["primary"] if primary else self.theme["card"],
                   color=(1,1,1,1) if primary else self.theme["text"])
        b.bind(on_release=lambda *_: fn())
        return b

    def clear(self):
        self.root.clear_widgets()

    def header(self, title, subtitle=""):
        h = BoxLayout(size_hint_y=None, height=dp(68), orientation="vertical")
        h.add_widget(self.label(title, 22, True))
        if subtitle:
            h.add_widget(self.label(subtitle, 11))
        self.root.add_widget(h)

    def nav(self):
        s = ScrollView(size_hint_y=None, height=dp(58), do_scroll_y=False)
        bar = BoxLayout(size_hint_x=None, width=dp(760), spacing=dp(5))
        items = [("Inicio", self.show_home), ("IA", self.show_ai), ("Materias", self.show_subjects),
                 ("Tareas", self.show_tasks), ("Calificaciones", self.show_grades),
                 ("Exámenes", self.show_exams), ("Proyectos", self.show_projects), ("⚙", self.show_settings)]
        for name, fn in items:
            bar.add_widget(self.button(name, fn))
        s.add_widget(bar)
        self.root.add_widget(s)

    def content(self):
        s = ScrollView()
        box = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=dp(4))
        box.bind(minimum_height=box.setter("height"))
        s.add_widget(box)
        self.root.add_widget(s)
        return box

    def card_text(self, box, text):
        box.add_widget(self.label(text, 14))

    def show_home(self):
        self.clear()
        self.header("AYUDA ESCOLAR", "Organiza tu vida académica.")
        self.nav()
        box = self.content()
        name = self.config.get("nombre") or "Estudiante"
        pending = [x for x in self.tasks if not x.get("completada")]
        overdue = [x for x in pending if self.is_overdue(x)]
        avg = self.average()
        box.add_widget(self.label(f"Hola, {name} 👋", 24, True))
        box.add_widget(self.label(f"Tareas pendientes: {len(pending)}   •   Vencidas: {len(overdue)}", 15))
        box.add_widget(self.label(f"Exámenes: {len(self.exams)}   •   Promedio: {avg:.1f}", 15))
        box.add_widget(self.label("Próximas tareas", 18, True))
        for t in sorted(self.tasks, key=lambda x: (x.get("completada", False), x.get("fecha","9999-12-31")))[:5]:
            box.add_widget(self.label(f"• {t.get('nombre','Sin nombre')} — {self.fmt(t.get('fecha',''))} — {t.get('prioridad','Baja')}", 13))

    def is_overdue(self, t):
        try:
            return (not t.get("completada")) and datetime.strptime(t.get("fecha",""), "%Y-%m-%d").date() < date.today()
        except Exception:
            return False

    def fmt(self, value):
        try:
            return datetime.strptime(value, "%Y-%m-%d").strftime("%d/%m/%Y")
        except Exception:
            return value

    def average(self):
        vals = []
        for x in self.grades:
            try: vals.append(float(x.get("calificacion", 0)))
            except Exception: pass
        return sum(vals)/len(vals) if vals else 0

    def popup(self, title, message):
        Popup(title=title, content=Label(text=message, color=self.theme["text"]),
              size_hint=(.9, .45)).open()

    def form(self, title, fields, save_fn):
        self.clear()
        self.header(title)
        self.nav()
        box = self.content()
        inputs = {}
        for key, hint in fields:
            box.add_widget(self.label(hint, 13, True))
            ti = TextInput(hint_text=hint, multiline=False, size_hint_y=None, height=dp(48))
            inputs[key] = ti
            box.add_widget(ti)
        box.add_widget(self.button("Guardar", lambda: save_fn(inputs), True))
        box.add_widget(self.button("Volver", self.show_home))

    def show_subjects(self):
        def save(i):
            name=i["nombre"].text.strip()
            if not name: return self.popup("Falta información","Escribe el nombre de la materia.")
            self.subjects.append({"nombre":name,"profesor":i["profesor"].text.strip()})
            self.save("subjects",self.subjects); self.show_subjects()
        self.form("Materias",[("nombre","Nombre de la materia"),("profesor","Profesor")],save)
        box=self.content()
        box.add_widget(self.label("Mis materias",18,True))
        for x in self.subjects:
            box.add_widget(self.label(f"• {x.get('nombre','')} — {x.get('profesor','Sin profesor')}",13))

    def show_tasks(self):
        def save(i):
            name=i["nombre"].text.strip(); d=i["fecha"].text.strip() or date.today().strftime("%Y-%m-%d"); p=i["prioridad"].text.strip() or "Media"
            try: datetime.strptime(d,"%Y-%m-%d")
            except Exception: return self.popup("Fecha inválida","Usa AAAA-MM-DD.")
            if not name: return self.popup("Falta información","Escribe el nombre de la tarea.")
            self.tasks.append({"nombre":name,"fecha":d,"prioridad":p,"completada":False})
            self.save("tasks",self.tasks); self.show_tasks()
        self.form("Tareas",[("nombre","Nombre de tarea"),("fecha","Fecha (AAAA-MM-DD)"),("prioridad","Prioridad: Baja / Media / Alta")],save)
        box=self.content(); box.add_widget(self.label("Tareas registradas",18,True))
        for x in self.tasks:
            box.add_widget(self.label(("✓ " if x.get("completada") else "• ")+f"{x.get('nombre')} — {self.fmt(x.get('fecha',''))} — {x.get('prioridad','Baja')}",13))

    def show_grades(self):
        def save(i):
            try: g=float(i["calificacion"].text.strip())
            except Exception: return self.popup("Dato inválido","Escribe una calificación numérica.")
            self.grades.append({"materia":i["materia"].text.strip(),"calificacion":g}); self.save("grades",self.grades); self.show_grades()
        self.form("Calificaciones",[("materia","Materia"),("calificacion","Calificación")],save)
        box=self.content(); box.add_widget(self.label(f"Promedio actual: {self.average():.2f}",18,True))
        for x in self.grades: box.add_widget(self.label(f"• {x.get('materia','Sin materia')}: {x.get('calificacion',0)}",13))

    def show_exams(self):
        def save(i):
            subject=i["materia"].text.strip(); d=i["fecha"].text.strip() or date.today().strftime("%Y-%m-%d"); topic=i["tema"].text.strip()
            try: datetime.strptime(d,"%Y-%m-%d")
            except Exception: return self.popup("Fecha inválida","Usa AAAA-MM-DD.")
            if not subject: return self.popup("Falta información","Escribe la materia.")
            self.exams.append({"materia":subject,"fecha":d,"tema":topic}); self.save("exams",self.exams); self.show_exams()
        self.form("Exámenes",[("materia","Materia"),("fecha","Fecha (AAAA-MM-DD)"),("tema","Tema")],save)
        box=self.content(); box.add_widget(self.label("Próximos exámenes",18,True))
        for x in sorted(self.exams,key=lambda z:z.get("fecha","9999-12-31")): box.add_widget(self.label(f"• {x.get('materia')} — {self.fmt(x.get('fecha',''))} — {x.get('tema','Sin tema')}",13))

    def show_projects(self):
        def save(i):
            name=i["nombre"].text.strip(); d=i["fecha"].text.strip() or date.today().strftime("%Y-%m-%d")
            if not name: return self.popup("Falta información","Escribe el nombre del proyecto.")
            self.projects.append({"nombre":name,"fecha":d}); self.save("projects",self.projects); self.show_projects()
        self.form("Proyectos",[("nombre","Nombre del proyecto"),("fecha","Fecha (AAAA-MM-DD)")],save)
        box=self.content(); box.add_widget(self.label("Proyectos",18,True))
        for x in self.projects: box.add_widget(self.label(f"• {x.get('nombre')} — {self.fmt(x.get('fecha',''))}",13))

    def local_ai(self, message):
        text = message.lower().strip()
        if not text: return "Escribe algo y te responderé."
        triggers=["recuerda que","recuerda esto","memoriza","guarda esto","aprende esto","quiero que recuerdes"]
        if any(t in text for t in triggers):
            self.memory.append({"texto":message,"fecha":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            self.save("memory",self.memory); return "Listo. Lo guardé en mi memoria local."
        if "qué recuerdas" in text or "que recuerdas" in text or "memoria" in text:
            return "Todavía no tengo información guardada." if not self.memory else "Esto es lo que recuerdo:\n\n" + "\n".join("• "+x.get("texto","") for x in self.memory[-10:])
        if "tarea" in text:
            pending=[t for t in self.tasks if not t.get("completada")]
            if "vencid" in text:
                pending=[t for t in pending if self.is_overdue(t)]
            return "No tienes tareas pendientes." if not pending else f"Tienes {len(pending)} tarea(s):\n\n"+"\n".join(f"• {t.get('nombre')} — {self.fmt(t.get('fecha',''))} — {t.get('prioridad','Baja')}" for t in pending[:10])
        if "promedio" in text or "calificacion" in text or "calificación" in text:
            return f"Tu promedio actual es {self.average():.2f}."
        if "examen" in text:
            return "No tienes exámenes registrados." if not self.exams else "Próximos exámenes:\n\n"+"\n".join(f"• {x.get('materia')} — {self.fmt(x.get('fecha',''))} — {x.get('tema','Sin tema')}" for x in self.exams[:10])
        if "materia" in text or "clase" in text:
            return "No tienes materias registradas." if not self.subjects else "Tus materias:\n\n"+"\n".join(f"• {x.get('nombre')} — Profesor: {x.get('profesor','Sin profesor')}" for x in self.subjects)
        if "proyecto" in text:
            return "No tienes proyectos registrados." if not self.projects else "Tus proyectos:\n\n"+"\n".join(f"• {x.get('nombre')} — {self.fmt(x.get('fecha',''))}" for x in self.projects)
        if text in ("hola","holaa","hey","buenas"):
            return "¡Hola! 👋 Soy tu asistente local de AYUDA ESCOLAR."
        if "qué puedes hacer" in text or "que puedes hacer" in text or text=="ayuda":
            return "Puedo consultar tareas, materias, calificaciones, exámenes, proyectos y memoria local."
        return "Soy un asistente local. Puedo consultar y organizar la información de AYUDA ESCOLAR."

    def show_ai(self):
        self.clear(); self.header("Asistente IA","Asistente local: no usa API.")
        self.nav()
        box=self.content()
        chat=TextInput(text="IA: ¡Hola! Soy tu asistente local.\n\n", readonly=True, multiline=True, size_hint_y=None, height=dp(330))
        box.add_widget(chat)
        inp=TextInput(hint_text="Escribe tu pregunta...", multiline=False, size_hint_y=None, height=dp(48)); box.add_widget(inp)
        def send():
            q=inp.text.strip()
            if not q:return
            chat.readonly=False; chat.text += f"Tú: {q}\nIA: {self.local_ai(q)}\n\n"; chat.readonly=True; inp.text=""
        box.add_widget(self.button("Enviar",send,True))

    def show_settings(self):
        self.clear(); self.header("Configuración")
        self.nav(); box=self.content()
        box.add_widget(self.label("Perfil",18,True))
        for key,hint in [("nombre","Nombre"),("carrera","Carrera"),("grupo","Grupo"),("semestre","Semestre"),("ciclo","Ciclo")]:
            ti=TextInput(text=self.config.get(key,""), multiline=False, size_hint_y=None, height=dp(48))
            box.add_widget(self.label(hint,12,True)); box.add_widget(ti); setattr(self, "_cfg_"+key, ti)
        def save():
            for key in ["nombre","carrera","grupo","semestre","ciclo"]: self.config[key]=getattr(self,"_cfg_"+key).text
            self.save("config",self.config); self.popup("Guardado","Configuración guardada.")
        box.add_widget(self.button("Guardar configuración",save,True))
        box.add_widget(self.button("Cambiar modo claro/oscuro",self.toggle_theme))

    def toggle_theme(self):
        self.dark=not self.dark; self.theme=DARK if self.dark else LIGHT
        self.show_home()

if __name__ == "__main__":
    AyudaEscolar().run()
