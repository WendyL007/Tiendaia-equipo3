import csv
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FUENTE = ROOT / "resultados_almacenamiento.csv"
TABLA = ROOT / "tabla_comparativa.csv"
SALIDA = ROOT / "reporte"
ORDEN_DESTINOS = {
    "seaweedfs-laptop": 0,
    "seaweedfs-codespace": 1,
    "supabase-laptop": 2,
    "supabase-codespace": 3,
    "b2-laptop": 4,
    "b2-codespace": 5,
}

def combinar(muestras):
    cantidad = sum(int(fila["n"]) for fila in muestras)
    if not cantidad:
        return 0.0, 0.0
    media = sum(float(fila["media"]) * int(fila["n"]) for fila in muestras) / cantidad
    varianza = sum(
        (int(fila["n"]) - 1) * float(fila["desv"]) ** 2
        + int(fila["n"]) * (float(fila["media"]) - media) ** 2
        for fila in muestras
    ) / max(cantidad - 1, 1)
    return media, math.sqrt(varianza)

def guardar_tabla(grupos, destinos, pruebas):
    with TABLA.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["prueba", "unidad", *destinos])
        for prueba in pruebas:
            muestra = next(
                grupos[(destino, prueba)][0]
                for destino in destinos
                if (destino, prueba) in grupos
            )
            fila = [prueba, muestra["unidad"]]
            for destino in destinos:
                registros = grupos.get((destino, prueba), [])
                if registros:
                    media, desv = combinar(registros)
                    fila.append(f"{media:.2f} +/- {desv:.2f}")
                else:
                    fila.append("")
            escritor.writerow(fila)

def svg_grafica(destinos, pruebas, grupos, titulo, nombre, etiqueta_x):
    ancho, alto = 940, 520
    izquierda, arriba, ancho_plot, alto_plot = 90, 75, 650, 340
    combinados = {
        destino: {
            prueba: combinar(grupos[(destino, prueba)])
            for prueba in pruebas
            if (destino, prueba) in grupos
        }
        for destino in destinos
    }
    maximo = max(
        (media + desv for serie in combinados.values() for media, desv in serie.values()),
        default=1.0,
    )
    maximo = max(maximo * 1.15, 1.0)
    colores = ["#1769aa", "#d1495b", "#2a9d8f", "#e09f3e", "#6a4c93", "#4f772d"]
    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{ancho / 2}" y="35" text-anchor="middle" font-family="sans-serif" font-size="22">{titulo}</text>',
    ]
    for paso in range(6):
        y_valor = maximo * paso / 5
        y = arriba + alto_plot * (1 - paso / 5)
        partes.extend([
            f'<line x1="{izquierda}" y1="{y:.1f}" x2="{izquierda + ancho_plot}" y2="{y:.1f}" stroke="#ddd"/>',
            f'<text x="{izquierda - 12}" y="{y + 5:.1f}" text-anchor="end" font-family="sans-serif" font-size="12">{y_valor:.2f}</text>',
        ])
    n_pruebas = max(len(pruebas), 1)
    posiciones = {
        prueba: izquierda + ancho_plot * (i + 0.5) / n_pruebas
        for i, prueba in enumerate(pruebas)
    }
    for i, prueba in enumerate(pruebas):
        x = posiciones[prueba]
        partes.append(
            f'<text x="{x:.1f}" y="{arriba + alto_plot + 25}" text-anchor="middle" '
            f'font-family="sans-serif" font-size="12">{etiqueta_x(prueba)}</text>'
        )
    for i, destino in enumerate(destinos):
        color = colores[i % len(colores)]
        puntos = []
        for prueba in pruebas:
            if prueba not in combinados[destino]:
                if len(puntos) > 1:
                    partes.append(
                        f'<polyline points="{" ".join(puntos)}" fill="none" stroke="{color}" stroke-width="2"/>'
                    )
                puntos = []
                continue
            media, desv = combinados[destino][prueba]
            x = posiciones[prueba]
            y = arriba + alto_plot * (1 - media / maximo)
            y1 = arriba + alto_plot * (1 - min(media + desv, maximo) / maximo)
            y2 = arriba + alto_plot * (1 - max(media - desv, 0) / maximo)
            puntos.append(f"{x:.1f},{y:.1f}")
            partes.extend([
                f'<line x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" stroke="{color}"/>',
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{color}"/>',
            ])
        if len(puntos) > 1:
            partes.append(
                f'<polyline points="{" ".join(puntos)}" fill="none" stroke="{color}" stroke-width="2"/>'
            )
        leyenda_y = arriba + 20 * i
        partes.extend([
            f'<line x1="770" y1="{leyenda_y}" x2="795" y2="{leyenda_y}" stroke="{color}" stroke-width="3"/>',
            f'<text x="802" y="{leyenda_y + 5}" font-family="sans-serif" font-size="13">{destino}</text>',
        ])
    partes.extend([
        f'<line x1="{izquierda}" y1="{arriba + alto_plot}" x2="{izquierda + ancho_plot}" y2="{arriba + alto_plot}" stroke="#333"/>',
        f'<line x1="{izquierda}" y1="{arriba}" x2="{izquierda}" y2="{arriba + alto_plot}" stroke="#333"/>',
        f'<text x="25" y="{arriba + alto_plot / 2}" transform="rotate(-90 25 {arriba + alto_plot / 2})" text-anchor="middle" font-family="sans-serif" font-size="14">{"Valor medio (con barra de desviación)"}</text>',
        f'<text x="{izquierda + ancho_plot / 2}" y="{alto - 24}" text-anchor="middle" font-family="sans-serif" font-size="14">{etiqueta_x("eje")}</text>',
        "</svg>",
    ])
    (SALIDA / nombre).write_text("\n".join(partes), encoding="utf-8")

