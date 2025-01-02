# Firstly the code uses a function to get user input. This function takes input lines and checks if there is a/any
#   ';' characters that are NOT within " ". If there isn't a ';' then user input is classified as multi-line input
#   and is concatenated. The function passes anything before a ';' into the lexer to get back the tokens. These
#   tokens are subsequently passed to the Parser class.

# The lexer simply moves the input string and tries to match against the regex for each token type in the
#   'patterns' list. If there is a char/word that can't be matched then the user has typed in something invalid.
#   The lexer function gives an error indicating where the erroneous char/word is. Otherwise a list of tuples
#   is returned. The tuple holds the token type and value, this is especially helpful for the id and literal types
#   which don't have pre-defined values. This list is passed onto the Parser class via the input function.

# Next the Parser class is used to check that each statement follows its own 'statement rules'. This is achieved
#   by comparing the current lexer token type with the expected lexer token type. If they don't match then an
#   error is given, otherwise the tokens can eventually be passed to the interpreter.

# Finally, the Interpreter class is used to perform the statement's required actions. Checks are in place to ensure
#   expressions can be evaluated correctly, and that variables are stored in the symbol table before attempting to
#   use/update/replace etc. If not then an appropriate error message is given, and the user can re-try their input.

import re

# A list of tuples to hold the lexer token types and their relevant regex
patterns = [
    ('APPEND', r'\bappend\b'),
    ('EXIT', r'\bexit\b'),
    ('LIST', r'\blist\b'),
    ('PRINTLENGTH', r'\bprintlength\b'),
    ('PRINTWORDS', r'\bprintwords\b'),
    ('PRINTWORDCOUNT', r'\bprintwordcount\b'),
    ('PRINT', r'\bprint\b'),
    ('REVERSE', r'\breverse\b'),
    ('SET', r'\bset\b'),
    ('CONSTANT', r'TAB|SPACE|NEWLINE'),
    ('END', r';'),
    ('PLUS', r'\+'),
    ('ID', r'[a-zA-Z][a-zA-Z0-9]*'),
    ('LITERAL', r'"(?:\\.|[^"\\])*"'),      # handles special chars, " within a literal require a '\' first
    ('WHITESPACE', r'\s+|\\t+|\\n+'),       # used so that lexer knows about whitespace chars
]


# Lexer function. Returns a list of token-value tuples based on the patterns matched, or gives error if invalid token
def lexer(input_string):
    tokens = []
    pos = 0

    # loop that moves through the input string trying to match lexical tokens/patterns
    while pos < len(input_string):
        lex_match = None

        # loop through each tuple in 'patterns' to see if input matches the current pattern
        for token_type, pattern in patterns:
            regex = re.compile(pattern)
            lex_match = regex.match(input_string, pos)

            # For 'LITERAL' tokens use the first capturing group, all other patterns use the entire matched string
            if lex_match:
                value = lex_match.group(0)

                # Find whitespaces but don't add to the list -> less work later on
                if token_type != 'WHITESPACE':
                    if token_type == 'LITERAL':
                        # Strip the double quotes from the literal
                        value = value[1:-1]
                        # Remove escape characters before inner quotes
                        value = re.sub(r'\\"', '"', value)
                    tokens.append((token_type, value))

                pos = lex_match.end()
                break

        # If user enters something not part of Lexer language give error message showing error location
        if not lex_match:
            raise ValueError(f"Unexpected token entered at position {pos}: '{input_string[pos]}'. Try input again")
    return tokens


# Function to get user input. Statements (input with a ';' not in quotes) are found and analysed one at a time in
# the lexer function.
def get_user_input():
    concat_input = ""

    # Getting input. Allow users to enter input over multiple lines.
    while True:
        user_input = input()
        concat_input += user_input + '\n'

        # if current line has odd number of "s then are within a literal, otherwise are outside
        if concat_input.count('"') % 2 == 1:
            in_literal = True
        else:
            in_literal = False

        # If not in a string literal, look for ';' to signify end of statement
        if not in_literal:
            end_matches = [match.end() for match in re.finditer(r';(?=(?:[^"]*"[^"]*")*[^"]*$)', concat_input)]

            # For each semicolon found, process the statement
            for end_pos in end_matches:
                input_to_process = concat_input[:end_pos]   # stores the string before the ';'
                concat_input = concat_input[end_pos + 1:]   # updates so the above won't be analyzed again

                # Each statement is passed to the lexer, resulting in a list of tokens, or an invalid token error
                try:
                    matches = lexer(input_to_process)
                    parser = Parser(matches)
                    parser.parse()

                # if lexer finds invalid token then will raise a ValueError which is then printed here.
                except ValueError as e:
                    print("ERROR:", e)


