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

instruction_stati = 0
vars_stati = 0
instruction_stati_first = False


# counts actual number of initialized variables
# argvs: actual_max - maximal number of valid variables yet
# return: int - new maxilam number of valid variables
def check_max_vars(actual_max):
    global global_frame
    global local_frame
    global temporary_frame

    local_cnt = 0

    if global_frame != None:                    # through global frame
        for i in global_frame:
            if check_if_any_value("GF", i):
                local_cnt += 1

    if temporary_frame != None:                 # through temporary frame
        for i in temporary_frame:
            if check_if_any_value("TF", i):
                local_cnt += 1

    if local_frame != []:                       # through all local frames
        for j in local_frame:
            for i in j:
                if i != None:
                    local_cnt += 1

    if local_cnt > actual_max:                  # find max
        return local_cnt
    else:
        return actual_max


############################################################
# checking correctness of arguments
############################################################
# checks other arguments except --help
# argvs: argv - list of arguments
# argvs: arguments_dic - dictionary of checked arguments
# return: dictionary - {name of argument: bool(used/unused)}
def check_arguments2(argv, arguments_dic):
    global src_file
    global input_file
    global stats_file
    global instruction_stati_first

    for i in argv[1::]:                                         # goes through all arguments

        if "--source" in i and not arguments_dic["source"]:     # --source
            if "--source=" == i[:9:]:
                arguments_dic["source"] = True                  # sets --source as used
                src_file = i[9::]
                
                try:                                            # checks if <file> is valid file and saves it into scr_file
                    with open(src_file, 'r') as file:
                        string = ""
                        for line in file:
                            string+= line
                        src_file = string

                except Exception:
                    exit(11)

            else:
                exit(10)
            
        elif "--input" in i and not arguments_dic["input"]:     # --input
            if "--input=" == i[:8:]:
                arguments_dic["input"] = True                   # sets --input as used
                input_file = i[8::]
                
                try:                                            # checks if <file> is valid file and saves it into input_file
                    with open(input_file, 'r') as file:
                        string = ""
                        for line in file:
                            string+= line
                        input_file = string

                except Exception:
                    exit(11)

            else:
                exit(10)

        elif "--stats" in i and not arguments_dic["stats"]:     # --stats
            if "--stats=" == i[:8:]:
                arguments_dic["stats"] = True                   # sets --stats as used
                stats_file = i[8::]                             # saves <file> into stats_file

            else:
                exit(10)

        elif i == "--insts" and not arguments_dic["insts"]:     # --insts
            arguments_dic["insts"] = True                       # sets --insts as used
            if arguments_dic["vars"] == True:                   # checks if was first --insts or --vars
                instruction_stati_first = False
            else:
                instruction_stati_first = True

        elif i == "--vars" and not arguments_dic["vars"]:       # --vars
            arguments_dic["vars"] = True                        # sets --vars as used

        else:
            exit(10)

    return arguments_dic


# checks which arguments were used during executing of script
# argvs: argv - list of arguments
# return: dictionary - {name of argument: bool(used/unused)}
def check_arguments(argv):
    arguments_dic = {"help": False, "source": False, "input": False, "stats": False, "insts": False, "vars": False}
    
    if len(argv) < 2:
        exit(10)
    
    elif len(argv) == 2:                                            # only one argument
        if argv[1] == "--help":                                     # help can be only on its own
            print("INTERPRET.PY")
            print("Help:")
            print("   possible arguments:")
            print("      --help................shows information about using of script")
            print("      --source=<file>.......sets source file to <file>")
            print("      --input=<file>........sets input file to <file>")
            print("      --stats=<file>........sets file for statistics to <file>")
            print("      --insts...............writes statistics about instructions into stats file")
            print("      --vars................writes statistics about variables into stats file")
            print("\n   --help - only on its own")
            print("   at least one of --source/--input must be used")
            print("   if --insts/--vars is used, --stats must be used too")

            arguments_dic["help"] = True
            exit(0)

        else:
            arguments_dic = check_arguments2(argv, arguments_dic) 
    
    else:
        arguments_dic = check_arguments2(argv, arguments_dic)

    
    if not arguments_dic["source"] and not arguments_dic["input"]:                          # checking forbidden combinations
        exit(10)

    if (arguments_dic["insts"] or arguments_dic["vars"]) and not arguments_dic["stats"]:    # checking forbidden combinations
        exit(10)

    return arguments_dic


# reads all lines at stdin
# return: string - whole readed stdin
def read_from_stdin():    
    string = ""
    while True:
        line = stdin.readline()
        string += line
        if not line:
            break
    
    return string