def main():
    with FUENTE.open(newline="", encoding="utf-8-sig") as archivo:
        filas = list(csv.DictReader(archivo))
    if not filas:
        raise SystemExit(f"No hay mediciones en {FUENTE}")

    grupos = defaultdict(list)
    for fila in filas:
        grupos[(fila["destino"], fila["prueba"])].append(fila)
    destinos = sorted(
        {fila["destino"] for fila in filas},
        key=lambda destino: (ORDEN_DESTINOS.get(destino, 99), destino),
    )
    pruebas = list(dict.fromkeys(fila["prueba"] for fila in filas))
    guardar_tabla(grupos, destinos, pruebas)
    SALIDA.mkdir(exist_ok=True)

    tamanos = ["subida 1 MB", "subida 10 MB", "subida 25 MB"]
    bajadas = ["bajada 1 MB", "bajada 10 MB", "bajada 25 MB"]
    svg_grafica(destinos, tamanos, grupos, "Velocidad de subida", "grafica_subida.svg",
                lambda prueba: prueba.split()[1] if prueba != "eje" else "Tamaño del archivo (MB)")
    svg_grafica(destinos, bajadas, grupos, "Velocidad de descarga", "grafica_bajada.svg",
                lambda prueba: prueba.split()[1] if prueba != "eje" else "Tamaño del archivo (MB)")
    svg_grafica(destinos, ["200 archivos de 10 KB"], grupos, "Latencia de archivos pequeños",
                "grafica_latencia_pequenos.svg",
                lambda prueba: "200 archivos" if prueba != "eje" else "Prueba")
    svg_grafica(destinos, ["rendimiento pequenos"], grupos, "Rendimiento de archivos pequeños",
                "grafica_rendimiento_pequenos.svg",
                lambda prueba: "200 archivos" if prueba != "eje" else "Prueba")
    print(f"Tabla y 4 gráficas generadas para {len(destinos)} destinos: {', '.join(destinos)}")

if __name__ == "__main__":
    main()
