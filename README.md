# 3 Win Decklists Analysis

This branch contains data from the old F&B expansion. This means that this data is no longer accessible on the web page. If you want to view this data, please visit [Accessibility](#accessibility).

## Index

- [Introduction](#introduction)
- [Accessibility](#accessibility)
- [Database Attributes](#database-attributes)
- [Analysis Links](#analysis-links)
- [Overview of Files](#overview-of-files)
- [Acknowledgements](#acknowledgements)
- [Contributions and Suggestions](#contributions-and-suggestions)

## Introduction

This project analyzes 3-0 decklists from the Runaway Discord server.

If you're primarily interested in the analysis, check the [Analysis Links](#analysis-links). However, it is recommended to review the attribute descriptions for a better understanding.

The project end up as an HTML page. The analysis folder contains Markdown files, but they use custom CSS and won't render correctly on GitHub.

## Accessibility

If you are interested in the data but not in the analysis, you can either **clone** this repository or simply **download** what you need from the `data` folder (and potentially the `scripts` folder).

If you are interested in text-based analysis, the easiest way to access it is to download the relevant `.md` files from the `analysis` folder and open them in any Markdown viewer. Note that GitHub does not support custom styles for Markdown files for security reasons, so they appear incorrectly on GitHub. You won't miss out on anything other than visualization, as PtM was originally created to be viewed as Markdown, and all HTML files are pretty much generated from these Markdown files.

If you are interested in the web-based interface:
1. **Clone** the repository or **download** `index.html` and the `docs` folder.
2. Navigate to the folder containing `index.html`. Ensure that the `docs` folder is inside it.
3. Create a local server in this folder. There are multiple ways to do this. I'm using `py -m http.server` (only if you have Python installed), but you can also use `Simple Web Server`, `Simple HTTP Server`, or even the Chrome extension `Web Server for Chrome`.
4. Navigate to the URL of your server at `/index.html`. (For Python method: If you see the message: `Serving HTTP on :: port 8000`, then go to `http://localhost:8000/index.html`.)
5. Now you have access to the final version of PtM before the switch to Rosetta. Congratulations!

**Note:** You should be able to view HTML pages in a browser without a local server, but `vis.html` will not load correctly.

## Database Attributes

Notes:
- Cards unplayable by class were filtered out and are not included in the database.
- Inventory is still considered, so most decks have over 30 cards.

Main derived attributes of the database:
- `Name`: The name of the card.
- `all_cards`: Total count of the card across all decks.
- `assassin_cards`: Count of the cards in Assassin decks.
- `illusionist_cards`: Count of the cards in Illusionist decks.
- `ninja_cards`: Count of the cards in Ninja decks.
- `assassin_deck_pct`: Average number of times a card is contained in an Assassin deck: (`assassin_cards / number_of_assassin_decks`).
- `illusionist_deck_pct`: Average number of times a card is contained in an Illusionist deck: (`illusionist_cards / number_of_illusionist_decks`).
- `ninja_deck_pct`: Average number of times a card is contained in a Ninja deck: (`ninja_cards / number_of_ninja_decks`).
- `deck_weighted_pct`: Weighted percentage of the card across all decks: (`(assassin_deck_pct + illusionist_deck_pct + ninja_deck_pct) / 3`).

Clarifications:
- `hero_deck_pct`: A value of 100% means the number of cards in the database is equal to the number of decks for that hero in the database.
- `deck_weighted_pct`: Compensates for uneven deck representation.

## Analysis Links

Data visualization:

- [Visualizations](docs/vis.html)

Access detailed analysis and card distribution for each class:

- [Assassin Analysis](docs/Assassin_info.html)
- [Illusionist Analysis](docs/Illusionist_info.html)
- [Ninja Analysis](docs/Ninja_info.html)

Complete card distribution statistics for each class:

- [Assassin Card Distribution](docs/Assassin_all_cards_stats.html)
- [Illusionist Card Distribution](docs/Illusionist_all_cards_stats.html)
- [Ninja Card Distribution](docs/Ninja_all_cards_stats.html)
- [All Cards Distribution](docs/all_cards_stats.html)
- [Shared Cards Analysis](docs/shared_cards_analysis.html)

### Draft

This analysis considers draft file v2. Results are based on 3-0 decks after May and *may include some decks from different versions*.

**Brief Explanation of Data:**

- **Expected number of appearances per draft:** The sum of appearances of all cards equals `14 * 3 * 8 = 336`.
- **Pick rate:** `number_of_times_picked / (expected_number_of_appearances_per_draft * number_of_win_of_class)` shown as a percentage.
  - A 100% pick rate closely (but not completely) corresponds to an instant win card.
  - A good pick rate is above 12.5% for non-class cards and approximately 33.3% (37.5%) for class cards.
- **Pick weight:** `if (class) {pick_rate * 3} else {pick_rate * 8}` - compares class and non-class cards.
  - It is expected that 8 players compete for non-class cards and 3 for class cards.
  - This attribute should be used cautiously, especially when comparing class and common cards.

Class summaries and complete card distribution statistics:

- [Assassin Draft Summary](docs/Assassin_draft_analysis.html)
- [Illusionist Draft Summary](docs/Illusionist_draft_analysis.html)
- [Ninja Draft Summary](docs/Ninja_draft_analysis.html)
- [Assassin Draft Card Distribution](docs/Assassin_all_cards_draft.html)
- [Illusionist Draft Card Distribution](docs/Illusionist_all_cards_draft.html)
- [Ninja Draft Card Distribution](docs/Ninja_all_cards_draft.html)
- [Non-Class Cards Draft](docs/draft_non-class_cards.html)
- [Draft File Distribution](docs/draft_analysis.html)

### Decks

Analysis of deck distribution for each class:

- [Assassin Deck Info](docs/Assassin_decks_stats.html)
- [Illusionist Deck Info](docs/Illusionist_decks_stats.html)
- [Ninja Deck Info](docs/Ninja_decks_stats.html)

Note: The method of obtaining decks from Fabrary lists only one piece of equipment of the same name.

## Overview of Files

### scripts/

Python scripts used to create most of the files in this project.

Required Python libraries:
- `pandas`
- `json`
- `warnings`
- `scipy`
- `numpy`

Additionally, if you wish to generate HTML content from Markdown files, you will need the following libraries (otherwise you will have to remove relevant passages):
- `markdown`
- `mistune`

#### Generating Files to be Analyzed

Scripts to generate files located in the `data` folder:
- **create_cards_csv.py**

#### Generating Analysis

Scripts for analysis and report generation:
- **cards_analysis.py**
- **decks_stats.py**
- **draft_analysis.py**
- **shared_cards_analysis.py**

Includes HTML file generation.

#### Utility Scripts

- **print_utility.py**: Utility functions used by other scripts.
- **run_all_scripts.js**: Executes all scripts in the correct order for data generation and analysis.

### data/

Contains raw data files:
- **all_cards.json**: Card data from the *the-fab-cube/flesh-and-blood-cards* repository.
- **complete_cards.csv**: Database created by *create_cards_csv.py*.
- **decks.txt**: Text file with all decks used in this project.
- **deck_stats.json**: Representation of each class.
- **draft files**: Text files with draft distribution settings.

## Acknowledgements

Thank you to:
- [Flesh and Blood Cards](https://github.com/the-fab-cube/flesh-and-blood-cards) for providing open access to card details.
- [Runaways TCG](https://x.com/tcgrunaways) for gathering an amazing community.
- Everyone who shared their decks on the Runaways Discord server.

## Contributions and Suggestions

I welcome suggestions for improvements and encourage you to point out any mistakes. For feedback or contributions, please open an issue or submit a pull request. You can also contact me on Discord: petr7410.