import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import warnings
import json
from datetime import datetime
from plotly.utils import PlotlyJSONEncoder

# Suppress Warning messages
warnings.simplefilter(action='ignore', category=Warning)
    
with open('../data/decks_stats.json', 'r') as f:
    deck_stats = json.load(f)

file_path = '../data/cards_stats.csv'
with open(file_path, 'r', encoding='utf-8') as file:
    cards = pd.read_csv(file, index_col="Name")

# Split cards into all_cards and all_equips
all_cards = cards[~cards["Types"].str.contains("Equipment")]
all_equips = cards[cards["Types"].str.contains("Equipment")]

def calculate_totals(df):
    totals = {
        'number_of_Fang': df['Fang_total_count'].sum(),
        'number_of_Cindra': df['Cindra_total_count'].sum(),
        'number_of_Arakni, Web of Deceit': df['Arakni, Web of Deceit_total_count'].sum(),
    }
    return totals

def add_percentages(df, totals):
    for col in ['Fang_total_count', 'Cindra_total_count', 'Arakni, Web of Deceit_total_count']:
        pct_col = col.replace('count', 'pct')
        df[pct_col] = (df[col] / totals[f'number_of_{col.split("_")[0]}'] * 100).round(2)
    df['weighted_pct'] = ((df['Fang_total_pct'] + df['Cindra_total_pct'] + df['Arakni, Web of Deceit_total_pct']) / 4).round(2)
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
    pitchList = ["None", "X", "XX"]
    grouped[group_by_col] = grouped[group_by_col].apply(lambda x: str(int(x)) if x not in pitchList else x)
    return grouped

grouped_sum_pitch = group_and_sum(all_cards, 'Pitch', ["Fang_total_pct", "Cindra_total_pct", "Arakni, Web of Deceit_total_pct"])
grouped_sum_defense = group_and_sum(all_cards, 'Defense', ["Fang_total_pct", "Cindra_total_pct", "Arakni, Web of Deceit_total_pct"])
grouped_sum_cost = group_and_sum(all_cards, 'Cost', ["Fang_total_pct", "Cindra_total_pct", "Arakni, Web of Deceit_total_pct"])

# Calculate percentages for each class
def calculate_percentages(df, col_name):
    types = ["Action", "Attack Reaction", "Instant", "Defense Reaction", "Block"]
    #keywords = ["Transcend", "Go again", "Stealth", "Ward", "Combo"]
    percentages = []
    
    for t in types:
        if "Action" in t:
            percentages.append(df[df["Types"].str.contains(t) & df["Types"].str.contains("Attack")][col_name].sum())
            percentages.append(df[df["Types"].str.contains(t) & ~df["Types"].str.contains("Attack")][col_name].sum())
        else:
            percentages.append(df[df["Types"].str.contains(t)][col_name].sum())
    
    #filtered_hero_cards = df[df["Card Keywords"].notna()]
    #for keyword in keywords:
    #    percentages.append(filtered_hero_cards[filtered_hero_cards["Card Keywords"].str.contains(keyword)][col_name].sum())
    
    return percentages

# Calculate and organize percentages
card_types = ["Attack Action", "Non-Attack Action", "Attack Reaction", "Instant", "Defense Reaction", "Block"]
card_types_data = {
    "Card Type": card_types,
    "Fang": calculate_percentages(all_cards, 'Fang_total_pct'),
    "Cindra": calculate_percentages(all_cards, 'Cindra_total_pct'),
    "Arakni, Web of Deceit": calculate_percentages(all_cards, 'Arakni, Web of Deceit_total_pct'),
}
card_types_df = pd.DataFrame(card_types_data)

# Prepare equipment data
all_equips = all_equips.reset_index()
data = {"Name": [], "Fang": [], "Cindra": [], "Arakni, Web of Deceit": []}

for _, row in all_equips.iterrows():
    name = row['Name']
    data["Name"].append(name)
    data["Fang"].append(row['Fang_total_pct'])
    data["Cindra"].append(row['Cindra_total_pct'])
    data["Arakni, Web of Deceit"].append(row['Arakni, Web of Deceit_total_pct'])
    
equips_df = pd.DataFrame(data)


#consider using rarity
def prepare_data(df, types_include, types_exclude, heroes): 
    # Has to include all types from the type_include
    if types_include:
        for t in types_include:
            df = df[df['Types'].str.contains(t)]

    # Apply negative filter (exclude rows containing any type in types_exclude)
    if types_exclude:
        df = df[~df['Types'].str.contains('|'.join(types_exclude))]

    selected_cards = df.sort_values(by="weighted_pct", ascending=False).reset_index()

    # Prepare the data dictionary
    data = {"Name": []}
    for hero in heroes:
        data[hero] = []

    # Populate the data dictionary
    for _, row in selected_cards.iterrows():
        data["Name"].append(row['Name'])
        for hero in heroes:
            data[hero].append(row[hero + '_total_pct'])

    return pd.DataFrame(data)

