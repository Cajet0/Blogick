import sys
import re
import numpy as np
############ PENDIENTES ############
# - SI NO HAY GLOBALES DEBE SEGUIR FUNCIONANDO; TRUENA SI NO HAY GLOBALES POR EL ORDEN EN EL ARCHIVO OBJECTO
# - 
# EXTRAS:
# 	- Warning: variable no utilizada.
####################################
# Diccionario de constantes
constantes = dict()

# Diccionario de funciones
funciones = dict()

# Matriz de cuadruplos
cuadruplos = np.zeros((1,4)) # Arreglo de cuadruplos
cuadruplos = np.delete(cuadruplos, 0,0) # Quita el renglon de 0's una vez inicializado

# Linea actual de ejecucion en cuadruplos
linea_actual = 0

# Memoria global
mem_global = dict()

# Memoria temporal de las funciones
mem_temp = dict()

# Stack de ejecucion para trabajar con modulos
stack_ej = []

#id_operaciones = {'*':0, '/':1, '+':2, '-':3, '<':4, '>':5, '==':6, '!=':7, '<=':8, '>=':9, '&&':10, '||':11, '!':12, '=':13, 'GOTO':14, 'GOTOF':15, 
# 'GOTOT':16, 'RETURN':17, 'ENDPROC':18, 'ERA':19, 'PRINT':20, 'SCAN':21, 'PARAM':22,'GOSUB':23}

# Abre el archivo e inicializa las estructuras a utilizar
def load_program(objFile):
	global cuadruplos, stack_ej

	# Abre el archivo
	f = open(objFile)
	
	s = ""
	# Junta todas las lineas en un string
	for line in f:
		s += line

	# Separa por secciones de acuerdo al identificador #
	arr_s = s.split("#") 

	# Obtiene el string de funciones
	s_funciones = arr_s[0]
	# String de constantes
	s_constantes = arr_s[1]
	#String de globales
	s_globales = arr_s[2]
	# String de cuadruplos
	s_cuadruplos = arr_s[3]

	# Arreglo de funciones
	# Quita la ultima casilla de hacer split con salto de linea, debido a que hay saltos de linea despues de las funciones
	arr_funciones = s_funciones.rsplit("\n",1)[0].split("\n")

	# Accede a cada funcion y regenera la estructura
	# Funcion = nombre, tipo, dir_inicio, cat_parametros, size, dir_variable
	for funcion in arr_funciones:
		atributos = funcion.split(" ")
		funciones[atributos[0]] = {'tipo':int(atributos[1]), 'dir_inicio':int(atributos[2]), 'params':int(atributos[3]), 'size':int(atributos[4]), 'dir_mem':int(atributos[5])}

	# Constantes
	# Quita la ultima y la primera casilla de hacer split con salto de linea, debido a que hay saltos de linea antes y despues de las constantes
	arr_constantes = s_constantes.rsplit("\n",1)[0].split("\n",1)[1].split("\n")

	for constante in arr_constantes:
		atributos = constante.rsplit(" ", 2)

		# Si es float
		if re.match(r'[0-9]+\.[0-9]+', atributos[0]):
			#constantes[atributos[2]] = {'tipo':int(atributos[1]),'valor':float(atributos[0])}
			constantes[atributos[2]] = float(atributos[0])
		elif atributos[0][0] == '_': 
			# El primer caracter de la constante
			atributos[0] = atributos[0][1:]
			constantes[atributos[2]] = atributos[0]
		elif atributos[0] == 'true':
			constantes[atributos[2]] = True
		elif atributos[0] == 'false':
			constantes[atributos[2]] = False
		else: # Si es Int
			#constantes[atributos[2]] = {'tipo':int(atributos[1]),'valor':int(atributos[0])}
			constantes[atributos[2]] = int(atributos[0])

	# Globales
	# Quita la ultima y la primera casilla de hacer split con salto de linea, debido a que hay saltos de linea antes y despues de las globales
	arr_globales = s_globales.rsplit("\n",1)[0].split("\n",1)[1].split("\n")
	
	for var_global in arr_globales:
		atributos = var_global.split(" ")
		# [0] = Nombre o valor si es una, [1] = Dir_mem, [2] = Tipo
		#mem_global[atributos[1]] = {'nombre':atributos[0], 'tipo':int(atributos[2])}
		mem_global[atributos[1]] = '*' # Variable sin valor
	# Cuadruplos
	# Quita la ultima y la primera casilla de hacer split con salto de linea, debido a que hay saltos de linea antes y despues de los cuadruplos
	arr_cuadruplos = s_cuadruplos.rsplit("\n",1)[0].split("\n",1)[1].split("\n")
	
	for i in range(0, len(arr_cuadruplos)):
		cuadruplo = arr_cuadruplos[i].split(" ")
		cuadruplos = np.append(cuadruplos, [[cuadruplo[0], cuadruplo[1], cuadruplo[2], cuadruplo[3]]], 0)


	print(funciones)

	# Mete el espacio del main en memoria temporal que es donde inicia el programa
	#mem_temp['main'] = {'tabla_var':dict(), 'dir_mem':funciones['main']['dir_mem']}
	mem_temp['main'] = {'tabla_var':dict()}
	# Mete la funcion main al stack de ejecucion
	stack_ej.append('main')

	print(cuadruplos)
	print(constantes)
	print(mem_global)
	f.close()

