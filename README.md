## Information
The Hunted draft data are out. You can check them out [HERE](https://petr7410.github.io/fab-3-0-decklists-analysis) thanks to the GitHub Pages.  

### Overview of Files in This Repository:

- **/data**  
  - **all_cards.csv** – Sourced from [flesh-and-blood-cards](https://github.com/the-fab-cube/flesh-and-blood-cards).  
  - **cards_stats.csv** – Contains all card statistics gathered from decks, including Cracked Bauble.  
  - **decks_by_date_counts.json** – Records the number of new 3-0 decklists added per date for each hero (based on available data).  
  - **decks_stats.json** – Shows the number of decks for each hero currently used in the analysis.  
  - **decks.json** – Stores all decks for each hero in JSON format.  
  - **decks.txt** – Extracted deck data from Fabrary.  
  - **HNTdraft_\*** – Draft files.  

- **/docs** – Contains all necessary data, HTML templates, scripts, and styles for GitHub Pages.  

- **/scripts**  
  - **create_card_data.py** – Generates `cards_stats.csv` from `all_cards.csv` and `decks.txt`.  
  - **create_site.py** – Builds all analysis pages.  
  - **init.json** – Configuration file required for correct analysis and site generation. A detailed description will be added in the main branch in the near future.  
  - **print_utility.py** – Adds headers and scripts to analysis pages. Used by `create_site.py`.  
  - **vis-py** – Generates the visualization site.  

- **README.md** – This file.  

### Required Python libraries to run locally:
- **pandas**  
- **markdown**  
- **scipy**  
- **numpy**  

### Description of all columns in the created main dataset:
Only brief explanation of attributes used by flesh-and-blood-cards, visit their repo for more information.  

Columns taken from the draft file:  
1. **Name**: The card's official title or name.  
2. **rarity**: Indicates the rarity of the card (common, rare, mythic)
3. **collector_number**: A unique identifier for the card within its set.  
4. **image_url**: The web address where the card’s image is hosted.  

Columns take from the flesh-and-blood-cards (For more details visit [flesh-and-blood-cards repository csv schemas](https://github.com/the-fab-cube/flesh-and-blood-cards/blob/develop/documentation/csv-schemas.md)):  
1. **Unique ID**: A unique identifier assigned to each card.
2. **Pitch**: Pitch value of the card.  
3. **Cost**: Cost value of the card.  
4. **Power**: Power value of the card.  
5. **Defense**: Defense value of the card.  
6. **Health**: Health value of the card.  
7. **Intelligence**: Intelligence value of the card.  
8. **Types**: The types of the card. (This is most likely why you are checking this in the first place) 
9. **Card Keywords**: Keywords that appear on the card .  
10. **Abilities and Effects**: Types of the abilities or effects of the card.  
11. **Ability and Effect Keywords**: Keywords the the card has.  
12. **Granted Keywords**: Keywords that the card grants.  
13. **Removed Keywords**: Keywords that the card removes.  
14. **Interacts with Keywords**: Keywords that the card interacts with.  
15. **Functional Text**: The text on the card.  
16. **Type Text**: The type text on the card.  
17. **Card Played Horizontally**: Is the card played horizontally.  
18. **Blitz Legal**: Is the card legal in Blitz.  
19. **CC Legal**: Is the card legal in CC.  
20. **Commoner Legal**: Is the card legal in Commoner.  

Columns calculated based on decks:  
1. **total_count**: The total count of the card in all decks   -> total_count  
2. **HERO_total_count**: The total count of the card in HERO decks  -> HERO_total_count  
3. **draft_average_occurrence**: The average occurrence of the card in one draft.  
4. **pick_rate**: `All Cards / (Draft Average Occurrence * Number_of_decks)`  
5. **HERO_pick_rate**: `HERO Cards / (Draft Average Occurrence * Number_of_HERO_decks)`  
6. **weighted_pick_rate**: `SUM(HERO pick rate) / COUNT(HERO pick rate)`  
7. **average_count_per_deck**: `All Cards / Number_of_decks`  
8. **HERO_average_count_per_deck**: `HERO Cards / Number_of_HERO_decks`  
9. **average_count_per_normalized_deck**: `average_count_per_deck`, but total count was calculated with respect to deck size, each card in a 30-card deck increased the total count by 1, but each card in a 35-card deck increased the total count by 1 / 35 * 30. (For equipment this is always empty)  
10. **HERO_average_count_per_normalized_deck**: Similar to above but only for HERO decks

### Disclaimer
This project is not affiliated with Legend Story Studios.  
**Legend Story Studios®, Flesh and Blood™, and all associated set names** are trademarks of Legend Story Studios.  
All Flesh and Blood artwork, card images, and characters are the property of Legend Story Studios.  
 © Legend Story Studios  