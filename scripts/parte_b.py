import time
import requests

# ==========================================
# PASO 1: Consulta GraphQL (Países)
# ==========================================
query_paises = """
{
  countries(filter: { code: { in: ["MX", "AR", "BR", "CO", "PE", "CL", "ES", "US", "CA", "JP"] } }) {
    name
    capital
    currency
  }
}
"""

t = time.perf_counter()
r = requests.post("https://countries.trevorblades.com/", json={"query": query_paises})
ms = (time.perf_counter() - t) * 1000

print("=== PASO 1: GraphQL Países ===")
print(f"Código: {r.status_code} | Tiempo: {ms:.0f} ms | Bytes: {len(r.content)}")


# ==========================================
# PASO 2: Comparativa REST vs GraphQL (10 Pokémon)
# ==========================================
pokemones = ["pikachu", "bulbasaur", "charmander", "squirtle", "eevee",
             "snorlax", "gengar", "onix", "psyduck", "jigglypuff"]

# --- Pruebas REST (10 llamadas individuales) ---
t = time.perf_counter()
bytes_rest = 0
for p in pokemones:
    res_rest = requests.get(f"https://pokeapi.co/api/v2/pokemon/{p}")
    bytes_rest += len(res_rest.content)
ms_rest = (time.perf_counter() - t) * 1000

print("\n=== PASO 2: Comparativa ===")
print(f"REST    -> Tiempo: {ms_rest:.0f} ms | Bytes: {bytes_rest} | Peticiones: 10")

# --- Pruebas GraphQL (1 sola llamada) ---
query_poke = """
{
  pokemon_v2_pokemon(where: {name: {_in: ["pikachu", "bulbasaur", "charmander", "squirtle", "eevee", "snorlax", "gengar", "onix", "psyduck", "jigglypuff"]}}) {
    name
    height
    pokemon_v2_pokemontypes {
      pokemon_v2_type {
        name
      }
    }
  }
}
"""

t = time.perf_counter()
res_gql = requests.post("https://graphql.pokeapi.co/v1beta2", json={"query": query_poke})
ms_gql = (time.perf_counter() - t) * 1000

print(f"GraphQL -> Tiempo: {ms_gql:.0f} ms | Bytes: {len(res_gql.content)} | Peticiones: 1")