# PokeAPI Python SDK

A lightweight, typed Python wrapper around the public [PokeAPI](https://pokeapi.co/).  
This SDK is designed to make it straightforward to fetch Pokémon data from
scripts, notebooks, or larger applications.

---

## Installation

```bash
pip3 install git+https://github.com/drpheel/pokeapi-sdk.git
```

## Quick-Start Example

```python
from pokeapi_sdk import PokeAPIClient

# Option 1 – regular usage
client = PokeAPIClient()

ditto = client.get_pokemon("ditto")
print(ditto["id"])  # 132

# Option 2 – automatic resource cleanup via `with`
with PokeAPIClient() as client:
    charizard = client.get_pokemon("charizard")
    print(charizard["id"])  # 6
```

---

## Design Decisions

Though this SDK is pretty simple, there's a few decisions I made that are somewhat significant:

- Have the client be a context manager, so you can set up and tear down resources in a `with` block.
- When we load all pokemon, do it in a generator so we don't have to load all the pokemon in memory - there's a lot!

---

## API Reference

Every interaction starts by instantiating a `PokeAPIClient`. All network
requests go through a shared `requests.Session` so underlying TCP connections
are reused for efficiency. **The client is a context-manager**, so you can wrap
it in a `with` block to ensure the session is closed automatically when you're
done, or call `close()` manually.

### Lifecycle helpers

| Method | Description |
|--------|-------------|
| `close()` | Close the internal `requests.Session`. Safe to call more than once. |
| `__enter__()` / `__exit__()` | Implement the context-manager protocol; typically accessed via `with PokeAPIClient() as c:`. |

### `PokeAPIClient.__init__(timeout: int = 10)`
Initialises a new client instance.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `timeout` | `int` | `10` | Maximum number of seconds to wait for any HTTP request before raising a timeout error. |

---

### `get_pokemon(identifier: Union[int, str]) -> Dict[str, Any]`
Fetch a single Pokémon by **name** or **National Pokédex ID**.

```python
charizard = client.get_pokemon("charizard")
# or
pikachu   = client.get_pokemon(25)
```

---

### `get_generation(identifier: Union[int, str]) -> Dict[str, Any]`
Retrieve data about a particular generation (e.g. *generation-i*, *generation-viii*).

```python
gen1 = client.get_generation(1)
print(len(gen1["pokemon_species"]))  # 151
```

---

### `get_paginated_resource(resource_name: str, *, limit: int = 20, offset: int = 0) -> Dict[str, Any]`
Low-level helper for manual pagination of any top-level PokeAPI resource.

```python
page2 = client.get_paginated_resource("pokemon", limit=50, offset=50)
```

---

### `get_all_resource_generator(resource_name: str, *, limit: int = 100) -> Iterator[Dict[str, Any]]`
A generator that lazily yields **all** items of a resource, transparently
following pagination under the hood.

```python
for item in client.get_all_resource_generator("ability"):
    print(item["name"])
```

---

### `get_all_pokemon_generator() -> Iterator[Dict[str, Any]]`
Convenience wrapper around `get_all_resource_generator("pokemon")`.

```python
first_500_names = [p["name"] for _, p in zip(range(500), client.get_all_pokemon_generator())]
```

---

### `find_pokemon_by_type(type_name: str) -> Iterator[Dict[str, Any]]`
Yield Pokémon that belong to a specific elemental **type** (e.g. *fire*).

```python
fire_pokemon = list(client.find_pokemon_by_type("fire"))
print(len(fire_pokemon))
```

---

### `get_flavor_text(pokemon_identifier: Union[int, str], *, version: str = "sword", language: str = "en") -> Optional[str]`
Look up a Pokémon's Pokédex **flavor text** for a given game version and language.

```python
entry = client.get_flavor_text("bulbasaur", version="red", language="en")
print(entry)
```

---

### `get_evolution_chain(pokemon_identifier: Union[int, str]) -> Optional[List[str]]`
Return the full evolution chain as a simple list of lowercase names.

```python
print(client.get_evolution_chain("eevee"))
# ['eevee', 'vaporeon', 'jolteon', 'flareon', 'espeon', 'umbreon', 'leafeon', 'glaceon', 'sylveon']
```

---

### `get_pokemon_by_generation(generation_identifier: Union[int, str], *, limit: Optional[int] = None, offset: int = 0, type_filter: Optional[str] = None) -> List[Dict[str, Any]]`
Return Pokémon **species** that belong to a specific generation. Results can be
optionally paginated and/or filtered by **type**.

```python
# First 10 Grass-type Pokémon from Generation-I
results = client.get_pokemon_by_generation(1, limit=10, type_filter="grass")
for p in results:
    print(p["name"])
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `generation_identifier` | `int \| str` | — | Numeric ID or slug (e.g. `"generation-i"`). |
| `limit` | `Optional[int]` | `None` | Maximum number of items to return. `None` → no limit. |
| `offset` | `int` | `0` | Starting index within the (filtered) list. |
| `type_filter` | `Optional[str]` | `None` | Restrict the results to Pokémon of a given type. |

---

## Contributing
Pull requests and feature suggestions are welcome! Please open an issue to
start the discussion.

## License
MIT