draconic_df = prepare_data(all_cards, ["Draconic"], ["Warrior", "Ninja"], ["Fang", "Cindra"])
ninja_assassin_df = prepare_data(all_cards, ["Ninja", "Assassin"], [], ["Cindra", "Arakni, Web of Deceit"])
warrior_assassin_df = prepare_data(all_cards, ["Warrior", "Assassin"], [], ["Fang", "Arakni, Web of Deceit"])
generic_df = prepare_data(all_cards, ["Generic"], [], ["Fang", "Cindra", "Arakni, Web of Deceit"])

# Define colors for each group
custom_color_sequence = ['red', '#ffd901', 'blue']

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
    "pitch_distribution": (grouped_sum_pitch, "Pitch", ["Fang_total_pct", "Cindra_total_pct", "Arakni, Web of Deceit_total_pct"], "Percentage of cards", "Pitch Distribution", custom_color_sequence),
    "defense_distribution": (grouped_sum_defense, "Defense", ["Fang_total_pct", "Cindra_total_pct", "Arakni, Web of Deceit_total_pct"], "Percentage of cards", "Defense Distribution", custom_color_sequence),
    "cost_distribution": (grouped_sum_cost, "Cost", ["Fang_total_pct", "Cindra_total_pct", "Arakni, Web of Deceit_total_pct"], "Percentage of cards", "Cost Distribution", custom_color_sequence),
    "card_types_keywords": (card_types_df, "Card Type", ["Fang", "Cindra", "Arakni, Web of Deceit"], "Percentage of cards", "Card Types and Keywords", custom_color_sequence),
    "equipment_comparison_classes": (equips_df, "Name", ["Fang", "Cindra", "Arakni, Web of Deceit"], "Percentage of equipments", "Equipment Distribution Across Classes", custom_color_sequence),
    "pure_draconic_cards": (draconic_df, "Name", ["Fang", "Cindra"], "Percentage of cards", "Pure Draconic Cards", ["red", "#ffd901"]),
    "ninja_assassin_cards": (ninja_assassin_df, "Name", ["Cindra", "Arakni, Web of Deceit"], "Percentage of cards", "Ninja/Assassin Cards", ["#ffd901", "blue"]),
    "warrior_assassin_cards": (warrior_assassin_df, "Name", ["Fang", "Arakni, Web of Deceit"], "Percentage of cards", "Warrior/Assassin Cards", ["red", "blue"]),
    "generic_cards": (generic_df, "Name", ["Fang", "Cindra", "Arakni, Web of Deceit"], "Percentage of cards", "Generic Cards", custom_color_sequence),
}

for filename, (data, x_col, y_col_list, yaxis_title, title, custom_color_sequence) in figures.items():
    fig = create_bar_figure(data, x_col, y_col_list, title, yaxis_title, custom_color_sequence)
    save_chart_as_json(fig, f'../docs/generated/vis_data/{filename}.json')

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

# Generate a full date range
date_range = pd.date_range(df['date'].min(), df['date'].max())

# Ensure each name has all dates
all_names = df['name'].unique()
full_index = pd.MultiIndex.from_product([all_names, date_range], names=['name', 'date'])

# Reindex the DataFrame to fill missing dates
df = df.set_index(['name', 'date']).reindex(full_index, fill_value=0).reset_index()

# Calculate the cumulative count for each name
df['cumulative_count'] = df.groupby('name')['count'].cumsum()

# Create the line chart
fig = px.line(df, x='date', y='cumulative_count', color='name', title='Cumulative Number of Decks Over Time',
              labels={"cumulative_count": "Number of decks", "date": "Date"},
              color_discrete_sequence=["blue", "red", "#ffd901"])

# Saving chart
save_chart_as_json(fig, '../docs/generated/vis_data/deck_statistics.json')

# Load decks data
with open('../data/decks.json', 'r') as f:
    decks = json.load(f)

# Calculating relevant stats
heroes = ["Fang", "Cindra", "Arakni, Web of Deceit"]

