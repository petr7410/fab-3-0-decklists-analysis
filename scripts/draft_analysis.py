import warnings
import pandas as pd
import numpy as np
import json
import markdown
from scipy.stats import hypergeom
from print_utility import add_style, add_html_format, card_with_image

warnings.simplefilter(action='ignore', category=Warning)

# Load the file
file_path = '../data/draft-file.txt'

# Read the file
with open(file_path, 'r') as file:
    lines = file.readlines()

# Initialize variables
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


# Analysis

with open('../data/deck_stats_2024-06.json', 'r') as f:
    deck_stats = json.load(f)

file_path = '../data/complete_cards_2024-06.csv'
with open(file_path, 'r', encoding='utf-8') as file:
    cards = pd.read_csv(file, index_col="Name")

classes = ["Assassin", "Illusionist", "Ninja"]
def check_class(types_str):
    types = types_str.split(", ")
    for class_ in classes:
        if class_ in types:
            return True
    return False

cards['class'] = cards['Types'].apply(check_class)

cards["draft_average_occurrence"] = cards.index.map(cards_prob_distribution)

assassin_all_cards = cards[cards['assassin_cards'] != 0]
illusionist_all_cards = cards[cards['illusionist_cards'] != 0]
ninja_all_cards = cards[cards['ninja_cards'] != 0]

setup_list = [("Assassin", "assassin_cards", assassin_all_cards),
              ("Illusionist", "illusionist_cards", illusionist_all_cards),
              ("Ninja", "ninja_cards", ninja_all_cards)]

for setup in setup_list:
    msg = ""
    hero_name, cards_count_name, hero_all_cards = setup

    # pick_rate = number of times picked / average number of times card appeared in all draft won by this hero
    hero_all_cards["pick_rate"] = (hero_all_cards[cards_count_name] / (hero_all_cards["draft_average_occurrence"] * deck_stats[hero_name]) *100 ).round(2)

    # pick_rate * 8 for non-class cards and *3 for class cards (considering 8 players are competing for non-class cards and around 3 players are competing for class cards)
    hero_all_cards["pick_rate_weighted"] = (hero_all_cards[cards_count_name] / (hero_all_cards["draft_average_occurrence"] * deck_stats[hero_name] / np.where(hero_all_cards['class'], 3, 8))).round(2)

    hero_all_cards = hero_all_cards.sort_values(by='pick_rate_weighted', ascending=False).reset_index()

    msg += f"# {hero_name} Analysis:  \n"

    number_of_cards = hero_all_cards[cards_count_name].sum()

    msg += f"\nTotal number of decks: {deck_stats[hero_name]}  \n"
    msg += f"\nTotal number of card: {number_of_cards}  \n"

    msg += f"\n\n## The best 20 class cards:  \n"
    hero_20_class_cards = hero_all_cards[hero_all_cards["class"] == True].head(20)
    for index, row in hero_20_class_cards.iterrows():
        name = row['Name']
        count = row[cards_count_name]
        draft_appearance = row["draft_average_occurrence"]
        pick_rate = row["pick_rate"]
        link = row["image_url"]
        msg +=  f"Card: {card_with_image(name, link)}, Overall count: **{count}**, Expected number of appearances per draft: **{round(draft_appearance, 3)}**, Pick rate: **{pick_rate}** %  \n"

    msg += f"\n\n## The best 20 non-class cards:  \n"
    hero_20_class_cards = hero_all_cards[hero_all_cards["class"] == False].head(20)
    for index, row in hero_20_class_cards.iterrows():
        name = row['Name']
        count = row[cards_count_name]
        draft_appearance = row["draft_average_occurrence"]
        pick_rate = row["pick_rate"]
        link = row["image_url"]
        msg +=  f"Card: {card_with_image(name, link)}, Overall count: **{count}**, Expected number of appearances per draft: **{round(draft_appearance, 3)}**, Pick rate: **{pick_rate}** %  \n"

    with open(f'../analysis/{hero_name}_draft_analysis.md', 'w') as f:
        f.write(add_style(msg))

    with open(f'../docs/{hero_name}_draft_analysis.html', 'w') as f:
        f.write(add_html_format(markdown.markdown(msg), hero_name + " Draft Analysis"))

    # Creating all cards list for hero
    msg = f'# {hero_name}: Draft pick rate analysis  \n'
    for index, row in hero_all_cards.iterrows():
        name = row['Name']
        count = row[cards_count_name]
        draft_appearance = row["draft_average_occurrence"]
        pick_rate = row["pick_rate"]
        pick_weight = row["pick_rate_weighted"]
        link = row["image_url"]
        msg +=  f"Card: {card_with_image(name, link)}, Overall count: **{count}**, Expected number of appearances per draft: **{round(draft_appearance, 3)}**, Pick rate: **{pick_rate}** %, Pick weight: **{round(pick_weight, 2)}**  \n"

    with open(f'../analysis/{hero_name}_all_cards_draft.md', 'w') as f:
        f.write(add_style(msg))

    with open(f'../docs/{hero_name}_all_cards_draft.html', 'w') as f:
        f.write(add_html_format(markdown.markdown(msg), hero_name + " All Cards Draft"))

msg = f'# All classes: Draft pick rate analysis  \n'
cards["pick_rate"] = (cards["all_cards"] / (cards["draft_average_occurrence"] * sum(deck_stats.values())) *100 ).round(2)
non_class_cards = cards[cards["class"] == False].sort_values(by='pick_rate', ascending=False).reset_index()
for index, row in non_class_cards.iterrows():
    name = row['Name']
    count = row["all_cards"]
    draft_appearance = row["draft_average_occurrence"]
    pick_rate = row["pick_rate"]
    link = row["image_url"]
    msg +=  f"Card: {card_with_image(name, link)}, Overall count: **{count}**, Expected number of appearances per draft: **{round(draft_appearance, 3)}**, Pick rate: **{pick_rate}** %  \n"

with open(f'../analysis/draft_non-class_cards.md', 'w') as f:
    f.write(add_style(msg))

with open(f'../docs/draft_non-class_cards.html', 'w') as f:
    f.write(add_html_format(markdown.markdown(msg), "Draft Non-Class Cards"))

msg = f'# Draft analysis  \n'
cards = cards.sort_values(by='draft_average_occurrence', ascending=False).reset_index()
for index, row in cards.iterrows():
    name = row['Name']
    x = row["draft_average_occurrence"]
    link = row["image_url"]
    msg +=  f"Card: {card_with_image(name, link)}, Average number of occurrences per draft: **{round(x, 3)}**  \n"

with open(f'../analysis/draft_analysis.md', 'w') as f:
    f.write(add_style(msg))

with open(f'../docs/draft_analysis.html', 'w') as f:
    f.write(add_html_format(markdown.markdown(msg), "Draft analysis"))
