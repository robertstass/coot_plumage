#!/usr/bin/env python
# Part of coot_plumage (github.com/robertstass/coot_plumage). Written by Robert Stass, Bowden group, STRUBI/OPIC (2024)

from bs4 import BeautifulSoup
import pandas as pd
import xmlrpc.client
import argparse
import sys
import os
class ArgumentParser():

    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Select residues from a molprobity html file to send to coot.")

        # Required arguments
        self.parser.add_argument("--column", "-c", default=default_column,
                            help=f"Column to filter (default: {default_column})")
        self.parser.add_argument("--filter_text", "-ft", default=default_filter_text,
                            help=f"Only select rows containing this text (default: {default_filter_text})")

        # Optional argument
        self.parser.add_argument("--port", type=int, default=default_port, help=f"Port number (default: {default_port})")

        # Positional HTML file argument
        self.parser.add_argument("html_file", help="Path to the molprobity HTML file")
        if len(sys.argv) == 1:
            self.usage()
            sys.exit()

    def usage(self):
        self.parser.print_help()

    def error(self, *msgs):
        self.usage()
        print("Error: " + '\n'.join(msgs))
        print(" ")
        sys.exit(2)

    def validate(self, args):
        if not os.path.exists(args.html_file):
            self.error("Error: HTML file '%s' not found." % args.html_file)


def parse_html_table(file_path, table_index=0):
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    tables = soup.find_all("table")  # Get all tables

    if not tables:
        raise ValueError("No tables found in the HTML file.")

    # Print number of tables found
    #print("Found %s tables in the HTML file." % len(tables))

    # Choose the correct table
    table = tables[table_index]  # Adjust index if necessary

    # Extract rows
    rows = []
    for row in table.find_all("tr"):
        cells = row.find_all(["td", "th"])
        row_data = [cell.get_text(" ", strip=True) for cell in cells]
        if row_data:
            rows.append(row_data)

    # Determine headers
    headers = rows[0] if rows else None
    data = rows[1:] if headers else rows

    df = pd.DataFrame(data, columns=headers if headers else None)

    df_head =  df.head(1)
    # Remove header rows where the first column is "#" or blank
    first_col = df.iloc[:, 0]  # Ensure first column is selected
    df = df[~first_col.isin(["#", ""])]

    # Reset index
    df = df.reset_index(drop=True)

    return df, df_head




# Default values
default_column = "Rotamer"
default_filter_text = "OUTLIER"
default_port = 5007
ResidueColumn = "#"
molprobity_table_number = 3 #This shouldn't change unless molprobity update their site.


def main(html_file, column, filter_text, port):

    # script
    df, df_head = parse_html_table(html_file, table_index=molprobity_table_number)
    try:
        subset_df = df[df[column].str.contains(filter_text)]
    except KeyError:
        raise KeyError("Invalid column name: '%s'" % column)

    print("Total residues: %d" % len(df))
    print("Filtered residues: %d" % len(subset_df))

    residue_list = [resi_string.split() for resi_string in subset_df[ResidueColumn]]
    residue_list = [(chain, int(residue)) for chain, residue in residue_list]

    print("Sending residue list to coot...")
    try:
        coot = xmlrpc.client.ServerProxy("http://127.0.0.1:%d" % port)
        coot.update_residue_list(residue_list)
        print('Command sent to coot.')
    except ConnectionRefusedError:
        print('ConnectionRefusedError: Make sure coot is open and has a xmlrpc server listening on port %d.' % port)
        print("For example by running run_script('molprobity_to_coot_server.py') in coot." )


if __name__ == "__main__":
    argparser = ArgumentParser()
    args = argparser.parser.parse_args()
    argparser.validate(args)
    main(args.html_file,
        args.column,
        args.filter_text,
        args.port)



