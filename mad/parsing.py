#!/usr/bin/env python

#
# This file is part of MAD.
#
# MAD is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MAD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MAD.  If not, see <http://www.gnu.org/licenses/>.
#

import ply.lex as lex
import ply.yacc as yacc

from mad.ast.settings import *
from mad.ast.definitions import *
from mad.ast.actions import *


reserved = {
    "autoscaling": "AUTOSCALING",
    "client": "CLIENT",
    "delay": "DELAY",
    "every": "EVERY",
    "fail": "FAIL",
    "FIFO":  "FIFO",
    "ignore": "IGNORE",
    "invoke": "INVOKE",
    "LIFO": "LIFO",
    "limit": "LIMIT",
    "limits": "LIMITS",
    "none": "NONE",
    "operation": "OPERATION",
    "period": "PERIOD",
    "priority": "PRIORITY",
    "queue": "QUEUE",
    "query": "QUERY",
    "retry": "RETRY",
    "service": "SERVICE",
    "settings": "SETTINGS",
    "tail-drop": "TAIL_DROP",
    "think": "THINK",
    "throttling": "THROTTLING",
    "timeout": "TIMEOUT"
}

# List of token names.   This is always required
tokens = [  "CLOSE_BRACKET",
            "CLOSE_CURLY_BRACKET",
            "CLOSE_SQUARE_BRACKET",
            "COLON",
            "COMMA",
            "IDENTIFIER",
            "OPEN_BRACKET",
            "OPEN_CURLY_BRACKET",
            "OPEN_SQUARE_BRACKET",
            "NUMBER",
            "REAL",
            "SLASH"] + list(reserved.values())

t_CLOSE_BRACKET = r"\)"
t_CLOSE_CURLY_BRACKET = r"\}"
t_CLOSE_SQUARE_BRACKET = r"\]"
t_COLON = r":"
t_COMMA = r","
t_OPEN_BRACKET = r"\("
t_OPEN_CURLY_BRACKET = r"\{"
t_OPEN_SQUARE_BRACKET = r"\["
t_SLASH = r"/"


def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_\-]+'
    t.type = reserved.get(t.value,'IDENTIFIER')    # Check for reserved words
    return t

def t_NUMBER(t):
    r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?'
    return t

def t_newline(t):
    # Define a rule so we can track line numbers
    r'\n+'
    t.lexer.lineno += 1


def t_COMMENT(t):
    r'\#.*'
    pass


# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t'


def t_error(t):
    # Error handling rule
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()


# -----------------------------
# Parsing rules
def p_unit(p):
    """
    unit : definition_list
    """
    p[0] = p[1]


def p_definition_list(p):
    """
    definition_list : definition definition_list
                    | definition
    """
    if len(p) == 3:
        p[0] = p[1] + p[2]
    elif len(p) == 2:
        p[0] = p[1]
    else:
        raise RuntimeError("Invalid production rules 'p_action_list'")


def p_definition(p):
    """
    definition : define_service
                | define_client
    """
    p[0] = p[1]


def p_define_service(p):
    """
    define_service : SERVICE IDENTIFIER OPEN_CURLY_BRACKET settings operation_list CLOSE_CURLY_BRACKET
                   | SERVICE IDENTIFIER OPEN_CURLY_BRACKET operation_list CLOSE_CURLY_BRACKET
    """
    if len(p) == 7:
        body = p[4] + p[5]
    else:
        body = p[4]
    p[0] = DefineService(p[2], body)


def p_settings(p):
    """
    settings : SETTINGS OPEN_CURLY_BRACKET setting_list CLOSE_CURLY_BRACKET
    """
    p[0] = Settings(**p[3])


def p_setting_list(p):
    """
    setting_list : setting setting_list
                 | setting
    """
    if len(p) == 3:
        p[0] = merge_map(p[1], p[2])
    elif len(p) == 2:
        p[0] = p[1]
    else:
        raise RuntimeError("Invalid production rules 'p_setting_list'")


