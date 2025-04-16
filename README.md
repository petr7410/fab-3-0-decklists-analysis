# FaB Draft Analysis Scripts

This branch provides scripts that can help you prepare and analyze exported Flesh and Blood draft decks and generate HTML pages with data.

> **Note:** Decks must be exported from [FaBrary](https://fabrary.net) with inclusion of date. On a FaBrary deck page, use **“Copy card list to clipboard”** to obtain the correct format. Please, refer to the `/data/decks.txt` for an example.


## How to Run Locally

### Required Python libraries to run locally:
- **pandas**  
- **markdown**  
- **scipy**  

### Run locally
Note: This repository contains all necessary data to run it without modifying anything. So you can test outputs before diving deeper into init.json logic.
1. Clone or download this repository.
2. Fill `decks.txt` with your exported decks and provide draft files. (You can also use `decks.txt` and draft files from other branches. Be aware that FaBrary recently changed its export format, which might affect compatibility with older exports.)
3. Update `all_cards.csv` if needed.
4. Edit `init.json` to point to your data files and define what you want to generate.
5. Run `create_card_data.py` to process the stats.
6. Run `create_site.py` to generate your custom HTML pages.
7. Open the generated pages using a local server.


## File Structure

### `/script`
- `print_utility.py`: Adds utility functions to the HTML generated by `create_site.py`.
- `create_card_data.py`: Generates the analysis files. Outputs:
  - deck statistics (`decks_stats.json`)
  - hero counts (`decks_by_date_counts.json`)
  - per-card statistics (`cards_stats.csv`)
  - full deck data in json (`decks.json`)
- `create_site.py`: Generates the HTML site based on `init.json`.
- `init.json`: Configuration file that controls how data and HTML files are generated (Detail description of this file in the next section).

### `/docs`
- `css/analysisStyles.css`: Styles for the generated HTML pages.
- `js/utility.js`: Enables image preview functionality for the generated HTML pages.
- `generated/`: The folder where all generated pages will be saved after running the `create_site.py`.

### `/data`
- `all_cards.csv`: Additional card metadata (e.g., Types, Keywords) not included in the draft file.
- `decks.txt`: Decks in FaBrary format.
- `HNTdraft_V0_2.txt` and `HNTdraft_V1_0.txt`: Draft format metadata. Use the provided examples as a reference—format and use the same order to avoid possible problems.


## Configuration: `init.json`

This is the central config file that controls data processing and HTML generation.  

You can view a working example at the `/scripts/init.json`

### Default Required Configuration:

- `data_range`: Time filter (leave blank to disable).
```json
"date_range": {
    "start_date": "2025-01-20 23:30:00",
    "end_date": ""
}
```

- `files`: Paths to required input files. At least one draft file is required. `draft_files` have to be a list, even if it has only one file. If you are using multiple files, please read the last section of this README to learn how the Pick Rate is calculated in this case.
```json
"files": {
    "all_cards": "../data/all_cards.csv",
    "decks": "../data/decks.txt",
    "draft_files": ["../data/HNTdraft_V0_2.txt", "../data/HNTdraft_V1_0.txt"]
}
```

- `draft_file_date`: Must list release dates in the same order as `draft_files`. (First date is required, but ignored.)
```json
"draft_file_date": ["2025-01-01 0:00:00", "2025-01-30 16:00:00"],
```

- `save`: Output paths for processed data files.
```json
"save": {
    "decks_stats": "../data/decks_stats.json",
    "decks_by_date_counts": "../data/decks_by_date_counts.json",
    "cards_stats": "../data/cards_stats.csv",
    "decks": "../data/decks.json"
}
```

- `cracked_bauble`: Defines Cracked Bauble as it may appear in decks but is not part of draft files.
```json
"cracked_bauble": {
    "rarity": "token",
    "collector_number": "HNT245",
    "type": [],
    "image_url": "https://storage.googleapis.com/fabmaster/cardfaces/2025-HNT/EN/HNT245.png"
}
```

- `weapons`: Token weapons that are not drafted but can be present in starting equipment.
```json
"weapons": ["Mark of the Huntsman", "Obsidian Fire Vein", "Kunai of Retribution"]
```

- `cannot_be_played_conditions`: Cards with any of provided types are excluded from the analysis for specific heroes. (Note: this is useful in cases like: Fang can play Draconic cards, but cannot play Draconic Ninja cards)
```json
"cannot_be_played_conditions": {
    "Fang": ["Ninja"],
    "Cindra": ["Warrior"]
}
```

- `can_be_played_conditions`: Additional playable card filters applied after excluding unplayables. If the card does not contain any of the mentioned keywords in type, it is filtered out.

```json
"can_be_played_conditions": {
    "Fang": ["Warrior", "Draconic", "Generic"],
    "Cindra": ["Ninja", "Draconic", "Generic"],
    "Arakni, Web of Deceit": ["Assassin", "Chaos", "Generic"]
}
```

- `html_to_create`: Defines what should be contained on the page. Detailed description below

### `html_to_create` Structure

The `html_to_create` section in `init.json` defines each HTML page you want to generate. Each top-level key is the name of the output site.

#### Example Structure with Explanations:

```json
"Site_Name": {  
  "name": "Site_Title",  
  "filter" : {
    "Types": ["Warrior", "Draconic", "Generic"]
  },
  "negative_filter" : {
    "Types": ["Ninja"]
  },
  "data": {
    "table1": {
      "filter": {
        "Types": ["Action"],
        "_Types": ["Attack"]
      },
      "negative_filter": {
        "Types": ["Equipment"]
      },
      "sort": "Fang_pick_rate",
      "limit": 20,
      "data": [
        "Fang_average_count_per_normalized_deck",
        "Fang_pick_rate",
        "Fang_total_count"
      ],
      "data_name": [
        "Fang average number of card per 30-card deck",
        "Fang Pick rate",
        "Fang Overall number"
      ],
      "group_by": {
        "columns": ["Cost"],
        "aggregation": {
          "Fang_average_count_per_normalized_deck": "sum",
          "Fang_pick_rate": "mean",
          "Fang_total_count": "sum"
        }
      },
      "bonus_data": [],
      "name": "All cards",
      "comment": "Comment",
      "data_table": false
    }
  }
}
```

#### Field-by-Field Explanation:

- **`Site_Name`**: Internal identifier for the site. Used to name the create html Page
- **`name`**: Displayed title on the resulting HTML page.
- **`filter`**: Filters cards that do not met defined conditions.
- **`negative_filter`**: Applies a global filter to exclude cards from this page, that meet condition.

#### Inside `data`:

Each key inside `data` defines a table or section:

- **`table1`**: Key only for your orientation in `init.json` file.

- **`filter`**: Filters cards that do not met defined conditions. If multiple conditions are set on the same field, the logical OR is applied. Prefix repeated keys with underscores to apply logical ANDs.
  - Example:
    ```json
    "Types": ["Draconic"],
    "_Types": ["Warrior"]
    ```

- **`negative_filter`**: Applies a global filter to exclude cards from this page, that meet condition. Uses the same logic, as filter. 

- **`sort`**: Column to sort the table by.

- **`limit`**  Max number of rows to display. If not defined no limit is applied

- **`data`**: The stats or columns to display in the table.

- **`data_name`** Custom column headers shown on the page. If omitted, raw column names are used.

- **`group_by`** Cannot be used the same time as `data_table` for the same table
  - **`columns`**: List of column(s) to group data by.
  - **`aggregation`**: Specifies how to combine grouped values.

- **`bonus_data`**: Should be only use combined with `data_table`. These are searchable but hidden by default. `data_table` always assumes there are three columns like this and for now this can be only changed in the print_utility.py for all tables.

- **`name`**: Header text (`<h3>`) above the table.

- **`comment`**: Descriptive italic text below the header and before the table.

- **`data_table`**: Enables advanced table features like search or sort. Note that `data_table` had the last three columns hidden (User is still able to search by them)


## Pick Rate Calculation for Multiple Draft Files

When multiple draft files are used:

1. Decks published before the second file's release use the first draft file.
2. If multiple files were already released when the deck was published:
   - Compute a ranking score for each based on card presence (`sum of draft_average_occurrenceX`).
   - Add a bonus to newer draft files to compensate for shifts in card usage (Uses maximum  `sum of draft_average_occurrenceX` difference of decks we are sure about).
   - Compare rankings from oldest to newest, and choose the highest-scoring draft file.
3. The selected draft file is used for pick rate calculation.


## Attributes Reference

This section summarizes the key attributes used in the dataset and generated outputs. They are grouped based on their origin: exported draft files, external card databases, and calculated statistics.

### Draft File Columns

These attributes are taken directly from draft file:

- **Name** - The official card name.
- **rarity** - Indicates if a card is *common*, *rare*, or *mythic*.
- **collector_number** - A unique identifier for the card within its set.
- **image_url** - Link to the card’s hosted image.


### Flesh-and-Blood Card Data ([More Details](https://github.com/the-fab-cube/flesh-and-blood-cards/blob/develop/documentation/csv-schemas.md))

These attributes are imported from the `flesh-and-blood-cards` database:

- **Unique ID** - A unique identifier assigned to each card.
- **Pitch** - The pitch value of the card.
- **Cost** - The cost value of the card.
- **Power** - The power value of the card.
- **Defense** - The defense value of the card.
- **Health** - The health value of the card.
- **Intelligence** - The Intelligence value of the card.
- **Types** - Types of the card. (*Ninja*, *Earth*, *Draconic*, *Instant*, ...)
- **Card Keywords** - Keywords that appear on the card.
- **Abilities & Effects** - Types of the abilities or effects of the card.
- **Ability Keywords** - Keywords the card has.
- **Granted Keywords** - Keywords that the card grants.
- **Removed Keywords** - Keywords that the card removes.
- **Interacts with Keywords** - Keywords that the card interacts with.
- **Functional Text** - The text on the card.
- **Type Text** - The type text on the card.
- **Card Played Horizontally** - Is the card played horizontally.
- **Blitz Legal** - Is the card legal in Blitz.
- **CC Legal** - Is the card legal in CC.
- **Commoner Legal** - Is the card legal in Commoner.

### Calculated Columns (Deck-Based Metrics)

These values are generated through `create_card_data.py`:

- **total_count** - Number of times this card appears across all decks.
- **HERO_total_count** - Total appearances of this card in HERO decks.
- **draft_average_occurrenceX** - Average number of times this card appears per draft, based on draft file `X`.
- **pick_rate** - `total_count / (draft_average_occurrence * total_number_of_decks)`
- **HERO_pick_rate** - Same as `pick_rate`, but for a specific hero only.
- **weighted_pick_rate** - Averaged pick rate across heroes: `SUM(HERO_pick_rate) / COUNT(HERO_pick_rate)`
- **average_count_per_deck** - How many copies of the card appear on average in decks.
- **HERO_average_count_per_deck** - How many copies of the card appear on average in HRO decks.
- **average_count_per_normalized_deck** - Adjusted average for decks normalized to 30 cards (undefined for equipment).
- **HERO_average_count_per_normalized_deck** -  Adjusted average for HERO decks normalized to 30 cards(undefined for equipment).


## Acknowledgements

Special thanks to the following projects and communities whose resources made this work possible:

- **[Flesh and Blood Cards](https://github.com/the-fab-cube/flesh-and-blood-cards)** - For providing detailed and structured card data.
- **[Runaways](https://discord.com/invite/EcKkyJJBm6)** - For building an amazing community around Flesh and Blood and to everyone who shared their 3-0 deck.
- **[FaBrary](https://fabrary.net/)** - For offering a robust deck-building and export platform.


## Disclaimer
This project is not affiliated with Legend Story Studios.  
**Legend Story Studios®, Flesh and Blood™, and all associated set names** are trademarks of Legend Story Studios.  
All Flesh and Blood artwork, card images, and characters are the property of Legend Story Studios.  
 © Legend Story Studios  
