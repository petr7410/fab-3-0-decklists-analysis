# Style definition
def add_style(msg):
    msg += """\
<style>
    img {
        width: 250px;
    }

    .tooltip {
        position: relative;
        display: inline-block;
    }

    .tooltip .tooltiptext {
        visibility: hidden;
        width: 250px;
        background-color: white;
        text-align: center;
        padding: 5px;
        border-radius: 6px;
        box-shadow: 0px 0px 10px 0px rgba(0, 0, 0, 0.2);

        /* Position the tooltip text */
        position: absolute;
        z-index: 1;
        top: 20px; /* Position it below the link */
        left: 105%; /* Position it to the right of the link */
        margin-left: 0;
    }

    .tooltip:hover .tooltiptext {
        visibility: visible;
    }
</style>"""
    return msg

# html definition
def add_html_format(msg):
    head = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Template</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>\n"""
    tail = """\
\n</body>
</html>"""
    return head + msg + tail
