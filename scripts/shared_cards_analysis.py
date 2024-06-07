import warnings
import pandas as pd
import json

# Suppress Warning messages
warnings.simplefilter(action='ignore', category=Warning)
    

with open('../data/deck_stats.json', 'r') as f:
    deck_stats = json.load(f)

file_path = '../data/complete_cards.csv'
with open(file_path, 'r', encoding='utf-8') as file:
    cards = pd.read_csv(file, index_col="Name")

pattern = 'Assassin|Illusionist|Ninja'
cards = cards[~cards['Types'].str.contains(pattern)]


cards['assassin_deck_pct'] = (cards['assassin_cards'] / deck_stats['Assassin'] * 100).round(2)
cards['illusionist_deck_pct'] = (cards['illusionist_cards'] / deck_stats['Illusionist'] * 100).round(2)
cards['ninja_deck_pct'] = (cards['ninja_cards'] / deck_stats['Ninja'] * 100).round(2)
cards['deck_weighted_pct'] = ((cards['assassin_deck_pct'] + cards['illusionist_deck_pct'] + cards['ninja_deck_pct']) / 3).round(2)

cards = cards.sort_values(by='deck_weighted_pct', ascending=False)
all_cards = cards[~cards["Types"].str.contains("Equipment")]
all_equips = cards[cards["Types"].str.contains("Equipment")].reset_index()
all_mystic = all_cards[all_cards["Types"].str.contains("Mystic")].reset_index()
all_generic = all_cards[all_cards["Types"].str.contains("Generic")].reset_index()

def card_with_image(card_name, card_link):
    return f'<a href="link" class="tooltip">**{card_name}**<span class="tooltiptext"><img src="{card_link}"></span></a>'

msg = "# Comparison of Generic / Mystic card across classes\n\n"

msg += "\n## Equipment cards  \n"
for index, row in all_equips.iterrows():
    name = row['Name']
    count = row["all_cards"]
    assassin = row["assassin_deck_pct"]
    illusionist = row["illusionist_deck_pct"]
    ninja = row["ninja_deck_pct"]
    weight = row["deck_weighted_pct"]
    link = row["image_url"]
    msg +=  f"Card: {card_with_image(name, link)}, Overall count: **{count}**, Weighted percentage: **{weight}** %  \n-> On average in **{assassin}** % of Assassin decks  \n-> On average in **{illusionist}** % of Illusionist decks  \n-> On average in **{ninja}** % of Ninja decks\n\n"


msg += "\n## Mystic cards  \n"
for index, row in all_mystic.iterrows():
    name = row['Name']
    count = row["all_cards"]
    assassin = row["assassin_deck_pct"]
    illusionist = row["illusionist_deck_pct"]
    ninja = row["ninja_deck_pct"]
    weight = row["deck_weighted_pct"]
    link = row["image_url"]
    msg +=  f"Card: {card_with_image(name, link)}, Overall count: **{count}**, Weighted percentage: **{weight}** %  \n-> On average in **{assassin}** % of Assassin decks  \n-> On average in **{illusionist}** % of Illusionist decks  \n-> On average in **{ninja}** % of Ninja decks\n\n"

msg += "\n## Generic cards  \n"
for index, row in all_generic.iterrows():
    name = row['Name']
    count = row["all_cards"]
    assassin = row["assassin_deck_pct"]
    illusionist = row["illusionist_deck_pct"]
    ninja = row["ninja_deck_pct"]
    weight = row["deck_weighted_pct"]
    link = row["image_url"]
    msg +=  f"Card: {card_with_image(name, link)}, Overall count: **{count}**, Weighted percentage: **{weight}** %  \n-> On average in **{assassin}** % of Assassin decks  \n-> On average in **{illusionist}** % of Illusionist decks  \n-> On average in **{ninja}** % of Ninja decks\n\n"

msg += """\
<style>
  img {
    width: 250px;
  }

  .tooltip {
    position: relative;
    display: inline-block;
  }

  .tooltip .tooltiptext {
    visibility: hidden;
    width: 250px;
    background-color: white;
    text-align: center;
    padding: 5px;
    border-radius: 6px;
    box-shadow: 0px 0px 10px 0px rgba(0, 0, 0, 0.2);

    /* Position the tooltip text */
    position: absolute;
    z-index: 1;
    top: 20px; /* Position it below the link */
    left: 105%; /* Position it to the right of the link */
    margin-left: 0;
  }

  .tooltip:hover .tooltiptext {
    visibility: visible;
  }
</style>\n"""

with open(f'../analysis/shared_cards_analysis.md', 'w') as f:
    f.write(msg)