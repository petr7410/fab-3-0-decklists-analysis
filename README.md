# Rosetta 3-0 Decklists Analysis

This branch contains data from the old F&B expansion. This means that this data is no longer accessible on the web page. If you want to view this data, please visit [Accessibility](#accessibility).

## Accessibility

### Compatibility with Newer Versions

If you want to run the newest `create_card_data.py` file, then be aware that the FaBrary export format has changed, so:

- You should either update the parsing logic in the main branch to match the Rosetta script  
**or**
- Ideally, write a converter that updates old-format exports to the new format  
**(or wait till I have enough time and energy to do so)**

### Access the version before release of Rosetta

If you are interested in the data but not in the analysis, you can either **clone** this repository or simply **download** what you need from the `data` folder (and potentially the `scripts` folder).

If you want to access the old data, you should do so by using web interface (As viewing the raw HTML file is not very useful)
1. **Clone** the repository or **download** `index.html` and the `docs` folder.
2. Navigate to the folder containing `index.html`. Ensure that the `docs` folder is inside it.
3. Create a local server in this folder. There are multiple ways to do this. I'm using `py -m http.server` (only if you have Python installed), but you can also use `Simple Web Server`, `Simple HTTP Server`, or even the Chrome extension `Web Server for Chrome`.
4. Navigate to the URL of your server at `/index.html`. (For Python method: If you see the message: `Serving HTTP on :: port 8000`, then go to `http://localhost:8000/index.html`.)
5. Now you have access to the final version of Rosetta before the switch to The Hunted.

**Note:** You should be able to view HTML pages in a browser without a local server, but `vis.html` will not load correctly.

## Description of all columns in the created main dataset:
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
