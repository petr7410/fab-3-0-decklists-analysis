import warnings
import pandas as pd
from collections import Counter
from datetime import datetime
import json
from scipy.stats import hypergeom
import re

warnings.simplefilter(action='ignore', category=Warning)

with open('init.json', 'r') as init_file:
    init_data = json.load(init_file)

# ---------------------------   EXTRACTING PROBABILITIES BASED ON THE DRAFT FILE     -------------------------------------
# Load card draft data
draft_files_prob_distribution = []
for file_path in init_data['files']['draft_files']:
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Initialize variables
    cards_draft = ""
    layouts = {}
    sets = {}
    all_sets = {}
    current_section = None
    layout_name = None

    # Parse the file
    for line in lines:
        line = line.strip()
        if line.startswith('[') and line.endswith(']'):
            current_section = line[1:-1]
        elif current_section == 'CustomCards':
            cards_draft += line + "\n"
        elif current_section == 'Layouts' and line.strip().startswith('- '):
            # Extract layout name and weight
            parts = line.split('(')
            if len(parts) == 2:
                layout_name = parts[0].strip()[2:]
                weight = int(parts[1].strip(')'))
                layouts[layout_name] = weight
        elif current_section == 'Layouts' and line.strip()[0] in "123456789":
            # Extract number of cards and set name
            parts = line.strip().split(' ')
            count = int(parts[0])
            set_name = ' '.join(parts[1:])
            if layout_name not in sets:
                sets[layout_name] = []
            sets[layout_name].append((count, set_name))
            if set_name not in all_sets:
                all_sets[set_name] = []
        elif current_section in all_sets:
            parts = line.split(' ')
            count = int(parts[0])
            card_name = ' '.join(parts[1:])
            all_sets[current_section].append((count, card_name))


    # Now, calculate the probabilities and expected counts

    # Calculate total number of layouts
    total_layouts = sum(layouts.values())

    # Calculate the probability of each layout being chosen
    layouts_average = {layout: hypergeom.mean(total_layouts, weight, 24) for layout, weight in layouts.items()}

    all_cards_average = {}

    for layout in sets:
        for set_count, set_name in sets[layout]:
            total_cards = sum(count for count, card in all_sets[set_name])
            cards_average = {card: hypergeom.mean(total_cards, weight, set_count) for weight, card in all_sets[set_name]}
            if layout not in all_cards_average:
                all_cards_average[layout] = {}
            for card, average in cards_average.items():
                if card not in all_cards_average[layout]:
                    all_cards_average[layout][card] = 0
                all_cards_average[layout][card] += average

    cards_prob_distribution = {}

    for layout in layouts_average:
        for card in all_cards_average[layout]:
            if card not in cards_prob_distribution:
                cards_prob_distribution[card] = 0
            cards_prob_distribution[card] += all_cards_average[layout][card] * layouts_average[layout]
    
    draft_files_prob_distribution.append(cards_prob_distribution)


# ---------------------------   CREATING CARDS DATA     -------------------------------------
# Load card draft data
if cards_draft[-4] == ",":
    cards_draft = cards_draft[:-4] + cards_draft[-3:]
cards_draft = json.loads(cards_draft)

cards = pd.DataFrame(cards_draft).set_index('name')

# Extract 'en' link from 'image_uris' and remove irrelevant columns
cards['image_url'] = cards['image_uris'].apply(lambda x: x['en'] if 'en' in x else None)
cards.drop(columns=['mana_cost', 'type', 'image_uris'], inplace=True)

# Adding Cracked Bauble (yellow)
cards.loc["Cracked Bauble (yellow)"] = init_data['cracked_bauble']

# Load all_cards.json
with open(init_data['files']['all_cards'], 'r', encoding='utf-8') as file:
    #all_cards = pd.read_csv(file)
    all_cards = pd.read_csv(file, delimiter='\t', encoding='utf-8', quoting=3) # TODO -> maybe some dynamic solution for this?

if '' in all_cards.columns:
    all_cards.drop(columns=[''], inplace=True)

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

# Creating file with cards detail for draft
all_cards['New Index'] = all_cards.apply(lambda row: f"{row['Name']}{pitch_color(row['Pitch'])}", axis=1)
all_cards.set_index('New Index', inplace=True)
cards = cards.merge(all_cards, left_index=True, right_index=True, how='inner')
cards.drop(columns=['Name'], inplace=True)
cards.index.name = "Name"

