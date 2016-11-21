from __future__ import print_function

# Librerias utilizadas
import numpy as np # Sirve para utilizar matrices y cubos
import io #Input Output
import re # Regular expresions

tokens = [
  	'PLUS','MINUS', 'MULTIPLY','DIVIDE','SEMICOLON','COMA','EQUALS',
    'L_BRACKET','R_BRACKET','L_PARENTHESIS','R_PARENTHESIS', 'L_BRACE', 'R_BRACE',
    'L_THAN','G_THAN', 'LE_THAN', 'GE_THAN', 'DIFFERENT', 'EQUALS_C', 'NOT', 'AND', 'OR',
    'FLT', 'INT','STRNG','CHR',
    'ID', 'AMPERSAND']

reserved = {
	'for' : 'FOR',
	'if' : 'IF',
	'else' : 'ELSE',
	'elif' : 'ELIF',
	'do' : 'DO',
	'while' : 'WHILE',
	'print' : 'PRINT',
	'scan' : 'SCAN',

	# Tipos
	'void' : 'VOID',
	'int' : 'INTEGER',
	'float' : 'FLOAT',
	'bool' : 'BOOLEAN',
	'true' : 'TRUE',
	'false' : 'FALSE',
	'char' : 'CHAR',
	'string' : 'STRING',

	'program' : 'PROGRAM',
	'main' : 'MAIN',
	'global' : 'GLOBAL',
	'func' : 'FUNC',
	'return' : 'RETURN'
}

# Tokens
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_SEMICOLON = r';'
t_COMA = r','
t_EQUALS = r'='

t_L_BRACKET = r'\['
t_R_BRACKET = r'\]'
t_L_PARENTHESIS = r'\('
t_R_PARENTHESIS = r'\)'
t_L_BRACE = r'{'
t_R_BRACE = r'}'

# Operadores booleanos
t_L_THAN = r'<'
t_LE_THAN = r'<='
t_G_THAN = r'>'
t_GE_THAN = r'>='
t_DIFFERENT = r'!='
t_EQUALS_C = r'=='
t_NOT = r'!'
t_AND = r'&&'
t_OR = r'\|\|'

# Operador por referencia
t_AMPERSAND = r'&'

# Tipos de datos
t_FLT = r'[0-9]+\.[0-9]+'
t_INT = r'[0-9]+'
t_CHR = r'\'[^\']\''
t_STRNG = r'\"[^\"]*\"'

# Caracteres a ignorar
t_ignore_NEXTLINE = r'\n'
t_ignore_WHITESPACE = r'\s'
t_ignore_COMMENT = r'\/\/.*'

# Lista de tokens mas los tokens reseverados
tokens = tokens + list(reserved.values())

# Define ID y verifica que no exista en las palabras reservadas
def t_ID(t):
	#r'[a-z]([a-z]|[0-9])*'
	r'([a-z]|[A-Z])\w*'
	t.type = reserved.get(t.value,'ID')
	return t

# VARIABLE - para saber si fue aprobado el codigo del lado del parser
aprobado = 0

# Dir Tabla de func que contiene las tablas de variables
tabla_func = {'global':{'tabla_var':dict()}}

##################### VARIABLES AUX - SEMANTICA #####################
variable_global = 0 # Auxiliar para saber si declaro variables globales o no
nombre_func = '' # Sirve para saber la funcion actual en la que estas trabanajdo
tipo_var = '' # Sirve para saber el tipo en una declaracion de muchas variables
id_funcion_llamada = '' # Sirve para saber el ID que se llamo en factor, para poder utilizarlo en la regla llamafunc caso de que haya llamado una funcion
cont_args = 0 # Sirve para llevar conteo de numero de argumentos de una funcion en una llamada
tipo_arg = '' # Sirve para saber el tipo de un argumento

# Pilas para generar CUADRUPLOS
POper = [] # Sirve para mantener el orden en que se ejecutan las operaciones
POpndo = [] # Sirve para mentener el orden de los operandos
contElifs = 0 # Cuenta los elifs pendientes
PSaltos = [] # Sirve para llevar el control de saltos en ejecucion

# CUADRUPLOS
cuadruplos = np.zeros((1,4)) # Arreglo de cuadruplos
cuadruplos = np.delete(cuadruplos, 0,0)
cuadruplos_str = np.zeros((1,4))
contResCuadruplos = 0

# CUBO SEMANTICO
cuboSemantico = np.zeros((14,5,5)) # Inicializa el cubo con 0s

# ID de operaciones
id_operaciones = {'*':0, '/':1, '+':2, '-':3, '<':4, '>':5, '==':6, '!=':7, '<=':8, '>=':9, '&&':10, '||':11, '!':12, '=':13, 'GOTO':14, 'GOTOF':15, 'GOTOT':16, 'RETURN':17, 'ENDPROC':18, 'ERA':19, 'PRINT':20, 'SCAN':21, 'PARAM':22,'GOSUB':23}
reverse_id_operaciones = ["*", "/", "+", "-", "<", ">", "==", "!=", "<=", ">=" , "&&", "||", "!", "=", 'GOTO', 'GOTOF', 'GOTOT', 'RETURN', 'ENDPROC', 'ERA', 'PRINT', 'SCAN', 'PARAM','GOSUB']
# 1er dim = Operador
# 2da dim = Tipo operando 1
# 3era dim = Tipo oeprando 2

# Dimensiones de tipo de operandos
# 0 = int
# 1 = float
# 2 = char
# 3 = bool
# 4 = string

# tipos de salida:
# error = 0
# int = 1
# float = 2
# char = 3
# bool = 4
# string = 5

#Operador: *
cuboSemantico[0][0][0] =  1
cuboSemantico[0][0][1] =  2
cuboSemantico[0][1][0] =  2
cuboSemantico[0][1][1] =  2

#Operador: /
cuboSemantico[1][0][0] =  1
cuboSemantico[1][0][1] =  2
cuboSemantico[1][1][0] =  2
cuboSemantico[1][1][1] =  2

#Operador: +
cuboSemantico[2][0][0] = 1
cuboSemantico[2][0][1] = 2
cuboSemantico[2][1][0] = 2
cuboSemantico[2][1][1] = 2
cuboSemantico[2][2][2] = 5
cuboSemantico[2][2][4] = 5
cuboSemantico[2][4][2] = 5
cuboSemantico[2][4][4] = 5

#Operador: -
cuboSemantico[3][0][0] = 1
cuboSemantico[3][0][1] = 2
cuboSemantico[3][1][0] = 2
cuboSemantico[3][1][1] = 2

#Operador: <
cuboSemantico[4][0][0] = 4
cuboSemantico[4][0][1] = 4
cuboSemantico[4][1][0] = 4
cuboSemantico[4][1][1] = 4
cuboSemantico[4][2][2] = 4

#Operador: >
cuboSemantico[5][0][0] = 4
cuboSemantico[5][0][1] = 4
cuboSemantico[5][1][0] = 4
cuboSemantico[5][1][1] = 4
cuboSemantico[5][2][2] = 4

#Operador: ==
cuboSemantico[6][0][0] = 4
cuboSemantico[6][0][1] = 4
cuboSemantico[6][1][0] = 4
cuboSemantico[6][1][1] = 4
cuboSemantico[6][2][2] = 4

#Operador: !=
cuboSemantico[7][0][0] = 4
cuboSemantico[7][0][1] = 4
cuboSemantico[7][1][0] = 4
cuboSemantico[7][1][1] = 4
cuboSemantico[7][2][2] = 4

#Operador: <=
cuboSemantico[8][0][0] = 4
cuboSemantico[8][0][1] = 4
cuboSemantico[8][1][0] = 4
cuboSemantico[8][1][1] = 4
cuboSemantico[8][2][2] = 4

#Operador: >=
cuboSemantico[9][0][0] = 4
cuboSemantico[9][0][1] = 4
cuboSemantico[9][1][0] = 4
cuboSemantico[9][1][1] = 4
cuboSemantico[9][2][2] = 4

#Operador: &&
cuboSemantico[10][3][3] = 4

#Operador: ||
cuboSemantico[11][3][3] = 4

#Operador: %
cuboSemantico[12][0][0] = 1

#Operador: =
cuboSemantico[13][0][0] = 1 # int = int genera int
cuboSemantico[13][0][1] = 1 # int = float genera int
#cuboSemantico[13][0][2] = 0 # int = char genera int
cuboSemantico[13][1][0] = 2 # float = int genera float
cuboSemantico[13][1][1] = 2 # float = float genera float
cuboSemantico[13][2][2] = 3 # char = char genera char
cuboSemantico[13][3][3] = 4 # bool = bool genera bool
cuboSemantico[13][4][2] = 5 # string = char genera string
cuboSemantico[13][4][4] = 5 # string = string genera string