# The Parser class is used to check the syntax of statements to ensure they match rules of the language
class Parser:

    # Constructor. Stores lexer tokens, variables track the current tuple and index of next tuple
    def __init__(self, lex_tokens):
        self.tokens = lex_tokens
        self.currToken = None
        self.currIndex = 0

    # Method checking if current token matches the expected token. If not, give error indicating what token should be
    def valid_match(self, expected_token):
        if self.currToken[0] == expected_token:
            self.next_token()                   # moves to next token (consumes current token)
        else:
            print(f'Expected {expected_token} but got a token {self.currToken[0]} with value "{self.currToken[1]}"')

    # Method to move onto the next token in the list
    def next_token(self):
        # check for out of bounds error, then index ino the tokens list to get the next tuple
        if self.currIndex < len(self.tokens):
            self.currToken = self.tokens[self.currIndex]
            self.currIndex += 1
        else:
            self.currToken = None

    # Method to start the parsing process
    def parse(self):
        self.statement()

    # Method to identify statement type, and check against its syntax rules
    def statement(self):

        # Get the first tuple (constructor sets currToken to None) and extract token type. Create "Interpreter" object
        self.next_token()
        token = self.currToken[0]
        interpreter = Interpreter(self.tokens)

        # APPEND and SET both follow order:      append/set -> id -> expression -> end
        if token == "APPEND" or token == "SET":
            self.next_token()
            self.valid_match('ID')
            expr_start = self.currIndex - 1     # holds position of expression start

            # After 'ID' should be a valid expression. If not give an error, otherwise should be followed by 'END'
            if self.expression() is False:
                print("ERROR: Instruction has invalid expression. Expressions follow format:   'value {+ value}'")
            else:
                expr_end = self.currIndex - 1    # index for the end of the expression
                self.valid_match('END')
                if token == "APPEND":
                    interpreter.do_append(expr_start, expr_end)
                else:
                    interpreter.do_set(expr_start, expr_end)

        # LIST follows order:           list -> end
        elif token == "LIST":
            self.next_token()
            self.valid_match('END')
            interpreter.list_vars()

        # EXIT follows order:           exit -> end
        elif token == "EXIT":
            self.next_token()
            self.valid_match('END')
            exit()

        # REVERSE follows order:        reverse -> id -> end
        elif token == "REVERSE":
            self.next_token()
            self.valid_match("ID")
            self.valid_match("END")
            interpreter.reverse()

        # Grouped the 4 print statements as have same order:    print/words/length/count -> expression -> end
        elif 'PRINT' in token:
            self.next_token()
            expr_start = self.currIndex - 1
            if self.expression() is False:
                print("ERROR: Instruction has invalid expression. Expressions follow format:  'value {+ value}'")
            else:
                expr_end = self.currIndex - 1
                self.valid_match('END')
                interpreter.expr_print(expr_start, expr_end)

        # This runs if the lexer token/s is/are valid but don't match a valid statement type, (eg ';' by itself)
        else:
            values = ' '.join([token[1] for token in self.tokens])
            print("ERROR: Invalid Input. This is not a recognised statement:    ", values)

    # Check if from the current token to the 'END' token meets expression criteria:     value {+ value}
    def expression(self):
        # track amount of '+' and 'values'. Valid expressions ALWAYS have one more 'value' than '+'
        value_count = 0
        plus_count = 0

        # check if the first token to be assessed is a value, if not then cannot be a valid expression
        if self.isvalue():
            value_count += 1
            valid_expression = True
            self.next_token()
        else:
            valid_expression = False

        # while expression follows the 'expression criteria' keep checking tokens
        while valid_expression:

            # if find an 'END' token, then a valid expression should have 1 more value than '+' tokens
            if self.currToken[0] == "END" and (value_count - plus_count == 1):
                valid_expression = True
                break                   # don't consume the 'END' token, but exit the loop
            else:
                valid_expression = False

            # If the current token is a 'PLUS' token, then it should only be followed by a value
            if self.currToken[0] == "PLUS":
                self.next_token()
                plus_count += 1

                # If the next token is a value then repeat the loop, if not then is an invalid expression
                if self.isvalue():
                    valid_expression = True
                    value_count += 1
                    self.next_token()
                else:
                    valid_expression = False

        return valid_expression

    # helper method to see if the current token is a 'value'
    def isvalue(self):
        if self.currToken[0] == "ID" or self.currToken[0] == "CONSTANT" or self.currToken[0] == "LITERAL":
            return True
        else:
            return False


