#!/usr/bin/python

#recursive descent parser for RE parser assignment
p1 = __import__('h2')
import sys
M_LEVEL = 0

def mprint( l, s ) :
	if l >= M_LEVEL :
		sys.stderr.write( s)

def error() :
	print "parse error:", token
	sys.exit(1)

def nextToken() :
	#read next token, store in global token
	global token
	global line
	token = line[0]
	line = line[1:]

	if token == ' ' : 
		nextToken()

	mprint(2, "nextToken: '%s'\n" %token )

def match( t ) :
	global token
	if token == t : nextToken()
	else : error()

def union() :
	global token
	result = concat()
	while token == '|' :
		match('|' )
		result.unionFsm(concat())
	return result

def concat() :
	global token
	result = char()
	

	while token != '|' and token != '\n':
		if token == ')' and paren > 0 : # parenthesis mismatch
			return result
		result.concatFsm(char())
	
	return result

def char() :
	global token
	global paren
	result = ""
	if token.isalpha() :
		result = p1.createfsm(token)
		match(token)
		if token == '*' :
			# do something with the result
			print (result, "did a closure")
			result.closureFsm()
			match('*')
		return result
	elif token == '(' :
		paren = paren + 1
		match('(')
		result = union()
		#print token
		#after it is done the next token should be )
		match(')')
		paren = paren - 1
		
		#check if the next token is *
		if token == '*' :
			#do something with the whole result
			#print(result , "did a group closure")
			result.closureFsm()
			match('*')
	elif token == ')' :
		error()	
	else :
		print 'not alpha' 
		error()
	

	return result

def re() :
	global token
	global paren 

	paren = 0
	result = union()
	return result

def parse() :
	nextToken()
	return re()

def main() :
	global line
	i = 0
	line = sys.stdin.readline()
	while line: 
		i = i + 1
		result = parse()
		out = "{}.dot".format(i)
		output = open(out, 'w')
		print >> output, result.dotGenerator()
		output.close()
		line = sys.stdin.readline()
		
	return 0

if __name__ == '__main__' :
	main()