# Stack para agregar las variables a su tabla de la funcion correspondiente
stack_var_func = []
####################################################################
################## DIRECCIONES MEMORIA VIRTUAL #############################
#memoria_virtual = {'global': {'int':, 'float:'}, 'local':{}, 'temporal', 'constante'}

# GLOBALES
dir_int_global = 10000
dir_float_global = 11000
dir_char_global = 12000
dir_bool_global = 13000
dir_string_global = 14000

# LOCALES
dir_int_local = 15000
dir_float_local = 16000
dir_char_local = 17000
dir_bool_local = 18000
dir_string_local = 19000

# TEMPORALES
dir_int_temp = 20000
dir_float_temp = 21000
dir_char_temp = 22000
dir_bool_temp = 23000
dir_string_temp = 24000

# CONSTANTES
dir_int_cons = 25000
dir_float_cons = 26000
dir_char_cons = 27000
dir_bool_cons = 28000
dir_string_cons = 29000

####################################################################

# Despliea el error a nivel lexico
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    global aprobado
    aprobado = 1
    #tabla_func = dict()
    t.lexer.skip(1)
    exit()

 # Construye el lexer
import ply.lex as lex
lex.lex()

# Inidica la regla inicial
start = 'program'

# Gramatica Libre de Contexto (Reglas)

def p_program(p):
	'program : PROGRAM seen_program SEMICOLON programaopciones MAIN seen_main bloqueprincipal endproc'

# Define el vacio
def p_e(p):
	'e :'
	pass

def p_programaopciones(p):
	'''programaopciones : opcionesdeclarar programaopciones
		| e'''

def p_opcionesdeclarar(p):
	'''opcionesdeclarar : globalvars
		| declarafuncion'''

def p_declarafuncion(p):
	'declarafuncion : tipofunc FUNC ID seen_funcion L_PARENTHESIS declaraparametros R_PARENTHESIS seen_dir_inicio bloqueprincipal endproc'

def p_tipofunc(p):
	'''tipofunc : tipo
		| VOID'''
	p[0] = p[1] # Asigna el valor del tipo a la regla "tipofunc"

def p_globalvars(p):
	'globalvars : GLOBAL seen_global variables'
	global variable_global
	variable_global = 0 # Una vez declaradas las variables globales apaga la bandera "variable_global"

def p_tipo(p):
	'''tipo : INTEGER
		| FLOAT
		| STRING
		| CHAR
		| BOOLEAN'''
	p[0] = p[1] # Asigna el valor del tipo a la regla "tipo"

def p_listaids(p):
	'listaids : ID seen_declara_variables esarr masids'
	p[0] = p[1]

def p_esarr(p):
	'''esarr : L_BRACKET INT R_BRACKET
		| e'''

def p_masids(p):
	'''masids : COMA listaids
		| e'''

def p_declaramarametros(p):
	'''declaraparametros : tipo ID opcionesdp seen_paso2_def_proc listadp
		| e'''

def p_opcionesdp(p):
	'''opcionesdp : L_BRACKET R_BRACKET
		| e'''

def p_listadp(p):
	'''listadp : COMA declaraparametros
		| e'''

def p_bloque(p):
	'bloque : L_BRACE listaestatutos R_BRACE'

def p_bloqueprincipal(p):
	'bloqueprincipal : L_BRACE listaestatutosprincipal R_BRACE'

def p_listaestatutos(p):
	'''listaestatutos : estatuto listaestatutos
		| e'''

def p_listaestatutosprincipal(p):
	'''listaestatutosprincipal : estatuto listaestatutosprincipal
		| variables listaestatutosprincipal
		| e'''

def p_estatuto(p):
	'''estatuto : asignacion SEMICOLON
		| if
		| escritura
		| scan
		| ciclo
		| llamafunc
		| RETURN exp seen_return SEMICOLON'''

def p_llamafunc(p):
	'llamafunc : ID seen_id_factor seen_llamada_func L_PARENTHESIS listargs R_PARENTHESIS seen_verifica_cant_args gosub SEMICOLON'


# Checar que exista la variable antes del equals
def p_asignacion(p):
	'asignacion : ID opesarr EQUALS seen_equals castono equals_pendiente'

def p_opesarr(p):
	'''opesarr : L_BRACKET exp R_BRACKET
		| e'''

def p_aritmetica(p):
	'aritmetica : term paso5_cuadruplo opexp'

def p_term(p):
	'term : factor paso4_cuadruplo opterm'

def p_factor(p):
	'''factor : ID opidfactor paso1_id_cuadruplo
		| INT paso1_int_cuadruplo
		| FLT paso1_float_cuadruplo
		| TRUE paso1_bool_cuadruplo
		| FALSE paso1_bool_cuadruplo
		| CHR paso1_char_cuadruplo
		| STRNG paso1_string_cuadruplo
		| L_PARENTHESIS paso6_cuadruplo exp R_PARENTHESIS paso7_cuadruplo'''

def p_opidfactor(p):
	'''opidfactor : seen_id_factor L_PARENTHESIS paso6_cuadruplo seen_llamada_func_factor listargs R_PARENTHESIS paso7_cuadruplo seen_verifica_cant_args gosub
		| L_BRACKET exp R_BRACKET
		| e'''
	p[0] = p[1] # Retorna el primer elemento de la regla

def p_listargs(p):
	'''listargs : exp seen_argumento_funcion masargs
		| AMPERSAND ID seen_argumento_ref_funcion masargs
		| e'''

def p_masargs(p):
	'''masargs : COMA listargs
		| e'''

#def p_enviargs(p): # CAMBIAR EN EL DOCS
#	'''enviargs : STRNG seen_arg_string
#		| CHR seen_arg_char
#		| condicion'''
#	p[0] = p[1] # Asigna valor de enviargs

def p_opterm(p):
	'''opterm : MULTIPLY paso2y3_cuadruplos term
		| DIVIDE paso2y3_cuadruplos term
		| e'''

def p_opexp(p):
	'''opexp : PLUS paso2y3_cuadruplos aritmetica
		| MINUS paso2y3_cuadruplos aritmetica
		| e'''

def p_castono(p):
	'''castono : castto L_PARENTHESIS exp R_PARENTHESIS
		| exp'''

def p_castto(p):
	'''castto : STRING
		| CHAR
		| INTEGER
		| FLOAT'''

#def p_castopc(p): # CAMBIAR EN EL DOCS
#	'''castopc : STRNG
#		| CHR
#	 	| exp'''

#def p_asignaopc(p):
#	'''asignaopc : exp
#		| STRNG paso1_string_cuadruplo
#		| CHR paso1_char_cuadruplo'''

def p_exp(p):
	'exp : exp_and if_paso3_cuadruplo listaor'

def p_listaor(p):
	'''listaor : OR if_paso1_cuadruplo exp
		| e'''

def p_exp_and(p):
	'exp_and : opcnegar exp_bcomp if_paso8_cuadruplo if_paso4_cuadruplo listand'

def p_listand(p):
	'''listand : AND if_paso2_cuadruplo exp_and
		| e'''

def p_exp_bcomp(p):
	'exp_bcomp : aritmetica esComp'

def p_esComp(p):
	'''esComp : bexpop if_paso6_cuadruplo aritmetica if_paso7_cuadruplo
		| e'''

def p_opcnegar(p):
	'''opcnegar : NOT if_paso5_cuadruplo
		| e'''


def p_bexpop(p):
	'''bexpop : L_THAN
		| G_THAN
		| EQUALS_C
		| DIFFERENT
		| LE_THAN
		| GE_THAN'''
	p[0] = p[1] # Regresa el valor de bexpop a la regla que la llamo

def p_escritura(p):
	'escritura : PRINT L_PARENTHESIS exp R_PARENTHESIS SEMICOLON seen_print'

def p_scan(p):
	'scan : SCAN L_PARENTHESIS ID R_PARENTHESIS SEMICOLON seen_scan'

def p_variables(p):
	'variables : tipo seen_tipo_var listaids SEMICOLON'

def p_ciclo(p):
	'''ciclo : while
		| dowhile
		| for'''

def p_while(p):
	'while : WHILE while_paso1_codigo L_PARENTHESIS exp while_paso2_codigo R_PARENTHESIS bloque while_paso3_codigo'

def p_dowhile(p):
	'dowhile : DO while_paso1_codigo bloque WHILE L_PARENTHESIS exp R_PARENTHESIS dowhile_paso4_codigo SEMICOLON'

def p_for(p):
	'for : FOR for_paso1_codigo L_PARENTHESIS exp for_paso2_codigo SEMICOLON for_paso3_codigo increment for_paso4_codigo R_PARENTHESIS for_paso6_codigo bloque for_paso5_codigo'

def p_increment(p):
	'increment : asignacion listaincrement'

def p_listaincrement(p):
	'''listaincrement : COMA increment
		| e'''