# The Interpreter class used to perform the relevant statement actions.
class Interpreter:
    # Class variable. Allows all instances of the Interpreter class to use the same symbol table
    symbol_table = []

    # Constructor. Store the set of tokens-value tuples for current statement
    def __init__(self, tokens):
        self.tokens = tokens

    # Method to append an expression onto an EXISTING variable
    def do_append(self, expr_start, expr_end):
        # extract the variable name, evaluate the expression, and attempt to find the var in symbol table
        id_token = self.tokens[1]       # get the second tuple as first is 'APPEND'
        var_name = id_token[1]
        evaluated_expr = self.eval_expression(expr_start, expr_end)
        record = self.get_table_record(var_name)

        # if variable name is not in table or evaluated expression is invalid, give error. Else update the value
        if record is not None:
            if evaluated_expr is not None:
                updated_value = record[1] + evaluated_expr
                index = Interpreter.symbol_table.index(record)
                Interpreter.symbol_table[index] = (var_name, updated_value)
        else:
            print(f'ERROR: the variable name {var_name} does not exist, append failed!')

    # Method to set a new variable, or override an existing one, in the symbol table
    def do_set(self, expr_start, expr_end):
        id_token = self.tokens[1]
        var_name = id_token[1]
        evaluated_expr = self.eval_expression(expr_start, expr_end)
        record = self.get_table_record(var_name)

        # If the evaluated expression is invalid don't do anything. If the variable doesn't exists then add it,
        # otherwise update it with new expression
        if evaluated_expr is not None:
            if record is not None:
                index = Interpreter.symbol_table.index(record)
                Interpreter.symbol_table[index] = (var_name, evaluated_expr)
            else:
                Interpreter.symbol_table.append((var_name, evaluated_expr))

    # Reverse by using regex to split words at whitespace or punctuation, and update value in table
    def reverse(self):
        id_token = self.tokens[1]
        var_name = id_token[1]
        record = self.get_table_record(var_name)

        if record is not None:
            # regex will find any words (based off assignment specs) to. REMOVES NON-WORD PUNCTUATION.
            words = re.findall(r"'?[a-zA-Z0-9]+(?:['-][a-zA-Z0-9]+)*'?", record[1])
            reversed_value = ' '.join(words[::-1])
            index = Interpreter.symbol_table.index(record)
            Interpreter.symbol_table[index] = (var_name, reversed_value)
        else:
            print(f'ERROR: the variable {var_name} does not exist. Reverse failed!')

    # Simply print out each variable and its value in the symbol table
    def list_vars(self):
        table_count = len(Interpreter.symbol_table)
        print(f'Identifier List ({table_count}):')
        for var_name, var_value in Interpreter.symbol_table:
            print(f'{var_name} : {var_value}')

    # Method to handle all of the print functions
    def expr_print(self, start, end):
        # find particular print function to use, evaluate expression, regex to split words at whitespace or punctuation
        token = self.tokens[0]
        token_type = token[0]
        evaluated_expr = self.eval_expression(start, end)

        if evaluated_expr is not None:
            # words may start and end with a '. Words contain at least 1 alphanumeric char, and may have a - or a '
            # between chars
            words = re.findall(r"'?[a-zA-Z0-9]+(?:['-][a-zA-Z0-9]+)*'?", evaluated_expr)
            if token_type == "PRINT":
                print(evaluated_expr)
            elif token_type == "PRINTLENGTH":
                print(f'Length:  {len(evaluated_expr)}')
            elif token_type == "PRINTWORDS":
                print("Words are:")
                for word in words:
                    print(word)
            elif token_type == "PRINTWORDCOUNT":
                print(f'Wordcount is: {len(words)}')
        else:
            print("Cannot print an invalid or non-exsistent expression")

    # Method to find symbol table record. If record doesn't exist return None
    def get_table_record(self, target_var):
        for record in Interpreter.symbol_table:
            if record[0] == target_var:
                return record
        return None

    # Evaluate an expression by concatenating 'values' and return result
    def eval_expression(self, start, end):
        concat_str = ""

        # loop through the tokens and concatenate their values. 'end + 1' to include end itself
        for i in range(start, end + 1):
            token, value = self.tokens[i]
            if token == 'ID':
                record = self.get_table_record(value)
                if record is not None:
                    id_value = record[1]       # extract the value
                    concat_str += id_value
                else:
                    print(f'ERROR: the variable {value} does not exist')
                    return None         # if variable doesn't exist then can't evaluate the expression
            elif token == 'LITERAL':
                concat_str += value
            elif token == 'CONSTANT':
                if value == 'SPACE':
                    concat_str += ' '
                elif value == 'TAB':
                    concat_str += "\t"
                else:
                    concat_str += "\n"
            elif token == 'PLUS':
                continue            # ignore any 'PLUS' tokens

        return concat_str


# Main program
def main():
    print("-----------------------------------------")
    print("A Simple Parser/Interpreter")
    print("Myles Stubbs")
    print("-----------------------------------------")
    get_user_input()


if __name__ == "__main__":
    main()
