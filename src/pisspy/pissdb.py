#!/usr/bin/env python3

#==============================================================================#
#$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$#
# pissdb
#
# provide functions to interact with the PISS database csv
#
#
#
# FUNCTIONS:
#
# init - make sure that the database is initialized and ready to go
#
# addEntry - add an entry to the database
#
# publish - publish all changes to the database

import os, csv;

# Default DB path and filename. May be configurable in future update
DBPATH = os.path.expanduser('~') + "/.pisspy/";
DBFILE = DBPATH + "pissdb.csv";

# CSV properties, do not modify or else this may break your existing database!
CSVDELEM = '\t';
CSVNEWLINE = '\n';
CSVENCODE = "utf-8";
CSVESCAPE = '\\';
CSVDIALECT = "piss";

# Concept and purgatory official definitions
CONCEPT = "__concept__";
PURGATORY = "__purgatory__";

csv.register_dialect(
    CSVDIALECT,
    delimiter = CSVDELEM,
    lineterminator = CSVNEWLINE,
    quoting = csv.QUOTE_ALL,
    escapechar = CSVESCAPE
);

# Each entry in the DB list is also a list, for a reason or another
# The format goes as follows for normal items
# [idNum, location, quantity, properties...]
# This format goes for allocated idNums that are printed but not used
# [idNum, "__concept__"]
# This format goes for allocated idNums that have been sent to purgatory
# [idNum, "__purgatory__"]
dbList = [];

class DbEntry:
    IDNUM = 0;
    # Both location and status are set to 1 because items aren't allowed to
    # be stored in __purgatory__ or __concept__
    LOCATION = 1;
    STATUS = 1;
    QUANTITY = 2;
    PROPERTIES = 3;

class DbResult:
    RELEVANCE = 0;
    DBINDEX = 1
    ENTRY = 2;

def init():
    # Create DB directory if it doesn't exist
    if(os.path.exists(DBPATH) != True):
        os.mkdir(DBPATH);

    # If the database file already exists, open it and populate the dbList
    if(os.path.exists(DBFILE)):
        # Open a file an attach a CSV reader to the file
        dbFile = open(DBFILE, 'r', encoding=CSVENCODE);
        dbCsvReader = csv.reader(dbFile, dialect=CSVDIALECT);

        # Go through all the CSV entries in the file and add them to the DB
        for entry in dbCsvReader:
            # Convert the id number in the entry to an int
            entry[DbEntry.IDNUM] = int(entry[DbEntry.IDNUM]);
            # Every entry into the DB list is also a list.
            # See the entry format above
            dbList.append(entry);

        # Close the DB file!
        dbFile.close();

def addEntry(entry):
    # Literally just append the entry to the list
    dbList.append(entry);

def updateEntry(idNum, properties):
    for entry in dbList:
        if(entry[DbEntry.IDNUM] == idNum):
            dbList.remove(entry);
            newEntry = properties;
            newEntry.insert(0, idNum);
            dbList.append(newEntry);
            return newEntry;

    return -1;

def search(keywords):
    # Initialize the variable we'll store results into
    # Format is as follows
    # (matching keywords, entry)
    results = [];
    dbIndex = 0;

    # Go through each entry in the db list
    for entry in dbList:
        matches = 0;

        # Prepare for ugly and inefficient code: I do not care!
        for property in entry:
            for keyword in keywords:
                if(property == keyword):
                    matches += 1;

        # If there was a match at all, add to the list of results
        if matches > 0:
            results.append((matches, dbIndex, entry));
        # Increment the dbIndex by 1
        dbIndex += 1;

    # Sort the results by relevance(decending matches)
    results.sort(reverse = True);

    return results;

def select(idNum):
    for entry in dbList:
        if(entry[DbEntry.IDNUM] == idNum):
            return entry;

    return -1;

def genIdNum():
    # First, search the database for a id number in "purgatory"
    searchResults = search([PURGATORY]);
    idNum = 0;

    # If there's an id number in purgatory, return that
    if(len(searchResults) > 0):
        searchResults.sort(reverse = True);
        # Here's the ugly part about using lists, numeric indexing!
        idNum = int(searchResults[0][DbResult.ENTRY][DbEntry.IDNUM]);

        # Change the status to concept in the db list...
        dbList[searchResults[0][DbResult.DBINDEX]][DbEntry.STATUS] = CONCEPT;

        return idNum;

    # Otherwise, sort the database list in decending order
    dbList.sort(reverse=True);
    # And set the id number to the highest id number + 1, if there are any
    # entries in the db list
    if(len(dbList) > 0):
        idNum = int(dbList[0][DbEntry.IDNUM]) + 1;
    # Otherwise the id number will default to 0

    # Lastly, add the id number to the database as a "concept"
    # Anything added to the DB has to be a list
    addEntry([idNum, CONCEPT]);

    return idNum;


def publish():
    # Open the database file for writing and attach a writer to it
    dbFile = open(DBFILE, 'w', encoding=CSVENCODE);
    dbCsvWriter = csv.writer(dbFile, dialect=CSVDIALECT);

    # Write the entire db list to the file
    dbCsvWriter.writerows(dbList);
    # Close the file!
    dbFile.close();