def p_if(p):
	'if : IF L_PARENTHESIS exp if_paso1_codigo R_PARENTHESIS bloque if_paso2_codigo listaelif else if_paso3_codigo'

def p_listaelif(p):
	'''listaelif : elif listaelif
		| e'''

def p_elif(p):
	'elif : ELIF L_PARENTHESIS exp if_paso1_codigo R_PARENTHESIS bloque if_paso2_codigo'

def p_else(p):
	'''else : ELSE bloque
		| e if_paso4_codigo'''

# Despliega error a nivel sintaxis
def p_error(p):
   	print("Syntax error at '%s'." % p.value)
   	# Cambia la variable a 1, lo cual es que no fue aprobado
   	global aprobado
   	aprobado = 1
   	#tabla_func = dict()
   	exit()

def error_semantico(e, msg):
	print("Error semantico en '%s'. %s" % (e,msg))
	global aprobado

   	aprobado = 1 # Cambia la variable a 1, lo cual es que no fue aprobado
   	#tabla_func = dict()
   	# CHECAR SI PONER EXIT O NO
   	print(tabla_func)
   	exit()

def error_memoria(scope, tipo):
	print("Has alcanzado el limite de memoria para variables '%s' de tipo '%s'.")
	exit()

################### REGLAS SEMANTICA ##################
def p_seen_main(p):
	'seen_main :'
	# p[-1] = MAIN
	# p[-3] = TIPO
	global nombre_func
	global dir_int_global, dir_float_global, dir_char_global, dir_bool_global, dir_string_global

	nombre_func = p[-1]

	if nombre_func in tabla_func:
		error_semantico(nombre_func, "Funcion ya declarada.")
	else:
		tipo = 0
		if p[-3] == 'int':
			tipo = 0
			tabla_func['global']['tabla_var'][nombre_func] = {'tipo':tipo, 'dir_mem':dir_int_global}
			inc_o_valida_dir_mem('g','i')
		elif p[-3] == 'float':
			tipo = 1
			tabla_func['global']['tabla_var'][nombre_func] = {'tipo':tipo, 'dir_mem':dir_float_global}
			inc_o_valida_dir_mem('g','f')
		elif p[-3] == 'char':
			tipo = 2
			tabla_func['global']['tabla_var'][nombre_func] = {'tipo':tipo, 'dir_mem':dir_char_global}
			inc_o_valida_dir_mem('g','c')			
		elif p[-3] == 'bool':
			tipo = 3
			tabla_func['global']['tabla_var'][nombre_func] = {'tipo':tipo, 'dir_mem':dir_bool_global}
			inc_o_valida_dir_mem('g','b')
		elif p[-3] == 'string':
			tipo = 4
			tabla_func['global']['tabla_var'][nombre_func] = {'tipo':tipo, 'dir_mem':dir_string_global}
			inc_o_valida_dir_mem('g','s')

		tabla_func[nombre_func] = {'tipo':tipo, 'dir_inicio':len(cuadruplos), 'dir_variable':0, 'tabla_var':dict(), 'tabla_param':dict()}

		# Rellena el GOTO del inicio del programa que lleva a MAIN
		cuadruplos[0][3] = len(cuadruplos)

def p_seen_funcion(p):
	'seen_funcion :'
	# p[-3] = tipo
	# p[-1] = ID
	global nombre_func
	global dir_int_global, dir_float_global, dir_char_global, dir_bool_global, dir_string_global

	nombre_func = p[-1]

	if nombre_func in tabla_func or nombre_func in tabla_func['global']['tabla_var']:
		error_semantico(nombre_func, "Funcion o variable global ya declarada.")
	else:
		if p[-3] == 'int':
			tipo = 0
			tabla_func['global']['tabla_var'][nombre_func] = {'tipo':tipo, 'dir_mem':dir_int_global}
			dir_variable = dir_int_global
			inc_o_valida_dir_mem('g','i')
		elif p[-3] == 'float':
			tipo = 1
			tabla_func['global']['tabla_var'][nombre_func] = {'tipo':tipo, 'dir_mem':dir_float_global}
			dir_variable = dir_float_global
			inc_o_valida_dir_mem('g','f')
		elif p[-3] == 'char':
			tipo = 2
			tabla_func['global']['tabla_var'][nombre_func] = {'tipo':tipo, 'dir_mem':dir_char_global}
			dir_variable = dir_char_global
			inc_o_valida_dir_mem('g','c')
		elif p[-3] == 'bool':
			tipo = 3
			tabla_func['global']['tabla_var'][nombre_func] = {'tipo':tipo, 'dir_mem':dir_bool_global}
			dir_variable = dir_bool_global
			inc_o_valida_dir_mem('g','b')
		elif p[-3] == 'string':
			tipo = 4
			tabla_func['global']['tabla_var'][nombre_func] = {'tipo':tipo, 'dir_mem':dir_string_global}
			dir_variable = dir_string_global
			inc_o_valida_dir_mem('g','s')
		else: # Para cuando es void
			tipo = -1
			dir_variable = 0

		tabla_func[nombre_func] = {'tipo':tipo, 'dir_inicio':'_', 'dir_variable': dir_variable, 'tabla_var':dict(), 'tabla_param':dict()}

def p_seen_paso2_def_proc(p):
	'seen_paso2_def_proc :'
	global nombre_func
	global dir_int_local, dir_float_local, dir_char_local, dir_bool_local, dir_string_local
	# p[-2] = ID
	# p[-3] = TIPO
 	ID = p[-2]
 	tipo = p[-3]

 	if tipo == 'int':
 		tipo = 0
 		tabla_func[nombre_func]['tabla_param'][ID] = {'tipo':tipo, 'dir_mem':dir_int_local}
 		inc_o_valida_dir_mem('l','i')
 	elif tipo == 'float':
 		tipo = 1
 		tabla_func[nombre_func]['tabla_param'][ID] = {'tipo':tipo, 'dir_mem':dir_float_local}
 		inc_o_valida_dir_mem('l','f')
 	elif tipo == 'char':
 		tipo = 2
 		tabla_func[nombre_func]['tabla_param'][ID] = {'tipo':tipo, 'dir_mem':dir_char_local}
 		inc_o_valida_dir_mem('l','c')
 	elif tipo == 'bool':
 		tipo = 3
 		tabla_func[nombre_func]['tabla_param'][ID] = {'tipo':tipo, 'dir_mem':dir_bool_local}
 		inc_o_valida_dir_mem('l','b')
 	elif tipo == 'string':
 		tipo = 4
 		tabla_func[nombre_func]['tabla_param'][ID] = {'tipo':tipo, 'dir_mem':dir_string_local}
 		inc_o_valida_dir_mem('l','s')
 	# Agrego en la tabla de parametros de la funcion: ".param#parametro" como key y como valor el id del parametro
 	tabla_func[nombre_func]['tabla_param']['.param'+str((len(tabla_func[nombre_func]['tabla_param'])+1)/2)] = ID


def p_seen_global(p):
	'seen_global :'
	global variable_global
	variable_global = 1

def p_seen_tipo_var(p):
	'seen_tipo_var :'
	# p[-1] = Tipo de variables
	global tipo_var

	if p[-1] == 'int':
			tipo = 0
	elif p[-1] == 'float':
		tipo = 1
	elif p[-1] == 'char':
		tipo = 2
	elif p[-1] == 'bool':
		tipo = 3
	elif p[-1] == 'string':
		tipo = 4

	tipo_var = tipo

def p_seen_declara_variables(p):
	'seen_declara_variables :'
	# p[-1] = ID
	# p[-2] =
	global variable_global
	global nombre_func

	ID = p[-1]

	if variable_global == 1: # Si es global la variable
		if ID in tabla_func['global']['tabla_var']:
			error_semantico(ID, "Funcion o variable ya declarada.")
		asigna_dir_memoria(ID, tipo_var, 'global', 0)

	else: # Si es variable local
		if ID in tabla_func:
			error_semantico(ID, "Funcion o variable ya declarada.")
		elif ID in tabla_func[nombre_func]['tabla_var']: # Si la variable ya esta declarada dentro de la funcion
			error_semantico(ID, "Variable ya declarada.")
		elif ID in tabla_func[nombre_func]['tabla_param']: # Si la variable ya esta declarada como parametro
			error_semantico(ID, "Parametro ya declarado con mismo id.")
		else:
			asigna_dir_memoria(ID, tipo_var, nombre_func, 0)


###################################################### SEMANTICA - CUADRUPLOS ###############################################################
# Se encarga de Meter el GOTO que dirige al MAIN
def p_seen_program(p):
	'seen_program :'
	global tabla_func
	global cuadruplos
	cuadruplos = np.append(cuadruplos, [[14, '_', '_', '_']], 0)

