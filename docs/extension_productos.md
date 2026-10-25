# Extensión de Productos (Lab 2)

## Filtros
GET /productos?categoria=bebidas&precio_max=100 (ambos opcionales).
precio_max no numérico responde 422.

## Índice único sobre id
- Velocidad: la búsqueda por id usa IXSCAN y examina 1 documento
  (totalDocsExamined: 1) en vez de recorrer toda la colección (COLLSCAN).
- Error que evita: dos productos con el mismo id (E11000 duplicate key)
