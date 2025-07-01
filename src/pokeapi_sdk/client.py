import requests
from typing import Dict, Any, Optional, Union, Iterator, List

class PokeAPIClient:
    """
    A Python client for interacting with the PokeAPI (https://pokeapi.co/).

    This client provides methods for fetching Pokémon and Generation data,
    and includes handling for paginated resources.
    """
    BASE_URL = "https://pokeapi.co/api/v2"

    def __init__(self, timeout: int = 10):
        """
        Initializes the PokeAPI client.

        Args:
            timeout (int): The timeout in seconds for HTTP requests.
        """
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "python-pokeapi-sdk"})
        self.timeout = timeout

    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        A helper method to make a GET request to a specific endpoint.

        Args:
            endpoint (str): The API endpoint to hit (e.g., 'pokemon/ditto').
            params (Optional[Dict[str, Any]]): A dictionary of query parameters.

        Returns:
            Dict[str, Any]: The JSON response from the API.

        Raises:
            requests.exceptions.HTTPError: If the API returns a non-200 status code.
        """
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = self.session.get(url, timeout=self.timeout, params=params)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while making the request: {e}")
            raise

    def _make_request_to_url(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        A helper method to make a GET request to a full URL.

        Args:
            url (str): The complete URL to hit.
            params (Optional[Dict[str, Any]]): A dictionary of query parameters.

        Returns:
            Dict[str, Any]: The JSON response from the API.

        Raises:
            requests.exceptions.HTTPError: If the API returns a non-200 status code.
        """
        try:
            response = self.session.get(url, timeout=self.timeout, params=params)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while making the request: {e}")
            raise

    def get_pokemon(self, identifier: Union[int, str]) -> Dict[str, Any]:
        """
        Retrieves a single Pokémon by its National Pokédex ID or name.

        Corresponds to: GET /api/v2/pokemon/{id or name}/

        Args:
            identifier (Union[int, str]): The Pokémon's ID (integer) or name (string).

        Returns:
            Dict[str, Any]: A dictionary containing the Pokémon's data.
        """
        # The identifier is part of the URL path, so we ensure it's a string.
        endpoint = f"pokemon/{str(identifier).lower()}"
        return self._make_request(endpoint)

    def get_generation(self, identifier: Union[int, str]) -> Dict[str, Any]:
        """
        Retrieves a single generation by its ID or name.

        Corresponds to: GET /api/v2/generation/{id or name}/

        Args:
            identifier (Union[int, str]): The generation's ID (integer) or name (string).

        Returns:
            Dict[str, Any]: A dictionary containing the generation's data.
        """
        endpoint = f"generation/{str(identifier).lower()}"
        return self._make_request(endpoint)

    def get_paginated_resource(self, resource_name: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Retrieves a paginated list of a given resource (e.g., 'pokemon', 'generation').

        Args:
            resource_name (str): The name of the resource (e.g., 'pokemon').
            limit (int): The number of results to return per page.
            offset (int): The index of the first result to return.

        Returns:
            Dict[str, Any]: A dictionary containing the paginated list and metadata.
        """
        params = {"limit": limit, "offset": offset}
        return self._make_request(resource_name, params=params)

    def get_all_resource_generator(self, resource_name: str, limit: int = 100) -> Iterator[Dict[str, Any]]:
        """
        Provides a generic generator to iterate through any paginated resource.
        
        Yields:
            Iterator[Dict[str, Any]]: A generator that yields summary dicts for the resource.
        """
        offset = 0
        while True:
            page = self.get_paginated_resource(resource_name, limit=limit, offset=offset)
            results = page.get("results", [])
            if not results:
                break
            for item in results:
                yield item
            offset += limit
            
    def get_all_pokemon_generator(self) -> Iterator[Dict[str, Any]]:
        """Provides a generator to iterate through all Pokémon."""
        return self.get_all_resource_generator("pokemon")
        
    # --- New High-Value Functions ---

    def find_pokemon_by_type(self, type_name: str) -> Iterator[Dict[str, Any]]:
        """
        Finds all Pokémon that belong to a specific type.

        Args:
            type_name (str): The type to search for (e.g., 'fire', 'water').

        Yields:
            Iterator[Dict[str, Any]]: A generator that yields Pokémon summary dicts.
        """
        type_data = self._make_request(f"type/{type_name.lower()}")
        pokemon_list = type_data.get("pokemon", [])
        for pokemon_entry in pokemon_list:
            yield pokemon_entry['pokemon']

    def get_flavor_text(self, pokemon_identifier: Union[int, str], version: str = "sword", language: str = "en") -> Optional[str]:
        """
        Retrieves a Pokémon's flavor text (Pokédex entry) for a specific game version.

        Args:
            pokemon_identifier: The name or ID of the Pokémon.
            version (str): The game version to get the text from (e.g., 'red', 'sword').
            language (str): The language of the flavor text.

        Returns:
            Optional[str]: The flavor text, or None if not found.
        """
        pokemon_species_data = self._make_request(f"pokemon-species/{str(pokemon_identifier).lower()}")
        for entry in pokemon_species_data.get("flavor_text_entries", []):
            if entry['language']['name'] == language and entry['version']['name'] == version:
                # Clean up the text by replacing newlines and other special characters.
                return entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
        return None

    def get_evolution_chain(self, pokemon_identifier: Union[int, str]) -> Optional[List[str]]:
        """
        Retrieves a Pokémon's full evolution chain as a simple list of names.

        Args:
            pokemon_identifier: The name or ID of the Pokémon.

        Returns:
            Optional[List[str]]: A list of Pokémon names in evolution order, or None.
        """
        try:
            species_data = self._make_request(f"pokemon-species/{str(pokemon_identifier).lower()}")
            evolution_chain_url = species_data['evolution_chain']['url']
            print(f"Evolution chain URL: {evolution_chain_url}")
            chain_data = self._make_request_to_url(evolution_chain_url)
            
            chain = []
            
            def _traverse_chain(chain_link: Dict[str, Any]):
                """Helper function to recursively parse the evolution chain."""
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
        """
        Gets all Pokémon species belonging to a specific generation, with optional filtering and pagination.

        Args:
            generation_identifier: The ID or name of the generation (e.g., 1, 'generation-i').
            limit (Optional[int]): The maximum number of Pokémon to return.
            offset (int): The starting index for the Pokémon list.
            type_filter (Optional[str]): A Pokémon type to filter by (e.g., 'grass', 'fire').

        Returns:
            A list of Pokémon species summary dicts.
        """
        generation_data = self._make_request(f"generation/{str(generation_identifier).lower()}")
        pokemon_species_list = generation_data.get("pokemon_species", [])
        print(f"Got Pokemon Species List")
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
        print(f"Sorted Pokemon Species List")
        # Apply pagination
        paginated_list = pokemon_species_list[offset:]
        if limit is not None:
            paginated_list = paginated_list[:limit]
        print(f"Paginated List: {paginated_list}")
        return paginated_list

    def close(self):
        """Closes the underlying requests Session."""
        if self.session is not None:
            self.session.close()

    def __enter__(self):
        """Enables usage of the client as a context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensures the requests Session is properly closed when exiting a context."""
        self.close()