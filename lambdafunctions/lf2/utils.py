
def reorder_dict(d, key_order):
    """Reorder keys in a dictionary."""
    return {key: d[key] for key in key_order if key in d}

def dict_to_html_table(data, cuisine_type, location):
    # Start building HTML table
    html_table = f"""<html>
            <head></head>
            <body>
            <h1> Here is your suggestions for {cuisine_type.title()} restaurants in {location}</h1>.
            <table border='1'>"""

    # Add table header
    html_table += "<tr>"
    for key in data[0].keys():
        html_table += f"<th>{key.title()}</th>"
    html_table += "</tr>"

    # Add table rows
    for item in data:
        html_table += "<tr>"
        for key, value in item.items():
            html_table += f"<td>{str(value).title()}</td>"
        html_table += "</tr>"

    # Close HTML table
    html_table += """</table>
        <br><br>
        <p> Hope you like the suggestions.
                </body>
            </html>"""

    return html_table
