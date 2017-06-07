import sys
import glob
import re
import textwrap

modules = [m for m in sys.modules.keys() if m.startswith('pyramid_oereb')]
files = glob.glob('pyramid_oereb/*.py*')
files += glob.glob('pyramid_oereb/*/*.py*')
files += glob.glob('pyramid_oereb/*/*/*.py*')
for file_ in [f for f in files]:
    with open(file_) as stream:
        data = stream.read()
        index = data.find('"""')
        if index > -1:
            new_lines = []
            line_number = -1
            is_attribute_line = False
            lines = data.split('\n')

            for line in lines:
                line_number += 1

                if re.search(':return(.)*:', line):
                    base_indent = len(line) - len(line.lstrip())
                    is_attribute_line = True
                    type_is_found = False
                    description_lines = []
                    attr = '' if re.search(':rtype(.)*:', lines[line_number - 1])\
                        else '        Returns:\n'
                    if len(attr) != 0 and len(lines[line_number - 1]) != 0:
                        attr = '\n' + attr
                    i = line_number
                    var, type = 'undef', 'undef'
                    while (not type_is_found and i < line_number + 200):
                        i += 1
                        if i == line_number + 5:
                            print('%s: %s' % (file_, i))
                        nextLine = lines[i]
                        if re.search(':rtype(.)*:', lines[i]):
                            type_is_found = True
                            nextLine = nextLine.replace(' ', '')
                            nextLine = nextLine.replace(':rtype', '')
                            var, type = nextLine.split(':')
                        else:
                            description_lines.append(nextLine)

                    line = line.split(':')[2] + ''.join(description_lines)
                    line = '%s:%s' % (type, line)
                    line = line.replace('    ', '')
                    line = textwrap.fill(line).strip()
                    line_width = 100 - base_indent
                    spaces = ''
                    for space in range(base_indent):
                        spaces = spaces + ' '
                    line = textwrap.fill(line, width=line_width, initial_indent=spaces,
                                         subsequent_indent='    ' + spaces)
                    new_lines.append('%s    %s' % (attr, line))

                elif re.search(':rtype(.)*:', line):
                    is_attribute_line = False

                elif not is_attribute_line:
                        new_lines.append(line)

            with open(file_, "wt") as dest:
                i = 0
                for line in new_lines:
                    i += 1
                    if re.match('^( )*$', line):
                        line = ''
                    if (i < len(new_lines)):
                        dest.write(line + '\n')
                    else:
                        dest.write(line)
