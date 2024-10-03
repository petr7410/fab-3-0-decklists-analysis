import warnings
import pandas as pd
from collections import Counter
from datetime import datetime
import json
from scipy.stats import hypergeom

warnings.simplefilter(action='ignore', category=Warning)

with open('init.json', 'r') as init_file:
    init_data = json.load(init_file)

# ---------------------------   EXTRACTING PROBABILITIES BASED ON THE DRAFT FILE     -------------------------------------
# Load card draft data
draft_files_prob_distribution = []
for file_path in init_data['files']['draft_files']:   # TODO this was changed from draft_file to draft_files
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

# Utility function to filter unplayable cards
def cannot_be_played(hero, card):
    card = cards.loc[card]
    for condition in init_data["cannot_be_played_conditions"][hero]:
        types = card["Types"].split(", ")
        if condition in types:
            return True
    return False

# Utility function to filter based on date
def is_date_between_filters(line):
    # Strip the newline at the end and extract the first part as the date
    date_str = line.strip()[:19]  # Extract the date part 'YYYY-MM-DD hh:mm:ss'
    
    # Parse the date from the line
    try:
        line_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return False, None, None, None
    
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
current_deck = None

with open(init_data['files']['decks'], "r", encoding='utf-8') as file:
    lines = file.readlines()
    current_hero = None
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

            current_deck = {"cards": [], "equips": []}
            deck_dict[hero].append(current_deck)
        
        # Checking for card
        if line.startswith("("):
            tmp = line.split(") ")
            if len(tmp) < 2 or "3-0" in tmp[0] or len(tmp) > 3:   # TODO not an ideal solution
                continue
            number = int(tmp[0][1:])
            card = tmp[1].replace("\n", "")
            if card not in card_dict[hero]:
                card_dict[hero][card] = 0
                if card not in all_cards:
                    all_cards[card] = 0
            if not cannot_be_played(hero, card):
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
                if not cannot_be_played(hero, equip):
                    equip_dict[hero][equip] += 1
                    all_cards[equip] += 1
                    current_deck["equips"].append(equip)

# Creating normalized deck data with different weight of cards based on the deck size
normalized_cards = {"all": {}}
deck_count_resp_draft = {"all": [0] * len(draft_files_prob_distribution)}
first_draft_decks = {"Florian": 20, "Verdance": 17, "Oscilio": 16, "Aurora": 9}  # TODO this is not universally usable
for hero in deck_dict:
    normalized_cards[hero] = {}
    deck_count_resp_draft[hero] = [0] * len(draft_files_prob_distribution)
    for deck in deck_dict[hero]:
        draft_file_average = [0] * len(draft_files_prob_distribution)  #TODO rename this
        for card in deck["cards"]:
            if card not in normalized_cards[hero]:
                normalized_cards[hero][card] = 0
            if card not in normalized_cards["all"]:
                normalized_cards["all"][card] = 0
            normalized_cards[hero][card] += 1 / len(deck["cards"]) * 30
            normalized_cards["all"][card] += 1 / len(deck["cards"]) * 30
            for i in range(len(draft_files_prob_distribution)):
                draft_file_average[i] += draft_files_prob_distribution[i][card]
        for card in deck["equips"]:
            for i in range(len(draft_files_prob_distribution)):
                draft_file_average[i] += draft_files_prob_distribution[i][card]
        """Part below is not universally usable!!!"""
        if first_draft_decks[hero] > 0:
            first_draft_decks[hero] -= 1
            index = 0
        else:
            if draft_file_average[0] > draft_file_average[1] + 2.25:
                index = 0
            else:
                index = 1
        deck_count_resp_draft[hero][index] += 1
        deck_count_resp_draft["all"][index] += 1
        #deck_count_resp_draft[hero][draft_file_average.index(max(draft_file_average))] += 1
        #deck_count_resp_draft["all"][draft_file_average.index(max(draft_file_average))] += 1

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
    decks_cards[hero + "_average_count_per_deck"] = decks_cards[hero + '_total_count'] / class_dict[hero]

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
    