def p_setting(p):
    """
    setting : queue
            | autoscaling
            | throttling
    """
    p[0] = p[1]


def p_queue(p):
    """
    queue : QUEUE COLON LIFO
          | QUEUE COLON FIFO
    """
    if p[3] == "LIFO":
        p[0] = {"queue": LIFO()}

    elif p[3] == "FIFO":
        p[0] = {"queue": FIFO()}

    else:
        raise RuntimeError("Queue discipline '%s' is not supported!" % p[1])


def p_throttling(p):
    """
    throttling : THROTTLING COLON NONE
               | THROTTLING COLON TAIL_DROP OPEN_BRACKET NUMBER CLOSE_BRACKET
    """
    throttling = NoThrottlingSettings()
    if len(p) == 7:
        throttling = TailDropSettings(int(p[5]))
    p[0] = {"throttling": throttling}


def p_autoscaling(p):
    """
    autoscaling : AUTOSCALING OPEN_CURLY_BRACKET autoscaling_setting_list CLOSE_CURLY_BRACKET
    """
    p[0] = {"autoscaling": Autoscaling(**p[3])}


def p_autoscaling_setting_list(p):
    """
    autoscaling_setting_list : autoscaling_setting autoscaling_setting_list
                             | autoscaling_setting
    """
    if len(p) == 3:
        p[0] = merge_map(p[1], p[2])
    elif len(p) == 2:
        p[0] = p[1]
    else:
        raise RuntimeError("Invalid production in 'autoscaling_setting_list'")


def p_autoscaling_setting(p):
    """
    autoscaling_setting : PERIOD COLON NUMBER
                        | LIMITS COLON OPEN_SQUARE_BRACKET NUMBER COMMA NUMBER CLOSE_SQUARE_BRACKET
    """
    if len(p) == 8:
        p[0] = {"limits": (int(p[4]), int(p[6]))}
    elif len(p) == 4:
        p[0] = {"period": int(p[3])}
    else:
        raise RuntimeError("Invalid product in 'autoscaling_setting'")


def p_operation_list(p):
    """
    operation_list : define_operation operation_list
                   | define_operation
    """
    if len(p) == 3:
        p[0] = p[1] + p[2]
    elif len(p) == 2:
        p[0] = p[1]
    else:
        raise RuntimeError("Invalid production rules 'p_operation_list'")


def p_define_client(p):
    """
    define_client : CLIENT IDENTIFIER OPEN_CURLY_BRACKET EVERY NUMBER OPEN_CURLY_BRACKET action_list CLOSE_CURLY_BRACKET CLOSE_CURLY_BRACKET
    """
    p[0] = DefineClientStub(p[2], int(p[5]), p[7])


def p_define_operation(p):
    """
    define_operation : OPERATION IDENTIFIER OPEN_CURLY_BRACKET action_list CLOSE_CURLY_BRACKET
    """
    p[0] = DefineOperation(p[2], p[4])


def p_action_list(p):
    """
    action_list : action action_list
                | action
    """
    if len(p) == 3:
        p[0] = p[1] + p[2]
    elif len(p) == 2:
        p[0] = p[1]
    else:
        raise RuntimeError("Invalid production rules 'p_action_list'")


def p_action(p):
    """
    action : invoke
           | query
           | think
           | fail
           | retry
           | ignore
    """
    p[0] = p[1]


def p_think(p):
    """
    think : THINK NUMBER
    """
    p[0] = Think(int(p[2]))


def p_fail(p):
    """
    fail : FAIL NUMBER
         | FAIL
    """
    if len(p) > 2:
        p[0] = Fail(float(p[2]))
    else:
        p[0] = Fail()