# goes through whole source code and saves all labels into global label_dict
# argvs: program - dictionary of source code
def get_labels(program):
    global label_dict

    for i in program:                               # through source code
        instruction = program[i]
        if instruction[0].upper() == "LABEL":       # through instruction
            arguments = instruction[1]
            
            if len(arguments) != 1:                 # through operands
                exit(32)

            if arguments[1][0] == "label":
                label_name = arguments[1][1]

                if label_name not in label_dict:    # check if label name exists yet
                    label_dict.update({label_name: i})
                else:
                    exit(52)


############################################################
# instruction functions
############################################################
# checks if value in operand can really be variable
# argvs: argument - single operand of instruction with type "var"
# return: list - [frame, name of variable]
def check_var(argument):
    arg_type = argument[0]
    var = argument[1]

    if arg_type != "var":
        exit(32)

    if re.sub(r"[GTL]F@[\w_$%&*?!-]+", "", var) == "":
        result = var.split("@")
        return result
         
    else:
        exit(32)


# checks if variable exists in frame
# argvs: frame - only GF/LF/TF
# argvs: variable - name of searching variable
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


# checks if variable in frame has any value yet
# argvs: frame - only GF/LF/TF
# argvs: variable - name of searching variable
# return: bool - if variable has value returns True else False
def check_if_any_value(frame, variable):
    global global_frame
    global temporary_frame
    global local_frame

    if frame == "GF":
        if global_frame[variable] == None:
            return False
    elif frame == "TF":
        if temporary_frame[variable] == None:
            return False
    elif frame == "LF":
        if local_frame[-1][variable] == None:
            return False

    return True


# gets variable from frames - does not check validity
# argvs: frame - only GF/LF/TF
# argvs: variable - name of searching variable
# return: list - [type, value]
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


# replace all valid escape sequences with their symvols
# argvs: string - string from source code or from variable
# return: string - deleted escape sequences and replaced by their symbols
def remove_escape_sequences(string):
    esc_seq = re.findall(r"\\\d{3}", string)
    words = re.split(r"\\\d{3}", string)

    new_string = words[0]

    for i in range(len(esc_seq)):
        esc_seq[i] = chr(int(esc_seq[i][1:]))

        new_string = new_string + esc_seq[i] + words[i+1]
    
    return new_string



# gets type of symbol (variable or constant)
# argvs: argument - operand of actual instruction
# return: list - [type, value of variable or constant from argument]
def check_symb(argument):
    global instruction_counter
    arg_type = argument[0]
    symb = argument[1]

    # because of implicit value of READ
    if symb == None:
        if arg_type == "string":
            symb = ""
        else:
            exit(56) 

    # checking if value in symbol corresponds to its type
    if arg_type == "int":
        if re.sub(r"-?[\d]+", "", symb) != "":
            exit(32)

    elif arg_type == "string":
        tmp_symb = symb
        tmp_symb = re.sub(r"\\\d{3}", "", tmp_symb)
        
        if re.sub(r"[^#\\\s]+", "", tmp_symb) != "":
            exit(32)
        else:
            symb = remove_escape_sequences(symb)

    elif arg_type == "bool":
        if symb != "true" and symb != "false":
            exit(32)

    elif arg_type == "nil":
        if symb != "nil":
            exit(32)

    elif arg_type == "var":                             # if variable - its own checking
        variable = check_var(argument)                  # checking var - if it is variable
        frame = variable[0]
        variable = variable[1]

        check_frame(frame, variable)                    # checking frame - if variable exists
        if not check_if_any_value(frame, variable): 
            exit(56)
        
        return get_var_value_and_type(frame, variable)
        
    else:
        exit(32)

    return [arg_type, symb]


# gets type of symbol (variable or constant)
# argvs: argument - operand of actual instruction
# return: string - type of variable or constant from argument
def check_symb_and_ret_type(argument):
    global instruction_counter
    arg_type = argument[0]
    symb = argument[1]

    # because of implicit value of READ
    if symb == None:
        if arg_type == "string":
            symb = ""
        else:
            exit(56)

    # checking if value in symbol corresponds to its type
    if arg_type == "int":                                                           
        if re.sub(r"-?[\d]+", "", symb) != "":
            exit(32)

    elif arg_type == "string":
        tmp_symb = symb
        tmp_symb = re.sub(r"\\\d{3}", "", tmp_symb)
        
        if re.sub(r"[^#\\\s]+", "", tmp_symb) != "":
            exit(32)
        else:
            symb = remove_escape_sequences(symb)

    elif arg_type == "bool":
        if symb != "true" and symb != "false":
            exit(32)

    elif arg_type == "nil":
        if symb != "nil":
            exit(32)

    elif arg_type == "var":                 # if variable - its own checking
        variable = check_var(argument)      # checking var
        frame = variable[0]
        variable = variable[1]

        check_frame(frame, variable)        # checking frame
        if not check_if_any_value(frame, variable):
            return ""
        
        return get_var_value_and_type(frame, variable)[0]
        
    else:
        exit(32)

    return arg_type


