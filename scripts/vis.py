import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import warnings
import json
from datetime import datetime
from plotly.utils import PlotlyJSONEncoder

# Suppress Warning messages
warnings.simplefilter(action='ignore', category=Warning)
    
with open('../data/deck_stats.json', 'r') as f:
    deck_stats = json.load(f)

file_path = '../data/complete_cards.csv'
with open(file_path, 'r', encoding='utf-8') as file:
    cards = pd.read_csv(file, index_col="Name")

# Split cards into all_cards and all_equips
all_cards = cards[~cards["Types"].str.contains("Equipment")]
all_equips = cards[cards["Types"].str.contains("Equipment")]

def calculate_totals(df):
    totals = {
        'number_of_assassin': df['assassin_cards'].sum(),
        'number_of_illusionist': df['illusionist_cards'].sum(),
        'number_of_ninja': df['ninja_cards'].sum()
    }
    return totals

def add_percentages(df, totals):
    for col in ['assassin_cards', 'illusionist_cards', 'ninja_cards']:
        pct_col = col.replace('cards', 'pct')
        df[pct_col] = (df[col] / totals[f'number_of_{col.split("_")[0]}'] * 100).round(2)
    df['weighted_pct'] = ((df['assassin_pct'] + df['illusionist_pct'] + df['ninja_pct']) / 3).round(2)
    return df

# Calculate totals
all_cards_totals = calculate_totals(all_cards)
all_equips_totals = calculate_totals(all_equips)

# Add percentages to all_cards and all_equips
all_cards = add_percentages(all_cards, all_cards_totals)
all_equips = add_percentages(all_equips, all_equips_totals)

# Sort cards by weighted_pct
all_cards = all_cards.sort_values(by='weighted_pct', ascending=False)
all_equips = all_equips.sort_values(by='weighted_pct', ascending=False)

# Fill NaN values with "None"
def fill_na_columns(df, columns):
    for col in columns:
        df[col] = df[col].fillna('None')
    return df

all_cards = fill_na_columns(all_cards, ['Pitch', 'Defense', 'Cost'])

# Group and sum by specified columns
def group_and_sum(df, group_by_col, sum_cols):
    grouped = df.groupby(group_by_col)[sum_cols].sum().reset_index()
    grouped[group_by_col] = grouped[group_by_col].apply(lambda x: str(int(x)) if x != 'None' else 'None')
    return grouped

grouped_sum_pitch = group_and_sum(all_cards, 'Pitch', ["assassin_pct", "illusionist_pct", "ninja_pct"])
grouped_sum_defense = group_and_sum(all_cards, 'Defense', ["assassin_pct", "illusionist_pct", "ninja_pct"])
grouped_sum_cost = group_and_sum(all_cards, 'Cost', ["assassin_pct", "illusionist_pct", "ninja_pct"])

# Calculate percentages for each class
def calculate_percentages(df, col_name):
    types = ["Action", "Attack Reaction", "Instant", "Defense Reaction"]
    keywords = ["Transcend", "Go again", "Stealth", "Ward", "Combo"]
    percentages = []
    
    for t in types:
        if "Action" in t:
            percentages.append(df[df["Types"].str.contains(t) & df["Types"].str.contains("Attack")][col_name].sum())
            percentages.append(df[df["Types"].str.contains(t) & ~df["Types"].str.contains("Attack")][col_name].sum())
        else:
            percentages.append(df[df["Types"].str.contains(t)][col_name].sum())
    
    filtered_hero_cards = df[df["Card Keywords"].notna()]
    for keyword in keywords:
        percentages.append(filtered_hero_cards[filtered_hero_cards["Card Keywords"].str.contains(keyword)][col_name].sum())
    
    return percentages

# Calculate and organize percentages
card_types = ["Attack Action", "Non-Attack Action", "Attack Reaction", "Instant", "Defense Reaction", "Transcend", "Go Again", "Stealth", "Ward", "Combo"]
card_types_data = {
    "Card Type": card_types,
    "Assassin": calculate_percentages(all_cards, 'assassin_pct'),
    "Illusionist": calculate_percentages(all_cards, 'illusionist_pct'),
    "Ninja": calculate_percentages(all_cards, 'ninja_pct')
}
card_types_df = pd.DataFrame(card_types_data)

