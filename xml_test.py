import pandas as pd
import sys

def read_file(filename):
    try:
        df = pd.read_csv(filename, sep='\t')
        if list(df.columns) != ['test_id', 'line', 'q', 'a_state', 'a_class', 'a', 'flag']:
            raise ValueError("Wrong file column names")
    except: sys.exit(sys.exc_info())
    return (df)

def read_config(filename):
    print("Reading config")
    try:
        config = pd.read_csv(filename, sep='\t')
        if list(config.columns) != ['on', 'test_id', 'format', 'file_name', 'flag', 'comment']:
            raise ValueError("Wrong config column names")
        if 1 not in config.on.values:
            raise ValueError("No test requested")
        config = config.loc[config['on'] == 1].drop_duplicates()
        for testname in set(config['test_id']):
            if len(set(config.loc[config['test_id'] == testname]['file_name'])) > 1:
                raise ValueError("Test \'"+testname+"\' in multiple files")
    except: sys.exit(sys.exc_info())
    return (config)

def verify_config(config):
    print("Verifying config")
    for filename in set(config['file_name']): read_file(filename)
    try:
        for testid in set(config['test_id']):
            filename = config.loc[config['test_id'] == testid]['file_name']
            df = read_file(filename.values[0])
            lines = set(df.loc[df['test_id'] == testid]['line'])
            if len(lines) == 0:
                raise ValueError("No \'"+testid+"\' in \'"+filename+"\'")
            elif not isinstance(list(lines)[0], int):
                raise TypeError("Column \'line\' might have null value");
            elif len(lines) < max(lines) or min(lines) != 0:
                raise ValueError("Wrong lines range for \'"+testid+"\' in \'"+filename+"\'")
            elif lines != set(range(min(lines), max(lines)+1)):
                raise ValueError("Wrong lines count for \'"+testid+"\' in \'"+filename+"\'")
    except: sys.exit(sys.exc_info())
    return (config)

def write_test(queries, output):
    tag = ["\t\t<q>", "</q>\n", "\t\t<a>", "</a>\n", "\t\t<a state=\'/", "\t\t<a class=\'/"]
    for i in range(max(set(queries['line'])) + 1):
        q = queries.loc[queries['line'] == i]['q'].values[0]
        s = queries.loc[queries['line'] == i]['a_state'].values[0]
        line = tag[0] + q + tag[1] + tag[4] + s + "\'/>\n"
        output.write(line)

def generate_xml(config, output):
    print("Writing output")
    output.write("<test>\n")
    for filename in set(config['file_name']):
        df = read_file(filename)
        for testid in set(config['test_id']):
            queries = df.loc[df['test_id'] == testid]
            output.write("\t<test-case id=\'" + testid + "\'>\n")
            write_test(queries, output)
            output.write("\t</test-case>\n")
    output.write("</test>\n")

config = verify_config(read_config('config.csv'))
output = open("output.xml", "w")
generate_xml(config, output)
output.close()
