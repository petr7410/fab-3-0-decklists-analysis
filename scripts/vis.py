import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import warnings
import json
from datetime import datetime
from plotly.utils import PlotlyJSONEncoder

# Suppress Warning messages
warnings.simplefilter(action='ignore', category=Warning)

# Load defined configuration from init.json
with open('./init.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

viz_config = config['visualization']
heroes = viz_config['heroes']
heroes_color = viz_config['heroes_color']
heroes_color_map = dict(zip(heroes, heroes_color))

# Load the relevant files    
with open(config['save']['decks_stats'], 'r') as f:
    deck_stats = json.load(f)

with open(config['save']['cards_stats'], 'r', encoding='utf-8') as file:
    cards = pd.read_csv(file, index_col="Name")

# Helper functions
def calculate_totals(df, heroes):
    return {f'number_of_{hero}': df[f'{hero}_total_count'].sum() for hero in heroes}

def add_percentages(df, heroes, totals):
    for hero in heroes:
        count_col = f'{hero}_total_count'
        pct_col = f'{hero}_total_pct'
        df[pct_col] = (df[count_col] / totals[f'number_of_{hero}'] * 100).round(2)
    df['weighted_pct'] = (df[[f'{hero}_total_pct' for hero in heroes]].sum(axis=1) / len(heroes)).round(2)
    return df

# Fill NaN values with "None"
def fill_na_columns(df, columns):
    for col in columns:
        df[col] = df[col].fillna('None')
    return df

# Group and sum by specified columns
def group_and_sum(df, group_by_col, sum_cols):
    # Group and sum
    grouped = df.groupby(group_by_col)[sum_cols].sum().reset_index()

    # Create a custom sort key: (is_not_numeric, numeric_or_string_value)
    def sort_key(val):
        try:
            return (0, int(val))  # numeric values come first
        except (ValueError, TypeError):
            return (1, str(val))  # non-numeric values come later, sorted alphabetically

    grouped = grouped.sort_values(by=group_by_col, key=lambda col: col.map(sort_key))

    return grouped

# Filter data and return sum of the col_name
def filter_and_sum(df, col_name, filter_include=None, filter_exclude=None):
    filtered_df = df.copy()

    if filter_include:
        for key, values in filter_include.items():
            key = key.replace("_", "")
            filtered_df[key] = filtered_df[key].fillna("none")
            filtered_df = filtered_df[filtered_df[key].apply(lambda x: any(val in x for val in values))]

    if filter_exclude:
        for key, values in filter_exclude.items():
            key = key.replace("_", "")
            filtered_df[key] = filtered_df[key].fillna("none")
            filtered_df = filtered_df[~filtered_df[key].apply(lambda x: any(val in x for val in values))]

    return filtered_df[col_name].sum()

# Filters cards, sort them by weighted_pct and returns df with column for each hero in heroes with total_pct for each remaining card
def create_card_data(df, types_include, types_exclude, heroes): 
    # Has to include all types from the type_include
    if types_include is not None:
        for key, values in types_include.items():
            key = key.replace("_", "")
            df[key] = df[key].fillna("none")
            df = df[df[key].apply(lambda x: any(val in x for val in values))]

    # Apply negative filter (exclude rows containing any type in types_exclude)
    if types_exclude is not None:
        for key, values in types_exclude.items():
            key = key.replace("_", "")
            df[key] = df[key].fillna("none")
            df = df[~df[key].apply(lambda x: any(val in x for val in values))]

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

def create_bar_figure(data, x_col, y_cols, title, yaxis_title, colors):
    fig = go.Figure()
    for y_col, color in zip(y_cols, colors):
        fig.add_trace(go.Bar(x=data[x_col], y=data[y_col], name=y_col.split('_')[0].capitalize(), marker_color=color))
    fig.update_layout(title_text=title, barmode='group', yaxis_title=yaxis_title)
    return fig

def save_chart_as_json(fig, filename):
    chart_data = fig.to_plotly_json()
    with open(filename, 'w') as f:
        json.dump(chart_data, f, cls=PlotlyJSONEncoder)

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


def create_plot(dataframe, title):
    fig = px.line(dataframe, x='number', y='deck_pct', color='hero', title=title, labels={
                     "deck_pct": "Percentage of decks",
                     "number": "Number of cards"
                 }, color_discrete_map=heroes_color_map)
    return fig

# Processing
cards = fill_na_columns(cards, ['Pitch', 'Defense', 'Cost'])
totals = calculate_totals(cards, heroes)
cards = add_percentages(cards, heroes, totals)
cards = cards.sort_values(by='weighted_pct', ascending=False)


# --- Create chart with decks by date data ---
if viz_config.get("decks_by_date_chart", False):
    with open(config['save']['decks_by_date_counts'], 'r') as file:
        decks_by_date_counts = json.load(file)

    rows = [(datetime.fromisoformat(d), n, c) for n, counts in decks_by_date_counts.items() for d, c in counts.items()]
    df = pd.DataFrame(rows, columns=['date', 'name', 'count'])
    date_range = pd.date_range(df['date'].min(), df['date'].max())
    full_index = pd.MultiIndex.from_product([df['name'].unique(), date_range], names=['name', 'date'])
    df = df.set_index(['name', 'date']).reindex(full_index, fill_value=0).reset_index()
    df['cumulative_count'] = df.groupby('name')['count'].cumsum()

    fig = px.line(df, x='date', y='cumulative_count', color='name', title='Cumulative Number of Decks Over Time',
                labels={"cumulative_count": "Number of decks", "date": "Date"},
                color_discrete_map=heroes_color_map,
                category_orders={"name": list(heroes_color_map.keys())}) # This line guarantees to correct order of heroes to guarantee the color match 
    save_chart_as_json(fig, '../docs/generated/vis_data/deck_statistics.json')


# --- Create data for initial bar-charts ---
# group_by_charts
figures = {}
for chart in viz_config.get("group_by_charts", []):
    grouped_data = group_and_sum(cards, chart["group_by"], [f'{hero}_total_pct' for hero in heroes])
    figures[chart["filename"]] = (grouped_data, chart["group_by"], [f'{hero}_total_pct' for hero in heroes], chart["x-axis"], chart["title"], heroes_color)

for chart in viz_config.get("custom_charts", []):
    bar_data = {
        "data": [],
    }

    for hero in heroes:
        bar_data[hero] = []

    for bar in chart["bars"]:
        name = bar["name"]
        filter_include = bar.get("filter")
        filter_exclude = bar.get("negative_filter")

        bar_data["data"].append(name)
        for hero in heroes:
            value = filter_and_sum(cards, f"{hero}_total_pct", filter_include, filter_exclude)
            bar_data[hero].append(value)

    df = pd.DataFrame(bar_data)
    figures[chart["filename"]] = (
        df,
        "data",
        heroes,
        chart["x-axis"],
        chart["title"],
        heroes_color
    )

for filename, (data, x_col, y_cols, yaxis_title, title, color_seq) in figures.items():
    fig = create_bar_figure(data, x_col, y_cols, title, yaxis_title, color_seq)
    save_chart_as_json(fig, f'../docs/generated/vis_data/{filename}.json')


# --- Create data for Shared Cards
for chart in viz_config['shared_cards']:
    df = create_card_data(cards, chart.get('filter'), chart.get('negative_filter'), chart['heroes'])
    filename = f"../docs/generated/vis_data/{chart['filename']}.json"
    fig = create_bar_figure(df, "Name", chart['heroes'], chart['title'], chart['x-axis'], heroes_color)
    save_chart_as_json(fig, filename)


# --- Create data for Number of specified cards in deck chart ~> To improve efficiency the pre-computation is done first ---
with open(config['save']['decks'], 'r') as f:
    decks = json.load(f)

# Precompute which cards match which chart -> This should improve efficiency when working with decks, as it does not apply filter on each card in deck (there is lot of duplicity), but only on all cards in set
card_matches = {card: set() for card in cards.index}

for i, chart in enumerate(viz_config['number_of_cards_in_deck']):
    filter_include = chart.get('filter')
    filter_exclude = chart.get('negative_filter')

    for card_name, card_data in cards.iterrows():
        match = True

        if filter_include:
            for field, values in filter_include.items():
                val = str(card_data.get(field.replace('_', ''), 'none'))
                if not any(str(v) in val for v in values):
                    match = False
        
        if match and filter_exclude:
            for field, values in filter_exclude.items():
                val = str(card_data.get(field.replace('_', ''), 'none'))
                if any(str(v) in val for v in values):
                    match = False

        if match:
            card_matches[card_name].add(i)
# card_matches[card_name] now contains set of indices. Each index corresponds to the index of chart, which filter criteria the card meets ~> This should be a bit more memory efficient, then doing this the other way around, as we would need to use the card name as a key

# Create data for charts
stats_templates = {(chart['filename'], chart['title']): {hero: {} for hero in heroes} for chart in viz_config['number_of_cards_in_deck']}

for i, chart in enumerate(viz_config['number_of_cards_in_deck']):
    filename = chart['filename']
    title = chart['title']
    for hero in heroes:
        if hero in chart.get("correction", []): # Correction to avoid initial spike if the class cannot play cards (As all decks would have 0 of card type)
            continue
        for deck in decks[hero]:
            count = sum(1 for card in deck["cards"] if i in card_matches[card])
            count += sum(1 for card in deck["equips"] if i in card_matches[card])
            stats_templates[(filename, title)][hero][count] = stats_templates[(filename, title)][hero].get(count, 0) + 1



for (filename, title), data_dict in stats_templates.items():
    df = create_dataframe(data_dict)
    fig = create_plot(df, title)
    filepath = f'../docs/generated/vis_data/{filename}.json'
    save_chart_as_json(fig, filepath)