# Se encarga de marcar donde termina una funcion, metiendo la instruccion ENDPROC a los cuadruplos
def p_endproc(p):
	'endproc :'
	global cuadruplos, contResCuadruplos
	global dir_int_local, dir_float_local, dir_char_local, dir_bool_local, dir_string_local
	# Libera los contadores de las dir de memoria local de la funcion
	dir_int_local = 15000
	dir_float_local = 16000
	dir_char_local = 17000
	dir_bool_local = 18000
	dir_string_local = 19000

	# Libera el contador para asignar el nombre a las variables temporales
	contResCuadruplos = 0

	cuadruplos = np.append(cuadruplos, [[18, '_', '_', '_']], 0)


# Se encarga de meter los RETURN de una FUNCION a los cuadruplos
def p_seen_return(p):
	'seen_return :'
	global cuadruplos, POpndo
	variable = POpndo.pop() # Regresa la variable o temporal
	cuadruplos = np.append(cuadruplos, [[17, '_', '_', variable]], 0)

# Se utiliza en la regla llamafunc y en factor, y es cuando haces llamada a una funcion en un estatuto o en una operacion aritmetica.
def p_seen_llamada_func(p):
	'seen_llamada_func :'
	global cuadruplos, id_funcion_llamada
	ID = id_funcion_llamada

	if tabla_func[ID]['tipo'] == -1:
		if ID in tabla_func: 
			cuadruplos = np.append(cuadruplos, [[19, '_', '_', ID]], 0)
		else:
			error_semantico(ID, "Funcion no declarada.")
	else:
		error_semantico(ID, "Funcion con valor de retorno sin utilizarse.")

def p_seen_llamada_func_factor(p):
	'seen_llamada_func_factor :'
	global cuadruplos, id_funcion_llamada
	ID = id_funcion_llamada

	if tabla_func[ID]['tipo'] != -1:
		if ID in tabla_func: 
			cuadruplos = np.append(cuadruplos, [[19, '_', '_', ID]], 0)
		else:
			error_semantico(ID, "Funcion no declarada.")
	else:
		error_semantico(ID, "Funcion sin valor de retorno.")

# Cada vez que encuentra un argumento, incrementa el numero del contador de argumentos de una funcion
def p_seen_argumento_funcion(p):
	'seen_argumento_funcion :'
	# p[-1] = Argumento
	global cont_args, id_funcion_llamada, tipo_arg, POpndo, cuadruplos
	cont_args += 1
	
	arg = p[-1] # Argumento que se asigna en la regla

	tipo_argumento = ''

	if cont_args > len(tabla_func[id_funcion_llamada]['tabla_param'])/2: # Se divide entre 2 debido a que genera el nombre del param y .param#num_param cada vez que encuentra un param
		error_semantico(id_funcion_llamada, "Exceso de argumentos.")
	#elif arg != None: # Si es CHAR o STRING, porque los numeros los saca de la pila de operadores
	#	tipo_argumento = tipo_arg
	else:
		operando = POpndo.pop() # Obtiene el ultimo operando
		tipo_argumento = obtiene_tipo_dir_memoria(operando) # Obtiene el tipo de acuerdo al operando
		arg = operando

	tabla_param_func = tabla_func[id_funcion_llamada]['tabla_param']
	param = tabla_param_func['.param'+str(cont_args)] # Obtiene el id del parametro

	# Checa el tipo de parametro de la funcion con el tipo del argumento
	if cuboSemantico[13][tabla_param_func[param]['tipo']][tipo_argumento] == 0:
		error_semantico(id_funcion_llamada, "Tipos de argumento y parametro incompatibles.")
	else: # Si son compatibles
		##################### IMPORTANTE - CAMBIAR LO QUE SE MANDA COMO PARAMETRO CHAR Y STRING #################
		#cuadruplos = np.append(cuadruplos, [[22,arg,'_','.param'+str(cont_args)]], 0)
		cuadruplos = np.append(cuadruplos, [[22,arg,'_',tabla_param_func[param]['dir_mem']]], 0)

def p_seen_argumento_ref_funcion(p):
	'seen_argumento_ref_funcion :'
	# p[-1] = Argumento por referencia
	global cont_args, id_funcion_llamada, tipo_arg, POpndo, cuadruplos
	cont_args += 1
	
	arg_ref = p[-1] # Argumento que se asigna en la regla

	tipo_argumento = ''

	if cont_args > len(tabla_func[id_funcion_llamada]['tabla_param'])/2: # Se divide entre 2 debido a que genera el nombre del param y .param#num_param cada vez que encuentra un param
		error_semantico(id_funcion_llamada, "Exceso de argumentos.")
	else:
		#operando = POpndo.pop() # Obtiene el ultimo operando

		# Checa si es variable global o local
		if arg_ref in tabla_func['global']['tabla_var']:
			operando = tabla_func['global']['tabla_var'][arg_ref]['dir_mem']
		elif arg_ref in tabla_func[nombre_func]['tabla_var']:
			operando = tabla_func[nombre_func]['tabla_var'][arg_ref]['dir_mem']
		else:
			error_semantico(arg_ref, "Variable no declarada al enviar parametro por referencia.")

		tipo_argumento = obtiene_tipo_dir_memoria(operando) # Obtiene el tipo de acuerdo al operando
		arg_ref = operando

	tabla_param_func = tabla_func[id_funcion_llamada]['tabla_param']
	param = tabla_param_func['.param'+str(cont_args)] # Obtiene el id del parametro y lo asigna a param

	# Checa el tipo de parametro de la funcion con el tipo del argumento
	if cuboSemantico[13][tabla_param_func[param]['tipo']][tipo_argumento] == 0:
		error_semantico(id_funcion_llamada, "Tipos de argumento y parametro incompatibles.")
	else: # Si son compatibles
		##################### IMPORTANTE - CAMBIAR LO QUE SE MANDA COMO PARAMETRO CHAR Y STRING #################
		#cuadruplos = np.append(cuadruplos, [[22,arg,'_','.param'+str(cont_args)]], 0)
		cuadruplos = np.append(cuadruplos, [[22,arg,'_','&'+str(tabla_param_func[param]['dir_mem'])]], 0)

# Verifica que cumpla con la cantidad de params en la llamada de una funcion
def p_seen_verifica_cant_args(p):
	'seen_verifica_cant_args :'
	global cont_args, id_funcion_llamada
	if cont_args < len(tabla_func[id_funcion_llamada]['tabla_param'])/2: # Si no cumple con el # de params
		error_semantico(id_funcion_llamada, "Parametros insuficientes.")
	else: # Reinicia el contador de argumentos
		cont_args = 0

# Genera GOSUB en cuadruplos de la funcion
def p_gosub(p):
	'gosub :'
	global cuadruplos, id_funcion_llamada
	dir_inicio = tabla_func[id_funcion_llamada]['dir_inicio']
	cuadruplos = np.append(cuadruplos, [[23, id_funcion_llamada, '_', dir_inicio]], 0)


#def p_seen_arg_string(p):
#	'seen_arg_string :'
#	global tipo_arg
#	tipo_arg = 4

#def p_seen_arg_char(p):
#	'seen_arg_char :'
#	global tipo_arg
#	tipo_arg = 2

# Almacena el id que se llamo en factor, implicitamente cuando se hacen operaciones aritmeticas
def p_seen_id_factor(p):
	'seen_id_factor :'
	# p[-1] = ID del factor
	global id_funcion_llamada
	id_funcion_llamada = p[-1]


def p_seen_dir_inicio(p):
	'seen_dir_inicio :'
	global cuadruplos
	tabla_func[nombre_func]['dir_inicio'] = len(cuadruplos)

############### CUADRUPLOS OPERACIONES ARITMETICAS ##########################
# Meter ID en POpndo
def p_paso1_id_cuadruplo(p):
	'paso1_id_cuadruplo :'
	global POpndo, cuadruplos
	# p[-1] = Arreglo, Variable o funcion
	# p[-2] = ID

	ID = p[-2]
	
	# Cambio-DIR
	if ID in tabla_func[nombre_func]['tabla_var']:
		POpndo.append(tabla_func[nombre_func]['tabla_var'][ID]['dir_mem'])
	elif ID in tabla_func[nombre_func]['tabla_param']:
		POpndo.append(tabla_func[nombre_func]['tabla_param'][ID]['dir_mem'])
	elif ID in tabla_func['global']['tabla_var']:
		if ID in tabla_func:
			dir_memoria = tabla_func['global']['tabla_var'][ID]['dir_mem']
			tipo = obtiene_tipo_dir_memoria(dir_memoria)
			genera_cuadruplos_temporal(13, dir_memoria, '_', tipo)
		else:
			POpndo.append(tabla_func['global']['tabla_var'][ID]['dir_mem'])
	else:
		error_semantico(ID, "Variable no declarada")


	# Preparado para arreglos y funciones
	"""if (p[-1] == "["): # Si es arreglo

	elif (p[-1] == "("): # Si es funcion

	else: # Si es variable"""

