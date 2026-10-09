import time
import requests

print("=== 1. GRAPHQL: Consulta de 10 países ===")
query_paises = """
{
  countries(filter: { code: { in: ["MX", "AR", "BR", "CO", "PE", "CL", "ES", "US", "CA", "JP"] } }) {
    name
    capital
    currency
  }
}
"""

t0 = time.perf_counter()
r_gql_paises = requests.post(
    "https://countries.trevorblades.com/",
    json={"query": query_paises},
    timeout=10
)
ms_paises = (time.perf_counter() - t0) * 1000

print(f"Peticiones: 1 | Bytes: {len(r_gql_paises.content)} | Tiempo: {ms_paises:.0f} ms")
print(f"Países obtenidos: {len(r_gql_paises.json()['data']['countries'])}\n")


print("=== 2. REST vs GRAPHQL: 10 Pokémon ===")
nombres = ["pikachu", "bulbasaur", "charmander", "squirtle", "eevee",
           "snorlax", "gengar", "onix", "psyduck", "jigglypuff"]

# --- Pruebas REST (10 peticiones individuales) ---
bytes_rest = 0
t0 = time.perf_counter()
for pokemon in nombres:
    r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon}", timeout=10)
    bytes_rest += len(r.content)
ms_rest = (time.perf_counter() - t0) * 1000

print(f"[REST]    Peticiones: {len(nombres)} | Bytes totales: {bytes_rest} | Tiempo total: {ms_rest:.0f} ms")


# --- Pruebas GraphQL (1 sola petición para los 10) ---
query_pokemon = """
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

t0 = time.perf_counter()
r_gql_poke = requests.post(
    "https://graphql.pokeapi.co/v1beta2",
    json={"query": query_pokemon},
    timeout=10
)
ms_gql = (time.perf_counter() - t0) * 1000

print(f"[GraphQL] Peticiones: 1  | Bytes totales: {len(r_gql_poke.content)} | Tiempo total: {ms_gql:.0f} ms")