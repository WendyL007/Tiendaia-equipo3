import pandas as pd
import matplotlib.pyplot as plt

df2 = pd.read_csv("docs/lab5/bench_2nucleos.csv")
df4 = pd.read_csv("docs/lab5/bench_4nucleos.csv")

fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

for ax, df, titulo in [(axes[0], df2, "2 Núcleos"), (axes[1], df4, "4 Núcleos")]:
    for nj in sorted(df["n_jobs"].unique()):
        sub = df[df["n_jobs"] == nj]
        ax.plot(sub["filas"], sub["entrenar_s"], marker="o", label=f"n_jobs={nj}")
    ax.set_title(f"Entrenamiento ({titulo})")
    ax.set_xlabel("Número de filas")
    ax.set_ylabel("Tiempo de entrenamiento (s)")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend()

plt.tight_layout()
plt.savefig("docs/lab5/grafica_entrenamiento.png", dpi=150)
print("Gráfica guardada en docs/lab5/grafica_entrenamiento.png")