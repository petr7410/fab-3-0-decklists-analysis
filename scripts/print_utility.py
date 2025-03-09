# html definition
def add_html_format(msg, title):
    head = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/2.1.8/css/dataTables.dataTables.min.css"/>
    <script type="text/javascript" src="https://cdn.datatables.net/2.1.8/js/dataTables.min.js"></script>
    <link rel="stylesheet" href="../css/analysisStyles.css">
</head>
<body>
    <div class="content">
        <div class="main-text">\n"""
    tail = """\
\n        </div>
    </div>
    <script type="module" src="../js/utility.js"></script>
    <script>
    $(document).ready(function() {
        $('table.dataTable').DataTable({
            "paging": true,
            "searching": true,
            "ordering": true,
            "order": [],
            "info": true,
            "lengthMenu": [10, 25, 50, 250],
            "columnDefs": [
                {
                    "targets": -3,
                    "visible": false,
                    "searchable": true
                },
                {
                    "targets": -2,
                    "visible": false,
                    "searchable": true
                },
                {
                    "targets": -1,
                    "visible": false,
                    "searchable": true
                }
            ]
        });
    });
    </script>
</body>
</html>"""
    return head + msg + tail

# card with image preview
def card_with_image(card_name, card_link):
    return f'<a href="link" class="tooltip">**{card_name}**<span class="tooltiptext"><img data-src="{card_link}"></span></a>'