# Corre el load y el execute
def run_program(objFile):
	load_program(objFile)
	execute_program()

# Ejecuta el programa
def execute_program():
	global linea_actual, cuadruplos, stack_ej
	# Mientras no sea la ultima linea de los cuadruplos
	#id_operaciones = {'*':0, '/':1, '+':2, '-':3, '<':4, '>':5, '==':6, '!=':7, '<=':8, '>=':9, '&&':10, '||':11, '!':12, '=':13, 'GOTO':14, 'GOTOF':15, 
	#'GOTOT':16, 'RETURN':17, 'ENDPROC':18, 'ERA':19, 'PRINT':20, 'SCAN':21, 'PARAM':22,'GOSUB':23}


	print("Executing...")
	while linea_actual < len(cuadruplos):
		# Obtiene el cuadruplo actual
		cuadruplo = cuadruplos[linea_actual]

		# Obtiene el top del stack
		top_stack_ej = stack_ej[len(stack_ej)-1]

		# Obtiene el operador de cuadruplos
		op = int(cuadruplo[0])
		if op == 0: # *
			# Da de alta var, y la multiplica
			val_op1 = obtiene_valor(cuadruplo[1])
			val_op2 = obtiene_valor(cuadruplo[2])
			mem_temp[top_stack_ej]['tabla_var'][cuadruplo[3]] = val_op1*val_op2
		elif op == 1: # /
			# Da de alta var, y la multiplica
			val_op1 = obtiene_valor(cuadruplo[1])
			val_op2 = obtiene_valor(cuadruplo[2])
			mem_temp[top_stack_ej]['tabla_var'][cuadruplo[3]] = val_op1/val_op2
		elif op == 2: # +
			# Da de alta var, y la suma
			val_op1 = obtiene_valor(cuadruplo[1])
			val_op2 = obtiene_valor(cuadruplo[2])
			mem_temp[top_stack_ej]['tabla_var'][cuadruplo[3]] = val_op1+val_op2
		elif op == 3: # -
			# Da de alta var, y la multiplica
			val_op1 = obtiene_valor(cuadruplo[1])
			val_op2 = obtiene_valor(cuadruplo[2])
			mem_temp[top_stack_ej]['tabla_var'][cuadruplo[3]] = val_op1-val_op2
		elif op == 4: # <
			# Da de alta var, y la multiplica
			val_op1 = obtiene_valor(cuadruplo[1])
			val_op2 = obtiene_valor(cuadruplo[2])
			mem_temp[top_stack_ej]['tabla_var'][cuadruplo[3]] = val_op1<val_op2
		elif op == 5: # >
			# Da de alta var, y la multiplica
			val_op1 = obtiene_valor(cuadruplo[1])
			val_op2 = obtiene_valor(cuadruplo[2])
			mem_temp[top_stack_ej]['tabla_var'][cuadruplo[3]] = val_op1>val_op2
		elif op == 6: # ==
			# Da de alta var, y la multiplica
			val_op1 = obtiene_valor(cuadruplo[1])
			val_op2 = obtiene_valor(cuadruplo[2])
			mem_temp[top_stack_ej]['tabla_var'][cuadruplo[3]] = val_op1==val_op2
		elif op == 7: # !=
			# Da de alta var, y la multiplica
			val_op1 = obtiene_valor(cuadruplo[1])
			val_op2 = obtiene_valor(cuadruplo[2])
			mem_temp[top_stack_ej]['tabla_var'][cuadruplo[3]] = val_op1!=val_op2
		elif op == 8: # <=
			# Da de alta var, y la multiplica
			val_op1 = obtiene_valor(cuadruplo[1])
			val_op2 = obtiene_valor(cuadruplo[2])
			mem_temp[top_stack_ej]['tabla_var'][cuadruplo[3]] = val_op1<=val_op2
		elif op == 9: # >=
			# Da de alta var, y la multiplica
			val_op1 = obtiene_valor(cuadruplo[1])
			val_op2 = obtiene_valor(cuadruplo[2])
			mem_temp[top_stack_ej]['tabla_var'][cuadruplo[3]] = val_op1>=val_op2
		elif op == 10: # &&
			# Da de alta var, y la multiplica
			val_op1 = obtiene_valor(cuadruplo[1])
			val_op2 = obtiene_valor(cuadruplo[2])
			mem_temp[top_stack_ej]['tabla_var'][cuadruplo[3]] = val_op1 and val_op2
		elif op == 11: # ||
			# Da de alta var, y la multiplica
			val_op1 = obtiene_valor(cuadruplo[1])
			val_op2 = obtiene_valor(cuadruplo[2])
			mem_temp[top_stack_ej]['tabla_var'][cuadruplo[3]] = val_op1 or val_op2
		elif op == 12: # !
			# Da de alta var, y la multiplica
			val_op1 = obtiene_valor(cuadruplo[1])
			mem_temp[top_stack_ej]['tabla_var'][cuadruplo[3]] = not val_op1
		elif op == 13: # =
			# Da de alta variable y le asigna valor
			# Valida si se asigna a global o local
			if scope_asignacion(cuadruplo[3]) == 'global':
				#print(mem_global)
				mem_global[cuadruplo[3]] = obtiene_valor(cuadruplo[1])
				#print(mem_global)
			else:
				mem_temp[top_stack_ej]['tabla_var'][cuadruplo[3]] = obtiene_valor(cuadruplo[1])
		elif op == 14: # GOTO
			# Agrega la funcion main al stack de ejecucion de funciones
			# stack_ej.append(mem_global[])
			# Se va a la linea indicada del MAIN
			linea_actual = int(cuadruplo[3])-1
		elif op == 15: # GOTOF
			# Si la condicion es falsa hace el salto de linea
			val_condicion = obtiene_valor(cuadruplo[1])
			if not val_condicion:
				linea_actual = int(cuadruplo[3])-1
		elif op == 16: # GOTOT
			# Si la condicion es verdadera hace el salto de linea
			val_condicion = obtiene_valor(cuadruplo[1])
			if val_condicion:
				linea_actual = int(cuadruplo[3])-1
		elif op == 17: # RETURN
			x=""
		elif op == 18: # ENDPROC
			x=""
		elif op == 19: # ERA
			mem_temp[cuadruplo[3]]={'tabla_var':dit(), 'dir_mem':int(funciones[cuadruplo[3]]['dir_mem'])}
		elif op == 20: # PRINT
			# Imprime variable
			print(obtiene_valor(cuadruplo[3]))
		elif op == 21: # SCAN
			x=""
		elif op == 22: # PARAM
			# Hacer la relacion de parametro con direccion de memoria
			mem_temp[top_stack_ej]['tabla_var'][cuadruplo[3]] = 
		elif op == 23: # GOSUB
			stack_ej.append(cuadruplo[1])
			linea_actual=int(cuadruplo[3])-1
		linea_actual += 1
