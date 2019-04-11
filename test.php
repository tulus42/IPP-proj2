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
                    break;

                case "--parse-only":
                    $parse_only_arg = is_param($parse_only_arg);
                    break;

                case "--int-only":
                    $int_only_arg = is_param($int_only_arg);
                    break;

                case (preg_match('/--directory=.*/', $argvs[$i]) ? true : false) :
                    $directory_path_arg = is_param($directory_path_arg);

                    $path = preg_replace('/--directory=/', '', $argvs[$i]);

                    if (substr($path, -1) != "/") {
                        $path = $path."/";
                    }

                    if(is_dir($path)) {
                        $GLOBALS['directory_path'] = $path;
                    }else{
                        echo "nespravna cesta\n";
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
        $GLOBALS['directory_path'] = "";
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
    echo "some helpful information\n";      // TODO
}



function get_input_file($source_file) {
    $file_name = str_replace(".src", ".in", $source_file);
    
    if (file_exists($file_name)) {
        return $file_name;
    } else {
        $fh = fopen($file_name, 'w+');
        fclose($fh);
        return $file_name;
    }
}


function rglob($pattern, $flags = 0) {
    $files = glob($pattern, $flags); 
    foreach (glob(dirname($pattern).'/*', GLOB_ONLYDIR|GLOB_NOSORT) as $dir) {
        $files = array_merge($files, rglob($dir.'/'.basename($pattern), $flags));
    }
    return $files;
}

// RETURN VALUE
function check_return_val($ret_val, $file_name) {
    $file_name = str_replace(".src", ".rc", $file_name);

    if (file_exists($file_name)) {
        $fh = fopen($file_name, 'r');
    } else {
        $fh = fopen($file_name, 'w+');
        fwrite($fh, 0);
        fclose($fh);

        $fh = fopen($file_name, 'r');
    }

    $file_ret = fread($fh, filesize($file_name));

    fclose($fh);

    if ($file_ret == $ret_val) {
        return TRUE;
    } else {
        return FALSE;
    }
}


// OUTPUT INT
function check_output_int($program_out, $file_name) {
    $file_name = str_replace(".src", ".out", $file_name);

    if (file_exists($file_name)) {

    } else {
        $fh = fopen($file_name, 'w+');
        fclose($fh);
    }

    $file_out = file_get_contents($file_name);

    $tmp = "";
    foreach ($program_out as $i) {
        $tmp = $tmp.$i;
    }
    $program_out = $tmp;


    if (md5($program_out) == md5_file($file_name)) {
        return TRUE;
    } else {
        return FALSE;
    }


}

// OUTPUT PARSE
function check_output_parse($program_output, $file_name) {
    $file_name = str_replace(".src", ".out", $file_name);

    if (file_exists($file_name)) {
        $fh = fopen($file_name, 'r');
    } else {
        $fh = fopen($file_name, 'w+');
        fclose($fh);

        $fh = fopen($file_name, 'r');
    }

    $file_out = fread($fh, filesize($file_name));

    fclose($fh);

    $tmp_file = "tmp_file";
    $file1 = "tmp_file1";
    file_put_contents($file1, $program_output);

    exec("java -jar /pub/courses/ipp/jexamxml/jexamxml.jar ".$file1." ".$file_name." > ".$tmp_file);

    $tmp_file = file_get_contents($tmp_file);

    if (strpos($tmp_file, "Two files are identical") != FALSE) {
        return TRUE;
    } else {
        return FALSE;
    }

}


///////////////////////////////////////////////////////
// PARSE TESTS
///////////////////////////////////////////////////////
function run_all_parse_tests($exec_file) {
    $arguments = $GLOBALS['arguments'];
    $dir_path = $GLOBALS['directory_path']; 

    // int-only
    if ($arguments[2]) {
        return;
    }

    $GLOBALS['html_code'] .=  "        <h2 style=\"color: indigo\">Parsing tests:</h2>";


    // recurslive == false
    if ($arguments[0] == FALSE) {

        foreach (glob($dir_path."*.src") as $source_file) {
            $input_file = get_input_file($source_file);

            $output = "";

            exec('php7.3 '.$exec_file.' < '.$source_file, $output, $return_var);
            

            $ret_val = check_return_val($return_var, $source_file);
            $out_val = check_output_parse($output, $source_file);
            
            html_element($ret_val, $out_val, $source_file, $return_var);
        }

    // recursive == true
    } else {
        $files = rglob($dir_path."*.src");

        foreach($files as $source_file) {
            $input_file = get_input_file($source_file);

            $output = "";

            exec('php7.3 '.$exec_file.' < '.$source_file, $output, $return_var);

            $ret_val = check_return_val($return_var, $source_file);
            $out_val = check_output_parse($output, $source_file);

            html_element($ret_val, $out_val, $source_file, $return_var);

        }
    }
}