# Prepare transcend data
filtered_cards = all_cards[all_cards["Card Keywords"].notna()]
transcend_cards = filtered_cards[filtered_cards["Card Keywords"].str.contains("Transcend")].sort_values(by='weighted_pct', ascending=False).reset_index()
data = {"Name": [], "Assassin": [], "Illusionist": [], "Ninja": []}

for _, row in transcend_cards.iterrows():
    name = row['Name']
    if name.startswith("Sacred Art"):
        name = "Sacred Art"
    data["Name"].append(name)
    data["Assassin"].append(row['assassin_pct'])
    data["Illusionist"].append(row['illusionist_pct'])
    data["Ninja"].append(row['ninja_pct'])

transcend_df = pd.DataFrame(data)

# Prepare equipment data
all_equips = all_equips.reset_index()
data = {"Name": [], "Assassin": [], "Illusionist": [], "Ninja": []}

for _, row in all_equips.iterrows():
    name = row['Name']
    if name.startswith("Heirloom"):
        name = "Heirloom"
    elif name.startswith("Stride") or name.startswith("Arousing") or name.startswith("Uphold"):
        name = "Class common: Arousing/Uphold/Stride"
    elif name.startswith("Mask") or name.startswith("Undertow") or name.startswith("Truths"):
        name = "Class common: Undertow/Truths/Mask"
    data["Name"].append(name)
    data["Assassin"].append(row['assassin_pct'])
    data["Illusionist"].append(row['illusionist_pct'])
    data["Ninja"].append(row['ninja_pct'])
    
equips_df = pd.DataFrame(data)

# Function to prepare comparison data by rarity
def prepare_rarity_data(df, rarity):
    cards_by_rarity = df[df["rarity"] == rarity].sort_values(by="weighted_pct", ascending=False).reset_index()
    pattern = 'Assassin|Illusionist|Ninja'
    selected_cards = cards_by_rarity[~cards_by_rarity['Types'].str.contains(pattern)]
    
    data = {"Name": [], "Assassin": [], "Illusionist": [], "Ninja": []}
    for _, row in selected_cards.iterrows():
        data["Name"].append(row['Name'])
        data["Assassin"].append(row['assassin_pct'])
        data["Illusionist"].append(row['illusionist_pct'])
        data["Ninja"].append(row['ninja_pct'])
    
    return pd.DataFrame(data)

all_common_cards = all_cards[all_cards["rarity"] == "common"]
common_df = prepare_rarity_data(all_common_cards, "common")

all_rare_cards = all_cards[all_cards["rarity"] == "rare"]
rare_df = prepare_rarity_data(all_rare_cards, "rare")

all_mythic_cards = all_cards[all_cards["rarity"] == "mythic"]
mythic_df = prepare_rarity_data(all_mythic_cards, "mythic")

# Prepare (generic) rarity data
generic_rarity_df = pd.DataFrame({
        "Name": ["All", "Common", "Rare", "Mythic"],
        "Assassin": [sum(common_df["Assassin"]) + sum(rare_df["Assassin"]) + sum(mythic_df["Assassin"]),
                     sum(common_df["Assassin"]), sum(rare_df["Assassin"]), sum(mythic_df["Assassin"])],
        "Illusionist": [sum(common_df["Illusionist"]) + sum(rare_df["Illusionist"]) + sum(mythic_df["Illusionist"]),
                        sum(common_df["Illusionist"]), sum(rare_df["Illusionist"]), sum(mythic_df["Illusionist"])],
        "Ninja": [sum(common_df["Ninja"]) + sum(rare_df["Ninja"]) + sum(mythic_df["Ninja"]),
                  sum(common_df["Ninja"]), sum(rare_df["Ninja"]), sum(mythic_df["Ninja"])]
    })

rarity_df = pd.DataFrame({
    "Name": ["Common", "Rare", "Mythic"],
    "Assassin": [sum(all_common_cards["assassin_pct"]), sum(all_rare_cards["assassin_pct"]), sum(all_mythic_cards["assassin_pct"])],
    "Illusionist": [sum(all_common_cards["illusionist_pct"]), sum(all_rare_cards["illusionist_pct"]), sum(all_mythic_cards["illusionist_pct"])],
    "Ninja": [sum(all_common_cards["ninja_pct"]), sum(all_rare_cards["ninja_pct"]), sum(all_mythic_cards["ninja_pct"])]
})