#'GOTOT':16, 'RETURN':17, 'ENDPROC':18, 'ERA':19, 'PRINT':20, 'SCAN':21, 'PARAM':22,'GOSUB':23}

def obtiene_valor(dir_memoria):
	global mem_global, constantes, linea_actual, stack_ej
	top_stack_ej = stack_ej[len(stack_ej)-1]

	int_dir = int(dir_memoria)
	if int_dir >= 10000 and int_dir < 15000: # Si es global
		if mem_global[dir_memoria] == '*':
			#print(linea_actual)
			#print(mem_global)
			print("Error ejecucion: Variable global sin previo valor.")
			exit()
		return cast_resultado(mem_global[dir_memoria], int_dir)
	elif int_dir >= 25000 and int_dir < 30000: # Si es constante
		return constantes[dir_memoria]
	else: # Si es temporal o local se considera temporal
		try:
			return cast_resultado(mem_temp[top_stack_ej]['tabla_var'][dir_memoria], int_dir)
		except KeyError:
			print("Error ejecucion: Variable local sin previo valor.")
			exit()

# Obtiene el tipo(int,float,char,bool,string) de la variable 
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

# Funcion que transforma el resultado al tipo de variable en la asignacion
def cast_resultado(valor, dir_memoria):
	tipo = obtiene_tipo_dir_memoria(dir_memoria)
	
	if tipo == 0:
		return int(valor)
	elif tipo == 1:
		return float(valor)
	else:
		return valor

def scope_asignacion(dir_memoria):
	int_dir = int(dir_memoria)
	if int_dir >= 10000 and int_dir < 15000: # Si es global
		return 'global'
	elif int_dir < 20000: # Si es local
		return 'temporal'
# Main que contiene los argumentos
def main(argv):
	run_program(argv[1])
	return 0

#if __name__ == '__main__':
main(sys.argv)