# update value in chosen frame
# argvs: frame - only GF/LF/TF
# argvs: var - name of variable that will be modified
# argvs: value - value that will be given to the variable
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


# checks if label exists and returns its position in source code
# argvs: label_name - name of searched label
# return: int - order number of label
def check_and_get_label(label_name):
    global label_dict

    if label_name not in label_dict:
        exit(52)

    return label_dict[label_name]


# gets line from input file - depends on arguments - may be file of stdin
# return: string - line readed from input file or stdin
def get_line():
    global input_file

    try:
        new_line = input_file.readline()        # read 1 line from input
    
        if new_line[-1] == "\n":                # if readed line ends with \n, delete it
            return new_line[:-1]
        else:
            return new_line

    except Exception:
        return ""



# 6.4.1 ######################################################################
# DEFVAR ####################
# create new variable in frame with no value
# argvs: argumetns - dictionary of operands of instruction
def handle_defvar(arguments):
    global global_frame
    global temporary_frame
    global local_frame

    if len(arguments) != 1:
        exit(32)

    whole_var = check_var(arguments[1])             # get char frame and name from source code
    frame = whole_var[0]
    variable = whole_var[1]

    if frame == "GF":                               # depends on chosen frame
        if variable in global_frame:                # if variable already exists -> redefinition
            exit(52)
        global_frame.update({variable: None})       # create new variable

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
# puts value into variable 
# argvs: argumetns - dictionary of operands of instruction
def handle_move(arguments):
    global global_frame
    global temporary_frame
    global local_frame

    if len(arguments) != 2:
        exit(32)

    try:
        whole_var = check_var(arguments[1])     # get char frame and name from source code
        frame1 = whole_var[0]
        variable1 = whole_var[1]
        
        symb2 = check_symb(arguments[2])        # get value from 2. argument
        
        check_frame(frame1, variable1)          # check if variable exist
        
        update_frame(frame1, variable1, symb2)
    except Exception:
        exit(32)


# CREATEFRAME #######################
# create new temporary frame - if there is anything, delete it
# argvs: argumetns - dictionary of operands of instruction
def handle_createframe(arguments):
    global temporary_frame
    
    if len(arguments) != 0:
        exit(32)

    temporary_frame = {}                    # create new temp. frame with no value


# PUSHFRAME #######################
# takes temporary frame and puts it into top of local frame
# argvs: argumetns - dictionary of operands of instruction
def handle_pushframe(arguments):
    global temporary_frame
    global local_frame

    if len(arguments) != 0:
        exit(32)

    if temporary_frame == None:             # only if temp. frame is not empty
        exit(55)

    local_frame.append(temporary_frame)     # put temporary frame into top of local frame
    temporary_frame = None                  # clear temporary frame


# POPFRAME #######################
# takes top frame from local frame and puts it into temporary frame
# argvs: argumetns - dictionary of operands of instruction
def handle_popframe(arguments):
    global temporary_frame
    global local_frame

    if len(arguments) != 0:
        exit(32)

    if local_frame != []:                   # only if local frame is not empty
        temporary_frame = local_frame[-1]   # put top frame from local frame into temp. frame
        del local_frame[-1]                 # del top frame from local frame
    else:
        exit(55)


# CALL ###########################
# call label (function) - puts global instruction counter into global calling stack and puts label number into instruction counter
# argvs: argumetns - dictionary of operands of instruction
def handle_call(arguments):
    global instruction_counter
    global calling_stack

    if len(arguments) != 1:
        exit(32)

    if "label" not in arguments[1]:         # called instruction must be label
        exit(32)

    label_name = arguments[1][1]

    label_number = check_and_get_label(label_name)      # check if label exists and get its order number

    calling_stack.append(instruction_counter)           # put actual instruction into stack

    instruction_counter = label_number - 1                 # new actual instruction is now called instruction 