# Meter CTE en POpndo
def p_paso1_int_cuadruplo(p):
	'paso1_int_cuadruplo :'
	global POpndo
	# p[-1] = CTE INT
	CTE_INT = p[-1]
	if CTE_INT not in tabla_func['global']['tabla_var']: # Si no existe la constante la crea, sino ya existia y agrega a la pila
		asigna_dir_memoria(CTE_INT, 0, 'global', 1) #0 = es el TIPO, 1 = BANDERA para indicar que es cte
	POpndo.append(tabla_func['global']['tabla_var'][CTE_INT]['dir_mem'])

def p_paso1_float_cuadruplo(p):
	'paso1_float_cuadruplo :'
	global POpndo
	# p[-1] = CTE FLOAt
	CTE_FLOAT = p[-1]
	if CTE_FLOAT not in tabla_func['global']['tabla_var']: # Si no existe la constante la crea, sino ya existia y agrega a la pila
		asigna_dir_memoria(CTE_FLOAT, 1, 'global', 1) # Primer 1 = Tipo, Segundo 1 = BANDERA para indicar que es cte
	POpndo.append(tabla_func['global']['tabla_var'][CTE_FLOAT]['dir_mem'])

def p_paso1_string_cuadruplo(p):
	'paso1_string_cuadruplo :'
	#p[-1] = CTE STRING
	CTE_STRING = p[-1][1:-1]
	CTE_STRING = '_' + CTE_STRING # Las ctes char y string empiezan con '_'
	if CTE_STRING not in tabla_func['global']['tabla_var']:
		asigna_dir_memoria(CTE_STRING, 4, 'global', 2)
	POpndo.append(tabla_func['global']['tabla_var'][CTE_STRING]['dir_mem'])

def p_paso1_char_cuadruplo(p):
	'paso1_char_cuadruplo :'
	#p[-1] = CTE CHAR
	CTE_CHAR = p[-1][1:-1]
	CTE_CHAR = '_' + CTE_CHAR # Las ctes char y string empiezan con '_'
	if CTE_CHAR not in tabla_func['global']['tabla_var']:
		asigna_dir_memoria(CTE_CHAR, 2, 'global', 2)
	POpndo.append(tabla_func['global']['tabla_var'][CTE_CHAR]['dir_mem'])

def p_paso1_bool_cuadruplo(p):
	'paso1_bool_cuadruplo :'
	global POpndo
	# p[-1] = CTE BOOL
	CTE_BOOL = p[-1]
	if CTE_BOOL not in tabla_func['global']['tabla_var']: # Si no existe la constante la crea, sino ya existia y agrega a la pila
		asigna_dir_memoria(CTE_BOOL, 3, 'global', 1) # Segundo 1 = BANDERA para indicar que es cte
	POpndo.append(tabla_func['global']['tabla_var'][CTE_BOOL]['dir_mem'])

# Meter operador aritmetico en POper
def p_paso2y3_cuadruplos(p):
	'paso2y3_cuadruplos :'
	global POper
	# p[-1] = Operador aritmetico
	POper.append(id_operaciones[p[-1]])

def p_paso4_cuadruplo(p):
	'paso4_cuadruplo :'
	# Sacamos el top
	global cuadruplos
	global POpndo
	global POper
	global contResCuadruplos

	if POper: # PENDIENTE CORREGIR ESTE IF
		operador = POper.pop()

		if (operador == 0 or operador == 1):
			opdo2 = POpndo.pop()
			opdo1 = POpndo.pop()

			tipo1 = obtiene_tipo_dir_memoria(opdo1)
			tipo2 = obtiene_tipo_dir_memoria(opdo2)

			res_tipo = cuboSemantico[operador][tipo1][tipo2]-1

			if res_tipo != -1:
				genera_cuadruplos_temporal(operador, opdo1, opdo2, res_tipo)
			else:
				error_semantico(operador,"Tipos incompatibles")
		else: # Si no es * y / dejamos el Stack a la normalidad
			POper.append(operador)

def p_paso5_cuadruplo(p):
	'paso5_cuadruplo :'
	global cuadruplos
	global POpndo
	global POper
	global contResCuadruplos

	if POper:
		operador = POper.pop()

		if (operador == 2 or operador == 3):
			opdo2 = POpndo.pop()
			opdo1 = POpndo.pop()

			tipo1 = obtiene_tipo_dir_memoria(opdo1)
			tipo2 = obtiene_tipo_dir_memoria(opdo2)

			res_tipo = cuboSemantico[operador][tipo1][tipo2]-1

			if res_tipo != -1:
				genera_cuadruplos_temporal(operador, opdo1, opdo2, res_tipo)
			else:
				error_semantico(operador,"Tipos incompatibles")
		else: # Si no es * y / dejamos el Stack a la normalidad
			POper.append(operador)

def p_paso6_cuadruplo(p):
	'paso6_cuadruplo :'
	global POper
	POper.append('(')

def p_paso7_cuadruplo(p):
	'paso7_cuadruplo :'
	global POper
	POper.pop()

############### CUADRUPLO CONDICION ##########################
# Agrega operador ||
def p_if_paso1_cuadruplo(p):
	'if_paso1_cuadruplo :'
	global POper
	POper.append(11)

# Agrega operador &&
def p_if_paso2_cuadruplo(p):
	'if_paso2_cuadruplo :'
	global POper
	POper.append(10)

#
def p_if_paso3_cuadruplo(p):
	'if_paso3_cuadruplo :'
	global cuadruplos
	global POpndo
	global POper
	global contResCuadruplos

	if POper:
		operador = POper.pop()

		if (operador == 11):
			opdo2 = POpndo.pop()
			opdo1 = POpndo.pop()

			tipo1 = obtiene_tipo_dir_memoria(opdo1)
			tipo2 = obtiene_tipo_dir_memoria(opdo2)

			res_tipo = cuboSemantico[operador][tipo1][tipo2]-1

			if res_tipo != -1:
				genera_cuadruplos_temporal(operador, opdo1, opdo2, res_tipo)
			else:
				error_semantico(operador,"Tipos incompatibles")
		else: # Si no es * y / dejamos el Stack a la normalidad
			POper.append(operador)

def p_if_paso4_cuadruplo(p):
	'if_paso4_cuadruplo :'
	global cuadruplos
	global POpndo
	global POper
	global contResCuadruplos

	if POper:
		operador = POper.pop()
		if operador == 10:
			opdo2 = POpndo.pop()
			opdo1 = POpndo.pop()

			tipo1 = obtiene_tipo_dir_memoria(opdo1)
			tipo2 = obtiene_tipo_dir_memoria(opdo2)

			res_tipo = cuboSemantico[operador][tipo1][tipo2]-1

			if res_tipo != -1:
				genera_cuadruplos_temporal(operador, opdo1, opdo2, res_tipo)
			else:
				error_semantico(operador,"Tipos incompatibles")
		else: # Si no es * y / dejamos el Stack a la normalidad
			POper.append(operador)

def p_if_paso5_cuadruplo(p):
	'if_paso5_cuadruplo :'
	#p[-1] = "!"
	global POper
	POper.append(12)

def p_if_paso6_cuadruplo(p):
	'if_paso6_cuadruplo :'
	#p[-1]=Operando booleano(<,>,<=,>=,==,!=)
	global POper
	POper.append(id_operaciones[p[-1]])

#Saca opdo 2 y 1, verifica su tipo de operacion, genera el cuadruplo y mete el temporal
def p_if_paso7_cuadruplo(p):
	'if_paso7_cuadruplo :'
	global cuadruplos
	global POpndo
	global POper
	global contResCuadruplos

	if POper:
		operador = POper.pop()

		opdo2 = POpndo.pop()
		opdo1 = POpndo.pop()

		tipo1 = obtiene_tipo_dir_memoria(opdo1)
		tipo2 = obtiene_tipo_dir_memoria(opdo2)

		# Checa el tipo que genera en el cubo semantico
		res_tipo = cuboSemantico[operador][tipo1][tipo2]-1

		if res_tipo != -1: # Como antes el 0 era error y le restamos -1, ahora el error es -1
			genera_cuadruplos_temporal(operador, opdo1, opdo2, res_tipo)
		else:
			error_semantico(operador,"Tipos incompatibles")

def p_if_paso8_cuadruplo(p):
	'if_paso8_cuadruplo :'
	global cuadruplos
	global POpndo
	global POper
	global contResCuadruplos

	if POper:
		operador = POper.pop()

		if (operador == 12):
			opdo = POpndo.pop()

			operando_tipo = obtiene_tipo_dir_memoria(opdo)

			if operando_tipo == 3:

				genera_cuadruplos_temporal(operador, opdo, '_', 3)
			else:
				error_semantico(operador,"Tipos incompatibles")

		else: # Si no es ! dejamos el Stack a la normalidad
			POper.append(operador)

