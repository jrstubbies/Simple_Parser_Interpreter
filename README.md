# Simple_Parser_Interpreter
A parser/interpreter for a simple imperative string-processing language

Overview:
    The interpreter reads in standard input and writes to standard output. The interpreter reads statements one at a time and perform any associated action immediately. The interpreter provides useful error messages if the input doesn't meet certain requirements.


String Language:
    Using EBNF grammar as below. The words: program, statement, expression, and values are EBNF tokens, while all other words are lexer tokens.

    program   := { statement }
    statement := append id expression end
                |   list end
                |   exit end
                |   print expression end
                |   printlength expression end
                |   printwords expression end
                |   printwordcount expression end
                |   set id expression end
                |   reverse id end
    expression := value { plus value }
    value     := id | constant | literal

    In which a:
        constant = SPACE | TAB | NEWLINE
        end = ;
        id = [a-zA-Z][a-zA-Z0-9]*
        literal = "(?:\\.|[^"\\])*"


Commands:
    Below are the intended actions to be taken for each command.

    Command         |  Parameter              |  Behaviour
    ---------------------------------------------------------------------------------------------------------------------
    append             id expression             Evaluate the expression and append it to the variable contents.
    list                                         List all variables and their contents.  
    exit                                         Exit the interpreter
    print              expression                Evaluate and print the expression
    printlength        expression                Evaluate the expression and print its length (characters)
    printwords         expression                Evaluate the expression and print the individual words
    printwordcount     expression                Evaluate the expression and print the number of words
    set                id expression             Set the contents of the variable to the expression
    reverse            id                        Reverse the order of the words in the contents of the variable.

    In which a:
        word = any set of letters or digits separated by whitespace or punctuation chars. AN EXCEPTION is words CAN contain
                a single-quote or a hyphen char. Valid examples:   "let's"  and   "x-ray"



An Example:

    -------------------------------------
    |       THE INPUT                   |
    -------------------------------------
        set one "The cat";
        set two "sat on the mat";
        set sentence one + SPACE + two;
        append sentence " by itself.";
        print sentence;
        printwordcount sentence;
        printwords sentence;
        printlength sentence;
        list;
        reverse	one;
        print   one;
        exit;

    -------------------------------------------------
    |       THE OUTPUT                              | 
    -------------------------------------------------
        The cat sat on the mat by itself.
        Wordcount: 8
        Words:
        The
        cat
        sat
        on
        the
        mat
        by
        itself
        Length: 33
        Identifier List(3):
        one : The cat
        two : sat on the mat
        sentence : The cat sat on the mat by itself.
        cat The