# RETURN ###########################
# returns from called label - global instruction counter gets top value from global calling stack
# argvs: argumetns - dictionary of operands of instruction
def handle_return(arguments):
    global instruction_counter
    global calling_stack

    if len(arguments) != 0:
        exit(32)

    if len(calling_stack) > 0:                          # only if calling stack is not empty
        instruction_counter = calling_stack[-1]         # take value from top of calling stack
        del calling_stack[-1]                           # remove value from top of calling stack
    else:
        exit(56)


# 6.4.2 ######################################################################
# PUSHS ###########################
# takes value from variabla and puts it into global stack
# argvs: argumetns - dictionary of operands of instruction
def handle_pushs(arguments):
    global data_stack

    if len(arguments) != 1:
        exit(32)

    symb = check_symb(arguments[1])     # get type and value of var from frame or if constant from source code

    data_stack.append(symb)             # put value at the top of stack

    
# POPS ###########################
# gets value from global stack and puts it into variable
# argvs: argumetns - dictionary of operands of instruction
def handle_pops(arguments):
    global data_stack

    if len(arguments) != 1:
        exit(32)

    if data_stack != []:                        # only if stack is not empty
        whole_var = check_var(arguments[1])     # get char frame and name from source code

        frame = whole_var[0]
        variable = whole_var[1]
        value = data_stack[-1]

        del data_stack[-1]                      # removes value from top of stack
        
        check_frame(frame, variable)            # check if variable exist
        
        update_frame(frame, variable, value)    # update variable in frame

    else:
        exit(56) 


# 6.4.3 ######################################################################
# ADD ###########################
# SUB ###########################
# MUL ###########################
# IDIV ##########################
# arithmetic operations - calculates result of two numbers and puts it into variable
# argvs: argumetns - dictionary of operands of instruction
# argvs: operator - only "and" or "or" - decides which operation will be done
def handle_maths(arguments, operator):
    if len(arguments) != 3:
        exit(32)

    # arg1
    whole_var = check_var(arguments[1])     # get char frame and name from source code

    frame = whole_var[0]
    variable_name = whole_var[1]

    check_frame(frame, variable_name)       # check if variable exist
    
    # arg2 
    symb2 = check_symb(arguments[2])        # get type and value of var from frame or if constant from source code
    type2 = symb2[0]
    if type2 != "int":                      # must be integer
        exit(53)
    try:
        value2 = int(symb2[1])
    except Exception:
        exit(53)

    # arg3
    symb3 = check_symb(arguments[3])        # get type and value
    type3 = symb3[0]
    if type3 != "int":                      # must be integer
        exit(53)
    try:
        value3 = int(symb3[1])
    except Exception:
        exit(53)

    if operator == "+":                                                         # calculating and updating variable in frame
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
# compares two values and puts result into variable
# argvs: argumetns - dictionary of operands of instruction
# argvs: operator - only "and" or "or" - decides which operation will be done
def handle_compare(arguments, operator):
    if len(arguments) != 3:
        exit(32)

    # arg1
    whole_var = check_var(arguments[1])     # get char frame and name from source code

    frame = whole_var[0]
    variable_name = whole_var[1]

    check_frame(frame, variable_name)       # check if variable exist
    
    # arg2 
    symb2 = check_symb(arguments[2])        # get type and value of var from frame or if constant from source code
    type2 = symb2[0]
    value2 = symb2[1]
    # arg3
    symb3 = check_symb(arguments[3])        # get type and value 
    type3 = symb3[0]
    value3 = symb3[1]

    if type2 != type3:                                  # comparing bool to anything else
        if type2 == "nil" or type3 == "nil":
            update_frame(frame, variable_name, ["bool", "false"])
        else:
            exit(53)

    result = "false"

    if type2 == "int":                              # comparing integers
        value2 = int(value2)
        value3 = int(value3)

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

    elif type2 == "string" or type2 == "bool":      # comparing strings and bool
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
        
    elif type2 == "nil":                            # comparing two nils
        if operator == "=":
            if value2 == value3:
                result = "true"
        else:
            exit(53)

    else:
        exit(99)

    update_frame(frame, variable_name, ["bool", result])        # update variable in frame


