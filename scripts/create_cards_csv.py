import pandas as pd
import json

MONTH_FILTER = None

# Loading card details
file_path = '../data/cards_draft.json'
with open(file_path, 'r', encoding='utf-8') as file:
    cards_draft = json.load(file)

cards = pd.DataFrame(cards_draft).set_index('name')

# Extract 'en' link from 'image_uris'
cards['image_url'] = cards['image_uris'].apply(lambda x: x['en'] if 'en' in x else None)

# Removing irrelevant columns
cards.drop(columns=['mana_cost', 'image_uris'], inplace=True)

# Adding Cracked Bauble
new_row_data = {'rarity': 'token', "collector_number": "MST224", "type": ["Resource"], "image_url": "https://storage.googleapis.com/fabmaster/cardfaces/2024-MST/EN/MST224.png"}
cards.loc["Cracked Bauble (yellow)"] = new_row_data

file_path = '../data/all_cards.json'
with open(file_path, 'r', encoding='utf-8') as file:
    all_cards = json.load(file)

all_cards = pd.DataFrame(all_cards)

# Define the pitch_color function
def pitch_color(pitch):
    if pitch == "1":
        return " (red)"
    elif pitch == "2":
        return " (yellow)"
    elif pitch == "3":
        return " (blue)"
    else:
        return ""

all_cards['New Index'] = all_cards.apply(lambda row: f"{row['Name']}{pitch_color(row['Pitch'])}", axis=1)

all_cards.set_index('New Index', inplace=True)

cards = cards.merge(all_cards, left_index=True, right_index=True, how='inner')

cards.index.name = "Name"

cards.to_csv('../data/cards_details.csv')


# Extracting cards from decks

other_heroes = {
    "Assassin": ["Illusionist", "Ninja"],
    "Illusionist": ["Assassin", "Ninja"],
    "Ninja": ["Assassin", "Illusionist"]
}

def can_be_played(hero, card):
    card = cards.loc[card]
    for other_hero in other_heroes[hero]:
        types = card["Types"].split(", ")
        if other_hero in types:
            return False
    return True

class_dict = {}
card_dict = {}
equip_dict = {}
all_cards = {}
data_filter = False

deck_dict = {"Assassin": [], "Illusionist": [], "Ninja": []}
current_deck = None

with open("../data/decks.txt", "r", encoding='utf-8') as file:
    lines = file.readlines()
    current_hero = None
    for line in lines:
        if MONTH_FILTER is not None and line.startswith("2024-"):
            month = line[5:7]
            if month == MONTH_FILTER:
                data_filter = True
                continue
            else:
                data_filter = False
                continue

        if MONTH_FILTER is not None and not data_filter:
            continue

        # Checking for deck class
        if line.startswith("Class: "):
            hero = line.split("Class: ")[1].replace("\n", "")
            if hero not in class_dict:
                class_dict[hero] = 0
                card_dict[hero] = {}
                equip_dict[hero] = {}
            class_dict[hero] += 1

            current_deck = {"cards": [], "equips": []}
            deck_dict[hero].append(current_deck)
        
        # Checking for card
        if line.startswith("("):
            tmp = line.split(") ", 1)
            if len(tmp) < 2 or "3-0" in tmp[0]:
                continue
            number = int(tmp[0][1:])
            card = tmp[1].replace("\n", "")
            if card not in card_dict[hero]:
                card_dict[hero][card] = 0
                if card not in all_cards:
                    all_cards[card] = 0
            if can_be_played(hero, card):
                card_dict[hero][card] += number
                all_cards[card] += number
                for _ in range(number):
                    current_deck["cards"].append(card)
        
        # Checking for equipments
        if line.startswith("Equipment: "):
            line = line.split("Equipment: ")[1]
            equips = line.replace("\n", "").split(", ")
            for equip in equips:
                if equip not in equip_dict[hero]:
                    equip_dict[hero][equip] = 0
                    if equip not in all_cards:
                        all_cards[equip] = 0
                if can_be_played(hero, equip):
                    equip_dict[hero][equip] += 1
                    all_cards[equip] += 1
                    current_deck["equips"].append(equip)

assassin_cards = card_dict["Assassin"] | equip_dict["Assassin"] 
illusionist_cards = card_dict["Illusionist"] | equip_dict["Illusionist"]
ninja_cards = card_dict["Ninja"] | equip_dict["Ninja"]

decks_cards = pd.DataFrame(index=all_cards.keys(), columns=['all_cards', 'assassin_cards', 'illusionist_cards', 'ninja_cards'])

for card in all_cards.keys():
    decks_cards.loc[card, 'all_cards'] = all_cards.get(card, 0)
    decks_cards.loc[card, 'assassin_cards'] = assassin_cards.get(card, 0)
    decks_cards.loc[card, 'illusionist_cards'] = illusionist_cards.get(card, 0)
    decks_cards.loc[card, 'ninja_cards'] = ninja_cards.get(card, 0)

decks_cards.index.name = "Name"

complete_cards = cards.merge(decks_cards, left_index=True, right_index=True, how='inner')

if MONTH_FILTER is None:
    decks_cards.to_csv('../data/decks_cards.csv')

    with open('../data/deck_stats.json', 'w') as f:
        json.dump(class_dict, f)


    # Creating scv card database

    complete_cards.to_csv('../data/complete_cards.csv')
else:
    with open('../data/deck_stats_' + MONTH_FILTER + '.json', 'w') as f:
        json.dump(class_dict, f)

    complete_cards.to_csv('../data/complete_cards_' + MONTH_FILTER + '.csv')

with open('../data/decks.json', 'w') as f:
    json.dump(deck_dict, f)
