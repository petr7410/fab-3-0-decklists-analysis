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
        'number_of_Florian': df['Florian_total_count'].sum(),
        'number_of_Verdance': df['Verdance_total_count'].sum(),
        'number_of_Oscilio': df['Oscilio_total_count'].sum(),
        'number_of_Aurora': df['Aurora_total_count'].sum()
    }
    return totals

def add_percentages(df, totals):
    for col in ['Florian_total_count', 'Verdance_total_count', 'Oscilio_total_count', 'Aurora_total_count']:
        pct_col = col.replace('count', 'pct')
        df[pct_col] = (df[col] / totals[f'number_of_{col.split("_")[0]}'] * 100).round(2)
    df['weighted_pct'] = ((df['Florian_total_pct'] + df['Verdance_total_pct'] + df['Oscilio_total_pct'] + df['Aurora_total_pct']) / 4).round(2)
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

grouped_sum_pitch = group_and_sum(all_cards, 'Pitch', ["Florian_total_pct", "Verdance_total_pct", "Oscilio_total_pct", "Aurora_total_pct"])
grouped_sum_defense = group_and_sum(all_cards, 'Defense', ["Florian_total_pct", "Verdance_total_pct", "Oscilio_total_pct", "Aurora_total_pct"])
grouped_sum_cost = group_and_sum(all_cards, 'Cost', ["Florian_total_pct", "Verdance_total_pct", "Oscilio_total_pct", "Aurora_total_pct"])

# Calculate percentages for each class
def calculate_percentages(df, col_name):
    types = ["Action", "Attack Reaction", "Instant", "Defense Reaction", "Block"] #Earth, Lightning, Wizard, Runeblade
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
    "Florian": calculate_percentages(all_cards, 'Florian_total_pct'),
    "Verdance": calculate_percentages(all_cards, 'Verdance_total_pct'),
    "Oscilio": calculate_percentages(all_cards, 'Oscilio_total_pct'),
    "Aurora": calculate_percentages(all_cards, 'Aurora_total_pct')
}
card_types_df = pd.DataFrame(card_types_data)

# Prepare equipment data
all_equips = all_equips.reset_index()
data = {"Name": [], "Florian": [], "Verdance": [], "Oscilio": [], "Aurora": []}

for _, row in all_equips.iterrows():
    name = row['Name']
    data["Name"].append(name)
    data["Florian"].append(row['Florian_total_pct'])
    data["Verdance"].append(row['Verdance_total_pct'])
    data["Oscilio"].append(row['Oscilio_total_pct'])
    data["Aurora"].append(row['Aurora_total_pct'])
    
equips_df = pd.DataFrame(data)


# Function to prepare comparison data by rarity
def prepare_data(df, type, heroes): #consider using rarity
    #cards_by_rarity = df[df["rarity"] == rarity].sort_values(by="weighted_pct", ascending=False).reset_index()
    selected_cards = df[df['Types'].str.contains(type)].sort_values(by="weighted_pct", ascending=False).reset_index()
    data = {"Name": []}
    for hero in heroes:
        data[hero] = []
    for _, row in selected_cards.iterrows():
        data["Name"].append(row['Name'])
        for hero in heroes:
            data[hero].append(row[hero + '_total_pct'])
    return pd.DataFrame(data)

#all_lightning_cards = all_cards[all_cards["Type"] == "Lightning"]
lightning_df = prepare_data(all_cards, "Lightning", ["Oscilio", "Aurora"])
earth_df = prepare_data(all_cards, "Earth", ["Florian", "Verdance"])
runeblade_df = prepare_data(all_cards, "Runeblade", ["Florian", "Aurora"])
wizard_df = prepare_data(all_cards, "Wizard", ["Verdance", "Oscilio"])
generic_df = prepare_data(all_cards, "Generic", ["Florian", "Verdance", "Oscilio", "Aurora"])

