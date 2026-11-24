# Sellify · DESIGN.md (v5)

Sistema de diseño de www.sellify.us. Toda página nueva sigue este archivo.
Los valores viven como variables CSS en `site.css`; en el código se usan los nombres, nunca valores sueltos.

## Dirección

- Referencia principal elegida por Alonso: aonnoysengupta.com. De ahí se toma el patrón, no el aspecto: fondo oscuro, una pieza animada en el hero, casos en un visor fijo con gráficas que se dibujan al hacer scroll.
- De digitalmakers.nl: texto que se enciende palabra por palabra y cinta de logos en movimiento.
- De miguelrecio.es: barra fija de agenda.
- Marca: manual Asterisko (asterisco naranja y gris, pizarra como color de apoyo).
- Idea propia de Sellify: el movimiento está en los números. Lo que se anima son cifras, barras y gráficas, porque la promesa es margen.

## Color

| Variable | Valor | Rol |
|---|---|---|
| `--bg` | `#0F0F10` | Fondo de página |
| `--panel` | `#1A1A1A` | Paneles y visores (oscuro de marca) |
| `--panel-2` | `#222325` | Panel elevado, campos |
| `--line` | `#2A2B2E` | Líneas divisorias |
| `--line-2` | `#3A3C40` | Bordes de campos y botones secundarios |
| `--text` | `#F2F2F2` | Texto principal |
| `--text-2` | `#B9BBBF` | Texto de apoyo |
| `--text-3` | `#8A8D92` | Leyendas y notas (contraste 5.4:1) |
| `--orange` | `#F58238` | Acción principal, margen, lo que te queda |
| `--orange-2` | `#FBBA89` | Hover y foco |
| `--slate` | `#ACBBD2` | La venta que Amazon te muestra |
| `--cost` | `#34363B` | Costos descontados |
| `--ok` | `#5BD68B` | Indicador de disponibilidad |

Sin degradados decorativos ni sombras. La profundidad se marca con líneas y con el panel `--panel` sobre `--bg`.

## Tipografía

- `--sans`: Hanken Grotesk variable (300 a 700, con cursiva). Es el equivalente web de la Helvetica Neue del manual. Titulares en 300; el énfasis del titular principal va en cursiva 600.
- `--mono`: DM Mono 400 y 500. Solo para leyendas de figuras y cifras de gráficas.
- Fuentes alojadas en `/assets/fonts`, sin peticiones a terceros.

| Uso | Tamaño | Interlínea |
|---|---|---|
| Leyenda mono | 12px | 1.4 |
| Nota | 14px | 1.5 |
| Cuerpo | 17px | 1.6 |
| Entrada | 20px | 1.5 |
| h3 | 24px | 1.2 |
| h2 | clamp(34px, 4.4vw, 64px) | 1.04 |
| h1 | clamp(42px, 6vw, 92px) | 1.0 |
| Cifra | clamp(72px, 12vw, 190px) | 0.9 |

Líneas de cuerpo de 60 a 75 caracteres. Sin mayúsculas sostenidas salvo la palabra SELLIFY.

## Espaciado y forma

- Escala: 4, 8, 12, 16, 24, 32, 48, 64, 96, 144.
- Ancho de contenido `--wrap` 1280px, margen lateral `--gutter`, separación de sección `--sec`.
- Radios: 6px (campos), 14px (paneles), 999px (botones y píldoras).

## Componentes

- Botón principal: píldora naranja con texto oscuro. Secundario: píldora con borde. Discreto: enlace subrayado.
- Leyenda de figura (`.cap`): mono 12px, dice qué es la figura y de dónde sale el dato.
- Visor de casos: panel con pestañas por cliente, texto a la izquierda y figura a la derecha.
- Barra de agenda (`.dock`): píldora fija abajo con disponibilidad y botón.

## Movimiento

1. El scroll mueve los datos: cifras, barras y gráficas avanzan con el scroll (scrub), no por tiempo.
2. Una sola secuencia de entrada, en el hero.
3. Con `prefers-reduced-motion`, todo aparece en su estado final y nada se fija ni se mueve.
4. Sin JavaScript la página se lee completa: el estado por defecto del CSS es el estado final.
5. Librerías: GSAP + ScrollTrigger y Lenis, alojadas en `/assets/vendor`.

## Imágenes

- Asterisco de marca dibujado en canvas con celdas cuadradas.
- Retrato del fundador en blanco y negro.
- Fotos de producto de clientes sobre una pieza clara, nunca recortadas sobre el fondo oscuro.
- Iconos: ninguno, salvo el asterisco y el triángulo de reproducir.

## Cómo se edita

- `index.html` y `en/index.html` salen de una sola plantilla: `tools/build.py`. Los textos de cada idioma están al final de ese archivo.
- Para cambiar un texto: edita `tools/build.py` y ejecuta `python3 tools/build.py .` desde la raíz.
- `tools/` y este archivo no se publican (ver `.vercelignore`).

## Datos de clientes

- Solo se publican cifras aprobadas por Alonso. Aprobado: ventas mensuales de Tatiana Irizar de mayo 2024 a enero 2025.
- Nunca se publican márgenes de clientes ni lo que cobra Sellify.
