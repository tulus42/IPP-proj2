from sys import *
import re
import io
import xml.etree.ElementTree as ET


src_file = ""
input_file = ""
stats_file = ""

global_frame = {}
temporary_frame = None
local_frame = []

data_stack = []

instruction_counter = 1
calling_stack = []

label_dict = {}

############################################################
# checking correctness of arguments
############################################################
def check_arguments2(argv, arguments_dic):
    global src_file
    global input_file
    global stats_file

    for i in argv[1::]:   

        if "--source" in i and not arguments_dic["source"]:
            if "--source=" == i[:9:]:
                arguments_dic["source"] = True
                src_file = i[9::]
                
                try:
                    with open(src_file, 'r') as file:
                        string = ""
                        for line in file:
                            string+= line
                        src_file = string

                except Exception:
                    print("Chyba pri otvarani suboru")
                    exit(11)

            else:
                print("Neplatny argument source")
                exit(10)
            
        elif "--input" in i and not arguments_dic["input"]:
            if "--input=" == i[:8:]:
                arguments_dic["input"] = True
                input_file = i[8::]
                
                try:
                    with open(input_file, 'r') as file:
                        string = ""
                        for line in file:
                            string+= line
                        input_file = string

                except Exception:
                    print("Chyba pri otvarani suboru")
                    exit(11)

            else:
                print("Neplatny argument input")
                exit(10)

        elif "--stats" in i and not arguments_dic["stats"]:
            if "--stats=" == i[:8:]:
                arguments_dic["stats"] = True
                stats_file = i[8::]
                
                try:
                    with open(stats_file, 'r') as file:
                        string = ""
                        for line in file:
                            string+= line
                        stats_file = string

                except Exception:
                    print("Chyba pri otvarani suboru")
                    exit(11)

            else:
                print("Neplatny argument stats")
                exit(10)

        elif i == "--insts" and not arguments_dic["insts"]:
            arguments_dic["insts"] = True

        elif i == "--vars" and not arguments_dic["vars"]:
            arguments_dic["vars"] = True

        else:
            print("neplatny argument")
            exit(10)

    return arguments_dic


def check_arguments(argv):
    arguments_dic = {"help": False, "source": False, "input": False, "stats": False, "insts": False, "vars": False}
    
    if len(argv) < 2:
        print("Argument missing")
        exit(10)
    
    elif len(argv) == 2:
        if argv[1] == "--help":
            print("some helpful instructions to use program")
            arguments_dic["help"] = True

        else:
            arguments_dic = check_arguments2(argv, arguments_dic) 
    
    else:
        arguments_dic = check_arguments2(argv, arguments_dic)

    
    if not arguments_dic["source"] and not arguments_dic["input"]:
        print("Argument is missing: --source or --input")
        exit(10)

    if (arguments_dic["insts"] or arguments_dic["vars"]) and not arguments_dic["stats"]:
        print("Argument is missing: --stats")
        exit(10)

    return arguments_dic


def read_from_stdin():    
    string = ""
    while True:
        line = stdin.readline()
        string += line
        if not line:
            break
    
    return string


def get_labels(program):
    global label_dict

    for i in program:
        instruction = program[i]
        if instruction[0].upper() == "LABEL":
            arguments = instruction[1]
            
            if len(arguments) != 1:
                exit(32)

            if arguments[1][0] == "label":
                label_name = arguments[1][1]

                if label_name not in label_dict:
                    label_dict.update({label_name: i})
                else:
                    exit(52)


############################################################
# instruction functions
############################################################
def check_var(argument):
    arg_type = argument[0]
    var = argument[1]

    if arg_type != "var":
        exit(32)

    if re.sub(r"[GTL]F@[\w_$%&*?!-]+", "", var) == "":
        result = var.split("@")
        return result
         
    else:
        print("Neplatna premenna", var)
        exit(32)


def check_frame(frame, variable):
    global global_frame
    global temporary_frame
    global local_frame

    if frame == "GF":
        if variable not in global_frame:
            exit(54)

    elif frame == "TF":
        if temporary_frame == None:
            exit(55)
        elif variable not in temporary_frame:
            exit(54)

    elif frame == "LF":
        if local_frame == []:
            exit(55)
        elif variable not in local_frame[-1]:
            exit(54)

    else:
        exit(32)

    return