############################################ GENERACION CODIGO ESTATUTOS #################################################################
########################## GENERACION CODIGO ESTATUTOS SECUENCIALES ##########################
############### GENERACION CODIGO ESTATUTO - ASIGNACION ##########################
# PENDIENTE, la verificacion de tipo de dato de retorno de la funcion
def p_seen_equals(p):
	'seen_equals :'
	#p[-1] = OPERADOR EQUALS
	global POper
	POper.append(13)

def p_equals_pendiente(p):
	'equals_pendiente :'
	global POper
	global nombre_func
	global POpndo
	global cuadruplos
	#p[-5] = ID al que se le asigna


	operacion = POper.pop()
	asignado = p[-5]

	ultimo_temporal = POpndo.pop()
	tipo_ultimo_temporal = obtiene_tipo_dir_memoria(ultimo_temporal)

	## CAMBIAR LAS TEMPORALES A QUE SEAN LOCALES
	if asignado in tabla_func[nombre_func]['tabla_var']: # Checa si esta declarado en la tabla de variables de la funcion donde se hizo la asignacion
		#if tabla_func[nombre_func]['tabla_var'][asignado]['tipo'] == tipo_ultimo_temporal:

		asignado_tipo = tabla_func[nombre_func]['tabla_var'][asignado]['tipo']
		if cuboSemantico[13][asignado_tipo][tipo_ultimo_temporal] != 0:
			cuadruplos = np.append(cuadruplos, [[13,ultimo_temporal,'_',tabla_func[nombre_func]['tabla_var'][asignado]['dir_mem']]], 0)
		else:
			error_semantico(asignado, "Tipos incompatibles")
	elif asignado in tabla_func[nombre_func]['tabla_param']: # Checa si esta en la tabla de params de la funcion
		asignado_tipo = tabla_func[nombre_func]['tabla_param'][asignado]['tipo']

		if cuboSemantico[13][asignado_tipo][tipo_ultimo_temporal] != 0:
			cuadruplos = np.append(cuadruplos, [[13,ultimo_temporal,'_',tabla_func[nombre_func]['tabla_param'][asignado]['dir_mem']]], 0)
		else:
			error_semantico(asignado, "Tipos incompatibles")
	elif asignado in tabla_func['global']['tabla_var']: #Si esta en la tabla de variables
		# Sino, es una global forzozamente
		asignado_tipo = tabla_func['global']['tabla_var'][asignado]['tipo']
		if cuboSemantico[13][asignado_tipo][tipo_ultimo_temporal] != 0:
			cuadruplos = np.append(cuadruplos, [[13,ultimo_temporal,'_',tabla_func['global']['tabla_var'][asignado]['dir_mem']]], 0)
		else:
			error_semantico(asignado, "Tipos incompatibles")
	else:
		error_semantico(asignado, "Variable no declarada")

############### GENERACION CODIGO ESTATUTO - ESCRITURA ##########################
def p_seen_scan(p):
	'seen_scan :'
	# p[-3] = variable del scan
	global cuadruplos

	ID = p[-3]

	if ID in tabla_func[nombre_func]['tabla_var']:
		dir_mem = tabla_func[nombre_func]['tabla_var'][ID]['dir_mem']
		if ID not in tabla_func:
			cuadruplos = np.append(cuadruplos, [[21,'_','_', dir_mem]], 0)
		else:
			error_semantico(ID, "No puedes leer en una funcion.")
	else:
		error_semantico(ID, "Variable utilizada no declarada en scan.")


############### GENERACION CODIGO ESTATUTO - LECTURA ##########################
def p_seen_print(p):
	'seen_print :'
	global POpndo
	global cuadruplos

	#valor = p[-3]

	#if valor != None: #Que es string o CHAR
	#	dir_mem = cte_char_o_string(valor)
	#	cuadruplos = np.append(cuadruplos, [[20, '_', '_', dir_mem]],0) 
	#else: 

	ultimo_temporal = POpndo.pop() # Saca el ultimo temporal en la pila
	# PENDIENTE, la verificacion de tipo de dato de retorno de la funcion
	#tipo = tabla_func['global']['tabla_var'][ultimo_temporal]['tipo']
	cuadruplos = np.append(cuadruplos, [[20,'_','_',ultimo_temporal]], 0)


############### GENERACION CODIGO ESTATUTO - IF ##########################

def p_if_paso1_codigo(p):
	'if_paso1_codigo :'
	global POpndo, PSaltos
	global cuadruplos, contElifs

	condicion = POpndo.pop()

	# Checa que el tipo de la ultima variable temporal que arrojo condicion sea booleano
	tipo_ultimo_temporal = obtiene_tipo_dir_memoria(condicion)

	if tipo_ultimo_temporal != 3:
		error_semantico(condicion, "Expresion no booleana.")
	else:
		cuadruplos = np.append(cuadruplos, [[15, condicion, '_','_']], 0)
		PSaltos.append(len(cuadruplos)-1)

def p_if_paso2_codigo(p):
	'if_paso2_codigo :'
	global PSaltos
	global cuadruplos, contElifs

	cuadruplos = np.append(cuadruplos, [[14, '_', '_','_']], 0)
	contElifs += 1
	salida = PSaltos.pop()
	cuadruplos[salida][3] = len(cuadruplos)
	PSaltos.append(len(cuadruplos)-1)

def p_if_paso3_codigo(p):
	'if_paso3_codigo :'
	global PSaltos, cuadruplos, contElifs
	while contElifs > 0:
		goto = PSaltos.pop()
		cuadruplos[goto][3] = len(cuadruplos)
		contElifs -= 1;

def p_if_paso4_codigo(p):
	'if_paso4_codigo :'
	global cuadruplos, PSaltos
	ultimo_go_to = PSaltos.pop()
	cuadruplos = np.delete(cuadruplos, ultimo_go_to, 0)


# def p_if_paso3_codigo(p):
# 	'if_paso3_codigo :'
# 	global PSaltos
# 	global cuadruplos, contElifs

# 	primer_goto = PSaltos.pop()
# 	falso = PSaltos.pop()
# 	PSaltos.append(primer_goto)

# 	gotos = []
# 	cont_gotos = contElifs
# 	while cont_gotos > 0:
# 		gotos.append(PSaltos.pop())
# 		cont_gotos = cont_gotos - 1
# 	imprime_cuadruplo()

# 	cuadruplos = np.append(cuadruplos, [[14, '_', '_', '_']], 0)
# 	PSaltos.append(len(cuadruplos)-1)

# 	cuadruplos[falso][3] = len(cuadruplos)

# 	print(gotos)
# 	print(contElifs)
# 	while contElifs > 0:
# 		print(contElifs)
# 		print(gotos)
# 		goto = gotos.pop()
# 		cuadruplos[goto][3] = len(cuadruplos)+1
# 		contElifs = contElifs - 1


# def p_if_paso4_codigo(p):
# 	'if_paso4_codigo :'
# 	global PSaltos, cuadruplos, POpndo, contElifs

# 	condicion = POpndo.pop()

# 	# Checa que el tipo de la ultima variable temporal que arrojo condicion sea booleano
# 	#if tabla_func['global']['tabla_var'][condicion]['tipo'] != 3:
# 	if obtiene_tipo_dir_memoria(condicion) != 3:
# 		error_semantico(condicion, "No booleano")
# 	else:
# 		goto_pendiente = PSaltos.pop()
# 		falso = PSaltos.pop()
# 		PSaltos.append(goto_pendiente)

# 		cuadruplos = np.append(cuadruplos, [[15, condicion, '_','_']], 0)
# 		PSaltos.append(len(cuadruplos)-1)
# 		cuadruplos[falso][3] = len(cuadruplos)-2

# def p_if_paso5_codigo(p):
# 	'if_paso5_codigo :'
# 	global PSaltos, cuadruplos, POpndo, contElifs

# 	cuadruplos = np.append(cuadruplos, [[14, '_', '_','_']], 0)	
# 	PSaltos.append(len(cuadruplos)-1)
# 	contElifs += 1
############### GENERACION CODIGO ESTATUTO - WHILE y DO WHILE ##########################
# NOTA: Do while utiliza while_paso1_codigo y dowhile_paso4_codigo
def p_while_paso1_codigo(p):
	'while_paso1_codigo :'
	global PSaltos

	PSaltos.append(len(cuadruplos))

def p_while_paso2_codigo(p):
	'while_paso2_codigo :'
	global PSaltos, POpndo, cuadruplos

	condicion = POpndo.pop()

	if obtiene_tipo_dir_memoria(condicion) != 3:
	#if tabla_func['global']['tabla_var'][condicion]['tipo'] != 3:
		error_semantico(condicion, "No booleano")
	else:
		cuadruplos = np.append(cuadruplos, [[15, condicion, '_','_']], 0)
		PSaltos.append(len(cuadruplos)-1)