def p_query(p):
    """
    query : QUERY IDENTIFIER SLASH IDENTIFIER
          | QUERY IDENTIFIER SLASH IDENTIFIER OPEN_CURLY_BRACKET query_option_list CLOSE_CURLY_BRACKET
    """
    parameters = {"service": p[2], "operation": p[4]}
    if len(p) > 5:
        parameters = merge_map(parameters, p[6])
    p[0] = Query(**parameters)


def p_query_option_list(p):
    """
    query_option_list : query_option COMMA query_option_list
                      | query_option
    """
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        p[0] = merge_map(p[1], p[3])
    else:
        raise RuntimeError("Invalid product rules for 'query_option_list'")


def p_query_option(p):
    """
    query_option : timeout
                 | priority
    """
    p[0] = p[1]


def p_timeout(p):
    """
    timeout : TIMEOUT COLON NUMBER
    """
    p[0] = {"timeout": int(p[3])}


def p_priority(p):
    """
    priority : PRIORITY COLON NUMBER
    """
    p[0] = {"priority": int(p[3])}


def p_invoke(p):
    """
    invoke : INVOKE IDENTIFIER SLASH IDENTIFIER
           | INVOKE IDENTIFIER SLASH IDENTIFIER OPEN_CURLY_BRACKET PRIORITY COLON NUMBER CLOSE_CURLY_BRACKET
    """
    priority = None
    if len(p) > 5:
        priority = int(p[8])
    p[0] = Trigger(p[2], p[4], priority)


def p_retry(p):
    """
    retry : RETRY OPEN_CURLY_BRACKET action_list CLOSE_CURLY_BRACKET
          | RETRY OPEN_BRACKET retry_option_list CLOSE_BRACKET OPEN_CURLY_BRACKET action_list CLOSE_CURLY_BRACKET
    """
    if len(p) == 5:
        p[0] = Retry(p[3])
    elif len(p) == 8:
        p[0] = Retry(p[6], **p[3])
    else:
        raise RuntimeError("Invalid product rules for 'retry_option_list'")


def p_retry_option_list(p):
    """
    retry_option_list : retry_option COMMA retry_option_list
                      | retry_option
    """
    if len(p) == 4:
        p[0] = merge_map(p[1], p[3])
    elif len(p) == 2:
        p[0] = p[1]
    else:
        raise RuntimeError("Invalid production in 'retry_option_list'")


def p_retry_option(p):
    """
    retry_option : LIMIT COLON NUMBER
                 | DELAY COLON IDENTIFIER OPEN_BRACKET NUMBER CLOSE_BRACKET
    """
    if len(p) == 4:
        p[0] = {"limit": int(p[3]) }
    elif len(p) == 7:
        p[0] = {"delay": Delay(int(p[5]), p[3])}
    else:
        raise RuntimeError("Invalid production in 'retry_option'")


def p_ignore(p):
    """
    ignore : IGNORE OPEN_CURLY_BRACKET action_list CLOSE_CURLY_BRACKET
    """
    p[0] = IgnoreError(p[3])


def p_error(t):
    raise MADSyntaxError((t.lineno, t.lexpos), t.value)


def merge_map(map_A, map_B):
    tmp = map_A.copy()
    tmp.update(map_B)
    return tmp


class MADSyntaxError(BaseException):

    def __init__(self, position, hint):
        self.position = position
        self.hint = hint

    @property
    def line_number(self):
        return self.position[0]

    def __repr__(self):
        return "Syntax error at line {line:d}, around '{hint}'.".format(
            line=self.position[0],
            hint=self.hint)


class Parser:

    def __init__(self, file_system, root_file):
        self.root_file = root_file
        self.file_system = file_system

    def parse(self, entry_rule="unit", logger=yacc.NullLogger()):
        lexer.lineno = 1
        text = self._content()
        parser = yacc.yacc(start=entry_rule, errorlog=logger)
        return parser.parse(lexer=lexer, input=text)

    def _content(self):
        lines = self.file_system.open_input_stream(self.root_file).readlines()
        return "\n".join(lines)