# Define colors for each group
custom_color_sequence = ['red', 'blue', 'green']

# Function to create a Plotly bar figure
def create_bar_figure(data, x_col, y_cols, title, yaxis_title, colors):
    fig = go.Figure()
    for y_col, color in zip(y_cols, colors):
        fig.add_trace(go.Bar(x=data[x_col], y=data[y_col], name=y_col.split('_')[0].capitalize(), marker_color=color))
    fig.update_layout(title_text=title, barmode='group', yaxis_title=yaxis_title)
    return fig

# Function to generate and save individual charts as JSON
def save_chart_as_json(fig, filename):
    chart_data = fig.to_plotly_json()
    with open(filename, 'w') as f:
        json.dump(chart_data, f, cls=PlotlyJSONEncoder)

# Create and save figures
figures = {
    "pitch_distribution": (grouped_sum_pitch, "Pitch", ["assassin_pct", "illusionist_pct", "ninja_pct"], "Percentage of cards", "Pitch Distribution"),
    "defense_distribution": (grouped_sum_defense, "Defense", ["assassin_pct", "illusionist_pct", "ninja_pct"], "Percentage of cards", "Defense Distribution"),
    "cost_distribution": (grouped_sum_cost, "Cost", ["assassin_pct", "illusionist_pct", "ninja_pct"], "Percentage of cards", "Cost Distribution"),
    "card_types_keywords": (card_types_df, "Card Type", ["Assassin", "Illusionist", "Ninja"], "Percentage of cards", "Card Types and Keywords"),
    "transcend_comparison_classes": (transcend_df, "Name", ["Assassin", "Illusionist", "Ninja"], "Percentage of cards", "Transcend Card Across Classes"),
    "equipment_comparison_classes": (equips_df, "Name", ["Assassin", "Illusionist", "Ninja"], "Percentage of equipments", "Equipment Distribution Across Classes"),
    "shared_cards_rarity_comparison": (generic_rarity_df, "Name", ["Assassin", "Illusionist", "Ninja"], "Percentage of cards", "Shared Cards Rarity Distribution"),
    "rarity_comparison": (rarity_df, "Name", ["Assassin", "Illusionist", "Ninja"], "Percentage of cards", "Rarity Distribution"),
    "common_cards": (common_df, "Name", ["Assassin", "Illusionist", "Ninja"], "Percentage of cards", "Common Cards"),
    "rare_cards": (rare_df, "Name", ["Assassin", "Illusionist", "Ninja"], "Percentage of cards", "Rare Cards"),
    "mythic_cards": (mythic_df, "Name", ["Assassin", "Illusionist", "Ninja"], "Percentage of cards", "Mythic Cards")
}

for filename, (data, x_col, y_col_list, yaxis_title, title) in figures.items():
    fig = create_bar_figure(data, x_col, y_col_list, title, yaxis_title, custom_color_sequence)
    save_chart_as_json(fig, f'../docs/vis_data/{filename}.json')

# Load decks by date data from JSON file
with open('../data/decks_by_date_counts.json', 'r') as file:
    decks_by_date_counts = json.load(file)

# Convert the data into a DataFrame
data = []
for name, date_counts in decks_by_date_counts.items():
    for date_str, count in date_counts.items():
        date = datetime.fromisoformat(date_str)
        data.append((date, name, count))

df = pd.DataFrame(data, columns=['date', 'name', 'count'])

# Determine the overall minimum and maximum dates
start_date = df['date'].min()
end_date = df['date'].max()

# Ensure each key has entries at the overall minimum and maximum dates
new_data = []
for name in df['name'].unique():
    name_df = df[df['name'] == name]
    
    if start_date not in name_df['date'].values:
        new_data.append((start_date, name, 0))
        
    if end_date not in name_df['date'].values:
        new_data.append((end_date, name, 0))

# Append the new data to the DataFrame
if new_data:
    new_df = pd.DataFrame(new_data, columns=['date', 'name', 'count'])
    df = pd.concat([df, new_df])

# Sort the DataFrame by date
df = df.sort_values(['name', 'date'])

# Calculate the cumulative count for each name
df['cumulative_count'] = df.groupby('name')['count'].cumsum()

