import os
import requests
from bs4 import BeautifulSoup
import json

# Define la carpeta temporal
temp_folder = "temp"

# Verifica si la carpeta temporal ya existe, y si no, créala
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)

def get_absolute_path(relative_path):
    """Obtener la ruta absoluta del archivo dada una ruta relativa."""
    script_directory = os.path.dirname(os.path.realpath(__file__))
    absolute_path = os.path.join(script_directory, relative_path)

    # Crear el directorio si no existe
    directory = os.path.dirname(absolute_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    return absolute_path

def download_pokemon_image_url(pokemon_number):
    """Obtener la URL de la imagen del Pokémon con el número de la Pokédex proporcionado."""
    # Eliminar ceros a la izquierda y el símbolo #
    # Eliminar ceros a la izquierda y el símbolo #
    cleaned_number = pokemon_number.lstrip('0#')
    
    # Asegurarse de que el número tenga tres dígitos
    cleaned_number = cleaned_number.zfill(3)
    
    image_url = f"https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Images/Pokemon%20-%20256x256/pokemon_icon_{cleaned_number}_00.png"
    return image_url

# Definir la URL de la página web
url = "https://pokemongo.fandom.com/wiki/List_of_current_Raid_Bosses"

# Realizar la solicitud HTTP y obtener el contenido de la página
response = requests.get(url)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    # Parsear el contenido HTML con BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Encontrar todos los elementos dentro del div principal
    elements = soup.find("div", class_="pogo-list-container bg-raid").find_all("div")

    # Inicializar variables para el título y los datos de la incursión
    raid_level = None
    boss_name = None
    boss_cp = None
    max_capture_cp = None

    # Crear un diccionario para almacenar los datos de incursión agrupados por "Raid Level"
    raid_data_by_level = {}

    for element in elements:
        if element.has_attr("class") and "pogo-list-header" in element["class"]:
            raid_level = element.get_text().strip()
            print("Raid Level:", raid_level)
            raid_data_by_level[raid_level] = []  # Inicializar una lista vacía para el nivel de incursión actual
        elif element.has_attr("class") and "pogo-list-item" in element["class"]:
            raid_info = element.find("div", class_="pogo-list-item-desc")
            no_dex = element.find("div", class_="pogo-list-item-number").text.strip()
            print("No Dex:", no_dex)
            boss_name = raid_info.find("div", class_="pogo-list-item-name").text.strip()
            print("Boss Name:", boss_name)
            boss_cp = raid_info.find("div", class_="pogo-raid-item-desc").find("b", class_="label").next_sibling.strip()
            print("Boss CP:", boss_cp)
            max_capture_cp = raid_info.find("b", string="Max capture CP").find_next("br").next_sibling.strip()
            print("Max Capture CP:", max_capture_cp)
            max_capture_cp_bosst = raid_info.find("div", class_="pogo-raid-item-desc").find("span", class_="pogo-raid-item-wb").text.strip()
            print("Max Capture CP (with Weather Boost):", max_capture_cp_bosst)
            shiny_info = element.find("div", class_="pogo-list-item-image")
            shiny = "Yes" if "shiny" in shiny_info.get("class") else "No"
            print("Shiny:", shiny)
            print("\n")

            # Obtener la URL de la imagen del Pokémon
            pokemon_image_url = download_pokemon_image_url(no_dex)

            # Agregar todos los campos al diccionario raid_data
            raid_data = {
                "No Dex": no_dex,
                "Boss Name": boss_name,
                "Boss CP": boss_cp,
                "Max Capture CP": max_capture_cp,
                "Max Capture CP Bosst": max_capture_cp_bosst,
                "Shiny": shiny,
                "Pokemon Image": pokemon_image_url  # Agregar la URL de la imagen del Pokémon al diccionario
            }
            
            # Agregar el diccionario de datos al nivel de incursión correspondiente
            raid_data_by_level[raid_level].append(raid_data)

    # Define la ruta completa del archivo JSON en la carpeta temporal
    json_file_path = os.path.join(temp_folder, "bossraid.json")

    # Guardar el diccionario en un archivo JSON en la carpeta temporal
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(raid_data_by_level, json_file, ensure_ascii=False, indent=2)

    print(f"Datos guardados en {json_file_path}")

else:
    print(f"Error al obtener la página. Código de estado: {response.status_code}")