def p_while_paso3_codigo(p):
	'while_paso3_codigo :'
	global PSaltos, cuadruplos

	falso = PSaltos.pop()
	retorno = PSaltos.pop()

	cuadruplos = np.append(cuadruplos, [[14, '_', '_', retorno]], 0)
	cuadruplos[falso][3] = len(cuadruplos)

def p_dowhile_paso4_codigo(p):
	'dowhile_paso4_codigo :'
	global POpndo, PSaltos, cuadruplos
	condicion = POpndo.pop()

	tipo_condicion = obtiene_tipo_dir_memoria(condicion)

	if tipo_condicion != 3:
		error_semantico(condicion, "No booleano")
	else:
		retorno = PSaltos.pop()
		cuadruplos = np.append(cuadruplos, [[16, condicion, '_', retorno]], 0)

############### GENERACION CODIGO ESTATUTO - WHILE ##########################
def p_for_paso1_codigo(p):
	'for_paso1_codigo :'
	global PSaltos
	PSaltos.append(len(cuadruplos))

def p_for_paso2_codigo(p): # PENDIENTE - Es igual a while_paso2_codigo
	'for_paso2_codigo :'
	global PSaltos, POpndo, cuadruplos

	condicion = POpndo.pop()

	tipo_condicion = obtiene_tipo_dir_memoria(condicion)

	if tipo_condicion != 3:
		error_semantico(condicion, "No booleano")
	else:
		cuadruplos = np.append(cuadruplos, [[15, condicion, '_', '_']], 0)
		PSaltos.append(len(cuadruplos)-1)

def p_for_paso3_codigo(p):
	'for_paso3_codigo :'
	global PSaltos,cuadruplos
	cuadruplos = np.append(cuadruplos, [[14, '_', '_','_']], 0)
	PSaltos.append(len(cuadruplos)-1)

def p_for_paso4_codigo(p):
	'for_paso4_codigo :'
	global PSaltos, cuadruplos

	incrementa = PSaltos.pop()
	falso = PSaltos.pop()
	retorno = PSaltos.pop()

	cuadruplos = np.append(cuadruplos, [[14, '_', '_', retorno]], 0)

	PSaltos.append(falso)
	PSaltos.append(incrementa)

def p_for_paso5_codigo(p):
	'for_paso5_codigo :'
	global PSaltos, cuadruplos
	incrementa = PSaltos.pop()
	falso = PSaltos.pop()

	cuadruplos = np.append(cuadruplos, [[14, '_', '_', incrementa+1]], 0)
	cuadruplos[falso][3] = len(cuadruplos)

def p_for_paso6_codigo(p):
	'for_paso6_codigo :'
	global PSaltos, cuadruplos
	incrementa = PSaltos[len(PSaltos)-1]

	cuadruplos[incrementa][3] = len(cuadruplos)



#######################################################
############## FUNCIONES AUXILIARES ##########################
def asigna_dir_memoria(variable, tipo, scope, cte):
	global dir_int_global, dir_float_global, dir_char_global, dir_bool_global, dir_string_global
	global dir_int_local, dir_float_local, dir_char_local, dir_bool_local, dir_string_local
	global dir_int_cons, dir_float_cons, dir_char_cons, dir_bool_cons, dir_string_cons

	tabla_variables = tabla_func[scope]['tabla_var']

	if cte == 0: #Si no es constante
		if scope == 'global': # Si es global
			if tipo == 0:
				tabla_variables[variable] = {'tipo':tipo, 'dir_mem':dir_int_global}
				inc_o_valida_dir_mem('g','i')
			elif tipo == 1:
				tabla_variables[variable] = {'tipo':tipo, 'dir_mem':dir_float_global}
				inc_o_valida_dir_mem('g','f')
			elif tipo == 2:
				tabla_variables[variable] = {'tipo':tipo, 'dir_mem':dir_char_global}
				inc_o_valida_dir_mem('g','c')
			elif tipo == 3:
				tabla_variables[variable] = {'tipo':tipo, 'dir_mem':dir_bool_global}
				inc_o_valida_dir_mem('g','b')
			elif tipo == 4:
				tabla_variables[variable] = {'tipo':tipo, 'dir_mem':dir_string_global}
				inc_o_valida_dir_mem('g','s')
		else: # Si es local
			if tipo == 0:
				tabla_variables[variable] = {'tipo':tipo, 'dir_mem':dir_int_local}
				inc_o_valida_dir_mem('l','i')
			elif tipo == 1:
				tabla_variables[variable] = {'tipo':tipo, 'dir_mem':dir_float_local}
				inc_o_valida_dir_mem('l','f')
			elif tipo == 2:
				tabla_variables[variable] = {'tipo':tipo, 'dir_mem':dir_char_local}
				inc_o_valida_dir_mem('l','c')
			elif tipo == 3:
				tabla_variables[variable] = {'tipo':tipo, 'dir_mem':dir_bool_local}
				inc_o_valida_dir_mem('l','b')
			elif tipo == 4:
				tabla_variables[variable] = {'tipo':tipo, 'dir_mem':dir_string_local}
				inc_o_valida_dir_mem('l','s')
	else: #Si si es constante
		if tipo == 0:
			tabla_variables[variable] = {'tipo':tipo, 'dir_mem':dir_int_cons}
			inc_o_valida_dir_mem('c','i')
		elif tipo == 1:
			tabla_variables[variable] = {'tipo':tipo, 'dir_mem':dir_float_cons}
			inc_o_valida_dir_mem('c','f')
		elif tipo == 2:
			tabla_variables[variable] = {'tipo':tipo, 'dir_mem':dir_char_cons}
			inc_o_valida_dir_mem('c','c')
		elif tipo == 3:
			tabla_variables[variable] = {'tipo':tipo, 'dir_mem':dir_bool_cons}
			inc_o_valida_dir_mem('c','b')
		elif tipo == 4:
			tabla_variables[variable] = {'tipo':tipo, 'dir_mem':dir_string_cons}
			inc_o_valida_dir_mem('c','s')


# Regresa el tipo dada la direccion de memoria de una variable
# 0=int, 1=float, 2=char, 3=bool, 4=string
def obtiene_tipo_dir_memoria(dir_memoria):
	residuo = dir_memoria % 5000

	if residuo < 1000:
		return 0
	elif residuo < 2000:
		return 1
	elif residuo < 3000:
		return 2
	elif residuo < 4000:
		return 3
	elif residuo < 5000:
		return 4

# Tipo: indica el tipo de temporal que es
def genera_cuadruplos_temporal(operador, opdo1, opdo2, tipo):
	global cuadruplos, contResCuadruplos
	global nombre_func
	global dir_bool_temp, dir_char_temp, dir_int_temp, dir_float_temp, dir_string_temp

	tabla_variables = tabla_func[nombre_func]['tabla_var']

	temporal = '.t'+str(contResCuadruplos)

	if tipo == 0:
		tabla_variables[temporal] = {'tipo':tipo, 'dir_mem':dir_int_temp}
		inc_o_valida_dir_mem('t','i')
	elif tipo == 1:
		tabla_variables[temporal] = {'tipo':tipo, 'dir_mem':dir_float_temp}
		inc_o_valida_dir_mem('t','f')
	elif tipo == 2:
		tabla_variables[temporal] = {'tipo':tipo, 'dir_mem':dir_char_temp}
		inc_o_valida_dir_mem('t','c')
	elif tipo == 3:
		tabla_variables[temporal] = {'tipo':tipo, 'dir_mem':dir_bool_temp}
		inc_o_valida_dir_mem('t','b')
	elif tipo == 4:
		tabla_variables[temporal] = {'tipo':tipo, 'dir_mem':dir_string_temp}
		inc_o_valida_dir_mem('t','s')

	dir_temporal = tabla_variables[temporal]['dir_mem']
	cuadruplos = np.append(cuadruplos, [[operador,opdo1,opdo2,dir_temporal]], 0)
	POpndo.append(dir_temporal)
	contResCuadruplos += 1

##### FUNCION QUE ACCESA REGRESA VALOR CTE STRING o CHAR O LA DA DE ALTA
#def cte_char_o_string(cte):
#
#	# Si viene con " al inicio es String
#	if cte[0] == "\"":
#		cte = cte[1:-1]
#		acceso_cte = '_' + cte
#		if acceso_cte not in tabla_func['global']['tabla_var']:
#			tabla_func['global']['tabla_var'][acceso_cte] = {'dir_mem':dir_string_cons, 'tipo':4}
#			inc_o_valida_dir_mem('c','s')
#	else: # Si viene con ' es Char
#		cte = cte[1:-1]
#		acceso_cte = '_' + cte
#		if acceso_cte not in tabla_func['global']['tabla_var']:
#			tabla_func['global']['tabla_var'][acceso_cte] = {'dir_mem':dir_char_cons, 'tipo':2}
#			inc_o_valida_dir_mem('c','c')
#
#	return tabla_func['global']['tabla_var'][acceso_cte]['dir_mem']


