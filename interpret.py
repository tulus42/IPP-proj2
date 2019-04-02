from sys import *
import xml.etree.ElementTree as ET


src_file = ""
input_file = ""
stats_file = ""

instruction_counter = 1


#################
# checking correctness of arguments
#################
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
    
    print(string)
    return string


#################
# handling instructions
#################
def get_highest_order_number(program):
    top = 0

    for instruction in program:
        if int(instruction.attrib["order"]) > top:
            top = int(instruction.attrib["order"])

    return top


def get_program_dictionary(program):
    dic = {}

    for instruction in program:
        dic.update({int(instruction.attrib["order"]): instruction})

    return dic


def instruction_switch(instruction):
    opcode = instruction.attrib["opcode"].upper()


    ###########
    # 6.4.1 ramce, volanie funkcii
    if opcode == "MOVE":
        handle_move()
    elif opcode == "CREATEFRAME":
        handle_createframe()
    elif opcode == "PUSHFRAME":
        handle_pushframe()
    elif opcode == "POPFRAME":
        handle_popframe()
    elif opcode == "DEFVAR":
        handle_defvar()
    elif opcode == "CALL":
        handle_call()
    elif opcode == "RETURN":
        handle_return()

    ###########
    # 6.4.2 datovy zasobnik
    elif opcode == "PUSHS":
        handle_pushs()
    elif opcode == "POPS":
        handle_pops()
        
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

    else
        exit(32)





def handle_instructions(program):
    global instruction_counter
    
    top_order = get_highest_order_number(program)

    program = get_program_dictionary(program) 

    

    print(program[2].attrib)

    while instruction_counter <= top_order:

        instruction_switch(program[instruction_counter])

        instruction_counter += 1









######### MAIN #########


arguments_dic = check_arguments(argv)
print(arguments_dic)

if not arguments_dic["source"] or not arguments_dic["input"]:
    if not arguments_dic["source"]:
        src_file = read_from_stdin()

    if not arguments_dic["input"]:
        input_file = read_from_stdin()

program = ET.fromstring(src_file)


handle_instructions(program)


for instruction in program:
    print(instruction.tag)
    print(instruction.attrib["order"])
    print(instruction.attrib["opcode"])
    print(instruction.text)
    for argument in instruction:
        print(argument.tag)
        print(argument.attrib)
        print(argument.text)