def check_if_any_value(frame, variable):
    global global_frame
    global temporary_frame
    global local_frame

    if frame == "GF":
        if global_frame[variable] == None:
            exit(56)
    elif frame == "TF":
        if temporary_frame[variable] == None:
            exit(56)
    elif frame == "LF":
        if local_frame[-1][variable] == None:
            exit(56)

    return


def get_var_value_and_type(frame, variable):
    global global_frame
    global temporary_frame
    global local_frame

    if frame == "GF":
        return global_frame[variable]
    elif frame == "TF":
        return temporary_frame[variable]
    elif frame == "LF":
        return local_frame[-1][variable]
    else:
        exit(99)


def remove_escape_sequences(string):
    esc_seq = re.findall(r"\\\d{3}", string)
    words = re.split(r"\\\d{3}", string)

    new_string = words[0]

    for i in range(len(esc_seq)):
        esc_seq[i] = chr(int(esc_seq[i][1:]))

        new_string = new_string + esc_seq[i] + words[i+1]
    
    return new_string



# returns value of symbol or variable
def check_symb(argument):
    arg_type = argument[0]
    symb = argument[1]

    if symb == None:
        if arg_type == "string":
            symb = ""
        else:
            exit(32) # TODO or maybe 56


    if arg_type == "int":
        if re.sub(r"[\d]+", "", symb) != "":
            print("nespravny argument int")
            exit(32)

    elif arg_type == "string":
        tmp_symb = symb
        tmp_symb = re.sub(r"\\\d{3}", "", tmp_symb)
        
        if re.sub(r"[^#\\\s]+", "", tmp_symb) != "":
            print("nespravny argument string")
            exit(32)
        else:
            symb = remove_escape_sequences(symb)

    elif arg_type == "bool":
        if symb != "true" or symb != "false":
            print("nespravny argument bool")
            exit(32)

    elif arg_type == "nil":
        if symb != "nil":
            print("nespravny argument nil")
            exit(32)

    elif arg_type == "var":
        variable = check_var(argument)
        frame = variable[0]
        variable = variable[1]

        check_frame(frame, variable)
        check_if_any_value(frame, variable)
        
        return get_var_value_and_type(frame, variable)
        
    else:
        print("argument nevyhovuje ziadnej moznosti")
        exit(32)

    return [arg_type, symb]


def update_frame(frame, var, value):
    global global_frame
    global temporary_frame
    global local_frame
    
    if frame == "GF":
        global_frame[var] = value
    elif frame == "TF":
        temporary_frame[var] = value
    elif frame == "LF":
        local_frame[-1][var] = value
    else:
        exit(99)


def check_and_get_label(label_name):
    global label_dict

    if label_name not in label_dict:
        exit(52)

    return label_dict[label_name]


def get_line():
    global input_file

    try:
        new_line = input_file.readline()
    
        if new_line[-1] == "\n":
            return new_line[:-1]
        else:
            return new_line

    except Exception:
        return ""



# 6.4.1 ######################################################################
# DEFVAR ####################
def handle_defvar(arguments):
    global global_frame
    global temporary_frame
    global local_frame

    if len(arguments) != 1:
        print("nespravny pocet argumentov")
        exit(32)

    whole_var = check_var(arguments[1])
    frame = whole_var[0]
    variable = whole_var[1]

    if frame == "GF":
        if variable in global_frame:
            exit(52)
        global_frame.update({variable: None})

    elif frame == "TF":
        if temporary_frame == None:
            exit(55)
        elif variable in temporary_frame:
            exit(52)
        temporary_frame.update({variable: None})

    elif frame == "LF":
        if local_frame == []:
            exit(55)
        elif variable in local_frame[-1]:
            exit(52)
        local_frame[-1].update({variable: None})
    else:
        exit(32)

# MOVE #######################
def handle_move(arguments):
    global global_frame
    global temporary_frame
    global local_frame

    if len(arguments) != 2:
        print("nespravny pocet argumentov")
        exit(32)

    whole_var = check_var(arguments[1])
    frame1 = whole_var[0]
    variable1 = whole_var[1]
    
    symb2 = check_symb(arguments[2])     # get value from 2. argument
    type2 = symb2[0]
    value2 = symb2[1]
    print(symb2)
    
    check_frame(frame1, variable1)      # check if variable exist
    
    update_frame(frame1, variable1, symb2)
    

