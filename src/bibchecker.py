import re
import bibtexparser
import json

class FormatString(object):
    stopwords = ["a", "an", "the",
                "and", "but", "or", "for", "nor",
                "in", "at", "of", "on", "to", "up", "from", "by"]
    def __init__(self):
        pass
    def single_whitespace(self, string):
        return ' '.join(string.split())
    def preserve(self, string, new_string):
        """
        Presever continued upper case (>=2) in string.
        """
        assert(len(string) == len(new_string))
        pattern = re.compile(r'[A-Z]{2,}')
        for match in pattern.finditer(string):
            st = match.start()
            end = match.end()
            new_string = new_string.replace(new_string[st:end], new_string[st:end].upper(), 1)
        return new_string

    def isstopword(self, word):
        return word.lower() in self.stopwords
    def head_cap(self, string):
        string = self.single_whitespace(string)
        new_string = string.lower().capitalize()
        return self.preserve(string, new_string)

    def case_cap(self, string):
        string = self.single_whitespace(string)
        split_list = string.split()
        format_str = split_list[0]
        format_str += ' ' + ' '.join([s.lower() if self.isstopword(s) else s.capitalize() for s in split_list[1:]])
        format_str = self.single_whitespace(format_str)
        return self.preserve(string, format_str)
    
    def lim_authors(self, string, max_aut=6):
        """
        Remove unncessary whitespace. If the number of authors > max_aut replace it with
        author1 and others
        """
        authors = self.single_whitespace(string)
        authors = string.split('and')
        if len(authors) > max_aut:
            authors = [authors[0], 'others']
        return ' and '.join(authors)

    def process(self, *arg):
        """
        process(self, string, key, [parameter for key])
        """
        string = arg[0]
        key = arg[1]
        if key == 'CaseCap':
            return self.case_cap(string)
        elif key == 'Headcap':
            return self.head_cap(string)
        elif key == 'author_limit':
            return self.lim_authors(string, max_aut=arg[2])
        else:
            raise NotImplementedError("%s not implemented!" % key)

class BibChecker(object):

    def __init__(self, config, mode=1):
        self.config = config
        self.mode = 1

    def issupported(self, entry):
        flag = entry['ENTRYTYPE'] in self.config.keys()
        if  not flag:
            if self.mode == 1:
                print("Warnning: type %s not supported." % entry['ENTRYTYPE'])
            elif self.mode == 2:
                raise NotImplementedError("Type %s not implemented." % entry['ENTRYTYPE'])
        return flag 

    def contain_fields(self, entry):
        """
        Check if entry contains require keys. Reture missing keys.
        """
        return set(self.config[entry['ENTRYTYPE']]['required_fields']) <= entry.keys()
    def write_entry(self, entry, file):
        """
        Write entry to file
        """
        def format_line(key, string, indent=2):
            output_str = ' ' * indent
            output_str += "{:<25}= ".format(key.capitalize())
            output_str += "{" + string + "}"
            return output_str
        f.write("@%s{ %s, \n" %(entry['ENTRYTYPE'], entry['ID']))
        keys = set(entry.keys()) - {'ID', 'ENTRYTYPE'}
        keys_order = ['title', 'author', 'journal', 'booktitle', 'year', 
                      'number', 'pages', 'volume']
        for key in keys_order:
            if key in entry:
                f.write(format_line(key, entry[key]))
                keys = keys - {key}
                if keys:
                    f.write(', \n')
        if not keys:
            f.write('\n }\n')
        else:
            while keys:
                key = keys.pop()
                f.write(format_line(key, entry[key]))
                if keys:
                    f.write(', \n')
                else:
                    f.write('\n }\n')

    def check(self, database, file):
        checked_entries = {'not_supported': [], 'missing_fields': [],
                           'processed': []}
        formatstr = FormatString()
        for entry in database.entries:
            if not self.issupported(entry):
                checked_entries['not_supported'].append(entry)
            else:
                if not self.contain_fields(entry):
                    checked_entries["missing_fields"].append(entry)
                else:
                    # processing entries
                    etype = entry['ENTRYTYPE']
                    for key in self.config[etype]:
                        if key == 'author_limit':
                            entry['author'] = formatstr.process(entry['author'], key, self.config[etype][key])
                        elif key in ['required_fields', 'exception']:
                            pass
                        else:
                            entry[key] = formatstr.process(entry[key], self.config[etype][key])
                    checked_entries['processed'].append(entry)
        for processed_type in checked_entries:
            file.write("%% %s \n" % processed_type)
            for entry in checked_entries[processed_type]:
                self.write_entry(entry, file)
        return checked_entries



if __name__ == '__main__':
    with open('demo/demo.bib',  encoding='utf-8') as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)
    file = "src/config.json"
    with open(file, 'r') as f:
        config = json.load(f)
    formatstr = FormatString()
    checker = BibChecker(config)
    with open('demo/out.bib', 'w') as f:
        checked_db = checker.check(bib_database, f)
        