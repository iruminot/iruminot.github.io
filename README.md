# iruminot.github.io

Sitio personal y de docencia de Ignacio Ruminot Aburto. Se publica con GitHub Pages en https://iruminot.github.io/

## Estructura

```
datos/sitio.json            ← lo que se edita: perfil, presentaciones, cursos y unidades
fuente/laboratorio.html     ← fuente del laboratorio interactivo (también se publica en claude.ai)
assets/sitio.css            ← estilos de las páginas personales
build.py                    ← genera todas las páginas
material/                   ← guías y syllabus en PDF (no se publica, está en .gitignore)

index.html                              (generado) Inicio
presentaciones/index.html               (generado) Presentaciones
docencia/index.html                     (generado) Años → semestres → cursos
docencia/<semestre>/<curso>/index.html  (generado) Unidades de un curso
docencia/laboratorio/index.html         (generado) Laboratorio interactivo
```

## Cómo actualizar

1. Editar `datos/sitio.json` (o `fuente/laboratorio.html`).
2. `python3 build.py`
3. `git add -A && git commit -m "..." && git push`

GitHub Pages publica los cambios en uno o dos minutos.

- **Agregar un curso**: agregar un objeto en `cursos` del semestre, con `slug`, `codigo`, `nombre`, `carreras` y `unidades`.
- **Agregar un semestre o año**: agregar un objeto en `semestres` o en `docencia`.
- **Enlazar material a una unidad**: en `recursos`, `{"titulo": "...", "lab": "calculo-fem"}` apunta a un tema del laboratorio, y `{"titulo": "...", "url": "...", "tipo": "Guía PDF"}` a cualquier otro archivo o página.
- **Agregar una presentación**: en `presentaciones`, `{"fecha": "2026-11-20", "titulo": "...", "evento": "...", "lugar": "...", "resumen": "...", "enlace": "presentaciones/archivo.pdf"}`.