# Define colors for each group
custom_color_sequence = ['red', 'green', 'blue', "yellow"]

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
    "pitch_distribution": (grouped_sum_pitch, "Pitch", ["Florian_total_pct", "Verdance_total_pct", "Oscilio_total_pct", "Aurora_total_pct"], "Percentage of cards", "Pitch Distribution", custom_color_sequence),
    "defense_distribution": (grouped_sum_defense, "Defense", ["Florian_total_pct", "Verdance_total_pct", "Oscilio_total_pct", "Aurora_total_pct"], "Percentage of cards", "Defense Distribution", custom_color_sequence),
    "cost_distribution": (grouped_sum_cost, "Cost", ["Florian_total_pct", "Verdance_total_pct", "Oscilio_total_pct", "Aurora_total_pct"], "Percentage of cards", "Cost Distribution", custom_color_sequence),
    "card_types_keywords": (card_types_df, "Card Type", ["Florian", "Verdance", "Oscilio", "Aurora"], "Percentage of cards", "Card Types and Keywords", custom_color_sequence),
    "equipment_comparison_classes": (equips_df, "Name", ["Florian", "Verdance", "Oscilio", "Aurora"], "Percentage of equipments", "Equipment Distribution Across Classes", custom_color_sequence),
    "lightning_cards": (lightning_df, "Name", ["Oscilio", "Aurora"], "Percentage of cards", "Lightning Cards", ["blue", "yellow"]),
    "earth_cards": (earth_df, "Name", ["Florian", "Verdance"], "Percentage of cards", "Earth Cards", ["red", "green"]),
    "runeblade_cards": (runeblade_df, "Name", ["Florian", "Aurora"], "Percentage of cards", "Runeblade Cards", ["red", "yellow"]),
    "wizard_cards": (wizard_df, "Name", ["Verdance", "Oscilio"], "Percentage of cards", "Wizard Cards", ["green", "blue"]),
    "generic_cards": (generic_df, "Name", ["Florian", "Verdance", "Oscilio", "Aurora"], "Percentage of cards", "Generic Cards", custom_color_sequence),
}

for filename, (data, x_col, y_col_list, yaxis_title, title, custom_color_sequence) in figures.items():
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
                 },color_discrete_sequence=["yellow", "red", "blue", "green"])

# Saving chart
save_chart_as_json(fig, '../docs/vis_data/deck_statistics.json')

# Load decks data
with open('../data/decks.json', 'r') as f:
    decks = json.load(f)

# Calculating relevant stats
heroes = ["Florian", "Verdance", "Oscilio", "Aurora"]

red_stats = {"Florian": {}, "Verdance": {}, "Oscilio": {}, "Aurora": {}}
yellow_stats = {"Florian": {}, "Verdance": {}, "Oscilio": {}, "Aurora": {}}
blue_stats = {"Florian": {}, "Verdance": {}, "Oscilio": {}, "Aurora": {}}
lightning_stats = {"Florian": {}, "Verdance": {}, "Oscilio": {}, "Aurora": {}}
earth_stats = {"Florian": {}, "Verdance": {}, "Oscilio": {}, "Aurora": {}}
runeblade_stats = {"Florian": {}, "Verdance": {}, "Oscilio": {}, "Aurora": {}}
wizard_stats = {"Florian": {}, "Verdance": {}, "Oscilio": {}, "Aurora": {}}
generic_stats = {"Florian": {}, "Verdance": {}, "Oscilio": {}, "Aurora": {}}
equip_stats = {"Florian": {}, "Verdance": {}, "Oscilio": {}, "Aurora": {}}
card_stats = {"Florian": {}, "Verdance": {}, "Oscilio": {}, "Aurora": {}}
total_stats = {"Florian": {}, "Verdance": {}, "Oscilio": {}, "Aurora": {}}

for hero in heroes:
    msg = f'# {hero} decks analysis  \n'

    for deck in decks[hero]:
        red_cards_number = 0
        yellow_cards_number = 0
        blue_cards_number = 0
        lightning_card_number = 0
        earth_card_number = 0
        runeblade_card_number = 0
        wizard_card_number = 0
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
            if "Lightning" in card_types:
                lightning_card_number += 1
            if "Earth" in card_types:
                earth_card_number += 1
            if "Runeblade" in card_types:
                runeblade_card_number += 1
            if "Wizard" in card_types:
                wizard_card_number += 1
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

        if lightning_card_number not in lightning_stats[hero]:
            lightning_stats[hero][lightning_card_number] = 0
        lightning_stats[hero][lightning_card_number] += 1

        if earth_card_number not in earth_stats[hero]:
            earth_stats[hero][earth_card_number] = 0
        earth_stats[hero][earth_card_number] += 1

        if runeblade_card_number not in runeblade_stats[hero]:
            runeblade_stats[hero][runeblade_card_number] = 0
        runeblade_stats[hero][runeblade_card_number] += 1

        if wizard_card_number not in wizard_stats[hero]:
            wizard_stats[hero][wizard_card_number] = 0
        wizard_stats[hero][wizard_card_number] += 1

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

# Correction
lightning_stats["Florian"][0] = 0
wizard_stats["Florian"][0] = 0

lightning_stats["Verdance"][0] = 0
runeblade_stats["Verdance"][0] = 0

earth_stats["Oscilio"][0] = 0
runeblade_stats["Oscilio"][0] = 0

earth_stats["Aurora"][0] = 0
wizard_stats["Aurora"][0] = 0

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
    "Number of lightning cards": lightning_stats,
    "Number of earth cards": earth_stats,
    "Number of runeblade cards": runeblade_stats,
    "Number of wizard cards": wizard_stats,
    "Number of generic cards": generic_stats,
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