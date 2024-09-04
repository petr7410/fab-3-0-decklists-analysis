import warnings
import pandas as pd
import json
import mistune
from print_utility import add_style, add_html_format, card_with_image

markdown = mistune.create_markdown()

# Suppress Warning messages
warnings.simplefilter(action='ignore', category=Warning)
    
with open('../data/decks.json', 'r') as f:
    decks = json.load(f)

with open('../data/complete_cards.csv', 'r', encoding='utf-8') as file:
    cards = pd.read_csv(file, index_col="Name")

heroes = ["Assassin", "Illusionist", "Ninja"]

for hero in heroes:
    msg = f'# {hero} decks analysis  \n'
    
    mythic_stats = {}
    nimbl_stats = {}
    transcend_stats = {}
    equip_stats = {}
    card_stats = {}
    total_stats = {}

    for deck in decks[hero]:
        mythic_cards = []
        nimbl_cards = []
        transcend_cards = []
        for card in deck["cards"]:
            if cards.loc[card]["rarity"] == "mythic":
                mythic_cards.append(card)
            if card.startswith("Nimbl"):
                nimbl_cards.append(card)
            if pd.notna(cards.loc[card]["Card Keywords"]) and "Transcend" in cards.loc[card]["Card Keywords"]:
                transcend_cards.append(card)

        if len(mythic_cards) not in mythic_stats:
            mythic_stats[len(mythic_cards)] = 0
        mythic_stats[len(mythic_cards)] += 1

        if len(nimbl_cards) not in nimbl_stats:
            nimbl_stats[len(nimbl_cards)] = {}
        nimblism_count = 0
        for nimbl in nimbl_cards:
            if nimbl.startswith("Nimblism"):
                nimblism_count += 1
        if nimblism_count not in nimbl_stats[len(nimbl_cards)]:
            nimbl_stats[len(nimbl_cards)][nimblism_count] = 0
        nimbl_stats[len(nimbl_cards)][nimblism_count] += 1

        if len(transcend_cards) not in transcend_stats:
            transcend_stats[len(transcend_cards)] = 0
        transcend_stats[len(transcend_cards)] += 1

        if len(deck["equips"]) not in equip_stats:
            equip_stats[len(deck["equips"])] = 0
        equip_stats[len(deck["equips"])] += 1

        if len(deck["cards"]) not in card_stats:
            card_stats[len(deck["cards"])] = 0
        card_stats[len(deck["cards"])] += 1

        if len(deck["equips"]) + len(deck["cards"]) not in total_stats:
            total_stats[len(deck["equips"]) + len(deck["cards"])] = 0
        total_stats[len(deck["equips"]) + len(deck["cards"])] += 1

    msg += "## Number of Mythic cards  \n"
    for mythic_number, mythic_count in sorted(mythic_stats.items()):
        msg += f"- Deck with **{mythic_number}** mythic cards appeared **{mythic_count}** times  \n"

    msg += "## Number of Nimbl cards  \n"
    for key in sorted(nimbl_stats.keys()):
        msg += f"- Deck with **{key}** Nimbl cards appeared **{sum(nimbl_stats[key].values())}** times  \n"
        for nimbl_number, nimbl_count in sorted(nimbl_stats[key].items()):
            msg += f"  - Deck with **{nimbl_number}** Nimblism and **{key-nimbl_number}** Nimble Strike appeared **{nimbl_count}** times  \n"

    msg += "## Number of Transcend cards  \n"
    for transcend_number, transcend_count in sorted(transcend_stats.items()):
        msg += f"- Deck with **{transcend_number}** transcend cards appeared **{transcend_count}** times  \n"

    msg += "## Number of Eqiupments  \n"
    for equip_number, equip_count in sorted(equip_stats.items()):
        msg += f"- Deck with **{equip_number}** equipments appeared **{equip_count}** times  \n"

    msg += "## Number of Cards  \n"
    for card_number, card_count in sorted(card_stats.items()):
        msg += f"- Deck with **{card_number}** cards appeared **{card_count}** times  \n"

    msg += "## Number of Cards with Eqiupments  \n"
    for total_number, total_count in sorted(total_stats.items()):
        msg += f"- Deck with **{total_number}** cards with eqipment appeared **{total_count}** times  \n"

    with open(f'../analysis/{hero}_decks_stats.md', 'w') as f:
        f.write(add_style(msg))

    with open(f'../docs/{hero}_decks_stats.html', 'w') as f:
        f.write(add_html_format(markdown(msg), hero + " Decks"))
