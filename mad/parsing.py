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

from mad.ast import Architecture, Service, Operation, Action, RequestAction, TriggerAction, UtilisationRule, Retry

reserved = {
    "architecture": "ARCHITECTURE",
    "autoscaling": "AUTOSCALING",
    "CoDel": "CODEL",
    "configuration": "CONFIGURATION",
    "delay": "DELAY",
    "fail": "FAIL",
    "FIFO": "FIFO",
    "LIFO": "LIFO",
    "limit": "LIMIT",
    "on-error": "ON_ERROR",
    "operation": "OPERATION",
    "queue": "QUEUE",
    "RED": "RED",
    "request": "REQUEST",
    "retry": "RETRY",
    "resources": "RESOURCES",
    "rules": "RULES",
    "scaled": "SCALED",
    "service": "SERVICE",
    "shared": "SHARED",
    "taildrop": "TAIL_DROP",
    "throttling": "THROTTLING",
    "timeout": "TIMEOUT",
    "trigger": "TRIGGER",
    "utilisation": "UTILISATION",
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


def p_architecture(p):
    """architecture : ARCHITECTURE IDENTIFIER COLON service_list"""
    p[0] = Architecture(p[2])


def p_service_list(p):
    """
    service_list : service service_list
                 | service
    """
    p[0] = aggregate_list(p, "service_list")


def p_service(p):
    """
    service : SERVICE IDENTIFIER COLON operation_list
            | SERVICE IDENTIFIER COLON configuration operation_list
    """
    if len(p) == 5:
        p[0] = Service(p[2], p[4])
    else:
        p[0] = Service(p[2], p[5])


def p_configuration(p):
    """
    configuration : CONFIGURATION COLON setting_list
    """
    p[0] = p[3]


def p_setting_list(p):
    """
    setting_list : setting setting_list
                 | setting
    """
    p[0] = aggregate_list(p, "setting_list")


def p_setting(p):
    """
    setting : queue
            | resources
            | throttling
            | autoscaling
    """
    p[0] = p[1]


def p_queue(p):
    """
    queue : QUEUE COLON LIFO
            | QUEUE COLON FIFO
    """
    if p[3] == "LIFO":
        p[0] = ("queue", "LIFO")
    else:
        p[0] = ("queue", "FIFO")


def p_resources(p):
    """
    resources : RESOURCES COLON SHARED
              | RESOURCES COLON SCALED
    """
    p[0] = ("resources", p[3])


def p_throttling(p):
    """
    throttling : THROTTLING COLON TAIL_DROP
               | THROTTLING COLON RED
               | THROTTLING COLON CODEL
    """
    p[0] = ("throttling", p[3])


def p_autoscaling(p):
    """
    autoscaling : AUTOSCALING COLON RULES OPEN_BRACKET UTILISATION COMMA NUMBER COMMA NUMBER COMMA NUMBER CLOSE_BRACKET
    """
    p[0] = UtilisationRule(float(p[7]), float(p[9]), float(p[11]))


def p_operation_list(p):
    """
    operation_list : operation operation_list
                   | operation
    """
    p[0] = aggregate_list(p, "operation_list")


def p_operation(p):
    """
    operation : OPERATION IDENTIFIER COLON action_list
    """
    p[0] = Operation(p[2], p[4])


def p_action_list(p):
    """
    action_list : action action_list
                | action
    """
    p[0] = aggregate_list(p, "action_list")


def p_action(p):
    """
    action : trigger
           | request
    """
    p[0] = p[1]


def p_trigger(p):
    """
    trigger : TRIGGER IDENTIFIER SLASH IDENTIFIER
    """
    p[0] = TriggerAction(p[2], p[4])


def p_request(p):
    """
    request : REQUEST IDENTIFIER SLASH IDENTIFIER
            | REQUEST IDENTIFIER SLASH IDENTIFIER OPEN_CURLY_BRACKET option_list CLOSE_CURLY_BRACKET
    """
    if len(p) > 5:
        options = dict(p[6])

        timeout = Action.DEFAULT_TIMEOUT
        if "timeout" in options:
            timeout = options["timeout"]

        p[0] = RequestAction(p[2], p[4], timeout)
    else:
        p[0] = RequestAction(p[2], p[4])


def p_option_list(p):
    """
    option_list : option COMMA option_list
                | option
    """
    p[0] = aggregate_list(p, "option_list", separator = True)


def p_option(p):
    """
    option : timeout
    """
    p[0] = p[1]


def p_timeout(p):
    """
    timeout : TIMEOUT COLON NUMBER
    """
    p[0] = ("timeout", float(p[3]))


def p_on_error(p):
    """
    on_error : ON_ERROR COLON error_strategy
    """
    p[0] = ("on-error", p[3])


def p_error_strategy(p):
    """
    error_strategy : FAIL
                   | RETRY OPEN_BRACKET LIMIT COLON NUMBER COMMA DELAY COLON NUMBER CLOSE_BRACKET
    """
    if p[1] == "fail":
        p[0] = "FAIL"
    else:
        p[0] = Retry(float(p[5]), float(p[9]))


def p_error(t):
    print("Syntax error at '%s'" % t.value)


def aggregate_list(p, rule_name, separator = False):
    tail = 2 if not separator else 3
    if len(p) == tail + 1:
        return [p[1]] + p[tail]
    elif len(p) == 2:
        return [p[1]]
    else:
        raise RuntimeError("Invalid production in rule '%s'" % rule_name)


class Parser:
    """
    Encapsulate the procedural code generated by PLY into a property class
    """

    def parse(self, text, entry_rule="architecture"):
        parser = yacc.yacc(start=entry_rule)
        return parser.parse(text)


