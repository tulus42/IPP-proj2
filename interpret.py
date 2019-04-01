from sys import *
import xml.etree.ElementTree as ET


src_file = ""
input_file = ""
stats_file = ""

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
                arguments_dic["source"] = True
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


######### MAIN #########


arguments_dic = check_arguments(argv)


if not arguments_dic["source"] or not arguments_dic["input"]:
    if not arguments_dic["source"]:
        src_file = read_from_stdin()
    if not arguments_dic["input"]:
        input_file = read_from_stdin()


program = ET.fromstring(src_file)

for instruction in program:
    print(instruction.attrib["order"])
    for argument in instruction:
        print(argument.tag)
        print(argument.attrib)
        print(argument.text)




