# Entornos de desarrollo

Este repositorio usa dos ramas para separar el trabajo en curso de la versión estable.

## 🧪 develop — desarrollo y pruebas

Rama de trabajo de la Mini App y nuevas funcionalidades.

- Aquí se construyen y prueban cambios.
- Cada push ejecuta la validación automática.
- La Mini App de esta rama no se publica como versión de producción.
- Es la rama que usamos durante el desarrollo.

## 🚀 main — producción

Rama estable.

- Solo recibe cambios que ya han sido probados en `develop`.
- Es la fuente de la versión pública de la Mini App.
- El despliegue de GitHub Pages se ejecuta desde `main`.

## Flujo

```text
develop 🧪
   ↓
pruebas automáticas
   ↓
correcciones
   ↓
versión validada
   ↓
main 🚀
   ↓
GitHub Pages / producción
```

### Regla del proyecto

No se debe desarrollar directamente sobre `main` salvo para correcciones urgentes de producción. El trabajo normal comienza en `develop` y pasa a `main` cuando está validado.