# AND ###########################
# OR ############################
# does logical operation and puts result into variable
# argvs: argumetns - dictionary of operands of instruction
# argvs: operator - only "and" or "or" - decides which operation will be done
def handle_and_or(arguments, operator):
    if len(arguments) != 3:
        exit(32)

    # arg1  
    whole_var = check_var(arguments[1])     # get char frame and name from source code

    frame = whole_var[0]
    variable_name = whole_var[1]

    check_frame(frame, variable_name)       # check if variable exist
    
    # arg2 
    symb2 = check_symb(arguments[2])        # get type and value of var from frame or if constant from source code
    type2 = symb2[0]
    value2 = symb2[1]
    # arg3
    symb3 = check_symb(arguments[3])        # get type and value
    type3 = symb3[0]
    value3 = symb3[1]

    if not (type2 == type3 == "bool"):      # check correctness of type
        exit(53)

    tmp_val2 = True if value2 == "true" else False      # preparing for operations transforming values into python values
    tmp_val3 = True if value3 == "true" else False

    if operator == "and":                                # do logical operations
        result = tmp_val2 and tmp_val3
    elif operator == "or":
        result = tmp_val2 or tmp_val3
    else:
        exit(99)

    result = "true" if result == True else "false"              # return values back to IPPcode values
    update_frame(frame, variable_name, ["bool", result])        # update variable in frame
    

# NOT ###########################
# negates bool value and puts result into variable
# argvs: argumetns - dictionary of operands of instruction
def handle_not(arguments):
    if len(arguments) != 2:
        exit(32)

    # arg1
    whole_var = check_var(arguments[1])     # get char frame and name from source code

    frame = whole_var[0]
    variable_name = whole_var[1]

    check_frame(frame, variable_name)       # check if variable exist
    
    # arg2 
    symb2 = check_symb(arguments[2])        # get type and value of var from frame or if constant from source code
    type2 = symb2[0]
    value2 = symb2[1]

    if type2 != "bool":                     # check correctness of type
        exit(53)

    if value2 == "true":
        update_frame(frame, variable_name, ["bool", "false"])       # update variable in frame
    else:
        update_frame(frame, variable_name, ["bool", "true"])


# INT2CHAR ###########################
# writes char with ord value of received int into variable
# argvs: argumetns - dictionary of operands of instruction
def handle_int2char(arguments):
    if len(arguments) != 2:
        exit(32)

    # arg1
    whole_var = check_var(arguments[1])     # get char frame and name from source code

    frame = whole_var[0]
    variable_name = whole_var[1]

    check_frame(frame, variable_name)       # check if variable exist
    
    # arg2 
    symb2 = check_symb(arguments[2])        # get type and value of var from frame or if constant from source code
    type2 = symb2[0]
    value2 = symb2[1]

    if type2 != "int":                      # check correctness of type
        exit(53)

    value2 = int(value2)

    if value2 > 1114111 or value2 < 0:      # check correctness of value
        exit(58)

    update_frame(frame, variable_name, ["string", chr(value2)])     # update variable in frame


# STR2INT ###########################
# gets ord number of chosen char and puts it into variable
# argvs: argumetns - dictionary of operands of instruction
def handle_str2int(arguments):
    if len(arguments) != 3:
        exit(32)

    # arg1
    whole_var = check_var(arguments[1])     # get char frame and name from source code

    frame = whole_var[0]
    variable_name = whole_var[1]

    check_frame(frame, variable_name)       # check if variable exist
    
    # arg2 
    symb2 = check_symb(arguments[2])        # get type and value of var from frame or if constant from source code
    type2 = symb2[0]
    value2 = symb2[1]
    # arg3 
    symb3 = check_symb(arguments[3])        # get type and value
    type3 = symb3[0]
    value3 = symb3[1]

    if type2 != "string":                   # check correctness of types
        exit(53)

    if type3 != "int":
        exit(53)

    value3 = int(value3)     

    if len(value2) - 1 < value3 or value3 < 0:      # check correctness of valuues
        exit(58)

    update_frame(frame, variable_name, ["int", ord(value2[value3])])        # update variable in frame


# 6.4.4 ######################################################################
# READ ###############################
# reads from stdin and puts it into variable
# argvs: argumetns - dictionary of operands of instruction
def handle_read(arguments):
    if len(arguments) != 2:
        exit(32)

    # arg1      
    whole_var = check_var(arguments[1])     # get char frame and name from source code

    frame = whole_var[0]
    variable_name = whole_var[1]

    check_frame(frame, variable_name)       # check if variable exist

    readed_line = get_line()                # read linee from std_in
    
    # arg2
    if arguments[2][0] != "type":           # check correctness of type
        exit(32)

    new_type = arguments[2][1]

    if new_type == "int":                   # depending on chosen typ do a conversion of readed line
        try:
            readed_line = int(readed_line)
        except Exception:
            readed_line = 0

    elif new_type == "string":
        pass

    elif new_type == "bool":
        if readed_line.upper() == "TRUE":
            readed_line = "true"
        else:
            readed_line = "false"

    else:
        exit(32)

    update_frame(frame, variable_name, [new_type, readed_line])     # update variable in frame


