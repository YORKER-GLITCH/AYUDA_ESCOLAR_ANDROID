# AYUDA ESCOLAR — versión Android

Esta carpeta contiene una primera adaptación móvil del proyecto original.

- No usa API ni créditos.
- Guarda datos localmente en el almacenamiento privado de la aplicación.
- Conserva la lógica de tareas, materias, calificaciones, exámenes, proyectos y memoria local.
- La interfaz se adapta a pantalla táctil con Kivy.

## Crear APK sin WSL

La forma más sencilla si WSL no funciona es usar una máquina Linux temporal/Google Colab o GitHub Actions con Buildozer.

Comando de compilación en Linux/Colab:

    pip install buildozer cython
    buildozer android debug

El APK aparecerá en la carpeta `bin/`.

## Nota

La versión Windows original usa Tkinter. Android no ejecuta Tkinter de forma nativa, por eso esta versión reemplaza únicamente la interfaz por Kivy y mantiene la lógica local.