# FUNCION QUE INCREMENTA LOS CONTADORES DE DIR_MEMORIA Y VALIDA LOS LIMITES
def inc_o_valida_dir_mem(scope, tipo):
	global dir_int_global, dir_float_global, dir_char_global, dir_bool_global, dir_string_global
	global dir_int_local, dir_float_local, dir_char_local, dir_bool_local, dir_string_local
	global dir_int_cons, dir_float_cons, dir_char_cons, dir_bool_cons, dir_string_cons
	global dir_int_temp, dir_float_temp, dir_char_temp, dir_bool_temp, dir_string_temp

	if scope == 'g': # Si es global
		if tipo == 'i':
			if dir_int_global+1 < 11000:
				dir_int_global += 1
			else:
				error_memoria("global", "int")
		elif tipo == 'f':
			if dir_float_global+1 < 12000:
				dir_float_global += 1
			else:
				error_memoria("global", "float")
		elif tipo == 'c':
			if dir_char_global+1 < 13000:
				dir_char_global += 1
			else:
				error_memoria("global", "char")
		elif tipo == 'b':
			if dir_bool_global+1 < 14000:
				dir_bool_global += 1
			else:
				error_memoria("global", "bool")
		elif tipo == 's':
			if dir_string_global+1 < 15000:
				dir_string_global += 1
			else:
				error_memoria("global", "string")
	elif scope == 'l': # Si es local
		if tipo == 'i':
			if dir_int_local+1 < 16000:
				dir_int_local += 1
			else:
				error_memoria("local", "int")
		elif tipo == 'f':
			if dir_float_local+1 < 17000:
				dir_float_local += 1
			else:
				error_memoria("local", "float")
		elif tipo == 'c':
			if dir_char_local+1 < 18000:
				dir_char_local += 1
			else:
				error_memoria("local", "char")
		elif tipo == 'b':
			if dir_bool_local+1 < 19000:
				dir_bool_local += 1
			else:
				error_memoria("local", "bool")
		elif tipo == 's':
			if dir_string_local+1 < 20000:
				dir_string_local += 1
			else:
				error_memoria("local", "string")
	elif scope == 't': # Si es temporal
		if tipo == 'i':
			if dir_int_temp+1 < 21000:
				dir_int_temp += 1
			else:
				error_memoria("temporal", "int")
		elif tipo == 'f':
			if dir_float_temp+1 < 22000:
				dir_float_temp += 1
			else:
				error_memoria("temporal", "float")
		elif tipo == 'c':
			if dir_char_temp+1 < 23000:
				dir_char_temp += 1
			else:
				error_memoria("temporal", "char")
		elif tipo == 'b':
			if dir_bool_temp+1 < 24000:
				dir_bool_temp += 1
			else:
				error_memoria("temporal", "bool")
		elif tipo == 's':
			if dir_string_temp+1 < 25000:
				dir_string_temp += 1
			else:
				error_memoria("temporal", "string")
	elif scope == 'c': # Si es constante
		if tipo == 'i':
			if dir_int_cons+1 < 26000:
				dir_int_cons += 1
			else:
				error_memoria("constante", "int")
		elif tipo == 'f':
			if dir_float_cons+1 < 27000:
				dir_float_cons += 1
			else:
				error_memoria("constante", "float")
		elif tipo == 'c':
			if dir_char_cons+1 < 28000:
				dir_char_cons += 1
			else:
				error_memoria("constante", "char")
		elif tipo == 'b':
			if dir_bool_cons+1 < 29000:
				dir_bool_cons += 1
			else:
				error_memoria("constante", "bool")
		elif tipo == 's':
			if dir_string_cons+1 < 30000:
				dir_string_cons += 1
			else:
				error_memoria("constante", "string")

############# FUNCIONES TESTING AUXILIARES ############

def imprime_cuadruplo():
	global cuadruplos, cuadruplos_str
	cuadruplos_str = np.copy(cuadruplos)
	for i in range(0,len(cuadruplos_str), 1):
		#print(reverse_id_operaciones[cuadruplos[i][0]])
		cuadruplos_str[i][0] = reverse_id_operaciones[int(float(cuadruplos[i][0]))]
	print()
	print(cuadruplos_str)

def imprime_tabla_func():
	print()
	print("GLOBALES:")
	tabla_var_globales = tabla_func['global']['tabla_var']
	for variable,atributos in tabla_var_globales.iteritems():
		print("    VAR:%s" % variable, end="; ")
		for atributo,valor in atributos.iteritems():
			print("%s:" %atributo, end="")
			print("%s; " %valor, end="")
		print()
	print()

	print("FUNCIONES:")
	tabla_var=dict()
	for func in tabla_func:
		if func != 'global':
			print("    nombre:%s" %func, end="")
			for atributo_func, valor_func in tabla_func[func].iteritems():
				if isinstance(valor_func,dict):
					tabla_var=valor_func
				else:
					print("; %s:" %atributo_func,end="")
					print("%s" %valor_func, end="")
			print()
			print("    tabla_var:")
			for variable,atributos in tabla_var.iteritems():
				print("\tVAR:%s" % variable, end="; ")
				for atributo,valor in atributos.iteritems():
					print("%s:" %atributo, end="")
					print("%s; " %valor, end="")
				print()
			print()
#######################################################
####### Funcion que genera el archivo objeto ##########
# Formato funciones: nombre, tipo, dir_inicio, cant_param, size
# Formato constantes: valor, tipo, dir_memoria
#######################################################
def genera_archivo_obj(archivo):
	global tabla_func, cuadruplos
	objFile = open(archivo+".gick", "w")
	
	contenido = "" # Contenido que tendra el archivo objeto
	# Escribe la las funciones, empieza en 1 porque excluye las variables globales	
	for funcion in tabla_func:
		if funcion != "global":
			nombre = funcion
			tipo = tabla_func[funcion]['tipo']
			dir_inicio = tabla_func[funcion]['dir_inicio']
			cant_parametros = len(tabla_func[funcion]['tabla_param'])/2
			size = len(tabla_func[funcion]['tabla_var']) + cant_parametros
			dir_variable = tabla_func[funcion]['dir_variable']
			# Funcion = nombre, tipo, dir_inicio, cat_parametros, size, dir_variable
			contenido += nombre + " " + str(tipo) + " " + str(dir_inicio) + " " + str(cant_parametros) + " " + str(size) + " " + str(dir_variable) + "\n"
		else:
			print

	# Agrega las constantes al archivo obj
	contenido += "#\n"
	globales = "void 0 *\n"
	for constante in tabla_func['global']['tabla_var']:
		if re.match(r'[0-9].*',constante) or constante[0] == '_' or constante == 'true' or constante =='false': # Si es float, int, char o string
			dir_mem = tabla_func['global']['tabla_var'][constante]['dir_mem']
			tipo = tabla_func['global']['tabla_var'][constante]['tipo']
			#if constante[0] == '_': #Si es string o char
				#constante = constante.replace(" ", '_') # Remplaza los espacios en blanco con '_' debido a que se usa split con espacios en blancos en maquina virtual
			contenido += constante + " " + str(tipo) + " " + str(dir_mem) + "\n"
		else: # Son variables globales
			nombre = constante
			dir_mem = tabla_func['global']['tabla_var'][constante]['dir_mem']
			tipo = tabla_func['global']['tabla_var'][constante]['tipo']
			globales += nombre + " " + str(dir_mem) + " " + str(tipo) + "\n"


	contenido += "#\n"
	contenido += globales
	contenido += "#\n"

	# Agrega cuadruplos
	for i in range(0, len(cuadruplos)):
		for j in range(0, len(cuadruplos[i])):
			contenido += str(cuadruplos[i][j])
			if j < len(cuadruplos[i])-1:
				contenido += " "

		contenido += "\n"
	contenido += "$"

	objFile.write(contenido)

	objFile.close()

#######################################################

# Construye el parser y el scanner
import ply.yacc as yacc
yacc.yacc()

while True:
    try:
    	#tabla_func = dict()
    	# Inicializa en 0, lo cual significa que es aprobado
    	aprobado = 0
    	# Lee de un archivo
    	archivo = raw_input('Escribe el nombre del archivo con extension .txt: ')
    	f = open(archivo, 'r')
    	s = ""
    	for line in f:
    		s += line
    except EOFError:
        break
    # Lo parsea
    yacc.parse(s, tracking=True)
    # Si fue aprobado despliega "Aprobado"
    print(s)
    if aprobado == 0:
    	print("Aprobado\n")
    	imprime_cuadruplo()
    	print(cuadruplos)
    	#imprime_tabla_func()
    	print(tabla_func)

    	archivo = archivo.split(".", 1)[0] # Quita el .txt del archivo inicial a compilar
    	genera_archivo_obj(archivo)
    f.close()