# WRITE #############################
# prints string into stdout
# argvs: argumetns - dictionary of operands of instruction
def handle_write(arguments):
    if len(arguments) != 1:
        exit(32)

    symb1 = check_symb(arguments[1])            # get type and value of var from frame or if constant from source code
    type1 = symb1[0]
    value1 = symb1[1]

    if type1 == "nil" and value1 == "nil":      # if have to write nil - write ""
        print("", end='')             
    else:
        print(value1, end='')


# 6.4.5 ######################################################################
# CONCAT #############################
# joins two string and put them into variable
# argvs: argumetns - dictionary of operands of instruction
def handle_concat(arguments):
    if len(arguments) != 3:
        exit(32)

    # arg1
    whole_var = check_var(arguments[1])     # get char frame and name from source code

    frame = whole_var[0]
    variable_name = whole_var[1]

    check_frame(frame, variable_name)       # check if variable exist

    # arg2 
    symb2 = check_symb(arguments[2])        # get type and value of var from frame or if constant from source code
    type2 = symb2[0]
    value2 = symb2[1]
    # arg3
    symb3 = check_symb(arguments[3])        # get type and value
    type3 = symb3[0]
    value3 = symb3[1]

    if not (type2 == type3 == "string"):    # check correctness of types
        exit(53)

    update_frame(frame, variable_name, ["string", value2 + value3])     # update variable in frame


# STRLEN #############################
# gets length of string and puts it into variable
# argvs: argumetns - dictionary of operands of instruction
def handle_strlen(arguments):
    if len(arguments) != 2:
        exit(32)

    # arg1
    whole_var = check_var(arguments[1])     # get char frame and name from source code

    frame = whole_var[0]
    variable_name = whole_var[1]

    check_frame(frame, variable_name)       # check if variable exist

    # arg2 
    symb2 = check_symb(arguments[2])        # get type and value of var from frame or if constant from source code
    type2 = symb2[0]
    value2 = symb2[1]

    if type2 != "string":                   # check correctness of type
        exit(53)

    update_frame(frame, variable_name, ["int", len(value2)])        # update variable in frame


# GETCHAR #############################
# gets char from string
# argvs: argumetns - dictionary of operands of instruction
def handle_getchar(arguments):
    if len(arguments) != 3:
        exit(32)

    # arg1
    whole_var = check_var(arguments[1])     # get char frame and name from source code

    frame = whole_var[0]
    variable_name = whole_var[1]

    check_frame(frame, variable_name)       # check if variable exist

    # arg2 
    symb2 = check_symb(arguments[2])        # get type and value of var from frame or if constant from source code
    type2 = symb2[0]
    value2 = symb2[1]
    # arg3
    symb3 = check_symb(arguments[3])        # get type and value
    type3 = symb3[0]
    value3 = symb3[1]

    if type2 != "string" or type3 != "int":     # check correctness of types
        exit(53)

    value3 = int(value3)

    if value3 > len(value2) - 1:                # check correctness of value
        exit(58)

    if value3 < 0:
        exit(57)

    update_frame(frame, variable_name, ["string", value2[value3]])      # update variable in frame
    

# SETCHAR #############################
# changes char in string by another char
# argvs: argumetns - dictionary of operands of instruction
def handle_setchar(arguments):
    if len(arguments) != 3:
        exit(32)

    # arg1
    whole_var = check_var(arguments[1])    # get char frame and name from source code

    frame = whole_var[0]
    variable_name = whole_var[1]

    check_frame(frame, variable_name)      # check if variable exist

    symb1 = check_symb(arguments[1])       # get type and value of var from frame or if constant from source code
    type1 = symb1[0]
    value1 = symb1[1]

    # arg2 
    symb2 = check_symb(arguments[2])       # get type and value
    type2 = symb2[0]
    value2 = symb2[1]
    # arg3
    symb3 = check_symb(arguments[3])       # get type and value
    type3 = symb3[0]
    value3 = symb3[1]

    if not (type1 == type3 == "string") or type2 != "int":      # check correctness of types
        exit(53)

    value2 = int(value2)

    if len(value1) == 0 or len(value1) - 1 < value2:            
        exit(58)

    if len(value3) < 1:
        exit(58)

    if value2 < 0:
        exit(57)

    old_string = value1                                         # string to be changed
    IndexToReplace = value2                                     # index for change
    new_letter = value3[0]                                      # new letter that will be in string at index
    new_string = "".join((old_string[:IndexToReplace], new_letter, old_string[IndexToReplace+1:]))      # replacement of letter


    update_frame(frame, variable_name, ["string", new_string])                                          # update variable in frame