def cannot_be_played(hero, card): # TODO this was completely reworked compared to the last version and this still miss some scalability
    card = cards.loc[card]
    card_types = set(card["Types"].split(", "))

    cannot_conditions = init_data.get("cannot_be_played_conditions", {}).get(hero, [])
    can_conditions = init_data.get("can_be_played_conditions", {}).get(hero, [])

    cannot_sets = [set(cond.split(", ")) for cond in cannot_conditions]
    can_sets = [set(cond.split(", ")) for cond in can_conditions]

    # If any disallowed set is fully contained in the card's types, reject the card
    if any(cannot_set.issubset(card_types) for cannot_set in cannot_sets):
        return True

    # If any allowed set is fully contained in the card's types, accept the card
    if any(can_set.issubset(card_types) for can_set in can_sets):
        return False

    # Default behavior: If neither rule applies, consider it unplayable
    return True

# Utility function to filter based on date
def is_date_between_filters(line, draft=False):
    # Strip the newline at the end and extract the first part as the date
    date_str = line.strip()[:19]  # Extract the date part 'YYYY-MM-DD hh:mm:ss'
    
    # Parse the date from the line
    try:
        line_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return False, None, None, None
    
    if draft:
        start_filter = ""
        end_filter = init_data["draft_file_date"][draft]
    else:
        start_filter = init_data["date_range"]["start_date"]
        end_filter = init_data["date_range"]["end_date"]
    
    # Parse the filters if they are not None
    if start_filter:
        start_date = datetime.strptime(start_filter, '%Y-%m-%d %H:%M:%S')
    else:
        start_date = None
        
    if end_filter:
        end_date = datetime.strptime(end_filter, '%Y-%m-%d %H:%M:%S')
    else:
        end_date = None

    # Check if the line_date is within the range, considering None filters
    filter_result = True
    if start_date and line_date < start_date:
        filter_result = False
    if end_date and line_date > end_date:
        filter_result = False
    
    year = line_date.year
    month = line_date.month
    day = line_date.day
    
    return filter_result, year, month, day

# Extracting cards from decks
class_dict = {}
card_dict = {}
equip_dict = {}
all_cards = {}
date_dict = {}
data_filter = False
date = False
deck_dict = {}
deck_draft = [[] for _ in range(len(init_data["draft_file_date"]))]
current_deck = None
in_equipment_section = True
pattern = re.compile(r"^\d+x\s+(.+)$")

