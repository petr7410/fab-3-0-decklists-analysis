import warnings
import pandas as pd
import json
import markdown
from print_utility import add_style, add_html_format, card_with_image

# Suppress Warning messages
warnings.simplefilter(action='ignore', category=Warning)
    

with open('../data/deck_stats.json', 'r') as f:
    deck_stats = json.load(f)

file_path = '../data/complete_cards.csv'
with open(file_path, 'r', encoding='utf-8') as file:
    cards = pd.read_csv(file, index_col="Name")

cards['assassin_deck_pct'] = (cards['assassin_cards'] / deck_stats['Assassin'] * 100).round(2)
cards['illusionist_deck_pct'] = (cards['illusionist_cards'] / deck_stats['Illusionist'] * 100).round(2)
cards['ninja_deck_pct'] = (cards['ninja_cards'] / deck_stats['Ninja'] * 100).round(2)
cards['deck_weighted_pct'] = ((cards['assassin_deck_pct'] + cards['illusionist_deck_pct'] + cards['ninja_deck_pct']) / 3).round(2)

assassin_all_cards = cards[cards['assassin_cards'] != 0]
illusionist_all_cards = cards[cards['illusionist_cards'] != 0]
ninja_all_cards = cards[cards['ninja_cards'] != 0]

# Sorting cards in descending order
cards = cards.sort_values(by='all_cards', ascending=False)
assassin_all_cards = assassin_all_cards.sort_values(by='assassin_cards', ascending=False)
illusionist_all_cards = illusionist_all_cards.sort_values(by='illusionist_cards', ascending=False)
ninja_all_cards = ninja_all_cards.sort_values(by='ninja_cards', ascending=False)

# Preparing data
all_equips = cards[cards["Types"].str.contains("Equipment")]
assassin_equips = assassin_all_cards[assassin_all_cards["Types"].str.contains("Equipment")]
illusionist_equips = illusionist_all_cards[illusionist_all_cards["Types"].str.contains("Equipment")]
ninja_equips = ninja_all_cards[ninja_all_cards["Types"].str.contains("Equipment")]

all_cards = cards[~cards["Types"].str.contains("Equipment")]
assassin_cards = assassin_all_cards[~assassin_all_cards["Types"].str.contains("Equipment")]
illusionist_cards = illusionist_all_cards[~illusionist_all_cards["Types"].str.contains("Equipment")]
ninja_cards = ninja_all_cards[~ninja_all_cards["Types"].str.contains("Equipment")]


# Setup for md file
setup_list = [("Assassin", "assassin_cards", "assassin_deck_pct", assassin_cards, assassin_equips),
              ("Illusionist", "illusionist_cards", "illusionist_deck_pct", illusionist_cards, illusionist_equips),
              ("Ninja", "ninja_cards", "ninja_deck_pct", ninja_cards, ninja_equips)]

