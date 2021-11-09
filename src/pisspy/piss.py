#!/usr/bin/env python3

#==============================================================================#
#$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$#
# piss.py - main script for the personal inventory system

import pissqrgen, pissdb, sys, os;

def printEntry(entry):
    # Print a separator
    print("\n\n\n#### #### #### ####")
    # Print the ID number
    print("ID Number:");
    print("\t" + pissqrgen.formatIdNum(entry[pissdb.DbEntry.IDNUM]));
    # If it's a __concept__ or if it's in __purgatory__, print the "status"
    # and return
    status = entry[pissdb.DbEntry.STATUS];
    if(status == "__concept__"):
        print("STATUS:\n\tMerely a concept...");
        return 0;

    if(status == "__purgatory__"):
        print("STATUS:\n\tSent to purgatory...");

    # Print the location
    print("Location:");
    print("\t" + entry[pissdb.DbEntry.LOCATION]);
    # Print the quantity
    print("Quantity:");
    print("\t" + entry[pissdb.DbEntry.QUANTITY]);
    # Print the properties
    print("Properties:");

    for property in entry[pissdb.DbEntry.PROPERTIES:]:
        print("\t" + property);

    return 0;

def yesNo(message):
    yes = input(message)

    if(yes.lower() == "y"):
        return True;

    return False;

# Main function. Not necissary, but it makes me feel better
def main(argv):
    # Generate qr code sheet
    if(argv[1] == "generate"):
        DPI = 300; # To be configurable in an update

        # Ask a bunch of questions. I will probably make presets and stuff
        # in a later date...
        paperWidth = float(input("Width in inches? "));
        paperHeight = float(input("Height in inches? "));
        paperMarginY = float(input("Top/Bottom margin in inches? "));
        paperMarginX = float(input("Left/Right margin in inches? "));
        countX = int(input("Horizontal label count? "));
        countY = int(input("Vertical label count? "));

        print("Generating label sheet...");

        width = int(paperWidth * DPI);
        height = int(paperHeight * DPI);
        marginX = int(paperMarginX * DPI);
        marginY = int(paperMarginY * DPI);


        sheet = pissqrgen.genSheet(
            width,
            height,
            countX,
            countY,
            marginX,
            marginY
        );

        filename = input("Save file as? ");
        if(os.path.exists(filename)):
            overwrite = yesNo("File exists! Overwrite(y/n)? ");

            if(overwrite == False):
                print("Giving up!");
                exit();

        sheet.save(filename);
        pissdb.publish();

    # Search entries
    if(argv[1] == "search"):
        # Initialize the database
        pissdb.init();
        print("Enter as many keywords as you want, then press Ctrl+D to search");

        keywords = [];
        while True:
            try:
                keyword = input("Keyword? ");
                keywords.append(keyword);
            except EOFError:
                break;

        searchResults = pissdb.search(keywords);
        i = 0;
        for result in searchResults:
            printEntry(result[pissdb.DbResult.ENTRY]);

            i += 1;
            if(i == 3):
                keepGoing = yesNo("Show more(y/n)? ");
                if(keepGoing == False):
                    exit();

                i = 0;

    # Update entries
    if(argv[1] == "update"):
        # Initialize the database
        pissdb.init();
        # Ask for an id number
        idNum = int(input("ID number? ").replace('-', ''), 16);
        entry = pissdb.select(idNum);
        # If we couldn't find an entry with that id number, give up!
        if(entry == -1):
            print("Entry not found!");
            exit();

        printEntry(entry);

        location = input("New location? ");
        quantity = input("New quantity? ");

        print("Enter as many properties as you want, then press Ctrl+D to finish");

        properties = [];
        while True:
            try:
                property = input("Property? ");
                properties.append(property);
            except EOFError:
                break;

        # Insert the location and quantity in the front of the properties list
        # They are technically just special properties
        properties.insert(0, quantity);
        properties.insert(0, location);

        entry = pissdb.updateEntry(idNum, properties);
        printEntry(entry);
        commit = yesNo("Commit(y/n)?");
        if(commit == False):
            print("Not commiting!");
            exit();

        pissdb.publish();

    if(argv[1] == "delete"):
        # Initialize the database
        pissdb.init();
        # Ask for an id number
        idNum = int(input("ID number? ").replace('-', ''), 16);
        entry = pissdb.select(idNum);
        # If we couldn't find an entry with that id number, give up!
        if(entry == -1):
            print("Entry not found!");
            exit();

        printEntry(entry);
        delete = yesNo("Delete this entry? ");

        if(delete == False):
            print("Not deleting!");

        pissdb.updateEntry(idNum, ["__purgatory__"]);
        pissdb.publish();

main(sys.argv);
