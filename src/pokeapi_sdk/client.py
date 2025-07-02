import requests
from typing import Dict, Any, Optional, Union, Iterator, List

class PokeAPIClient:
    BASE_URL = "https://pokeapi.co/api/v2"

    def __init__(self, timeout: int = 10):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "python-pokeapi-sdk"})
        self.timeout = timeout

    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = self.session.get(url, timeout=self.timeout, params=params)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while making the request: {e}")
            raise

    def _make_request_to_url(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            response = self.session.get(url, timeout=self.timeout, params=params)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while making the request: {e}")
            raise

    def get_pokemon(self, identifier: Union[int, str]) -> Dict[str, Any]:
        # The identifier is part of the URL path, so we ensure it's a string.
        endpoint = f"pokemon/{str(identifier).lower()}"
        return self._make_request(endpoint)

    def get_generation(self, identifier: Union[int, str]) -> Dict[str, Any]:
        endpoint = f"generation/{str(identifier).lower()}"
        return self._make_request(endpoint)

    def get_paginated_resource(self, resource_name: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        params = {"limit": limit, "offset": offset}
        return self._make_request(resource_name, params=params)

    def get_all_resource_generator(self, resource_name: str, limit) -> Iterator[Dict[str, Any]]:
        offset = 0
        while True:
            page = self.get_paginated_resource(resource_name, limit=limit, offset=offset)
            results = page.get("results", [])
            if not results:
                break
            for item in results:
                yield item
            offset += limit
            
    def get_all_pokemon_generator(self, limit: int = 100) -> Iterator[Dict[str, Any]]:
        return self.get_all_resource_generator("pokemon", limit=limit)
        
    def find_pokemon_by_type(self, type_name: str) -> Iterator[Dict[str, Any]]:
        type_data = self._make_request(f"type/{type_name.lower()}")
        pokemon_list = type_data.get("pokemon", [])
        for pokemon_entry in pokemon_list:
            yield pokemon_entry['pokemon']

    def get_flavor_text(self, pokemon_identifier: Union[int, str], version: str = "sword", language: str = "en") -> Optional[str]:
        pokemon_species_data = self._make_request(f"pokemon-species/{str(pokemon_identifier).lower()}")
        for entry in pokemon_species_data.get("flavor_text_entries", []):
            if entry['language']['name'] == language and entry['version']['name'] == version:
                # Clean up the text by replacing newlines and other special characters.
                return entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
        return None

    def get_evolution_chain(self, pokemon_identifier: Union[int, str]) -> Optional[List[str]]:
        try:
            species_data = self._make_request(f"pokemon-species/{str(pokemon_identifier).lower()}")
            evolution_chain_url = species_data['evolution_chain']['url']
            chain_data = self._make_request_to_url(evolution_chain_url)
            
            chain = []
            
            def _traverse_chain(chain_link: Dict[str, Any]):
                chain.append(chain_link['species']['name'])
                if 'evolves_to' in chain_link and chain_link['evolves_to']:
                    for next_link in chain_link['evolves_to']:
                        _traverse_chain(next_link)

            _traverse_chain(chain_data['chain'])
            return chain
        except requests.exceptions.HTTPError:
            return None

    def get_pokemon_by_generation(
        self, 
        generation_identifier: Union[int, str], 
        limit: Optional[int] = None, 
        offset: int = 0,
        type_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        generation_data = self._make_request(f"generation/{str(generation_identifier).lower()}")
        pokemon_species_list = generation_data.get("pokemon_species", [])
        # If a type filter is provided, find the intersection of the two lists.
        if type_filter:
            type_pokemon = self.find_pokemon_by_type(type_filter)
            type_pokemon_names = {p['name'] for p in type_pokemon}
            
            # Filter the generation list by the names found in the type list
            pokemon_species_list = [
                p for p in pokemon_species_list if p['name'] in type_pokemon_names
            ]

        # Sort by the entry number in the URL to ensure consistent order.
        pokemon_species_list.sort(key=lambda p: int(p['url'].split('/')[-2]))
        # Apply pagination
        paginated_list = pokemon_species_list[offset:]
        if limit is not None:
            paginated_list = paginated_list[:limit]
        return paginated_list

    def get_all_pokemon_range(self, start: int, end: int) -> List[Dict[str, Any]]:
        results = []
        offset = start

        while offset < end:
            fetch_limit = min(100, end - offset)
            page = self.get_paginated_resource('pokemon', limit=fetch_limit, offset=offset)
            page_results = page.get("results", [])
            if not page_results:
                break
            results.extend(page_results)
            if len(page_results) < fetch_limit:
                break
            offset += fetch_limit
        return results

    def close(self):
        if self.session is not None:
            self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()