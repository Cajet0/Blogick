import sys
import re
import numpy as np
############ PENDIENTES ############
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
# mem_temp = []

# Stack de ejecucion para trabajar con modulos
stack_ej = []

# Stack que contiene las lineas en las que me quede en ejecucion
stack_linea_ej = []

# Funcion_a_llamar se guarda al momento de hacer el ERA, utilizada para asignar el valor del argumento de una funcion al mandar un parametro
funcion_a_llamar = {}

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
		#funciones[atributos[0]] = {'tipo':int(atributos[1]), 'dir_inicio':int(atributos[2]), 'params':int(atributos[3]), 'size':int(atributos[4]), 'dir_mem':None}

	# Constantes
	# Quita la ultima y la primera casilla de hacer split con salto de linea, debido a que hay saltos de linea antes y despues de las constantes
	arr_constantes = s_constantes.rsplit("\n",1)[0].split("\n",1)[1].split("\n")

	for constante in arr_constantes:
		atributos = constante.rsplit(" ", 2)

		# Si es float
		if re.match(r'[0-9]+\.[0-9]+', atributos[0]):
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
			constantes[atributos[2]] = int(atributos[0])

	# Globales
	# Quita la ultima y la primera casilla de hacer split con salto de linea, debido a que hay saltos de linea antes y despues de las globales
	arr_globales = s_globales.rsplit("\n",1)[0].split("\n",1)[1].split("\n")
	
	for var_global in arr_globales:
		atributos = var_global.split(" ")
		mem_global[atributos[1]] = '*' # Variable sin valor
	# Cuadruplos
	# Quita la ultima y la primera casilla de hacer split con salto de linea, debido a que hay saltos de linea antes y despues de los cuadruplos
	arr_cuadruplos = s_cuadruplos.rsplit("\n",1)[0].split("\n",1)[1].split("\n")
	
	for i in range(0, len(arr_cuadruplos)):
		cuadruplo = arr_cuadruplos[i].split(" ")
		cuadruplos = np.append(cuadruplos, [[cuadruplo[0], cuadruplo[1], cuadruplo[2], cuadruplo[3]]], 0)


	print(funciones)

	# Mete el espacio del main en memoria temporal que es donde inicia el programa
	stack_ej.append({'nombre_func':'main', 'tabla_var':dict()})

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
	global linea_actual, cuadruplos, stack_ej, stack_linea_ej, funcion_a_llamar

	# Mientras no sea la ultima linea de los cuadruplos
	print("Executing...")
	while linea_actual < len(cuadruplos):
		# Obtiene el cuadruplo actual
		cuadruplo = cuadruplos[linea_actual]

		# Obtiene el top del stack
		#top_stack_ej = stack_ej[len(stack_ej)-1]
		top_stack_ej = stack_ej[len(stack_ej)-1]

		# Obtiene el operador de cuadruplos
		op = int(cuadruplo[0])
		if op == 0: # *
			# Da de alta var, y la multiplica
			val_op1 = obtiene_valor(cuadruplo[1])
			val_op2 = obtiene_valor(cuadruplo[2])
			top_stack_ej['tabla_var'][cuadruplo[3]] = val_op1 * val_op2
		elif op == 1: # /
			# Da de alta var, y la multiplica
			val_op1 = obtiene_valor(cuadruplo[1])
			val_op2 = obtiene_valor(cuadruplo[2])
			top_stack_ej['tabla_var'][cuadruplo[3]] = val_op1 / val_op2
		elif op == 2: # +
			# Da de alta var, y la suma
			val_op1 = obtiene_valor(cuadruplo[1])
			val_op2 = obtiene_valor(cuadruplo[2])
			top_stack_ej['tabla_var'][cuadruplo[3]] = val_op1 + val_op2
		elif op == 3: # -
			# Da de alta var, y la multiplica
			val_op1 = obtiene_valor(cuadruplo[1])
			val_op2 = obtiene_valor(cuadruplo[2])
			top_stack_ej['tabla_var'][cuadruplo[3]] = val_op1 - val_op2
		elif op == 4: # <
			# Da de alta var, y la multiplica
			val_op1 = obtiene_valor(cuadruplo[1])
			val_op2 = obtiene_valor(cuadruplo[2])
			top_stack_ej['tabla_var'][cuadruplo[3]] = val_op1 < val_op2
		elif op == 5: # >
			# Da de alta var, y la multiplica
			val_op1 = obtiene_valor(cuadruplo[1])
			val_op2 = obtiene_valor(cuadruplo[2])
			top_stack_ej['tabla_var'][cuadruplo[3]] = val_op1 * val_op2
		elif op == 6: # ==
			# Da de alta var, y la multiplica
			val_op1 = obtiene_valor(cuadruplo[1])
			val_op2 = obtiene_valor(cuadruplo[2])
			top_stack_ej['tabla_var'][cuadruplo[3]] = val_op1 == val_op2
		elif op == 7: # !=
			# Da de alta var, y la multiplica
			val_op1 = obtiene_valor(cuadruplo[1])
			val_op2 = obtiene_valor(cuadruplo[2])
			top_stack_ej['tabla_var'][cuadruplo[3]] = val_op1 != val_op2
		elif op == 8: # <=
			# Da de alta var, y la multiplica
			val_op1 = obtiene_valor(cuadruplo[1])
			val_op2 = obtiene_valor(cuadruplo[2])
			top_stack_ej['tabla_var'][cuadruplo[3]] = val_op1 <= val_op2
		elif op == 9: # >=
			# Da de alta var, y la multiplica
			val_op1 = obtiene_valor(cuadruplo[1])
			val_op2 = obtiene_valor(cuadruplo[2])
			top_stack_ej['tabla_var'][cuadruplo[3]] = val_op1 >= val_op2
		elif op == 10: # &&
			# Da de alta var, y la multiplica
			val_op1 = obtiene_valor(cuadruplo[1])
			val_op2 = obtiene_valor(cuadruplo[2])
			top_stack_ej['tabla_var'][cuadruplo[3]] = val_op1 and val_op2
		elif op == 11: # ||
			# Da de alta var, y la multiplica
			val_op1 = obtiene_valor(cuadruplo[1])
			val_op2 = obtiene_valor(cuadruplo[2])
			top_stack_ej['tabla_var'][cuadruplo[3]] = val_op1 or val_op2
		elif op == 12: # !
			# Da de alta var, y la multiplica
			val_op1 = obtiene_valor(cuadruplo[1])
			top_stack_ej['tabla_var'][cuadruplo[3]] = not val_op1
		elif op == 13: # =
			# Da de alta variable y le asigna valor
			# Valida si se asigna a global o local
			if scope_asignacion(cuadruplo[3]) == 'global':
				mem_global[cuadruplo[3]] = obtiene_valor(cuadruplo[1])
			else:
				top_stack_ej['tabla_var'][cuadruplo[3]] = obtiene_valor(cuadruplo[1])
		elif op == 14: # GOTO
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
			dir_memoria = int(cuadruplo[3])
			# Actualiza el valor de la funcion en mem_global
			# CAMBIAR LA DIRECCION DE MEMORIA EN MEMP_TEMP A STRING O CAMBIAR A INT EN GLOBALES
			mem_global[str(top_stack_ej['dir_mem'])] = obtiene_valor(cuadruplo[3])
			# Me salgo del scope
			stack_ej.pop()
			# Me regreso a la linea en la que me quede
			linea_actual = stack_linea_ej.pop()
		elif op == 18: # ENDPROC - Si llego al final de la funcion
			if top_stack_ej['nombre_func'] != 'main':
				if mem_global[str(top_stack_ej['dir_mem'])] == '*' and funciones[top_stack_ej['nombre_func']]['tipo'] != -1:
					print("Funcion con valor de retorno sin regresar")
					exit()
				# Me salgo del scope si no es main
				stack_ej.pop()
				#Me regreso a la linea en que me quede
				linea_actual = stack_linea_ej.pop()
			else: # Si es main, acabo el 
				exit()
		elif op == 19: # ERA
			#mem_temp[cuadruplo[3]]={'tabla_var':dict(), 'dir_mem':int(funciones[cuadruplo[3]]['dir_mem'])}
			#funcion_a_llamar = cuadruplo[3]
			funcion_a_llamar={'nombre_func':cuadruplo[3], 'tabla_var':dict(), 'dir_mem':int(funciones[cuadruplo[3]]['dir_mem'])}

		elif op == 20: # PRINT
			# Imprime variable
			print(obtiene_valor(cuadruplo[3]))
		elif op == 21: # SCAN
			scan = raw_input()
			tipo = obtiene_tipo_dir_memoria(int(cuadruplo[3]))
			# Valida el tipo de variable, valida y lo asigna de acuerdo al input
			if tipo == 0:
				try:
					top_stack_ej['tabla_var'][cuadruplo[3]] = int(float(scan))
				except ValueError:
					print("Error de ejecucion: Asignacion no entera.")
					exit()
			elif tipo == 1:
				try:
					top_stack_ej['tabla_var'][cuadruplo[3]] = float(scan)
				except ValueError:
					print("Error de ejecucion: Asignacion no flotante.")
					exit()
			elif tipo == 2:	
				if len(scan) == 1:
					top_stack_ej['tabla_var'][cuadruplo[3]] = scan
				else:
					print("Error de ejecucion: No es tipo caracter.")	
					exit()
			elif tipo == 3:
				if scan == 'true':
					top_stack_ej['tabla_var'][cuadruplo[3]] = True
				elif scan == 'false':
					top_stack_ej['tabla_var'][cuadruplo[3]] = False
				else:
					print("Error de ejecucion: Asignacion no booleana.")
					exit()
			elif tipo == 4:
				top_stack_ej['tabla_var'][cuadruplo[3]] = scan
		elif op == 22: # PARAM
			# Hacer la relacion de parametro con direccion de memoria
			#mem_temp[funcion_a_llamar]['tabla_var'][cuadruplo[3]] = obtiene_valor(cuadruplo[1])
			funcion_a_llamar['tabla_var'][cuadruplo[3]] = obtiene_valor(cuadruplo[1])
		elif op == 23: # GOSUB
			stack_ej.append(funcion_a_llamar)
			# Agrego el scope a la pila
			#stack_ej.append(cuadruplo[1])
			# Guardo la linea actual en la que llame a la funcion
			stack_linea_ej.append(linea_actual)
			# Actualizo la linea actual para ejecutar la funcion
			linea_actual=int(cuadruplo[3])-1
		linea_actual += 1

def obtiene_valor(dir_memoria):
	global mem_global, constantes, linea_actual, stack_ej
	top_stack_ej = stack_ej[len(stack_ej)-1]

	int_dir = int(dir_memoria)
	if int_dir >= 10000 and int_dir < 15000: # Si es global
		if mem_global[dir_memoria] == '*':
			print("Error ejecucion: Variable global sin previo valor.")
			exit()
		return cast_resultado(mem_global[dir_memoria], int_dir)
	elif int_dir >= 25000 and int_dir < 30000: # Si es constante
		return constantes[dir_memoria]
	else: # Si es temporal o local se considera temporal
		try:
			return cast_resultado(top_stack_ej['tabla_var'][dir_memoria], int_dir)
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