# Create the line chart
fig = px.line(df, x='date', y='cumulative_count', color='name', title='Cumulative Number of Decks Over Time', labels={
                     "cumulative_count": "Number of decks",
                     "date": "Date"
                 },color_discrete_sequence=custom_color_sequence)

# Saving chart
save_chart_as_json(fig, '../docs/vis_data/deck_statistics.json')

# Load decks data
with open('../data/decks.json', 'r') as f:
    decks = json.load(f)

# Calculating relevant stats
heroes = ["Assassin", "Illusionist", "Ninja"]

red_stats = {"Assassin": {}, "Illusionist": {}, "Ninja": {}}
yellow_stats = {"Assassin": {}, "Illusionist": {}, "Ninja": {}}
blue_stats = {"Assassin": {}, "Illusionist": {}, "Ninja": {}}
equip_stats = {"Assassin": {}, "Illusionist": {}, "Ninja": {}}
card_stats = {"Assassin": {}, "Illusionist": {}, "Ninja": {}}
total_stats = {"Assassin": {}, "Illusionist": {}, "Ninja": {}}

for hero in heroes:
    msg = f'# {hero} decks analysis  \n'

    for deck in decks[hero]:
        red_cards_number = 0
        yellow_cards_number = 0
        blue_cards_number = 0
        for card in deck["cards"]:
            match cards.loc[card]["Pitch"]:
                case 1:
                    red_cards_number += 1
                case 2:
                    yellow_cards_number += 1
                case 3: 
                    blue_cards_number += 1

        if red_cards_number not in red_stats[hero]:
            red_stats[hero][red_cards_number] = 0
        red_stats[hero][red_cards_number] += 1

        if yellow_cards_number not in yellow_stats[hero]:
            yellow_stats[hero][yellow_cards_number] = 0
        yellow_stats[hero][yellow_cards_number] += 1

        if blue_cards_number not in blue_stats[hero]:
            blue_stats[hero][blue_cards_number] = 0
        blue_stats[hero][blue_cards_number] += 1

        if len(deck["equips"]) not in equip_stats[hero]:
            equip_stats[hero][len(deck["equips"])] = 0
        equip_stats[hero][len(deck["equips"])] += 1

        if len(deck["cards"]) not in card_stats[hero]:
            card_stats[hero][len(deck["cards"])] = 0
        card_stats[hero][len(deck["cards"])] += 1

        if len(deck["equips"]) + len(deck["cards"]) not in total_stats[hero]:
            total_stats[hero][len(deck["equips"]) + len(deck["cards"])] = 0
        total_stats[hero][len(deck["equips"]) + len(deck["cards"])] += 1

# Function to create a DataFrame from the dictionary using global min and max
def create_dataframe(data_dict):
    # Determine global minimum and maximum numbers
    all_keys = [] 
    for values in data_dict.values():
        for key in values.keys():
            all_keys.append(key)
    global_min = min(all_keys)
    global_max = max(all_keys)

    data = []
    for hero, values in data_dict.items():
        for number in range(global_min, global_max + 1):
            count = values.get(number, 0) # Treat missing values as 0
            deck_pct = round(count / deck_stats[hero] * 100, 2)
            data.append((number, hero, deck_pct))
    
    return pd.DataFrame(data, columns=['number', 'hero', 'deck_pct'])

# Function to create the Plotly figure
def create_plot(dataframe, title):
    fig = px.line(dataframe, x='number', y='deck_pct', color='hero', title=title, labels={
                     "deck_pct": "Percentage of decks",
                     "number": "Number of cards"
                 }, color_discrete_sequence=custom_color_sequence)
    return fig

# Dictionary of all datasets and their respective titles
data_dicts = {
    "Number of red cards": red_stats,
    "Number of yellow cards": yellow_stats,
    "Number of blue cards": blue_stats,
    "Number of equipment cards": equip_stats,
    "Number of non-equipment cards": card_stats,
    "Number of all cards": total_stats
}

# Generate and save charts for each dataset
for title, data_dict in data_dicts.items():
    df = create_dataframe(data_dict)
    fig = create_plot(df, title)
    filename = f'../docs/vis_data/{title.lower().replace(" ", "_")}.json'
    save_chart_as_json(fig, filename)