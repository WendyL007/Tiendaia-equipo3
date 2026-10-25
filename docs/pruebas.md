# Tabla de pruebas Lab 2

| # | Petición | Esperado | Obtenido |
|---|---|---|---|
| 1 | POST /api/clientes correo repetido | 409 | 409 |
| 2 | POST /api/clientes correo inválido | 422 | (pon lo que te salió) |
| 3 | POST /api/ventas cliente 9999 | 422 | 422 |
| 4 | POST /api/ventas cantidad 0 | 422 | 422 |
| 5 | GET /api/productos/9999 | 404 | 404 |
| 6 | GET /api/ia/predict sin entrenar | 409 | 409 |
| 7 | POST /api/ia/train con pocas ventas | 400 | 400 |
| 8 | Clientes detenido + venta | 5xx | 500 (health: clientes false) |
| 9 | restart y contar ventas | mismo número | (antes y después) |
| 10 | GET /api/productos sin filtros | 200, todos | 200 |
| 11 | ?categoria=bebidas | 200, 2 productos | 200 |
| 12 | ?categoria=bebidas&precio_max=100 | solo Agua de jamaica | OK |
| 13 | ?precio_max=abc | 422 | 422 |