#!/usr/bin/env python3
"""
This is a utility for converting a directory tree of text files into JSON
format suitable for use by Clarity. It will recurse through the directory
tree rooted at the specified directory, load the text files, and write
the JSON result to stdout.

Run as follows to generate the file 'input.json' using files in the 
directory tree rooted at "data". The files will be entered with the "Nursing"
report type, a source of "Columbia", and an index that starts at 3000000.

    python3 ./docs_to_json.py -d "data" -i 3000000 -t "Nursing" -s "Columbia" > input.json

Upload input.json to Clarity's Amazon AWS instance with this command:

    curl 'http://18.220.133.76:8983/solr/sample/update?commit=true' \
         --data-binary @input.json -H 'Content-type:application/json'

"""

import os
import sys
import json
import optparse
import datetime

VERSION_MAJOR = 0
VERSION_MINOR = 1

MODULE_NAME = 'docs_to_json.py'

###############################################################################
def to_json(doc_list, index_start, report_type, source):
    """
    Generate JSON output using the strings in 'doc_list' for the
    'report_text' field.
    """

    index = int(index_start)

    # current datetime will be used as the timestamp for all docs
    now = datetime.datetime.utcnow().isoformat()
    
    dict_list = []
    for doc in doc_list:
        
        this_dict = {}
        this_dict['report_type'] = report_type
        this_dict['id'] = str(index)
        this_dict['report_id'] = str(index)
        this_dict['source'] = source
        this_dict['report_date'] = now + 'Z'
        this_dict['subject'] = "-1"
        this_dict['report_text'] = doc

        dict_list.append(this_dict)
        index += 1

    return json.dumps(dict_list, indent=4)


###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(MODULE_NAME, VERSION_MAJOR, VERSION_MINOR)

###############################################################################
def show_help():
    print(get_version())
    print("""
    USAGE: python3 ./{0} -d <dirname>  [-hv]

    OPTIONS:

        -d, --dir    <quoted string>  Path to directory containing docs to ingest.
        -i, --index  <integer>        Starting value for Solr document id
        -t, --type   <quoted string>  JSON report type field
        -s, --source <quoted string>  JSON source field

    FLAGS:

        -h, --help           Print this information and exit.
        -v, --version        Print version information and exit.

    """.format(MODULE_NAME))

###############################################################################
if __name__ == '__main__':

    optparser = optparse.OptionParser(add_help_option=False)
    optparser.add_option('-d', '--dir', action='store', dest='directory')
    optparser.add_option('-i', '--index', action='store', dest='index')
    optparser.add_option('-t', '--type', action='store', dest='report_type')
    optparser.add_option('-s', '--source', action='store', dest='source')
    optparser.add_option('-v', '--version',  action='store_true', dest='get_version')
    optparser.add_option('-h', '--help',     action='store_true', dest='show_help', default=False)

    opts, other = optparser.parse_args(sys.argv)

    # show help if no command line arguments
    if opts.show_help or 1 == len(sys.argv):
        show_help()
        sys.exit(0)

    if opts.get_version:
        print(get_version())
        sys.exit(0)

    directory = opts.directory
    if directory is None:
        print('error: a directory must be specified on the command line')
        sys.exit(-1)

    if not os.path.isdir(directory):
        print('error: directory {0} does not exist'.format(directory))
        sys.exit(-1)
        
    index = opts.index
    if index is None:
        print('error: a starting index must be specified on the command line')
        sys.exit(-1)
    index = int(index)

    report_type = opts.report_type
    if report_type is None:
        print('error: a report type must be specified on the command line')
        sys.exit(-1)

    source = opts.source
    if source is None:
        print('error: a source must be specified on the command line')
        sys.exit(-1)
        
    docs = []

    # recurse through the file tree rooted at 'directory'
    for root, subdirs, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)

            # read text files; skip binaries and anything else causing an error
        
            try:
                infile = open(filepath, 'r')
            except (OSError, IOError) as e:
                continue
            except Excdeption as e:
                continue

            with infile:
                try:
                    doc = infile.read()
                except UnicodeDecodeError as e:
                    continue
                except (OSError, IOError) as e:
                    continue
                except Exception as e:
                    continue

            if 0 == len(doc):
                continue

            # successfully read document, so add text to list
            docs.append(doc)

    # convert to JSON for import into Clarity Solr
    json_string = to_json(docs, index, report_type, source)
    print(json_string)
    
    
    

    
