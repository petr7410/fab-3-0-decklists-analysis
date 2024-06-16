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
  msg +=  f"Card: {card_with_image(name, link)}, Overall count: **{count}**, Weighted percentage: **{weight}** %  \n  - On average in **{assassin}** % of Assassin decks  \n  - On average in **{illusionist}** % of Illusionist decks  \n  - On average in **{ninja}** % of Ninja decks\n\n"


msg += "\n## Mystic cards  \n"
for index, row in all_mystic.iterrows():
  name = row['Name']
  count = row["all_cards"]
  assassin = row["assassin_deck_pct"]
  illusionist = row["illusionist_deck_pct"]
  ninja = row["ninja_deck_pct"]
  weight = row["deck_weighted_pct"]
  link = row["image_url"]
  msg +=  f"Card: {card_with_image(name, link)}, Overall count: **{count}**, Weighted percentage: **{weight}** %  \n  - On average in **{assassin}** % of Assassin decks  \n  - On average in **{illusionist}** % of Illusionist decks  \n  - On average in **{ninja}** % of Ninja decks\n\n"

msg += "\n## Generic cards  \n"
for index, row in all_generic.iterrows():
  name = row['Name']
  count = row["all_cards"]
  assassin = row["assassin_deck_pct"]
  illusionist = row["illusionist_deck_pct"]
  ninja = row["ninja_deck_pct"]
  weight = row["deck_weighted_pct"]
  link = row["image_url"]
  msg +=  f"Card: {card_with_image(name, link)}, Overall count: **{count}**, Weighted percentage: **{weight}** %  \n  - On average in **{assassin}** % of Assassin decks  \n  - On average in **{illusionist}** % of Illusionist decks  \n  - On average in **{ninja}** % of Ninja decks\n\n"

with open(f'../analysis/shared_cards_analysis.md', 'w') as f:
  f.write(add_style(msg))

with open(f'../docs/shared_cards_analysis.html', 'w') as f:
  f.write(add_html_format(markdown.markdown(msg), "Shared cards analysis"))