///////////////////////////////////////////////////////
// INTERPRET TESTS
///////////////////////////////////////////////////////
function run_all_int_tests($exec_file) {
    $arguments = $GLOBALS['arguments'];
    $dir_path = $GLOBALS['directory_path']; 


    // parse-only
    if ($arguments[1]) {
        return;
    }
    
    $GLOBALS['html_code'] .=  "        <h2 style=\"color: indigo\">Interpreting tests:</h2>";



    // recurslive == false
    if ($arguments[0] == FALSE) {
        foreach (glob($dir_path."*.src") as $source_file) {
            $input_file = get_input_file($source_file);
            $output = "";

            
            exec('python3.6 "'.$exec_file.'" --source="'.$source_file.'" --input="'.$input_file.'"', $output, $return_var);
            
            $ret_val = check_return_val($return_var, $source_file);
            $out_val = check_output_int($output, $source_file);

            html_element($ret_val, $out_val, $source_file, $return_var);
        }

    // recursive == true
    } else {
        $files = rglob($dir_path."*.src");

        foreach($files as $source_file) {
            $input_file = get_input_file($source_file);
            $output = "";

            exec('python3.6 "'.$exec_file.'" --source="'.$source_file.'" --input="'.$input_file.'"', $output, $return_var);

            $ret_val = check_return_val($return_var, $source_file);
            $out_val = check_output_int($output, $source_file);

            html_element($ret_val, $out_val, $source_file, $return_var);
        }
    }
}



///////////////////////////////////////////////////////
// HTML
///////////////////////////////////////////////////////
function html_header() {
    return "<!DOCTYPE html>
    <html lang=\"en\">
        <head>
            <meta charset=\"UTF-8\">
            <title>Testing log</title>
        </head>
        <body>
            <h1 style=\"text-align: center; color: darkred\">Testing log</h1>";
}


function html_element($ret_val, $out_val, $source_file, $return_var) {
    if ($ret_val && ($return_var != 0)) {
        $GLOBALS['html_code'] .= "<h3 style=\"color:limegreen\">".$source_file."</h3>
        <p style=\"margin-left: 60px; color:limegreen\">Returned value: CORRECT - non 0</p>
        <p style=\"margin-left: 60px; color:limegreen\">Output value: NONE</p>";

        $GLOBALS['correct_test_counter'] += 1;

    } elseif ($ret_val) {
        if ($out_val) {
            $GLOBALS['html_code'] .= "<h3 style=\"color:limegreen\">".$source_file."</h3>
            <p style=\"margin-left: 60px; color:limegreen\">Returned value: CORRECT</p>
            <p style=\"margin-left: 60px; color:limegreen\">Output value: CORRECT</p>";

            $GLOBALS['correct_test_counter'] += 1;
            
        } else {
            $GLOBALS['html_code'] .= "<h3 style=\"color:red\">".$source_file."</h3>
            <p style=\"margin-left: 60px; color:limegreen\">Returned value: CORRECT</p>
            <p style=\"margin-left: 60px; color:red\">Output value: FAIL</p>";
        }

    } else {
        $GLOBALS['html_code'] .= "<h3 style=\"color:red\">".$source_file."</h3>
        <p style=\"margin-left: 60px; color:red\">Returned value: FAIL - returned: ".$return_var."</p>
        <p style=\"margin-left: 60px; color:red\">Output value: NONE</p>";
    }

    $GLOBALS['test_counter'] += 1;
}


function end_html($string) {
    $res = ($GLOBALS['correct_test_counter'] / $GLOBALS['test_counter']) * 100;
    $string .= "        <h2 style=\"color: indigo\">Results: ".round($res,2)."%</h2>
    <p style=\"margin-left: 60px\">Succesfull tests: ".$GLOBALS['correct_test_counter']."</p>
    <p style=\"margin-left: 60px\">All tests: ".$GLOBALS['test_counter']."</p>
    \n    </body>
    </html>";

    file_put_contents("htmllog.html", $string);
}

///////////////////////////////////////////////////////
// MAIN
///////////////////////////////////////////////////////
$parse_file = "parse.php";
$interpret_file = "interpret.py";
$directory_path = "";

$test_counter = 0;
$correct_test_counter = 0;

//              recursive,parse,int    //
$arguments = array(FALSE, FALSE, FALSE);

$html_code = html_header();


handle_arguments($argv);

run_all_parse_tests($parse_file);

run_all_int_tests($interpret_file);


end_html($html_code);

?>
