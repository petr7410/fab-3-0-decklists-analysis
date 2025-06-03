import json
from pathlib import Path

with open("./init.json", "r", encoding="utf-8") as f:
    config = json.load(f)

viz = config["visualization"]

html = []

# Base HTML and head
html.append("""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>Flesh and Blood Deck Statistics</title>
  <link rel=\"stylesheet\" href=\"../css/analysisStyles.css\">
  <script src=\"https://cdn.plot.ly/plotly-latest.min.js\"></script>
  <script src=\"../js/vis_logic.js\" defer></script>
</head>
<body>
  <h1>3-0 Decks Statistics</h1>
""")

# Static charts
static_charts = []

if viz.get("decks_by_date_chart", False):
    static_charts.append(("deck_statistics", "Number of recorded decks", "deck_statistics.json"))

for chart in viz.get("group_by_charts", []):
    static_charts.append((chart["filename"], chart["title"], chart["filename"] + ".json"))

static_config = {}
for chart_id, title, filename in static_charts:
    static_config[chart_id] = filename
    html.append(f"""
<div class=\"chart-container\">
  <h2>{title}</h2>
  <div id=\"{chart_id}\" class=\"chart full-width\"></div>
</div>
""")

# Custom charts (bar charts like card_types_keywords)
custom_charts = viz.get("custom_charts", [])
custom_config = {}
for chart in custom_charts:
    custom_config[chart["filename"]] = f"{chart['filename']}.json"
    html.append(f"""
<div class=\"chart-container\">
  <h2>{chart['title']}</h2>
  <div id=\"{chart['filename']}\" class=\"chart full-width\"></div>
</div>
""")

# Shared cards
shared_cards = viz.get("shared_cards", [])
shared_chart_map = {c['title']: f"{c['filename']}.json" for c in shared_cards}
html.append("""
<div class=\"chart-container\">
  <h2>Shared Cards by Classification</h2>
  <select id=\"shared-chart-select\"></select>
  <select id=\"shared-group-select\"></select>
  <div id=\"cards-classification\" class=\"chart full-width\"></div>
</div>
""")

# Number of cards charts
number_cards = viz.get("number_of_cards_in_deck", [])
number_card_map = {c['title']: f"{c['filename']}.json" for c in number_cards}
html.append("""
<div class=\"chart-container\">
  <h2>Number of Specified Cards in Deck</h2>
  <p>Note: Cumulative Increase represents the graphical visualization of the calculation of discrete expected value.</p>
  <select id=\"type-select\"></select>
  <select id=\"mode-select\"></select>
  <div id=\"number-of-cards\" class=\"chart full-width\"></div>
</div>
""")

# Embed chart config as JSON
full_chart_config = {
    "static": static_config,
    "custom": custom_config,
    "shared": shared_chart_map,
    "number": number_card_map,
    "groups": viz["heroes"]
}

html.append(f"""
<script id=\"chart-config\" type=\"application/json\">
{json.dumps(full_chart_config, indent=2)}
</script>
""")

html.append("""
</body>
</html>
""")

# Write output
output_path = Path("../docs/generated/vis.html")
output_path.write_text("\n".join(html), encoding="utf-8")
print(f"Generated: {output_path}")