# CREATEFRAME #######################
def handle_createframe(arguments):
    global temporary_frame
    
    if len(arguments) != 0:
        exit(32)

    temporary_frame = {}


# PUSHFRAME #######################
def handle_pushframe(arguments):
    global temporary_frame
    global local_frame

    if len(arguments) != 0:
        exit(32)

    local_frame.append(temporary_frame)
    temporary_frame = None


# POPFRAME #######################
def handle_popframe(arguments):
    global temporary_frame
    global local_frame

    if len(arguments) != 0:
        exit(32)

    if local_frame != []:
        temporary_frame = local_frame[-1]
    else:
        exit(55)

# CALL ###########################
def handle_call(arguments):
    global instruction_counter
    global calling_stack

    if len(arguments) != 1:
        exit(32)

    if "label" not in arguments[1]:
        exit(32)

    label_name = arguments[1]["label"]

    label_number = check_and_get_label(label_name)

    calling_stack.append(instruction_counter)

    instruction_counter = label_number


# RETURN ###########################
def handle_return(arguments):
    global instruction_counter
    global calling_stack

    if len(arguments) != 0:
        exit(32)

    if len(calling_stack) > 0:
        instruction_counter = calling_stack[-1]
        del calling_stack[-1]
    else:
        exit(56)


# PUSHS ###########################
def handle_pushs(arguments):
    global data_stack

    if len(arguments) != 1:
        exit(32)

    symb = check_symb(arguments[1])

    data_stack.append(symb)

    
# POPS ###########################
def handle_pops(arguments):
    global data_stack

    if len(arguments) != 1:
        exit(32)

    if data_stack != []:
        whole_var = check_var(arguments[1])

        frame = whole_var[0]
        variable = whole_var[1]
        value = data_stack[-1]

        del data_stack[-1]
        
        check_frame(frame, variable)      # check if variable exist
        
        update_frame(frame, variable, value)

    else:
        exit(56) 


# 6.4.2 ######################################################################
# ADD ###########################
# SUB ###########################
# MUL ###########################
# IDIV ##########################

