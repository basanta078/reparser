#!/usr/bin/python

import sys
from h2 import * 

from ply import lex

tokens = (
	'UNION',
	'CLOSURE',
	'CHAR',
	'LPAREN',
	'RPAREN'
)

t_ignore = ' \t'
#t_CONCAT = r''
t_UNION	= r'\|'
t_CLOSURE = r'\*'
t_CHAR = r'[a-z]'
t_LPAREN = r'\('
t_RPAREN = r'\)'

def t_newline( t ) :
	r'\n+'
	t.lexer.lineno += len(t.value)

def t_error( t ):
	print "Illegal character '%s' on line %d" % (t.value[0], t.lexer.lineno )
	t.lexer.skip(1)

lex.lex()


import ply.yacc as yacc



def p_program( p ) :
	'program : union_list'
	global index
	out = "{}.dot".format(index)
	output = open(out, 'w')
	print >> output, p[1].dotGenerator()
	output.close()

def p_union_list( p ) :
	'''union_list : union_list UNION concat_list
		| concat_list'''
	if len(p) == 2 :
		p[0] = p[1]
	else :
		p[1].unionFsm(p[3])
		p[0] = p[1]

	#for i in p :
	#	print "union" , i

def p_concat_list( p ) :
	'''concat_list : concat_list char_closure
		| char_closure'''
	if len(p) == 2:
		p[0] = p[1]
	else : 
		p[1].concatFsm(p[2])
		p[0] = p[1]
	#for i in p: 
	#	print "concat" , i

def p_char_closure( p ) :
	'''char_closure : char CLOSURE 
		| char'''
	if len(p) == 2 :
		p[0] = p[1]
	else : 
		p[1].closureFsm()
		p[0] = p[1]
	#for i in p: 
	#	print "char" , i

def p_char( p ):
	'''char : CHAR 
		| LPAREN union_list RPAREN'''
	if len(p) == 2 :
		p[0] = createfsm(p[1])
	else : 
		p[0] = p[2]
	#for i in p: 
	#	print "c", i 


def p_error( p ) :
	print "Syntax error ", str( p)
	sys.exit(2)


yacc.yacc()

def main( arg=sys.argv ) :

                # Now, this lexer actually takes a string; it doesn't (that I yet know)                # read from a file.  So, you can parse the file as you like, and feed it
                # to the lexer.

        # we're going to read a line at a time from stdin
	global index
        index = 0

        line = sys.stdin.readline() 
	while line :
		index += 1
                '''lex.input( line )

                line_cnt += 1
                print "\nLine #", line_cnt

                        # attempt to get that first token
                tok = lex.token()
                while tok :
                        print tok
                        tok = lex.token()
		'''
		yacc.parse(line)
                line = sys.stdin.readline()

                # NOTE:  tok is an instance of LexToken.  Has these attributes:
                #   type - the type, from the 'tokens' list, assigned by magic
                #   value - the string that matched, unless you did something
                #   lineno - the line # (see t_newline())
                #   lexpos - the position of the character, from the beginning


if __name__ == '__main__' :
        main()