with open(init_data['files']['decks'], "r", encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines:
        if line.startswith("20") and line[4] == "-" and line[7] == "-":   # TODO not an ideal solution
            if date and line == date:
                print("Warning! two decks with the exact same time detected: " + line)
            date = line
            data_filter, year, month, day = is_date_between_filters(line)

        if not data_filter:
            continue

        # Checking for hero and initializing if hero was found
        if line.startswith("Hero: "):
            hero = line.split("Hero: ")[1].replace("\n", "")
            if hero not in class_dict:
                class_dict[hero] = 0
                card_dict[hero] = {}
                equip_dict[hero] = {}
                date_dict[hero] = []
                deck_dict[hero] = []
            class_dict[hero] += 1
            date_dict[hero].append((year, month, day))

            current_deck = {"cards": [], "equips": [], "hero": hero} # TODO This is a redundant information contained in the output file, consider removing this
            deck_dict[hero].append(current_deck)

            for i in range(len(deck_draft)):
                if i == len(deck_draft) - 1: # TODO Please check why this as I no longer remember how this exactly works
                    deck_draft[i].append(current_deck)
                elif is_date_between_filters(date, i+1)[0]:
                    deck_draft[i].append(current_deck)
                    break

        # Toggle sections based on headers
        if line.startswith("Arena cards"):
            in_equipment_section = True
            continue

        if line.startswith("Deck cards"):
            in_equipment_section = False
            continue

        # Parse equipment lines in the "Arena cards" section
        match = pattern.match(line)
        if match:
            tmp = line.split(" ", 1)
            number = int(tmp[0][:-1])  # Extract count (e.g., "1x" -> 1)
            card = match.group(1).strip()  # Extract card name
            if in_equipment_section:
                if card in init_data["weapons"]:
                    continue
                if card not in equip_dict[hero]:
                    equip_dict[hero][card] = 0
                    if card not in all_cards:
                        all_cards[card] = 0
                if not cannot_be_played(hero, card):
                    equip_dict[hero][card] += number # TODO There is no way to gain advantage by having the same equipment twice other then denying it from other players, so this is maybe not wanted
                    all_cards[card] += number
                    current_deck["equips"].append(card)
            else:
                if card not in card_dict[hero]:
                    card_dict[hero][card] = 0
                    if card not in all_cards:
                        all_cards[card] = 0
                if not cannot_be_played(hero, card):
                    card_dict[hero][card] += number
                    all_cards[card] += number
                    for _ in range(number):
                        current_deck["cards"].append(card)

# Creating normalized deck data with different weight of cards based on the deck size
normalized_cards = {"all": {}}
for hero in deck_dict:
    normalized_cards[hero] = {}
    for deck in deck_dict[hero]:
        for card in deck["cards"]:
            if card not in normalized_cards[hero]:
                normalized_cards[hero][card] = 0
            if card not in normalized_cards["all"]:
                normalized_cards["all"][card] = 0
            normalized_cards[hero][card] += 1 / len(deck["cards"]) * 30
            normalized_cards["all"][card] += 1 / len(deck["cards"]) * 30


def find_highest_index_and_update_corrections(values, correction_list, index):
    highest_value = values[0]
    highest_index = 0

    for j in range(1, index + 1):
        current_value = values[j]
        correction = correction_list[j][highest_index]
        if current_value + correction > highest_value:
            highest_value = current_value
            highest_index = j

    for j in range(index + 1, len(values)):
        correction_list[j][highest_index] = max(correction_list[j][highest_index], values[j] - values[highest_index])

    return highest_index


threshold_list = [[float(0)] * i for i in range(len(deck_draft))]
deck_count_resp_draft = {"all": [0] * len(draft_files_prob_distribution)}
for j in range(len(deck_draft)):
    for deck in deck_draft[j]:
        draft_file_average = [0] * len(deck_draft)
        for card in deck["cards"]:
            if card == "Cracked Bauble (yellow)": #Fix for Cracked Bauble as it cannot be drafted
                continue
            for i in range(len(deck_draft)):                    
                draft_file_average[i] += draft_files_prob_distribution[i][card]
        for card in deck["equips"]:
            for i in range(len(draft_files_prob_distribution)):
                draft_file_average[i] += draft_files_prob_distribution[i][card]
        
        index = find_highest_index_and_update_corrections(draft_file_average, threshold_list, j)
        if deck["hero"] not in deck_count_resp_draft:
            deck_count_resp_draft[deck["hero"]] = [0] * len(draft_files_prob_distribution)
        deck_count_resp_draft[deck["hero"]][index] += 1
        deck_count_resp_draft["all"][index] += 1

heroes = card_dict.keys()

decks_cards = pd.DataFrame(index=all_cards.keys(), columns=['total_count'] + [hero + '_total_count' for hero in heroes] + ['average_count_per_normalized_deck'] + [hero + '_average_count_per_normalized_deck' for hero in heroes])

decks_cards.index.name = "Name"

for card in all_cards.keys():
    decks_cards.loc[card, 'total_count'] = all_cards.get(card, 0)
    for hero in heroes:
        hero_cards = card_dict[hero] | equip_dict[hero]
        decks_cards.loc[card, hero + '_total_count'] = hero_cards.get(card, 0)

for card in normalized_cards["all"].keys():
    decks_cards.loc[card, 'average_count_per_normalized_deck'] = normalized_cards["all"].get(card, 0) / sum(class_dict.values())
    for hero in heroes:
        hero_cards = normalized_cards[hero]
        decks_cards.loc[card, hero + '_average_count_per_normalized_deck'] = hero_cards.get(card, 0) / class_dict[hero]

for i in range(len(draft_files_prob_distribution)):
    decks_cards["draft_average_occurrence" + str(i + 1)] = decks_cards.index.map(draft_files_prob_distribution[i])

sum_of_products = sum(   # TODO this is strange design, maybe try to improve this
    decks_cards["draft_average_occurrence" + str(i+1)] * deck_count_resp_draft["all"][i]
    for i in range(len(deck_count_resp_draft["all"]))
)
decks_cards["pick_rate"] = decks_cards['total_count'] / sum_of_products
decks_cards["average_count_per_deck"] = decks_cards['total_count'] / sum(class_dict.values())
for hero in heroes:
    sum_of_products = sum(   # TODO this is strange design, maybe try to improve this
        decks_cards["draft_average_occurrence" + str(i+1)] * deck_count_resp_draft[hero][i]
        for i in range(len(deck_count_resp_draft["all"]))
    )
    decks_cards[hero + "_pick_rate"] = decks_cards[hero + '_total_count'] / sum_of_products
    decks_cards[hero + "_average_count_per_deck"] = decks_cards[hero + '_total_count'] / class_dict[hero] # TODO this does not work correctly

decks_cards["weighted_pick_rate"] = decks_cards[[hero + "_pick_rate" for hero in heroes]].mean(axis=1)

complete_cards = cards.merge(decks_cards, left_index=True, right_index=True, how='inner')

with open(init_data['save']['decks_stats'], 'w') as f:
    json.dump(class_dict, f)

with open(init_data["save"]['decks_by_date_counts'], 'w') as f:
    result_dict = {}
    for name, dates in date_dict.items():
        date_counts = Counter(dates)
        result_dict[name] = {datetime(year, month, day).isoformat(): count for (year, month, day), count in date_counts.items()}

    json.dump(result_dict, f)

complete_cards.to_csv(init_data['save']['cards_stats'])

with open(init_data['save']['decks'], 'w') as f:
    json.dump(deck_dict, f)
    