red_stats = {"Fang": {}, "Cindra": {}, "Arakni, Web of Deceit": {}}
yellow_stats = {"Fang": {}, "Cindra": {}, "Arakni, Web of Deceit": {}}
blue_stats = {"Fang": {}, "Cindra": {}, "Arakni, Web of Deceit": {}}
draconic_stats = {"Fang": {}, "Cindra": {}, "Arakni, Web of Deceit": {}}
warrior_stats = {"Fang": {}, "Cindra": {}, "Arakni, Web of Deceit": {}}
ninja_stats = {"Fang": {}, "Cindra": {}, "Arakni, Web of Deceit": {}}
assassin_stats = {"Fang": {}, "Cindra": {}, "Arakni, Web of Deceit": {}}
generic_stats = {"Fang": {}, "Cindra": {}, "Arakni, Web of Deceit": {}}
equip_stats = {"Fang": {}, "Cindra": {}, "Arakni, Web of Deceit": {}}
card_stats = {"Fang": {}, "Cindra": {}, "Arakni, Web of Deceit": {}}
total_stats = {"Fang": {}, "Cindra": {}, "Arakni, Web of Deceit": {}}

for hero in heroes:
    msg = f'# {hero} decks analysis  \n'

    for deck in decks[hero]:
        red_cards_number = 0
        yellow_cards_number = 0
        blue_cards_number = 0
        draconic_card_number = 0
        warrior_card_number = 0
        ninja_card_number = 0
        assassin_card_number = 0
        generic_card_number = 0
        for card in deck["cards"]:
            match cards.loc[card]["Pitch"]:
                case 1:
                    red_cards_number += 1
                case 2:
                    yellow_cards_number += 1
                case 3: 
                    blue_cards_number += 1
            card_types = cards.loc[card]["Types"]
            if "Draconic" in card_types:
                draconic_card_number += 1
            if "Warrior" in card_types:
                warrior_card_number += 1
            if "Ninja" in card_types:
                ninja_card_number += 1
            if "Assassin" in card_types:
                assassin_card_number += 1
            if "Generic" in card_types:
                generic_card_number += 1

        if red_cards_number not in red_stats[hero]:
            red_stats[hero][red_cards_number] = 0
        red_stats[hero][red_cards_number] += 1

        if yellow_cards_number not in yellow_stats[hero]:
            yellow_stats[hero][yellow_cards_number] = 0
        yellow_stats[hero][yellow_cards_number] += 1

        if blue_cards_number not in blue_stats[hero]:
            blue_stats[hero][blue_cards_number] = 0
        blue_stats[hero][blue_cards_number] += 1

        if draconic_card_number not in draconic_stats[hero]:
            draconic_stats[hero][draconic_card_number] = 0
        draconic_stats[hero][draconic_card_number] += 1

        if warrior_card_number not in warrior_stats[hero]:
            warrior_stats[hero][warrior_card_number] = 0
        warrior_stats[hero][warrior_card_number] += 1

        if ninja_card_number not in ninja_stats[hero]:
            ninja_stats[hero][ninja_card_number] = 0
        ninja_stats[hero][ninja_card_number] += 1

        if assassin_card_number not in assassin_stats[hero]:
            assassin_stats[hero][assassin_card_number] = 0
        assassin_stats[hero][assassin_card_number] += 1

        if generic_card_number not in generic_stats[hero]:
            generic_stats[hero][generic_card_number] = 0
        generic_stats[hero][generic_card_number] += 1

        if len(deck["equips"]) not in equip_stats[hero]:
            equip_stats[hero][len(deck["equips"])] = 0
        equip_stats[hero][len(deck["equips"])] += 1

        if len(deck["cards"]) not in card_stats[hero]:
            card_stats[hero][len(deck["cards"])] = 0
        card_stats[hero][len(deck["cards"])] += 1

        if len(deck["equips"]) + len(deck["cards"]) not in total_stats[hero]:
            total_stats[hero][len(deck["equips"]) + len(deck["cards"])] = 0
        total_stats[hero][len(deck["equips"]) + len(deck["cards"])] += 1

# Correction to avoid initial spike if the class cannot play cards
ninja_stats["Fang"][0] = 0
warrior_stats["Cindra"][0] = 0
draconic_stats["Arakni, Web of Deceit"][0] = 0

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
    "Number of draconic cards": draconic_stats,
    "Number of warrior cards": warrior_stats,
    "Number of ninja cards": ninja_stats,
    "Number of assassin cards": assassin_stats,
    "Number of generic cards": generic_stats,
    "Number of equipment cards": equip_stats,
    "Number of non-equipment cards": card_stats,
    "Number of all cards": total_stats
}

# Generate and save charts for each dataset
for title, data_dict in data_dicts.items():
    df = create_dataframe(data_dict)
    fig = create_plot(df, title)
    filename = f'../docs/generated/vis_data/{title.lower().replace(" ", "_")}.json'
    save_chart_as_json(fig, filename)