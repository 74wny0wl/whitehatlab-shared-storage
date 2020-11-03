#! /usr/bin/python3

import re

def get_input():
    content = ""
    with open('codeit.au3', 'r') as f:
        content = f.read()
    return content

def set_output(content):
    with open('codeit_deobfuscated.au3', 'w') as f:
        f.write(content)

def remove_numbers_definitions(content):
    definition_pattern = re.compile(r'''((Global )?(\$[A-Za-z]+) = (Number\(" (\d+) "\))(,\s*)?)''')

    for definition_match in re.findall(definition_pattern, content):
        whole_match = re.escape(definition_match[0])
        global_match = re.escape(definition_match[1])
        variable_match = re.escape(definition_match[2])
        number_obj = re.escape(definition_match[3])
        integer_value = definition_match[4]
        separator = re.escape(definition_match[5])
        
        content = re.sub(whole_match, "" , content)
        content = re.sub(variable_match, integer_value, content)
    return content

def remove_empty_lines(content):
    content = re.sub(r'''\n{2,}''', r'''\n\n''', content)
    return content

def concat_multiline_concats(content):
    definition_with_pattern = re.compile(r'''((Local\s*|Global\s*)?(\$[A-Za-z]+)(\s*=\s*")(.+)("\s*\n+\s*)(\$[A-Za-z]+)(\s*&=))''')

    for definition_match in re.findall(definition_with_pattern, content):

        variable_name_definion = re.escape(definition_match[2])
        variable_name_usage = re.escape(definition_match[6])
        if variable_name_definion != variable_name_usage:
            continue

        whole_definition_match = re.escape(definition_match[0])
        variable_param = definition_match[1]
        variable_initial_value = definition_match[4]
        new_variable_definition = variable_param + ' ' + definition_match[2] + ' = "' + variable_initial_value

        variable_usage_pattern = re.compile('(('+variable_name_definion+')(\s*&=\s*")([\$\w\d]+)("\n\t*))')
        for usage_match in re.findall(variable_usage_pattern, content):
            whole_usage_match = re.escape(usage_match[0])
            variable_concated_value = usage_match[3]
            new_variable_definition += variable_concated_value
            content = re.sub(whole_usage_match, '', content)
        new_variable_definition += '"'

        definition_pattern = re.compile(r'''((Local\s*|Global\s*)?('''+variable_name_definion+''')(\s*=\s*")(.+)("))''')
        content = re.sub(definition_pattern, new_variable_definition, content)

    return content

def unroll_arrays(content):
    string_split_pattern = re.compile(r'''((Local\s*|Global\s*)?(\$[A-Za-z]+)(\s*=\s*StringSplit\()(\$[A-Za-z]+)(,\s*")([\$\w\d]+)(",\s*)(\d)(\s*\)))''')
    for string_split_match in re.findall(string_split_pattern, content):
        separator = string_split_match[6]
        array_visibility = string_split_match[1]
        array_name = string_split_match[2]
        variable_name_to_split = string_split_match[4]
        variable_to_split_match = re.findall(r'''((Local\s*|Global\s*)?('''+re.escape(variable_name_to_split)+''')(\s*=\s*")(.+)("))''', content)[0]
        value_to_split = variable_to_split_match[4]
        content = re.sub(re.compile(re.escape(variable_to_split_match[0])), '', content)

        new_variable_definition = array_visibility + array_name + ';'
        i = 1
        for element in re.split(re.escape(separator), value_to_split):
            new_variable_definition += '\n' + array_name + '[' + str(i) + '] = "' + element + '"'
            i += 1
        
        old_variable_definition_pattern = re.compile(re.escape(string_split_match[0]))
        content = re.sub(old_variable_definition_pattern, new_variable_definition, content)

    return content

def remove_array(content, array_name):
    for i in range(1, 256):
        array_element_name = "\$" + array_name + "\[" + str(i) + "\]"
        array_element_definiton = '((' + array_element_name +')' + r'''\s*=\s*("[\w\d]*")''' + ')'
        array_element_definiton_pattern = re.compile(array_element_definiton)
        for array_element_definiton_match in re.findall(array_element_definiton_pattern, content):
            array_element_definiton_instance = array_element_definiton_match[0]
            array_element_usage = array_element_definiton_match[1]
            array_element_value = array_element_definiton_match[2]
            content = re.sub(re.escape(array_element_definiton_instance), '', content)
            content = re.sub(re.escape(array_element_usage), array_element_value, content)
    
    return content

def remove_character_encoding(content, encoder_name):
    encoder_usage_pattern = re.compile('(('+encoder_name+')' + r'''\("([\w\d]*)"\))''')
    for encoder_usage_match in re.findall(encoder_usage_pattern, content):
        encoder_usage = encoder_usage_match[0]
        encoded_string = encoder_usage_match[2]
        decoded_string = bytes.fromhex(encoded_string).decode("utf-8")
        content = re.sub(re.escape(encoder_usage), '"'+decoded_string+'"', content)
    return content

def remove_function(content, function_name):
    function_definition_pattern = re.compile(r'Func\s'+re.escape(function_name)+r'''[\w\d\&\$=\(\)\-\<\>\+.,_;\n\t\s]+?EndFunc''')
    for function_definition_match in re.findall(function_definition_pattern, content):
        content = re.sub(re.escape(function_definition_match), '', content)
    return content

def main():
    content = get_input()

    content = remove_numbers_definitions(content)
    content = concat_multiline_concats(content)
    content = remove_empty_lines(content)
    content = unroll_arrays(content)
    content = remove_array(content, 'os')
    content = remove_empty_lines(content)
    content = remove_character_encoding(content, 'arehdidxrgk')
    content = remove_function(content, 'areihnvapwn')
    content = remove_function(content, 'arehdidxrgk')
    content = remove_empty_lines(content)
    
    set_output(content)
    

if __name__ == "__main__":
    main()