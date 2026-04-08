# 🎯 TICKETS SPRINT MVP FRONTEND (Viernes Deadline)

## Ticket 1: Catálogo Principal (Cards)
**Asignado a:** Alexander
**Endpoint:** `GET /api/v1/simulaciones`
**Descripción:** Renderizar la grilla de bootcamps disponibles. Las tarjetas deben mostrar el `title`, `difficulty_level`, `estimated_hours` y el nombre de la `company` asociada.
**Criterios de Aceptación:** Diseño responsive, manejo de estado de carga (loading spinner) si el endpoint tarda.

## Ticket 2: Vista de Detalle (Acordeón Coursera)
**Asignado a:** Alexander
**Endpoint:** `GET /api/v1/simulaciones/{slug}`
**Descripción:** Al hacer clic en un curso, redirigir al detalle. Iterar sobre el array `modules` para renderizar títulos de sección. Dentro de cada módulo, iterar sobre `tasks` para listar las tareas.
**Criterios de Aceptación:** - Usar íconos diferentes según el `task_type` (Ej: ⏯️ para 'video', 💻 para 'interactive', 📄 para 'reading').
- Usar el archivo `CONTRATO_FRONTEND.json` proporcionado para mockear la UI mientras se conecta la API.

## Ticket 3: Consumo de Auth y Token
**Asignado a:** Alexander
**Endpoint:** `POST /api/v1/token`
**Descripción:** Validar que el login envíe el correo en el campo `username` del FormData. Guardar el token devuelto en LocalStorage/Zustand y pasarlo en los headers de las peticiones GET.