# 6.4.6 ######################################################################
# TYPE #############################
# gets type of variable and puts into another like string
# argvs: argumetns - dictionary of operands of instruction
def handle_type(arguments):
    if len(arguments) != 2:
        exit(32)

    # arg1
    whole_var = check_var(arguments[1])

    frame = whole_var[0]
    variable_name = whole_var[1]

    check_frame(frame, variable_name)      # check if variable exist

    # arg2 
    type2 = check_symb_and_ret_type(arguments[2])

    update_frame(frame, variable_name, ["string", type2])


# 6.4.7 ######################################################################
# JUMP #############################
# unconditioned jump - jumps to chosen label - changes instruction counter so that next executed instruction will be defferent than next one
# instruction_counter is changed as global variable
# argvs: argumetns - dictionary of operands of instruction
def handle_jump(arguments):
    global instruction_counter

    if len(arguments) != 1:
        exit(32)

    label_type = arguments[1][0]
    label_name = arguments[1][1]

    if label_type != "label":
        exit(32)

    label_number = check_and_get_label(label_name)
    instruction_counter = label_number - 1


# JUMPIFEQ #############################
# JUMPIFNEQ ############################
# conditioned jumps - changes instruction counter so that next executed instruction will be defferent than next one
# instruction_counter is changed as global variable
# argvs: argumetns - dictionary of operands of instruction
# argvs: operator - only "==" - JUMPIFEQ, or "!=" - JUMPIFNEQ 
def handle_jump_if(arguments, operator):
    global instruction_counter

    if len(arguments) != 3:
        exit(32)

    # arg1
    label_type = arguments[1][0]
    label_name = arguments[1][1]

    if label_type != "label":
        exit(32)

    label_number = check_and_get_label(label_name)

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

    if value2 == value3:
        if operator == "==":
            instruction_counter = label_number - 1
    else:
        if operator == "!=":
            instruction_counter = label_number - 1


# EXIT #############################
# ends program with selected value
# argvs: argumetns - dictionary of operands of instruction
def handle_exit(arguments):
    global arguments_dic

    if len(arguments) != 1:
        exit(32)

    symb1 = check_symb(arguments[1])
    type1 = symb1[0]
    value1 = symb1[1]
    value1 = int(value1)

    if type1 != "int":
        exit(53)

    if value1 < 0 or value1 > 49:
        exit(57)

    print_stati(arguments_dic)
    exit(value1)


# 6.4.7 ######################################################################
# DPRINT #############################
# writes string into stderr
# argvs: argumetns - dictionary of operands of instruction
def handle_dprint(arguments):
    if len(arguments) != 1:
        exit(32)

    symb1 = check_symb(arguments[1])
    value1 = symb1[1]

    print(value1, file=stderr)


# BREAK #############################
# writes information about actual state of executed program into stderr
# argvs: argumetns - dictionary of operands of instruction
def handle_break(arguments):
    global instruction_counter
    global global_frame
    global temporary_frame
    global local_frame
    global calling_stack
    global data_stack
    global label_dict
    
    if len(arguments) != 0:
        exit(32)

    print("Actual instruction:", instruction_counter, file=stderr)
    print("Global frame:", global_frame, file=stderr)
    print("Temporary frame:", temporary_frame, file=stderr)
    print("Local frame:", local_frame, file=stderr)
    print("Calling stack:", calling_stack, file=stderr)
    print("Data stack:", data_stack, file=stderr)
    print("All reachable labels:", label_dict, file=stderr)


####################################################################################################
#                                main handling instructions                                        #
####################################################################################################
# gets highest number of instruction to get end of program
# argvs: program - source code in xml format
# return: int - highest order number of instruction
def get_highest_order_number(program):
    top = 0

    for instruction in program:
        if int(instruction.attrib["order"]) > top:
            top = int(instruction.attrib["order"])

    return top


# temporary functions for transformation of xml code
# argvs: instruction - instruction in xml format
# return: dictionary - key = instruction order number, value = list of operands
def get_instruction_dictionary(instruction):
    dic = {}

    # cycle for transforming all operands of instruction
    for argument in instruction:
        dic.update({int(argument.tag[-1]): [argument.attrib["type"], argument.text]})

    return dic


