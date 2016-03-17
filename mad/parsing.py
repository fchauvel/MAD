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

from mad.ast import *


reserved = {
    "client": "CLIENT",
    "every": "EVERY",
    "FIFO":  "FIFO",
    "invoke": "INVOKE",
    "LIFO": "LIFO",
    "operation": "OPERATION",
    "queue": "QUEUE",
    "query": "QUERY",
    "service": "SERVICE",
    "settings": "SETTINGS",
    "think": "THINK",
}

# List of token names.   This is always required
tokens = [  "CLOSE_BRACKET",
            "CLOSE_CURLY_BRACKET",
            "COLON",
            "COMMA",
            "IDENTIFIER",
            "OPEN_BRACKET",
            "OPEN_CURLY_BRACKET",
            "NUMBER",
            "SLASH"] + list(reserved.values())

t_CLOSE_BRACKET = r"\)"
t_CLOSE_CURLY_BRACKET = r"\}"
t_COLON = r":"
t_COMMA = r","
t_OPEN_BRACKET = r"\("
t_OPEN_CURLY_BRACKET = r"\{"
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
    t.lexer.lineno += len(t.value)


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
    define_service : SERVICE IDENTIFIER COLON settings operation_list
                   | SERVICE IDENTIFIER COLON operation_list
    """
    if len(p) == 6:
        body = p[4] + p[5]
    else:
        body = p[4]
    p[0] = DefineService(p[2], body)


def p_settings(p):
    """
    settings : SETTINGS COLON setting_list
    """
    p[0] = p[3]


def p_setting_list(p):
    """
    setting_list : setting setting_list
                 | setting
    """
    if len(p) == 3:
        p[0] = p[1].merged_with(p[2])
    elif len(p) == 2:
        p[0] = p[1]
    else:
        raise RuntimeError("Invalid production rules 'p_setting_list'")


def p_setting(p):
    """
    setting : queue
    """
    p[0] = p[1]


def p_queue(p):
    """
    queue : QUEUE COLON LIFO
          | QUEUE COLON FIFO
    """
    if p[3] == "LIFO":
        p[0] = Settings(queue=LIFO())
    elif p[3] == "FIFO":
        p[0] = Settings(queue=FIFO())
    else:
        raise RuntimeError("Queue discipline '%s' is not supported!" % p[1])


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
    define_client : CLIENT IDENTIFIER COLON EVERY NUMBER COLON action_list
    """
    p[0] = DefineClientStub(p[2], int(p[5]), p[7])


def p_define_operation(p):
    """
    define_operation : OPERATION IDENTIFIER COLON action_list
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
    """
    p[0] = p[1]


def p_think(p):
    """
    think : THINK NUMBER
    """
    p[0] = Think(int(p[2]))


def p_query(p):
    """
    query : QUERY IDENTIFIER SLASH IDENTIFIER
    """
    p[0] = Query(p[2], p[4])


def p_invoke(p):
    """
    invoke : INVOKE IDENTIFIER SLASH IDENTIFIER
    """
    p[0] = Trigger(p[2], p[4])


def p_error(t):
    print("Syntax error at '%s'" % t.value)


class Source:

    def read(self, location):
        raise NotImplementedError("Source::read is not yet implemented")


class Parser:

    def __init__(self, source):
        self.source = source

    def parse(self, location, entry_rule="unit"):
        text = self.source.read(location)
        #parser = yacc.yacc(start=entry_rule, errorlog=yacc.NullLogger())
        parser = yacc.yacc(start=entry_rule)
        return parser.parse(lexer=lexer, input=text)


