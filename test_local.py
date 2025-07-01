# test_local.py
from pokeapi_sdk import PokeAPIClient
import requests
import random

print("--- Starting local SDK test ---")

# 1. Initialize the client
client = PokeAPIClient()

# 2. Test fetching a specific Pokémon
try:
    print("\nTesting get_pokemon('ditto')...")
    ditto = client.get_pokemon("ditto")
    print(f"Successfully fetched {ditto['name'].capitalize()} (ID: {ditto['id']})")
except requests.exceptions.HTTPError as e:
    print(f"An error occurred: {e}")

# 3. Test the generator
try:
    print("\nTesting the Pokémon generator (first 5)...")
    pokemon_generator = client.get_all_pokemon_generator()
    for i, pokemon in enumerate(pokemon_generator):
        if i >= 5:
            break
        print(f"- {pokemon['name'].capitalize()}")
    
    # --- 1. Get a specific Pokémon by name ---
    print("--- Fetching a specific Pokémon (Pikachu) ---")
    try:
        pikachu_data = client.get_pokemon("pikachu")
        print(f"Name: {pikachu_data['name'].capitalize()}")
        print(f"ID: {pikachu_data['id']}")
        print(f"Base Experience: {pikachu_data['base_experience']}")
        types = [t['type']['name'] for t in pikachu_data['types']]
        print(f"Types: {', '.join(types)}")
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")

    print("\n" + "="*40 + "\n")

    # --- 2. Get a specific Generation by ID ---
    print("--- Fetching a specific Generation (Gen 1) ---")
    try:
        gen1_data = client.get_generation(1)
        print(f"Generation Name: {gen1_data['name'].upper()}")
        print(f"Main Region: {gen1_data['main_region']['name'].capitalize()}")
        print(f"Number of Pokémon: {len(gen1_data['pokemon_species'])}")
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")

    print("\n" + "="*40 + "\n")

    # --- 3. Handle pagination with a simple paginated fetch ---
    print("--- Fetching a paginated list of Pokémon (first 5) ---")
    try:
        pokemon_page = client.get_paginated_resource("pokemon", limit=5, offset=0)
        print(f"Total Pokémon count: {pokemon_page['count']}")
        for pokemon in pokemon_page['results']:
            print(f"- {pokemon['name'].capitalize()}")
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")

    print("\n" + "="*40 + "\n")

    # --- 3.5. Fetch multiple random pages ---
    print("--- Fetching multiple random pages of Pokémon ---")
    try:
        # Get 3 random pages with different offsets
        page_size = 10
        total_pokemon = 1008  # Approximate total number of Pokémon
        max_offset = total_pokemon - page_size
        
        for page_num in range(1, 4):
            # Generate a random offset
            random_offset = random.randint(0, max_offset)
            print(f"\n--- Page {page_num} (offset: {random_offset}) ---")
            
            pokemon_page = client.get_paginated_resource("pokemon", limit=page_size, offset=random_offset)
            print(f"Showing Pokémon {random_offset + 1}-{random_offset + len(pokemon_page['results'])} of {pokemon_page['count']}")
            
            for i, pokemon in enumerate(pokemon_page['results'], 1):
                print(f"  {random_offset + i:3d}. {pokemon['name'].capitalize()}")
                
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")

    print("\n" + "="*40 + "\n")

    # --- 4. Use the generator to iterate through all Pokémon ---
    print("--- Using a generator to list the first 10 Pokémon efficiently ---")
    try:
        pokemon_generator = client.get_all_pokemon_generator()
        for i, pokemon in enumerate(pokemon_generator):
            if i >= 10:
                break
            print(f"- {pokemon['name'].capitalize()}")
        print("... and so on, without loading all at once.")
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")


    # 1. Test find_pokemon_by_type
    try:
        print("\nTesting find_pokemon_by_type('fire')...")
        fire_pokemon_gen = client.find_pokemon_by_type("fire")
        # Get the first 5 fire Pokémon
        first_five = [next(fire_pokemon_gen) for _ in range(5)]
        names = [p['name'] for p in first_five]
        assert 'charmander' in names
        assert 'vulpix' in names
        print(f"✅ Found fire Pokémon, including: {', '.join(names)}")
    except Exception as e:
        print(f"❌ Test failed: {e}")

    # 2. Test get_flavor_text
    try:
        print("\nTesting get_flavor_text('pikachu', version='sword')...")
        flavor_text = client.get_flavor_text('pikachu', version='sword')
        assert flavor_text is not None
        assert "electricity" in flavor_text
        print(f"✅ Got flavor text for Pikachu: \"{flavor_text[:80]}...\"")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    # 3. Test get_evolution_chain
    try:
        print("\nTesting get_evolution_chain('charmander')...")
        evo_chain = client.get_evolution_chain('charmander')
        expected_chain = ['charmander', 'charmeleon', 'charizard']
        assert evo_chain == expected_chain
        print(f"✅ Got correct evolution chain: {' -> '.join(evo_chain)}")
        
        print("\nTesting get_evolution_chain('eevee')...")
        eevee_chain = client.get_evolution_chain('eevee')
        # Eevee has many evolutions, so we just check for a few key ones.
        assert 'eevee' in eevee_chain
        assert 'vaporeon' in eevee_chain
        assert 'jolteon' in eevee_chain
        assert 'flareon' in eevee_chain
        print(f"✅ Got Eevee's complex evolution chain ({len(eevee_chain)} members).")

    except Exception as e:
        print(f"❌ Test failed: {e}")

    try:
        print("\nTesting get_pokemon_by_generation(1)...")
        gen1_pokemon_list = client.get_pokemon_by_generation(1)
        assert len(gen1_pokemon_list) == 151
        print(f"✅ Got all {len(gen1_pokemon_list)} Pokémon from Generation 1.")

        print("\nTesting get_pokemon_by_generation(1) with pagination...")
        paginated_list = client.get_pokemon_by_generation(3, limit=10, offset=10)
        assert len(paginated_list) == 10
        assert paginated_list[0]['name'] == 'mightyena'
        print(f"✅ Got 10 Pokémon with offset 10. First was '{paginated_list[0]['name']}'.")

        print("\nTesting get_pokemon_by_generation(1) with type filter 'grass'...")
        grass_pokemon = client.get_pokemon_by_generation(6, type_filter='grass')
        grass_names = {p['name'] for p in grass_pokemon}
        assert 'quilladin' in grass_names
        assert 'chespin' in grass_names
        assert 'charmander' not in grass_names
        print(f"✅ Found {len(grass_pokemon)} grass Pokémon in Gen 6, including 'quilladin'.")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")

except requests.exceptions.HTTPError as e:
    print(f"An error occurred: {e}")


print("\n--- Local SDK test finished ---")