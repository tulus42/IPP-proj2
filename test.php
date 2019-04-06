<?php

//////////////////////////////////////////////////
// arguments parsing functions:
//////////////////////////////////////////////////

// check if there is any argument and choose how to handle it
function handle_arguments($argvs) {
    $argc = count($argvs);
    $directory_path_arg = FALSE;
    $recursive_arg = FALSE;
    $parse_script_file_arg = FALSE;
    $int_script_file_arg = FALSE;
    $parse_only_arg = FALSE;
    $int_only_arg = FALSE;

    echo "argc: ".$argc."\n";

    // no arguments -> ok, else:
    if ($argc != 1) {
        // 1 argument -> --help or --stats=file
        if ($argc == 2 && $argvs[1] == "--help") 
            show_help();

        // other arguments
        for ($i = 1; $i < $argc; $i++) {

            switch($argvs[$i]) {
                case "--recursive":
                    $recursive_arg = is_param($recursive_arg);
                    echo "recursive\n";
                    break;

                case "--parse-only":
                    $parse_only_arg = is_param($parse_only_arg);
                    echo "parse only\n";
                    break;

                case "--int-only":
                    $int_only_arg = is_param($int_only_arg);
                    echo "int only\n";
                    break;

                case (preg_match('/--directory=.*/', $argvs[$i]) ? true : false) :
                    $directory_path_arg = is_param($directory_path_arg);
                    $path = preg_replace('/--directory=/', '', $directory_path_arg);

                    if(preg_match('#^(\w+/){1,2}\w+\.\w+$#',$path)) {
                        echo $path;  // valid path.
                    }else{
                        exit(10); // invalid path
                    }
                     
                    break;

                case (preg_match('/--parse-script=.*/', $argvs[$i]) ? true : false) :
                    $parse_script_file_arg = is_param($parse_script_file_arg);
                    $parse_file = preg_replace('/--parse-script=/', '', $parse_script_file_arg);

                    if (count(glob($parse_file)) != 1) {
                        exit(10);
                    }
                    break;

                case (preg_match('/--int-script=.*/', $argvs[$i]) ? true : false) :
                    $int_script_file_arg = is_param($int_script_file_arg);
                    $interpret_file = preg_replace('/--int-script=/', '', $int_script_file_arg);

                    if (count(glob($interpret_file)) != 1) {
                        exit(10);
                    }
                    
                    
                    break;

                default:
                    exit(10);
            
            }
        }
    }

    if ($int_only_arg && $parse_only_arg) {
        exit(10);
    }

    if ($int_only_arg && $parse_script_file_arg) {
        exit(10);
    }

    if ($parse_only_arg && $int_script_file_arg) {
        exit(10);
    }

    if ($directory_path_arg == FALSE) {
        $GLOBALS['directory_path'] = getcwd();
    }

    if ($int_script_file_arg == FALSE) {
        $GLOBALS['interpret_file'] = "interpret.py";
    }

    if ($parse_script_file_arg == FALSE) {
        $GLOBALS['parse_file'] = "parse.php";
    }

    $GLOBALS['arguments'][0] = $recursive_arg;
    $GLOBALS['arguments'][1] = $parse_only_arg;
    $GLOBALS['arguments'][2] = $int_only_arg;

}


// checks if is argument already used
function is_param($param) {
    if ($param == FALSE) {
        return(TRUE);
    } else {
        exit(10);
    }
}


function show_help() {
    echo "some helpful information\n";
}


///////////////////////////////////////////////////////
// PARSE TESTS
///////////////////////////////////////////////////////
function run_all_parse_tests($exec_file) {
    $arguments = $GLOBALS['arguments'];

    if ($arguments[2]) {
        echo "making no parse tests\n";
        return;
    }

    $source_file = get_src_file();

    $output = shell_exec('php7.2 '.$exec_file.' < '.$source_file);
    echo "<pre>$output</pre>";

}


///////////////////////////////////////////////////////
// INTERPRET TESTS
///////////////////////////////////////////////////////
function run_all_int_tests($exec_file) {
    $arguments = $GLOBALS['arguments'];

    if ($arguments[1]) {
        echo "making no interpret tests\n";
        return;
    }
    
    $output = shell_exec('python3.6 '.$exec_file.' --source='.$source_file.' --input='.$input_file);
    echo "<pre>$output</pre>";
    
}






///////////////////////////////////////////////////////
// MAIN
///////////////////////////////////////////////////////
$parse_file = "";
$interpret_file = "";
$directory_path = "";

//              recursive,parse,int    //
$arguments = array(FALSE, FALSE, FALSE);

handle_arguments($argv);

run_all_parse_tests($parse_file);

run_all_int_tests($interpret_file);





?>
