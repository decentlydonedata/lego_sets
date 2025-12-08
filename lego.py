## Libraries
from os import read # For reading CSV files
import csv # For handling CSV files
from turtle import pd # For data manipulation
import pandas # For data manipulation
from sklearn.cluster import KMeans # For K-Means clustering
from sklearn.preprocessing import StandardScaler # For feature scaling
from enum import Enum # For creating enumerations
import random # For random selections
import urllib.request # For downloading images
from PIL import Image # For image handling
import statistics # For statistical calculations
import scipy.stats as stats # For statistical functions
import math # For mathematical functions for statistics purposes

## Constants
MAX_YEAR = 2025 # Hardcoded max year
MIN_YEAR = 2000 # Hardcoded min year
CLUSTERS = 1000 # Number of clusters for K-Means, increase for more precision but slower and may not be good for recommendations based on preferences
NUMBER_OF_SETS_PER_CLUSTER = 3
CONFIDENCE_LEVEL = 0.95 # Confidence level for confidence interval calculations

## Utility functions
# Read integer function
def read_int(prompt, min_val, max_val): 
    while True:
        try:
            value = int(input(prompt))
            if min_val <= value <= max_val:
                return value
            else:
                print(f"Please enter an integer between {min_val} and {max_val}.")
        except ValueError:
            print("Invalid input. Please enter an integer.")
# Read float function
def read_float(prompt, min_val, max_val):
    while True:
        try:
            value = float(input(prompt))
            if min_val <= value <= max_val:
                return value
            else:
                print(f"Please enter a number between {min_val} and {max_val}.")
        except ValueError:
            print("Invalid input. Please enter a number.")
