from sys import *
import re
import xml.etree.ElementTree as ET


src_file = ""
input_file = ""
stats_file = ""

global_frame = {}
temporary_frame = None
local_frame = []


instruction_counter = 1
calling_stack = 0


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


def get_var_value(frame, variable):
    if frame == "GF":
        return global_frame[variable]
    elif frame == "TF":
        return temporary_frame[variable]
    elif frame == "LF":
        return local_frame[-1][variable]
    else:
        exit(99)

# returns value of symbol or variable
def check_symb(argument):
    arg_type = argument[0]
    symb = argument[1]

    if arg_type == "int":
        if re.sub(r"[\d]+", "", symb) != "":
            print("nespravny argument int")
            exit(32)

    elif arg_type == "string":
        if re.sub(r"[^#\\\s]+", "", symb) != "":
            print("nespravny argument string")
            exit(32)

    elif arg_type == "bool":
        if symb != "true" or symb != "false":
            print("nespravny argument bool")
            exit(32)

    elif arg_type == "nil":
        if symb != "nil":
            print("nespravny argument nil")
            exit(32)

    elif arg_type == "var":
        variable = check_var(argument)[1]
        frame = variable[0]
        variable = variable[1]

        check_frame(frame, variable)
        return get_var_value(frame, variable)
        
    else:
        print("argument nevyhovuje ziadnej moznosti")
        exit(32)

    return symb


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

    symb = check_symb(arguments[2])     # get value from 2. argument

    check_frame(frame1, variable1)      # check if variable exist

    update_frame(frame1, variable1, symb)



# PUSHFRAME #######################
def handle_pushframe():
    global temporary_frame
    global local_frame

    local_frame.append(temporary_frame)
    temporary_frame = None


# POPFRAME #######################
def handle_popframe():
    global temporary_frame
    global local_frame

    if local_frame != []:
        temporary_frame = local_frame[-1]
    else:
        exit(55)

# CALL ###########################
def handle_call():
    global instruction_counter
    global calling_stack

    check_label()

    calling_stack.append(instruction_counter)




###################################################################
# handling instructions
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
        temporary_frame = {}
        
    elif opcode == "PUSHFRAME":
        handle_pushframe()
        
    elif opcode == "POPFRAME":
        handle_popframe()

    elif opcode == "DEFVAR":
        handle_defvar(arguments)

    elif opcode == "CALL":
        handle_call()
        
    elif opcode == "RETURN":
        #handle_return()
        pass

    ###########
    # 6.4.2 datovy zasobnik
    elif opcode == "PUSHS":
        #handle_pushs()
        pass
    elif opcode == "POPS":
        #handle_pops()
        pass
        
    ###########
    # 6.4.3 aritmeticke, relacne, booleovske a konverzne instrukcie
    elif opcode == "ADD":
        pass
    elif opcode == "SUB":
        pass
    elif opcode == "MUL":
        pass
    elif opcode == "IDIV":
        pass
    elif opcode == "LT":
        pass
    elif opcode == "GT":
        pass
    elif opcode == "EQ":
        pass
    elif opcode == "AND":
        pass
    elif opcode == "OR":
        pass
    elif opcode == "NOT":
        pass
    elif opcode == "INT2CHAR":
        pass
    elif opcode == "STR2INT":
        pass

    ###########
    # 6.4.4 vytupne a vystupne instrukcie
    elif opcode == "READ":    
        pass
    elif opcode == "WRITE":
        pass

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
    
    top_order = get_highest_order_number(program)

    program = get_program_dictionary(program) 

    print(program)
    
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
        input_file = read_from_stdin()

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