def handle_maths(arguments, operator):
    if len(arguments) != 3:
        exit(32)

    # arg1
    whole_var = check_var(arguments[1])

    frame = whole_var[0]
    variable_name = whole_var[1]

    check_frame(frame, variable_name)      # check if variable exist
    
    # arg2 
    symb2 = check_symb(arguments[2])
    type2 = symb2[0]
    value2 = int(symb2[1])
    # arg3
    symb3 = check_symb(arguments[3])
    type3 = symb3[0]
    value3 = int(symb3[1])

    if not (type2 == type3 == "int"):
        exit(53)

    if operator == "+":
        update_frame(frame, variable_name, ["int", value2 + value3])
    elif operator == "-":
        update_frame(frame, variable_name, ["int", value2 - value3])
    elif operator == "*":
        update_frame(frame, variable_name, ["int", value2 * value3])
    elif operator == "/":
        if value3 == 0:
            exit(57)
        update_frame(frame, variable_name, ["int", value2 // value3])
    else:
        exit(99)


# LT ############################
# GT ############################
# EQ ############################
def handle_compare(arguments, operator):
    if len(arguments) != 3:
        exit(32)

    # arg1
    whole_var = check_var(arguments[1])

    frame = whole_var[0]
    variable_name = whole_var[1]

    check_frame(frame, variable_name)      # check if variable exist
    
    # arg2 
    symb2 = check_symb(arguments[2])
    type2 = symb2[0]
    value2 = symb2[1]
    # arg3
    symb3 = check_symb(arguments[3])
    type3 = symb3[0]
    value3 = symb3[1]

    if type2 != type3:
        exit(53)

    result = "false"

    if type2 == "int":
        if operator == "<":
            if int(value2) < int(value3):
                result = "true"
        elif operator == ">":
            if int(value2) > int(value3):
                result = "true"
        elif operator == "=":
            if int(value2) == int(value3):
                result == "true"
        else:
            exit(99)

    elif type2 == "string":
        if operator == "<":
            if value2 < value3:
                result = "true"
        elif operator == ">":
            if value2 > value3:
                result = "true"
        elif operator == "=":
            if value2 == value3:
                result = "true"
        else:
            exit(99)

    elif type2 == "bool":
        if operator == "<":
            if value2 < value3:         # TODO - check if valid
                result = "true"
        elif operator == ">":
            if value2 > value3:         # TODO - check if valid
                result = "true"
        elif operator == "=":
            if value2 == value3:
                result = "true"
        else:
            exit(99)
        
    elif type2 == "nil":
        if operator == "=":
            if value2 == value3:
                result == "true"
        else:
            exit(53)

    else:
        exit(99)

    update_frame(frame, variable_name, ["bool", result])


# AND ###########################
# OR ############################
def handle_and_or(arguments, operator):
    if len(arguments) != 3:
        exit(32)

    # arg1
    whole_var = check_var(arguments[1])

    frame = whole_var[0]
    variable_name = whole_var[1]

    check_frame(frame, variable_name)      # check if variable exist
    
    # arg2 
    symb2 = check_symb(arguments[2])
    type2 = symb2[0]
    value2 = symb2[1]
    # arg3
    symb3 = check_symb(arguments[3])
    type3 = symb3[0]
    value3 = symb3[1]

    if not (type2 == type3 == "bool"):
        exit(53)

    tmp_val2 = True if value2 == "true" else False
    tmp_val3 = True if value3 == "true" else False

    if operator == "and":
        result = tmp_val2 and tmp_val3
    elif operator == "or":
        result = tmp_val2 or tmp_val3
    else:
        exit(99)

    result = "true" if result == True else "false"
    update_frame(frame, variable_name, ["bool", result])
    

# NOT ###########################
def handle_not(arguments):
    if len(arguments) != 2:
        exit(32)

    # arg1
    whole_var = check_var(arguments[1])

    frame = whole_var[0]
    variable_name = whole_var[1]

    check_frame(frame, variable_name)      # check if variable exist
    
    # arg2 
    symb2 = check_symb(arguments[2])
    type2 = symb2[0]
    value2 = symb2[1]

    if type2 != "bool":
        exit(53)

    if value2 == "true":
        update_frame(frame, variable_name, ["bool", "false"])
    else:
        update_frame(frame, variable_name, ["bool", "true"])


# INT2CHAR ###########################
def handle_int2char(arguments):
    pass
    # TODO


# INT2CHAR ###########################
def handle_str2int(arguments):
    pass
    # TODO
    

# 6.4.2 ######################################################################
# READ ###############################
def handle_read(arguments):
    if len(arguments) != 2:
        exit(32)

    # arg1
    whole_var = check_var(arguments[1])

    frame = whole_var[0]
    variable_name = whole_var[1]

    check_frame(frame, variable_name)      # check if variable exist

    readed_line = get_line()
    
    # arg2
    if arguments[2][0] != "type":
        print("nespravny typ")
        exit(32)

    new_type = arguments[2][1]
    print(arguments[2])
    print("typ:", new_type)

    if new_type == "int":
        try:
            readed_line = int(readed_line)
        except Exception:
            readed_line = 0

    elif new_type == "string":
        pass

    elif new_type == "bool":
        if readed_line.upper == "TRUE":
            readed_line = "true"
        else:
            readed_line = "false"

    else:
        print("chyba handle read")
        exit(32)

    update_frame(frame, variable_name, [new_type, readed_line])


# WRITE #############################
def handle_write(arguments):
    pass



###################################################################
# main handling instructions
###################################################################
def get_highest_order_number(program):
    top = 0

    for instruction in program:
        if int(instruction.attrib["order"]) > top:
            top = int(instruction.attrib["order"])

    return top

# temporary functions
def get_instruction_dictionary(instruction):
    dic = {}

    for argument in instruction:
        dic.update({int(argument.tag[-1]): [argument.attrib["type"], argument.text]})

    return dic


def get_program_dictionary(program):
    dic = {}

    for instruction in program:
        new_instruction = get_instruction_dictionary(instruction)

        dic.update({int(instruction.attrib["order"]): [instruction.attrib["opcode"].upper(), new_instruction]})

    return dic


def instruction_switch(instruction):
    global global_frame
    global temporary_frame
    global local_frame

    opcode = instruction[0]
    arguments = instruction[1]

    ###########
    # 6.4.1 ramce, volanie funkcii
    if opcode == "MOVE":
        handle_move(arguments)
        
    elif opcode == "CREATEFRAME":
        handle_createframe(arguments)
        
    elif opcode == "PUSHFRAME":
        handle_pushframe(arguments)
        
    elif opcode == "POPFRAME":
        handle_popframe(arguments)

    elif opcode == "DEFVAR":
        handle_defvar(arguments)

    elif opcode == "CALL":
        handle_call(arguments)
        
    elif opcode == "RETURN":
        handle_return(arguments)
        

    ###########
    # 6.4.2 datovy zasobnik
    elif opcode == "PUSHS":
        handle_pushs(arguments)
        
    elif opcode == "POPS":
        handle_pops(arguments)
       
        
    ###########
    # 6.4.3 aritmeticke, relacne, booleovske a konverzne instrukcie
    elif opcode == "ADD":
        handle_maths(arguments, "+")
        
    elif opcode == "SUB":
        handle_maths(arguments, "-")
       
    elif opcode == "MUL":
        handle_maths(arguments, "*")
        
    elif opcode == "IDIV":
        handle_maths(arguments, "/")
        
    elif opcode == "LT":
        handle_compare(arguments, "<")
        
    elif opcode == "GT":
        handle_compare(arguments, ">")
        
    elif opcode == "EQ":
        handle_compare(arguments, "=")

    elif opcode == "AND":
        handle_and_or(arguments, "and")

    elif opcode == "OR":
        handle_and_or(arguments, "or")

    elif opcode == "NOT":
        handle_not(arguments)

    elif opcode == "INT2CHAR":
        handle_int2char(arguments)

    elif opcode == "STR2INT":
        handle_str2int(arguments)

    ###########
    # 6.4.4 vytupne a vystupne instrukcie
    elif opcode == "READ":    
        handle_read(arguments)
        
    elif opcode == "WRITE":
        handle_write(arguments)

    ###########
    # 6.4.5 praca s retazcami
    elif opcode == "CONCAT":
        pass
    elif opcode == "STRLEN":
        pass
    elif opcode == "GETCHAR":
        pass

    ###########
    # 6.4.6 praca s typmi
    elif opcode == "TYPE":
        pass

    ###########
    # 6.4.7 riadenie toku programu
    elif opcode == "LABEL":
        pass
    elif opcode == "JUMP":
        pass
    elif opcode == "JUMPIFEQ":
        pass
    elif opcode == "JUMPIFNEQ":
        pass
    elif opcode == "EXIT":
        pass
        
    ###########
    # 6.4.8 ladiace instrukcie
    elif opcode == "DPRINT":
        pass
    elif opcode == "BREAK":
        pass

    else:
        exit(32)





def handle_instructions(program):
    global instruction_counter
    global label_dict
    
    top_order = get_highest_order_number(program)

    program = get_program_dictionary(program) 

    get_labels(program)

    print(program)
    print(program[2][1][2][1])
    
    while instruction_counter <= top_order:

        instruction_switch(program[instruction_counter])

        instruction_counter += 1








########################
######### MAIN #########


arguments_dic = check_arguments(argv)

if not arguments_dic["source"] or not arguments_dic["input"]:
    if not arguments_dic["source"]:
        src_file = read_from_stdin()

    if not arguments_dic["input"]:
        input_file = None

if arguments_dic["input"] == True:
    input_file = io.StringIO(input_file)

program = ET.fromstring(src_file)

handle_instructions(program)


"""for instruction in program:
    print("Instruction", instruction.attrib["order"])
    print(instruction.attrib["opcode"])
    print("Len(instruction):", len(instruction))
    # print(instruction[0].text)
    for argument in instruction:
        print("Arg", argument.tag[-1])
        print(argument.attrib)
        print(argument.text)"""

print("\nGF:",global_frame)
print("Labels:", label_dict)