# transforms xml format into dictionary
# argvs: program - source code in xml format
# return: dictionary - source code trensformed into dictionary
def get_program_dictionary(program):
    dic = {}

    # cycle goes through all instructions
    for instruction in program:
        new_instruction = get_instruction_dictionary(instruction)
        
        dic.update({int(instruction.attrib["order"]): [instruction.attrib["opcode"].upper(), new_instruction]})

    return dic


# swich of instructions - gets instruction name and calls function to handle this instruction
# argvs: instruction - list of [opcode, dictionary of operands]
def instruction_switch(instruction):
    global global_frame
    global temporary_frame
    global local_frame

    opcode = instruction[0]
    arguments = instruction[1]

    ###########
    # 6.4.1 frames, calling functions
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
    # 6.4.2 data stack
    elif opcode == "PUSHS":
        handle_pushs(arguments)
        
    elif opcode == "POPS":
        handle_pops(arguments)
       
        
    ###########
    # 6.4.3 arithmetic, relation, bool and conversion instructions
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

    elif opcode == "STRI2INT":
        handle_str2int(arguments)

    ###########
    # 6.4.4 in/out instructions
    elif opcode == "READ":    
        handle_read(arguments)
        
    elif opcode == "WRITE":
        handle_write(arguments)

    ###########
    # 6.4.5 work with strings
    elif opcode == "CONCAT":
        handle_concat(arguments)

    elif opcode == "STRLEN":
        handle_strlen(arguments)

    elif opcode == "GETCHAR":
        handle_getchar(arguments)

    elif opcode == "SETCHAR":
        handle_setchar(arguments)

    ###########
    # 6.4.6 work with types
    elif opcode == "TYPE":
        handle_type(arguments)

    ###########
    # 6.4.7 handling of program stream
    elif opcode == "LABEL":
        pass

    elif opcode == "JUMP":
        handle_jump(arguments)
    elif opcode == "JUMPIFEQ":
        handle_jump_if(arguments, "==")
        
    elif opcode == "JUMPIFNEQ":
        handle_jump_if(arguments, "!=")

    elif opcode == "EXIT":
        handle_exit(arguments)
        
    ###########
    # 6.4.8 debbug instructions
    elif opcode == "DPRINT":
        handle_dprint(arguments)

    elif opcode == "BREAK":
        handle_break(arguments)

    else:
        exit(32)




# function calls necessary functions before executing and then executes each instruction
# argvs: program - xml format of source file
def handle_instructions(program):
    global instruction_counter
    global label_dict
    global instruction_stati
    global vars_stati
    
    # getting last instruction to know when program ends
    top_order = get_highest_order_number(program)

    # transforming xml format into own format for better work with instructions and operands
    program_dic = get_program_dictionary(program) 

    # getting all label names and positions befor executing starts
    get_labels(program_dic)

    # main cycle that goes until last instruction in source file is done
    while instruction_counter <= top_order:
        try:
            actual_instruction = program_dic[instruction_counter]
        except Exception:
            exit(32)

        instruction_switch(actual_instruction)

        instruction_counter += 1
        instruction_stati += 1
        vars_stati = check_max_vars(vars_stati)


# writes statistics into chosen file
# argvs: arguments_dic - dictionary of used program arguments
def print_stati(arguments_dic):
    global stats_file
    global instruction_stati_first
    global vars_stati
    global instruction_stati

    # writes statistics only if argument "--stats" was used
    if arguments_dic["stats"]:
        with open(stats_file, 'w+') as the_file:
            if arguments_dic["insts"] and arguments_dic["vars"]:
                # choosing order of statistics depending on order of arguments
                if instruction_stati_first:
                    new_string = str(instruction_stati) + "\n" + str(vars_stati)
                    the_file.write(new_string)
                else:
                    new_string = str(vars_stati) + "\n" + str(instruction_stati)
                    the_file.write(new_string)
            
            # if only 1 statistic is needed
            elif arguments_dic["insts"]:
                the_file.write(str(instruction_stati))
            
            elif arguments_dic["vars"]:
                the_file.write(str(vars_stati))



####################################################################################################
#                                          MAIN                                                    #
####################################################################################################

arguments_dic = check_arguments(argv)


if not arguments_dic["source"] or not arguments_dic["input"]:
    if not arguments_dic["source"]:
        src_file = read_from_stdin()

    if not arguments_dic["input"]:
        input_file = stdin

if arguments_dic["input"] == True:
    input_file = io.StringIO(input_file)

program = ET.fromstring(src_file)

handle_instructions(program)

print_stati(arguments_dic)
