# 3 Win Decklists Analysis

To see images in Analysis Links, [visit the 3-0 Decklists Analysis](https://petr7410.github.io/fab-3-0-decklists-analysis).

## Index

- [Introduction](#introduction)
- [Overview of Files](#overview-of-files)
- [Database Attributes](#database-attributes)
- [Analysis Links](#analysis-links)
- [Acknowledgements](#acknowledgements)
- [Contributions and Suggestions](#contributions-and-suggestions)

## Introduction

This project provides an analysis of 3-0 decklists from the Runaway Discord server.

If you are only interested in the analysis, check the [Analysis Links](#analysis-links). However, it is recommended to at least review the attribute descriptions.

In the end, this project ended as html page. You can access the analysis folder for md files, but these are using custom css, so they won't render correctly on GitHub.

## Overview of Files

### scripts/

Contains Python scripts used to create files in the analysis folder.

To run these scripts, you need to have Python installed with the following libraries: `pandas`, and `json`.

#### create_cards_csv.py
This script processes text files containing card information, calculates the frequency and distribution of cards for each class, and generates a comprehensive CSV file with all card data.

#### cards_analysis.py
This script loads the deck statistics and card data, calculates the percentage of each class's deck composition, and sorts and exports the data into a CSV file. It is necessary to fill in the section *Setup for md file* to get the correct output for each hero.

### data/
This directory contains the raw data files, including:
- **all_cards.json**: Card data from the *the-fab-cube/flesh-and-blood-cards* repository.
- **complete_cards.csv**: Database created by *create_cards_csv.py* containing all the data you need for your analysis.
- **decks.txt**: Text file with all decks used in this project.
- **deck_stats.json**: Representation of each class.
- **draft files**: Text files with the settings of the draft distribution. This can be used for further analysis.
- Additional less important files.

## Database Attributes

Notes:
- Cards unplayable by class were filtered out and are not included in the database.
- Inventory is still considered, so most decks have over 30 cards.

The main derived attributes of the database are:
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
- `hero_deck_pct`: For example, if the value of this attribute is equal to 100%, it means that the number of cards in the database is equal to the number of Assassin decks in the database.
- `deck_weighted_pct`: This attribute is used to compensate for uneven deck representation. It is hard to give it a direct meaning.

## Analysis Links

To access detailed analysis and card distribution for each class, refer to the following links:

- [Assassin Analysis](docs/Assassin_info.html)
- [Illusionist Analysis](docs/Illusionist_info.html)
- [Ninja Analysis](docs/Ninja_info.html)

To access the complete card distribution statistics for each class:

- [Complete Card Distribution for Assassin](docs/Assassin_all_cards_stats.html)
- [Complete Card Distribution for Illusionist](docs/Illusionist_all_cards_stats.html)
- [Complete Card Distribution for Ninja](docs/Ninja_all_cards_stats.html)
- [Complete Card Distribution for All cards](docs/all_cards_stats.html)
- [Analysis of shared cards across all classes](docs/shared_cards_analysis.html)

### Draft

The following analysis considers the draft file v2.

Take this analysis with a grain of salt, as it is based on decks from the newest draft file (v2). However, there is a high chance that some decks used different files (v1).

Additionally, the sample size is small, as only 3-0 decks from June are considered.

**Brief Explanation of Data:**

- **Expected number of appearances per draft:** The sum of appearances of all cards is equal to `14 * 3 * 8 = 336`.
- **Pick rate:** `number_of_times_picked / (expected_number_of_appearances_per_draft * number_of_win_of_class)` shown as a percentage.
  - This is the pick rate by the winner. A 100 % pick rate would closely (but not completely) correspond to an instant win card.
  - A good pick rate for non-class cards is above 12.5 %, and for class cards, it is above approximately 33.3 % (37.5 %).
- **Pick weight:** `if (class) {pick_rate * 3} else {pick_rate * 8}` metric to compare class and non-class cards.
  - Expecting 8 players to compete for non-class cards and 3 players to compete for class cards.
  - It is possible to use a different number than 3 (for example, 8/3), but it is normal to end up with some cards from different classes.
  - Do not take this attribute too seriously, especially when comparing class and common cards.

To access stats and brief summary of classes:

- [Draft: Assassin Brief Summary](docs/Assassin_draft_analysis.html)
- [Draft: Illusionist Brief Summary](docs/Illusionist_draft_analysis.html)
- [Draft: Ninja Brief Summary](docs/Ninja_draft_analysis.html)

To access the complete card distribution statistics for each class:

- [Draft: Complete Card Distribution for Assassin](docs/Assassin_all_cards_draft.html)
- [Draft: Complete Card Distribution for Illusionist](docs/Illusionist_all_cards_draft.html)
- [Draft: Complete Card Distribution for Ninja](docs/Ninja_all_cards_draft.html)

To access pick rate of non-class cards (Correction of uneven class distribution is not included):

- [Draft Non-Class Cards](docs/draft_non-class_cards.html)

To access card distribution of the current draft file (v2):

- [Draft File Distribution](docs/draft_analysis.html)

### Decks

To access the analysis with respect to the deck distribution of classes:

- [Decks: Assassin Info](docs/Assassin_decks_stats.html)
- [Decks: Illusionist Info](docs/Illusionist_decks_stats.html)
- [Decks: Ninja Info](docs/Ninja_decks_stats.html)

Note: The current method of getting a deck from Fabrary lists only one equipment of the same name.

## Acknowledgements

Thank you to:
- The [Flesh and Blood Cards](https://github.com/the-fab-cube/flesh-and-blood-cards) for providing open access to card details.
- [Runaways TCG](https://x.com/tcgrunaways) for gathering an amazing community.
- briguy for creating the amazing draft file.
- All the people who shared their decks on the Runaways Discord server.

## Contributions and Suggestions

I welcome suggestions for improvements and encourage you to point out any mistakes. If you have any feedback or contributions, please feel free to open an issue or submit a pull request. You can also contact me on Discord: petr7410.