# Read string function
def read_string(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        else:
            print("Input cannot be empty. Please enter a valid string.")
 
## Program Classes 
# Class of a Lego set
class LegoSet:
    def __init__(legoset, id, year, theme, themegroup, subtheme, name, image, price, pieces, minifigs, packaging, owncount, wantcount):
        legoset.id = id # ID of the set (e.g., 10276-1) every lego set has a unique ID
        legoset.year = int(year) # Year of release
        legoset.theme = theme # Theme of the set (e.g., Star Wars, City, Friends) (more specific than theme group)
        legoset.themegroup = themegroup # Theme group of the set (e.g., Licensed, Modern Day, Basic)
        legoset.themegroup_number = 0 # Numerical representation of theme group for clustering
        legoset.subtheme = subtheme # Subtheme of the set (e.g., Star Wars: The Mandalorian, City: Police) (more specific than theme)
        legoset.name = name # Name of the set
        legoset.image = image # Unique part of image URL of the set
        legoset.price = float(price) # Recommended Retail Price of the set in USD
        legoset.pieces = int(pieces) # Number of pieces in the set
        legoset.minifigs = int(minifigs) # Number of minifigures in the set
        legoset.packaging = packaging # Packaging type of the set (e.g., Box, Polybag)
        legoset.owncount = int(owncount) # Number of users who own the set
        legoset.wantcount = int(wantcount) # Number of users who want the set       
        legoset.hours_to_build = legoset.pieces / 250 # Estimated hours to build the set (1 hour per 100 pieces)
        legoset.cluster = 0 # Cluster number assigned to the set
# Class to hold a list of LegoSet objects
class LegoData:
    def __init__(legos): # Initialize LegoData with an empty list
        legos.list = [] # List to hold LegoSet objects
    def add_set(legos, lego_set): # Add a LegoSet object to the list
        legos.list.append(lego_set)
    def remove_set(legos, lego_set): # Remove a LegoSet object from the list
        legos.list.remove(lego_set) 
    def num_of_sets(legos): # Return number of sets in the list
        return int(len(legos.list))

## Load and process data
# Convert CSV data to list of LegoSet objects
def csv_to_class_list(file):
    lego_list = []
    with open(file, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # Skip header row
        for row in reader:
           lego_list.append(LegoSet(*row))
    return lego_list

## Theme functions
# Search for theme group
def list_theme_group(lego_data):
    themegroups = []
    for legoset in lego_data.list: # Iterate through all Lego sets
        if legoset.themegroup not in themegroups: # If the theme group is not already in the list
            themegroups.append(legoset.themegroup) # Add the theme group to the list
    print("Available theme groups:")
    for themegroup in themegroups:
        i = themegroups.index(themegroup) + 1
        print(f"{i} : {themegroup}")
    user_input = read_int("Enter a theme group from the list above: ", 1, len(themegroups))
    if user_input:
        return themegroups[user_input - 1] # returns the selected theme group if input is valid
    return None
# Print a list of themes within a theme group and then pick the specific theme
def list_themes_in_group(themegroup, lego_data):
    themes = []
    for legoset in lego_data.list: # Iterate through all Lego sets
        if legoset.themegroup == themegroup: # If the set's theme group matches the selected theme group
            if legoset.theme not in themes: # If the theme is not already in the list
                themes.append(legoset.theme) # Add the theme to the list
    print(f"Themes in {themegroup} theme group:")
    for theme in themes:
        i = themes.index(theme) + 1
        print(f"{i} : {theme}")
    # Ask user to pick a theme from the list
    user_input = read_int("Enter a theme from the list above: ", 1, len(themes))
    if user_input:
        return themes[user_input - 1] # returns the selected theme if valid
    return None
# Make a LegoData class to hold a list of LegoSet objects with the theme array
def create_lego_data(target_theme, lego_data):
    themed_lego_data = LegoData()
    themed_lego_data.list = []
    for legoset in lego_data.list:
        if legoset.theme == target_theme:
            themed_lego_data.add_set(legoset)
    return themed_lego_data

## Searching for sets
# Search for a set by ID
def search_setid(prompt, lego_data):
    # Ask for a set ID
    user_input = read_string(prompt)
    return find_set_by_id(user_input, lego_data)
# Search for a set by name
def search_setname(prompt, lego_data):
    # Ask for a set name
    user_input = read_string(prompt)
    possible_sets = []
    print("Found set:")
    for lego_set in lego_data.list:
        if user_input in lego_set.name:
            possible_sets.append(lego_set)
    while len(possible_sets) > 15:
        print(f"{len(possible_sets)} sets found. Please refine your search.")
        refined_input = read_string("\nEnter part of set name to refine search: ")
        refined_possible_sets = []
        for lego_set in possible_sets:
            if refined_input in lego_set.name:
                refined_possible_sets.append(lego_set)
        possible_sets = refined_possible_sets
    while len(possible_sets) == 0:
        print("No sets found with that name.")
        while True:
            again = read_string("Would you like to try again? (y/n): ")
            if again.lower() == 'y':
                return search_setname(prompt, lego_data)
            if again.lower() == 'n':
                return 
            else:
                print("Invalid input")
    if len(possible_sets) <= 15:
        for lego_set in possible_sets:
            print_set_details(lego_set)
    return find_set_by_id(read_string("\nEnter ID to confirm set: "), lego_data)
def search_settheme(themed_lego_data):
    # Ask for a set theme
    if len(themed_lego_data.list) == 0:
        print("No sets found with that theme.")
        return None
    elif len(themed_lego_data.list) > 15:
        print(f"{len(themed_lego_data.list)} sets found. Please refine your search.")
        user_input = read_string("Enter part of set name to refine search: ")
        refined_lego_data = LegoData()
        refined_lego_data.list = []
        for set in themed_lego_data.list:
            if user_input in set.name:
                refined_lego_data.add_set(set)
        if len(refined_lego_data.list) == 0:
            print("No sets found with that name.")
            return None
        print("Found sets:")
        for set in refined_lego_data.list:
            print_set_details(set)
    else:
        print("Found sets:")
        for set in themed_lego_data.list:
            print_set_details(set)
    new_id = read_string("Enter ID to confirm set: ")
    while True:
        for lego_set in themed_lego_data.list:
            if lego_set.id == new_id:
                return find_set_by_id(new_id, themed_lego_data)
        print("No set found with that ID.")
        new_id = read_string("Enter ID to confirm set: ")
        
# Find and return a set by ID, if not found print not found and return None
def find_set_by_id(set_id, lego_data):
    for set in lego_data.list:
        if set.id == set_id:
            return set
    print("Set not found")
    return None
# Ask user whether to search by ID or name while loop, and return the found set
def ask_for_search(lego_data):
    while True:
        search_type = read_string("\nSearch by id, name or theme? (id/name/theme): ")
        if search_type == 'id':
            return search_setid("Enter set ID: ", lego_data)
        elif search_type == 'name':
            return search_setname("Enter part of set name (Case Sensitive): ", lego_data)
        elif search_type == 'theme':
            theme = list_themes_in_group(list_theme_group(lego_data), lego_data)
            themed_lego_data = create_lego_data(theme, lego_data)
            return search_settheme(themed_lego_data)
        else:
            print("Invalid input. Please enter 'id', 'name' or 'theme'.")

## Clustering functions
# Given a theme group , return a numerical value for clustering
def themegroup_to_number(lego_set):
    if lego_set.themegroup == "Pre-School":
        return 1
    elif lego_set.themegroup == "Junior":
        return 2
    elif lego_set.themegroup == "Art and Crafts":
        return 3
    elif lego_set.themegroup == "Action & Adventure":
        return 4
    elif lego_set.themegroup == "Construction":
        return 5
    elif lego_set.themegroup == "Educational":
        return 6
    elif lego_set.themegroup == "Basic":
        return 7
    elif lego_set.themegroup == "Modern Day":
        return 8
    elif lego_set.themegroup == "Licensed":
        return 9
    elif lego_set.themegroup == "Historical":
        return 10
    elif lego_set.themegroup == "Model Making":
        return 11
    elif lego_set.themegroup == "Technical":
        return 12
    else:
        return 13
# Set attributes for clustering
def set_attributes(lego_data: LegoData):
    for lego_set in lego_data.list:
            lego_set.hours_to_build = lego_set.pieces / 250
            if lego_set.pieces < 10:
                lego_set.hours_to_build = 0
    for set in lego_data.list:
        set.themegroup_number = themegroup_to_number(lego_data.assign_themegroup(set))
def set_clusters(lego_data: LegoData):
    clusters = lego_data.num_of_sets() // NUMBER_OF_SETS_PER_CLUSTER
    print(f"Setting number of clusters to {clusters} based on {lego_data.num_of_sets()} sets.")
    return clusters
# Cluster lego sets based on attributes
def cluster(lego_data: LegoData):
    cluster_lego_data = []
    for lego_set in lego_data.list:
        cluster_lego_data.append([lego_set.themegroup_number, lego_set.price, lego_set.pieces, lego_set.minifigs, lego_set.year])
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(cluster_lego_data)
    # Apply K-Means clustering
    clusters = set_clusters(lego_data)
    print(f"Clustering into {clusters} clusters.")
    if clusters < 1:
        clusters = 1
    kmeans = KMeans(n_clusters=clusters, random_state=42, n_init='auto')
    cluster_labels = kmeans.fit_predict(data_scaled)
    for lego_set, label in zip(lego_data.list, cluster_labels):
        lego_set.cluster = label
    return lego_data
def simple_cluster(lego_data: LegoData):
    cluster_lego_data = []
    for lego_set in lego_data.list:
        cluster_lego_data.append([lego_set.price, lego_set.pieces, lego_set.minifigs])
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(cluster_lego_data)
    # Apply K-Means clustering
    clusters = set_clusters(lego_data)
    print(f"Clustering into {clusters} clusters.")
    if clusters < 1:
        clusters = 1
    kmeans = KMeans(n_clusters=clusters, random_state=42, n_init='auto')
    cluster_labels = kmeans.fit_predict(data_scaled)
    for lego_set, label in zip(lego_data.list, cluster_labels):
        lego_set.cluster = label
    return lego_data

## Set recommendation system
# Recommendation options enumeration
class RecommendationOptions(Enum):
    RANDOM_SET = 1
    TAILORED_SET = 2
    FIND_SIMILAR = 3
    ADD_TO_FAVOURITES = 4
    EXIT = 5
# Recommendation menu function loop
def recommendation_menu(lego_data, favourites):
    while True:
        print("\nRecommendation Options:")
        print("1. Recommend a random set")
        print("2. Recommend a set based on preferences")
        print("3. Find similar sets")
        print("4. Add set to favourites")
        print("5. Back to main menu")
        rec_choice = read_int("Enter your choice (1-5): ",1,5)
        if rec_choice in range(1, 6):
            rec_choice = RecommendationOptions(int(rec_choice))
            if rec_choice == RecommendationOptions.RANDOM_SET:
                recommend_set(lego_data)
            elif rec_choice == RecommendationOptions.TAILORED_SET:
                tailored_set(lego_data)
            elif rec_choice == RecommendationOptions.FIND_SIMILAR:
                target_set = ask_for_search(lego_data)
                if target_set:
                    themed_lego_data = create_lego_data(target_set.theme, lego_data)
                    similar_sets(target_set, themed_lego_data)
            elif rec_choice == RecommendationOptions.ADD_TO_FAVOURITES:
                set_to_add = ask_for_search(lego_data)
                if set_to_add:
                    favourites.add_set(set_to_add)
                    print("Set added to favourites.")
            elif rec_choice == RecommendationOptions.EXIT:
                break
        else:
            print("Invalid input. Please enter a number between 1 and 5.")
# Recommend a random set
def recommend_set(lego_data):
    recommended_set = random.choice(lego_data.list)
    print("\nRecommended set:")
    print_set_details(recommended_set)
    return recommended_set
# Recommend a set based on user preferences
def tailored_set(lego_data):
    lego_data.add_set(ask_for_set_pref(lego_data))
    print("Set preferences recorded. \n")
    target_set = find_set_by_id("TARGET_ID", lego_data)
    print(f"Looking for... Pieces: {target_set.pieces}, Price: ${target_set.price}, Minifigs: {target_set.minifigs}, Theme: {target_set.theme}")
    themed_lego_data = create_lego_data(target_set.theme, lego_data)
    print(f"Number of sets in themed data: {themed_lego_data.num_of_sets()}")
    similar_sets(target_set, themed_lego_data, detailed_clustering=False)
    lego_data.remove_set(target_set)
def ask_for_set_pref(lego_data):
    print("\nEnter details for the new Lego set:")
    legoset = LegoSet("TARGET_ID", 0, "Theme", "Themegroup", "Subtheme", "Name", "Image", 0.0, 0, 0, "Packaging", 0, 0)
    legoset.themegroup = list_theme_group(lego_data)
    if legoset.themegroup:
        legoset.theme = list_themes_in_group(legoset.themegroup, lego_data)
    legoset.themegroup_number = themegroup_to_number(legoset)
    legoset.price = read_float("What is your ideal price in USD? (5-200) (Smaller values are more likely to be matched): ", 5, 200)
    legoset.minifigs = read_int("What is your ideal minifigure count? (0-5): ", 0, 5)
    legoset.pieces = int(-19.079+9.288*legoset.price)
    return legoset
# Find similar sets based on cluster
def similar_sets(target_set, lego_data, detailed_clustering=True):
    # Find sets in the same cluster as the target set
    print("Clustering sets...")
    if detailed_clustering:
        cluster(lego_data)
    else:
        simple_cluster(lego_data)
    target_cluster = target_set.cluster
    similar_sets = [set for set in lego_data.list if set.cluster == target_cluster and set.id != target_set.id]
    print(f"\nFound {len(similar_sets)} similar sets:")
    for set in similar_sets:
        print_set_details(set)
    if not similar_sets:
        print("No similar sets found.")

## Specific set system
# Set menu options enumeration
class SetMenuOptions(Enum):
    FULL_SET_DETAILS = 1
    GET_LINK = 2
    DISPLAY_IMAGE = 3
    ADD_TO_FAVOURITES = 4
    EXIT = 5
# Set menu loop
def set_menu(lego_set, favourites):
    while True:
        print("\nSet Menu Options:")
        print("1. Full set details")
        print("2. Get link to set")
        print("3. Display image of set")
        print("4. Add to favourites")
        print("5. Back to main menu")
        set_choice = read_int("Enter your choice (1-5): ",1,5)
        if set_choice in range(1, 6):
            set_choice = SetMenuOptions(int(set_choice))
            if set_choice == SetMenuOptions.FULL_SET_DETAILS:
                print_set_details_full(lego_set)
            elif set_choice == SetMenuOptions.GET_LINK:
                set_link(lego_set)
            elif set_choice == SetMenuOptions.DISPLAY_IMAGE:
                display_set_image(lego_set)
            elif set_choice == SetMenuOptions.ADD_TO_FAVOURITES:
                if lego_set:
                    if lego_set in favourites.list:
                        print("Set is already in favourites.")
                    else:
                        favourites.add_set(lego_set)
                        print("Set added to favourites.")
            elif set_choice == SetMenuOptions.EXIT:
                break
        else:
            print("Invalid input. Please enter a number between 1 and 4.")
# Prints brief details of a LegoSet
def print_set_details(lego_set):
    print(f"ID: {lego_set.id}, Name: {lego_set.name}, Year: {lego_set.year}, Pieces: {lego_set.pieces}, Minifigs: {lego_set.minifigs}, Price: ${lego_set.price}")
# Prints full details of a LegoSet
def print_set_details_full(lego_set):
    print("Full set details:")
    print(f"ID: {lego_set.id}, Name: {lego_set.name}, Year: {lego_set.year}, \n"
        f"Theme: {lego_set.theme}, Theme Group: {lego_set.themegroup}, Subtheme: {lego_set.subtheme}, \n"
        f"Price: ${lego_set.price}, Pieces: {lego_set.pieces}, Minifigs: {lego_set.minifigs}, \n"
        f"Packaging: {lego_set.packaging} \n"
        f"Own Count: {lego_set.owncount}, Want Count: {lego_set.wantcount}")
    set_link(lego_set)
# Get link to a set given set
def set_link(lego_set):
    if lego_set:
        name_formatted = lego_set.name.replace(' ', '-')
        name_formatted = name_formatted.replace(':', '')
        name_formatted = name_formatted.replace('.', '')
        name_formatted = name_formatted.replace("'", '')
        print(f"Link to set {lego_set.id}: https://brickset.com/sets/{lego_set.id}-1/{name_formatted}")
    else:
        print("No set provided to get link.")
# Display image of a set given its URL
def display_set_image(lego_set):
    if lego_set and lego_set.image:
        try:
            image_url = f"https://images.brickset.com/sets/images/{lego_set.image}.jpg"
            image_path = "temp_image.jpg"
            print(f"Downloading image from {image_url}...")
            urllib.request.urlretrieve(image_url, image_path)
            img = Image.open(image_path)
            img.show()
        except Exception as e:
            print(f"Error displaying image: {e}")
    else:
        print("No image URL available for this set.")

## Favourites system
# Favourites menu options enumeration
class FavouritesMenuOptions(Enum):
    VIEW_FAVOURITES = 1
    ADD_TO_FAVOURITES = 2
    REMOVE_FROM_FAVOURITES = 3
    EXPORT_FAVOURITES = 4
    BACK_TO_MAIN_MENU = 5
# Print favourites menu options
def print_favourites_menu():
    print("\nFavourites Menu Options:")
    print("1. View favourites")
    print("2. Add to favourites")
    print("3. Remove from favourites")
    print("4. Export favourites")
    print("5. Back to main menu")
# Favourites class to manage favourite Lego sets
class Favourites:
    def __init__(self):
        self.list = []
    def avg_price(self):
        total_price = sum(lego_set.price for lego_set in self.list)
        return total_price / len(self.list) if self.list else 0
    def avg_pieces(self):
        total_pieces = sum(lego_set.pieces for lego_set in self.list)
        return total_pieces / len(self.list) if self.list else 0
    def common_theme(self):
        theme_count = {} # Dictionary to count themes
        for lego_set in self.list:
            if lego_set.theme in theme_count:
                theme_count[lego_set.theme] += 1
            else:
                theme_count[lego_set.theme] = 1
        if theme_count:
            return max(theme_count, key=theme_count.get)
        return None
    def add_set(self, lego_set):
        self.list.append(lego_set)
    def remove_set(self, lego_set):
        self.list.remove(lego_set)
    def print_favourites(self):
        for i, lego_set in enumerate(self.list):
            print(f"{i + 1}. ", end="")
            print_set_details(lego_set)
        print(f"Average Price: ${self.avg_price():.2f}")
        print(f"Average Pieces: {self.avg_pieces():.2f}")
        print(f"Most Common Theme: {self.common_theme()}")
    def export_favourites(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', 'Name', 'Year', 'Theme', 'ThemeGroup', 'Subtheme', 'Image', 'Price ', 'Pieces', 'Minifigs', 'Packaging', 'OwnCount', 'WantCount', 'Link'])
            for lego_set in self.list:
                writer.writerow([lego_set.id, lego_set.name, lego_set.year, lego_set.theme, lego_set.themegroup, lego_set.subtheme, lego_set.image, lego_set.price, lego_set.pieces, lego_set.minifigs, lego_set.packaging, lego_set.owncount, lego_set.wantcount, f"https://brickset.com/sets/{lego_set.id}-1/{lego_set.name.replace(' ', '-')}"])
        print(f"Favourites exported to {filename}")
# Favourites menu loop
def favourites_menu(favourites, lego_data):
    while True:
        print_favourites_menu()
        fav_choice = read_int("Enter your choice (1-5): ",1,5)
        if fav_choice in range(1, 6):
            fav_choice = FavouritesMenuOptions(int(fav_choice))
            if fav_choice == FavouritesMenuOptions.VIEW_FAVOURITES:
                favourites.print_favourites()
            elif fav_choice == FavouritesMenuOptions.ADD_TO_FAVOURITES:
                set_to_add = ask_for_search(lego_data)
                if set_to_add:
                    if set_to_add in favourites.list:
                        print("Set is already in favourites.")
                        set_to_add = ask_for_search(lego_data)
                    else:
                        favourites.add_set(set_to_add)
                        print("Set added to favourites.")
            elif fav_choice == FavouritesMenuOptions.REMOVE_FROM_FAVOURITES:
                if len(favourites.list) == 0:
                    print("No sets in favourites to remove.")
                    continue
                elif len(favourites.list) <= 15:
                    print("Favourites:")
                    for lego_set in favourites.list:
                        print_set_details(lego_set)
                    set_id = read_string("Enter the ID of the set to remove: ")
                    set_to_remove = find_set_by_id(set_id, favourites)
                else:
                    print(f"{len(favourites.list)} sets in favourites. Please search to remove a set.")
                    set_to_remove = ask_for_search(favourites)
                if set_to_remove:
                    favourites.remove_set(set_to_remove)
                    print("Set removed from favourites.")
                else:
                    print("Set not found in favourites.")
            elif fav_choice == FavouritesMenuOptions.EXPORT_FAVOURITES:
                filename = read_string("Enter filename to export favourites: ")
                while filename == "" or any(c in filename for c in '<>:"/\\|?* '):
                    print("Invalid filename. Please avoid using special characters <>:\"/\\|?* and spaces.")
                    filename = read_string("Enter filename to export favourites: ")
                favourites.export_favourites(f"{filename}.csv")
            elif fav_choice == FavouritesMenuOptions.BACK_TO_MAIN_MENU:
                break
        else:
            print("Invalid input. Please enter a number between 1 and 5.")

## Statistics functions
# Subset selection for statistics enum
class SubsetOptions(Enum):
    THEME = 1
    THEME_GROUP = 2
    KEYWORD = 3
    YEAR_RANGE = 4
    FAVOURITES = 5
# Ask user for subset to analyse
def types_of_subsets(lego_data, favourites):
    print("\nWhat kind of legos would you like to analyse?:")
    print("1. Sets of a specific theme")
    print("2. Sets of a specific theme group")
    print("3. Sets which contain a specific keyword")
    print("4. Sets from a specific year")
    print("5. Favourites list")
    choice = read_int("Enter your choice (1-5): ", 1, 5)
    if choice == SubsetOptions.THEME.value:
        theme = list_themes_in_group(list_theme_group(lego_data), lego_data)
        print(f"\nCreating subset for theme: {theme}")
        return create_lego_data(theme, lego_data)
    elif choice == SubsetOptions.THEME_GROUP.value:
        themegroup = list_theme_group(lego_data)
        themedgroup_lego_data = LegoData()
        for legoset in lego_data.list:
            if legoset.themegroup == themegroup:
                themedgroup_lego_data.add_set(legoset)
        print(f"\nCreating subset for theme group: {themegroup}")
        return themedgroup_lego_data
    elif choice == SubsetOptions.KEYWORD.value:
        keyword = read_string("Enter keyword to search for in set names: ")
        keyword_lego_data = LegoData()
        for legoset in lego_data.list:
            if keyword.lower() in legoset.name.lower():
                keyword_lego_data.add_set(legoset)
        print(f"\nCreating subset for keyword: {keyword}")
        return keyword_lego_data
    elif choice == SubsetOptions.YEAR_RANGE.value:
        year = read_int(f"Enter year (e.g., {MIN_YEAR}-{MAX_YEAR}): ", MIN_YEAR, MAX_YEAR)
        year_lego_data = LegoData()
        for legoset in lego_data.list:
            if legoset.year == year:
                year_lego_data.add_set(legoset)
        print(f"\nCreating subset for year: {year}")
        return year_lego_data
    elif choice == SubsetOptions.FAVOURITES.value:
        fav_lego_data = LegoData()
        for legoset in favourites.list:
            fav_lego_data.add_set(legoset)
        print(f"\nCreating subset for favourites: {favourites.list}")
        return fav_lego_data
    else:
        print("Invalid input. Please enter a number between 1 and 5.")
        return None
# Run statistics on a given attribute
def run_statistics(subset, attribute):
    values = []
    for legoset in subset.list:
        attr_value = getattr(legoset, attribute, None)
        if attr_value is not None:
            values.append(attr_value)
    if not values:
        print("No data available for the selected attribute.")
        return
    mean = statistics.mean(values)
    median = statistics.median(values)
    stdev = statistics.pstdev(values) if len(values) > 1 else 0
    conf_interval = stats.t.interval(CONFIDENCE_LEVEL, len(values)-1, loc=mean, scale=stdev/math.sqrt(len(values))) if len(values) > 1 else (mean, mean)
    print(f"Statistics for {attribute.capitalize()}:")
    print(f"Mean: {mean:.2f}")
    print(f"Median: {median:.2f}")
    print(f"Standard Deviation: {stdev:.2f}")
    print(f"{int(CONFIDENCE_LEVEL*100)}% Confidence Interval: ({conf_interval[0]:.2f}, {conf_interval[1]:.2f})")
# Attribute options enumeration
class AttributeOptions(Enum):
    PRICE = 1
    PIECES = 2
    MINIFIGS = 3
    YEAR = 4
    OWN_COUNT = 5
    WANT_COUNT = 6
    HOURS_TO_BUILD = 7
# Attribute menu function
def attribute_menu():
    print("\nAttributes available to Analyse:")
    print("1. Price")
    print("2. Pieces")
    print("3. Minifigs")
    print("4. Year")
    print("5. Own Count")
    print("6. Want Count")
    print("7. Hours to Build")
    choice = read_int("Enter your choice (1-7): ", 1, 7)
    return AttributeOptions(choice)
# Function to analyse attribute based on user input
def analyse_attribute(lego_data, subset, choice):
    if choice == AttributeOptions.PRICE:
        print("\nAnalyzing Price statistics for subset...")
        run_statistics(subset, 'price')
        print("\nAnalyzing Price statistics for entire dataset...")
        run_statistics(lego_data, 'price')
    elif choice == AttributeOptions.PIECES:
        print("\nAnalyzing Pieces statistics for subset...")
        run_statistics(subset, 'pieces')
        print("\nAnalyzing Pieces statistics for entire dataset...")
        run_statistics(lego_data, 'pieces')
    elif choice == AttributeOptions.MINIFIGS:
        print("\nAnalyzing Minifigs statistics for subset...")
        run_statistics(subset, 'minifigs')
        print("\nAnalyzing Minifigs statistics for entire dataset...")
        run_statistics(lego_data, 'minifigs')
    elif choice == AttributeOptions.YEAR:
        print("\nAnalyzing Year statistics for subset...")
        run_statistics(subset, 'year')
        print("\nAnalyzing Year statistics for entire dataset...")
        run_statistics(lego_data, 'year')
    elif choice == AttributeOptions.OWN_COUNT:
        print("\nAnalyzing Own Count statistics for subset...")
        run_statistics(subset, 'owncount')
        print("\nAnalyzing Own Count statistics for entire dataset...")
        run_statistics(lego_data, 'owncount')
    elif choice == AttributeOptions.WANT_COUNT:
        print("\nAnalyzing Want Count statistics for subset...")
        run_statistics(subset, 'wantcount')
        print("\nAnalyzing Want Count statistics for entire dataset...")
        run_statistics(lego_data, 'wantcount')
    elif choice == AttributeOptions.HOURS_TO_BUILD:
        print("\nAnalyzing Hours to Build statistics for subset...")
        run_statistics(subset, 'hours_to_build')
        print("\nAnalyzing Hours to Build statistics for entire dataset...")
        run_statistics(lego_data, 'hours_to_build')
    print("Analysis complete.")
## Main menu functions
# Print menu options recommend a random set, recommend a set based on preferences, find similar sets, Get link to a set, exit
def print_menu():
    print("\nMenu Options:")
    print("1. Recommendations menu")
    print("2. Set finder menu")
    print("3. Favourites menu")
    print("4. Statistics menu")
    print("5. Exit")
class MenuOptions(Enum):
    RECOMMENDATIONS = 1
    SET_FINDER = 2
    FAVOURITES = 3
    STATISTICS = 4
    EXIT = 5
# Welcome message
def welcome():
    print("Welcome to the Lego Set Recommender!")
    print("You can get recommendations based on your preferences or explore similar sets.")
    print("Let's find your perfect Lego set!")
# Main program loop
def main():
    welcome()
    lego_data = LegoData()
    favourites = Favourites()
    print("Loading Lego data...")
    lego_data.list = csv_to_class_list('lego_data_cleaned.csv')
    while True:
        print_menu()
        choice = read_int("Enter your choice (1-5): ",1,5)
        if choice in range(1, 6):
            choice = MenuOptions(int(choice))
            if choice == MenuOptions.RECOMMENDATIONS:
                recommendation_menu(lego_data, favourites)
            elif choice == MenuOptions.SET_FINDER:
                searched_set = ask_for_search(lego_data)
                if searched_set:
                    set_menu(searched_set, favourites)
                else:
                    print("No set found. Returning to main menu.")
            elif choice == MenuOptions.FAVOURITES:
                favourites_menu(favourites, lego_data)
            elif choice == MenuOptions.STATISTICS:
                subset = types_of_subsets(lego_data, favourites)
                if subset:
                    attribute_choice = attribute_menu()
                    analyse_attribute(lego_data, subset, attribute_choice)
                else:
                    print("No sets found in the selected subset for analysis.")
            elif choice == MenuOptions.EXIT:
                print("Thank you for using the Lego Set Recommender. Goodbye!")
                break
        else:
            print("Invalid input. Please enter a number between 1 and 5.")
main()