for setup in setup_list:
    msg = ""
    hero_name, cards_count_name, card_deck_pct_name, hero_cards, hero_equip = setup

    # Creating info md file
    msg += f"# {hero_name} Analysis:  \n"

    number_of_cards = hero_cards[cards_count_name].sum()

    msg += f"\nTotal number of decks: {deck_stats[hero_name]}  \n"
    msg += f"\nTotal number of card: {number_of_cards}  \n"

    msg += f"\n\n## Basic distributions:  \n"

    msg += f"\n### Pitch distribution:  \n"
    hero_cards['Pitch'] = hero_cards['Pitch'].fillna('None')
    grouped_sum = hero_cards.groupby('Pitch')[cards_count_name].sum()
    grouped_sum = (grouped_sum / number_of_cards * 100).round(2)
    for group, total in grouped_sum.items():
        msg += f"Pitch value: **{group}** corresponds to **{total} %** of cards, represents **{round(total*0.3, 1)}** cards in a deck of 30 cards.  \n"

    msg += f"\n### Defense distribution:  \n"
    hero_cards['Defense'] = hero_cards['Defense'].fillna('None')
    grouped_sum = hero_cards.groupby('Defense')[cards_count_name].sum()
    grouped_sum = (grouped_sum / number_of_cards * 100).round(2)
    for group, total in grouped_sum.items():
        msg += f"Defense value: **{group}** corresponds to **{total} %** of cards, represents **{round(total*0.3, 1)}** cards in a deck of 30 cards.  \n"

    msg += f"\n### Cost distribution:  \n"
    hero_cards['Cost'] = hero_cards['Cost'].fillna('None')
    grouped_sum = hero_cards.groupby('Cost')[cards_count_name].sum()
    grouped_sum = (grouped_sum / number_of_cards * 100).round(2)
    for group, total in grouped_sum.items():
        msg += f"Cost value: **{group}** corresponds to **{total} %** of cards, represents **{round(total*0.3, 1)}** cards in a deck of 30 cards.  \n"

    msg += f"\n\n## Summary of card types and keywords  \n"

    pct_action_attack = (hero_cards[hero_cards["Types"].str.contains("Action") & hero_cards["Types"].str.contains("Attack")][cards_count_name].sum() / number_of_cards * 100).round(2)
    msg += f"Percentage of attack action cards: **{pct_action_attack} %** (represents **{round(pct_action_attack*0.3, 1)}** cards in a deck of 30 cards)  \n"

    pct_non_attack_action = (hero_cards[hero_cards["Types"].str.contains("Action") & ~hero_cards["Types"].str.contains("Attack")][cards_count_name].sum() / number_of_cards * 100).round(2)
    msg += f"Percentage of non-attack action cards: **{pct_non_attack_action} %** (represents **{round(pct_non_attack_action*0.3, 1)}** cards in a deck of 30 cards)  \n"

    pct_attack_reaction = (hero_cards[hero_cards["Types"].str.contains("Attack Reaction")][cards_count_name].sum() / number_of_cards * 100).round(2)
    msg += f"Percentage of attack reaction cards: **{pct_attack_reaction} %** (represents **{round(pct_attack_reaction*0.3, 1)}** cards in a deck of 30 cards)  \n"

    pct_instant = (hero_cards[hero_cards["Types"].str.contains("Instant")][cards_count_name].sum() / number_of_cards * 100).round(2)
    msg += f"Percentage of instant cards: **{pct_instant} %** (represents **{round(pct_instant*0.3, 1)}** cards in a deck of 30 cards)  \n"

    pct_defense_reaction = (hero_cards[hero_cards["Types"].str.contains("Defense Reaction")][cards_count_name].sum() / number_of_cards * 100).round(2)
    msg += f"Percentage of defense reaction cards: **{pct_defense_reaction} %** (represents **{round(pct_defense_reaction*0.3, 1)}** cards in a deck of 30 cards)  \n"

    filtered_hero_cards = hero_cards[hero_cards["Card Keywords"].notna()]
    pct_transcend = (filtered_hero_cards[filtered_hero_cards["Card Keywords"].str.contains("Transcend")][cards_count_name].sum() / number_of_cards * 100).round(2)
    msg += f"Percentage of transcend cards: **{pct_transcend} %** (represents **{round(pct_transcend*0.3, 1)}** cards in a deck of 30 cards)  \n"

    pct_go_again = (filtered_hero_cards[filtered_hero_cards["Card Keywords"].str.contains("Go again")][cards_count_name].sum() / number_of_cards * 100).round(2)
    msg += f"Percentage of go again cards: **{pct_go_again} %** (represents **{round(pct_go_again*0.3, 1)}** cards in a deck of 30 cards)  \n"

    pct_stealth = (filtered_hero_cards[filtered_hero_cards["Card Keywords"].str.contains("Stealth")][cards_count_name].sum() / number_of_cards * 100).round(2)
    msg += f"Percentage of stealth cards: **{pct_stealth} %** (represents **{round(pct_stealth*0.3, 1)}** cards in a deck of 30 cards)  \n"

    pct_ward = (filtered_hero_cards[filtered_hero_cards["Card Keywords"].str.contains("Ward")][cards_count_name].sum() / number_of_cards * 100).round(2)
    msg += f"Percentage of ward cards: **{pct_ward} %** (represents **{round(pct_ward*0.3, 1)}** cards in a deck of 30 cards)  \n"

    pct_combo = (filtered_hero_cards[filtered_hero_cards["Card Keywords"].str.contains("Combo")][cards_count_name].sum() / number_of_cards * 100).round(2)
    msg += f"Percentage of combo cards: **{pct_combo} %** (represents **{round(pct_combo*0.3, 1)}** cards in a deck of 30 cards)  \n"

    msg += f"\n\n## Top 20 cards based on rarity + equipment + transcend  \n"
    msg += "\n### Top 20 common cards  \n"
    hero_20_common_cards = hero_cards[hero_cards["rarity"] == "common"].head(20).reset_index()
    for index, row in hero_20_common_cards.iterrows():
        name = row['Name']
        x = row[cards_count_name]
        y = row[card_deck_pct_name]
        link = row["image_url"]
        msg +=  f"Card: {card_with_image(name, link)}, Overall count: **{x}**, On average in **{y}** % of decks  \n"

    msg += "\n### Top 20 rare cards\n"
    hero_20_rare_cards = hero_cards[hero_cards["rarity"] == "rare"].head(20).reset_index()
    for index, row in hero_20_rare_cards.iterrows():
        name = row['Name']
        x = row[cards_count_name]
        y = row[card_deck_pct_name]
        link = row["image_url"]
        msg +=  f"Card: {card_with_image(name, link)}, Overall count: **{x}**, On average in **{y}** % of decks  \n"

    msg += "\n### Mythic cards  \n"
    hero_mythic_cards = hero_cards[hero_cards["rarity"] == "mythic"].reset_index()
    for index, row in hero_mythic_cards.iterrows():
        name = row['Name']
        x = row[cards_count_name]
        y = row[card_deck_pct_name]
        link = row["image_url"]
        msg +=  f"Card: {card_with_image(name, link)}, Overall count: **{x}**, On average in **{y}** % of decks  \n"

    msg += "\n### Equipment cards  \n"
    hero_equip_cards = hero_equip.reset_index()
    for index, row in hero_equip_cards.iterrows():
        name = row['Name']
        x = row[cards_count_name]
        y = row[card_deck_pct_name]
        link = row["image_url"]
        msg +=  f"Card: {card_with_image(name, link)}, Overall count: **{x}**, On average in **{y}** % of decks  \n"

    msg += "\n### Transcend cards  \n"
    hero_transcend_cards = filtered_hero_cards[filtered_hero_cards["Card Keywords"].str.contains("Transcend")].reset_index()
    for index, row in hero_transcend_cards.iterrows():
        name = row['Name']
        x = row[cards_count_name]
        y = row[card_deck_pct_name]
        link = row["image_url"]
        msg +=  f"Card: {card_with_image(name, link)}, Overall count: **{x}**, On average in **{y}** % of decks  \n"

    with open(f'../analysis/{hero_name}_info.md', 'w') as f:
        f.write(add_style(msg))

    with open(f'../docs/{hero_name}_info.html', 'w') as f:
        f.write(add_html_format(markdown.markdown(msg), hero_name + " Analysis"))

    # Creating all cards list for hero
    msg = f'# {hero_name}: All cards  \n'
    hero_all_cards = hero_cards.reset_index()
    for index, row in hero_all_cards.iterrows():
        name = row['Name']
        x = row[cards_count_name]
        y = row[card_deck_pct_name]
        link = row["image_url"]
        msg +=  f"Card: {card_with_image(name, link)}, Overall count: **{x}**, On average in **{y}** % of decks  \n"

    with open(f'../analysis/{hero_name}_all_cards_stats.md', 'w') as f:
        f.write(add_style(msg))

    with open(f'../docs/{hero_name}_all_cards_stats.html', 'w') as f:
        f.write(add_html_format(markdown.markdown(msg), hero_name + " All Cards"))

# Creating all cards list for all cards
hero_name = ""
msg = f'# All cards with equipment  \n'
cards = cards.sort_values(by='deck_weighted_pct', ascending=False).reset_index()
for index, row in cards.iterrows():
    name = row['Name']
    x = row["all_cards"]
    y = row["deck_weighted_pct"]
    link = row["image_url"]
    msg +=  f"Card: {card_with_image(name, link)}, Overall count: **{x}**, Weighted percentage: **{y}** %  \n"

with open(f'../analysis/all_cards_stats.md', 'w') as f:
    f.write(add_style(msg))

with open(f'../docs/all_cards_stats.html', 'w') as f:
    f.write(add_html_format(markdown.markdown(msg), "All Cards"))

