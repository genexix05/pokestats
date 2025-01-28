# utils/pokeapi.py
import requests
import pokebase


def get_pokemon_stats(pokemon_name):
    try:
        pokemon = pokebase.pokemon(pokemon_name)
        stats = {stat.stat.name: stat.base_stat for stat in pokemon.stats}
        sprite_url = pokemon.sprites.front_default
        return stats, sprite_url
    except Exception as e:
        print(f"No se pudo encontrar el Pokémon {pokemon_name}: {e}")
        return None, None

def get_pokemon_names():
    response = requests.get('https://pokeapi.co/api/v2/pokemon?limit=10000')
    data = response.json()
    names = [pokemon['name'] for pokemon in data['results']]
    return set(names)