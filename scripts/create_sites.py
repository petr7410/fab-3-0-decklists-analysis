import warnings
import json
import pandas as pd
import markdown
from print_utility import add_html_format, card_with_image

# Suppress Warning messages (A value is trying to be set on a copy of a slice from a DataFrame.)
warnings.simplefilter(action='ignore', category=Warning)

with open('init.json', 'r') as init_file:
    init_data = json.load(init_file)

with open(init_data['save']['cards_stats'], 'r', encoding='utf-8') as file:
    cards = pd.read_csv(file, index_col="Name")

sites = init_data["html_to_create"]

def create_site(site_config, name):
    filtered_cards = cards
    if "filter" in site_config:
        for key, values in site_config["filter"].items():
            filtered_cards = filtered_cards[filtered_cards[key].apply(lambda x: any(val in x for val in values))]

    if "negative_filter" in site_config:
        for key, values in site_config["negative_filter"].items():
            filtered_cards = filtered_cards[~filtered_cards[key].apply(lambda x: any(val in x for val in values))]

    msg = "# " + site_config["name"] + "  \n\n"
    for group_key, group_config in site_config["data"].items():
        if "name" in group_config:
            msg += "### " + group_config["name"] + "\n"
        if "comment" in group_config:
            msg += "*" + group_config["comment"] + "*  \n"

        msg += process_card_group(filtered_cards, group_config)

    with open(f'../docs/generated/{name}.html', 'w') as f:
        f.write(add_html_format(markdown.markdown(msg, extensions=['tables']).replace('<!-- dataTable -->\n<table>', '<table class="dataTable">'), site_config["name"]))


def process_card_group(cards, group_config):
    # Apply filters
    card_group_filtered = cards
    if "filter" in group_config:
        for key, values in group_config["filter"].items():
            key = key.replace("_", "")
            card_group_filtered[key] = card_group_filtered[key].fillna("none")
            card_group_filtered = card_group_filtered[card_group_filtered[key].apply(lambda x: any(val in x for val in values))]

    if "negative_filter" in group_config:
        for key, values in group_config["negative_filter"].items():
            key = key.replace("_", "")
            card_group_filtered[key] = card_group_filtered[key].fillna("none")
            card_group_filtered = card_group_filtered[~card_group_filtered[key].apply(lambda x: any(val in x for val in values))]

    # Apply group_by if specified  #TODO check if this works with multiple columns
    if "group_by" in group_config:  
        group_by_columns = group_config["group_by"]["columns"]
        agg_funcs = group_config["group_by"]["aggregation"]

        # Fill NaN or None values in the group_by_columns with 'none'
        card_group_filtered[group_by_columns] = card_group_filtered[group_by_columns].fillna("none")
        
        # Perform the group_by operation with aggregation
        if group_by_columns:
            card_group_filtered = card_group_filtered.groupby(group_by_columns).agg(agg_funcs).reset_index()
        else:
            card_group_filtered = card_group_filtered.agg(agg_funcs).to_frame().T.reset_index(drop=True)
   
    # Sort the data if required
    if "sort" in group_config:
        sort_column = group_config["sort"]
        if sort_column not in ["Pitch", "Defense", "Cost"]:
            card_group_filtered['sort_column'] = card_group_filtered[sort_column]
            card_group_filtered = card_group_filtered.sort_values(by='sort_column', ascending=False)
        else:
            card_group_filtered['sort_column'] = card_group_filtered[sort_column].replace("XX", 20).replace("none", 100)
            card_group_filtered['sort_column'] = pd.to_numeric(card_group_filtered['sort_column'], errors='coerce')
            card_group_filtered = card_group_filtered.sort_values(by='sort_column')
    
    # Apply limit
    if "limit" in group_config:
        card_group_filtered = card_group_filtered.head(group_config["limit"])

    card_group_filtered = card_group_filtered.reset_index()
    
    msg = ""
    if "data_table" in group_config and group_config["data_table"]:
        msg += "<!-- dataTable -->\n" 
    if "group_by" in group_config and not group_config["group_by"]["columns"]:
        for index, row in card_group_filtered.iterrows():
            for i in range (len(group_config["data"])):
                if "data_name" in group_config:
                    msg += f'{group_config["data_name"][i]}: **{round(row[group_config["data"][i]], 3)}**, '
                else:
                    msg += f'{group_config["data"][i]}: **{round(row[group_config["data"][i]], 3)}**, '
            msg = msg[:-2]
            msg += "  \n"
        return msg
    
    if "group_by" in group_config:
        msg += "| Group | "
    else:
        msg += "| Name | "
    for j in range (len(group_config["data"])):
        msg += group_config["data_name"][j]
        msg += " | "
    if "bonus_data" in group_config:
        for j in range (len(group_config["bonus_data"])):
            msg += group_config["bonus_data"][j]
            msg += " | "
    msg += "  \n| :---: | "
    for _ in range (len(group_config["data"])):
        msg += ":---: | "
    if "bonus_data" in group_config:
        for _ in range (len(group_config["bonus_data"])):
            msg += ":---: | "
    msg += "  \n"
    for index, row in card_group_filtered.iterrows():
        msg += "| "
        if "group_by" in group_config:
            group_name = str(row[group_by_columns])  # Convert to string
            group_name = group_name.split('Name')[0].strip()
            msg += group_name + " | "
        else:
            link = row['image_url']
            name = row['Name']
            msg += card_with_image(name, link) + " | "

        for i in range (len(group_config["data"])):
            if "data_name" in group_config:
                msg += str(round(row[group_config["data"][i]], 3)) + " | "
            else:
                msg += str(round(row[group_config["data"][i]], 3)) + " | "

        if "bonus_data" in group_config:
            for i in range (len(group_config["bonus_data"])):
                msg += str(row[group_config["bonus_data"][i]]) + " | "

        msg += "  \n"
    msg += "\n\n"
    return msg


for key in sites:
    create_site(sites[key], key)