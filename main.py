#:::::::::::::::::::::::::::NUESTRA API EN FLASK ::::::::::::::::::::::::::::::::
#Vamos a utilizar 3 librerías

#Flask es un framework minimalista escrito en Python que permite crear aplicaciones 
# web rápidamente y con un mínimo número de líneas de código. 
#En si es para la construccion de la API
# • Jsonifi para convertir array en Json
# • Request para poder recibir info,

from flask import Flask, jsonify, request
#flask_cors que es para permitir que el Front End se comunique con la API
from flask_cors import CORS
#json porque necesitamos mover objetos JSON
import json

import re
import xml.etree.ElementTree as ET
# https://www.josedomingo.org/pledin/2015/01/trabajar-con-ficheros-xml-desde-python_1/
from xml.etree import ElementTree
from xml.dom import minidom




#Objetos
from evento import Evento





eventos = []
fechas = []




def Leer_xml_original(ruta):

    archivo_valido = True 
    try:
        archivo_xml = ET.parse(ruta)
        
    except:
        archivo_valido = False
    if archivo_valido:

        mi_doc_xml = open(ruta, "r")
        cadena = ""
        for linea in mi_doc_xml:
            cadena = cadena + str(linea)

        if cadena == "":
            return "ERROR: Documento vacío"
        else:
     
            mi_doc_xml = open("entrada_leida.xml", "w")                    
            mi_doc_xml.write(str(cadena))
            return str(cadena)

    else : 
        return "ERROR: Documento no válido"
              
def leer_xml():
    ruta = "entrada_leida.xml"
    archivo_valido = True 
    try:
        archivo_xml = ET.parse(ruta)
    except:
        archivo_valido = False
    if archivo_valido:

        #Obtenemos raiz del xml, ese nos permitirá ubicarnos y obtener la info
        # del xml 
        raiz = archivo_xml.getroot()
        for elemento in raiz:
            extraer_datos(elemento.text)

    else : 
        return "Documento no válido"

def extraer_datos(cadena):

    if "Reportado por:" in cadena and "Usuarios afectados:" in cadena and "Error:" in cadena and " - " in cadena:
        f1 = cadena.split("Reportado por:")
        parte1 = f1[0]
        f2 = f1[1].split("Usuarios afectados:")
        parte2 = f2[0]
        f3 = f2[1].split("Error:")
        parte3 = f3[0]
        f4 = f3[1].split(" - ")
        parte4 = f4[0]
        parte5 = f4[1]

        if len(f1) == 2 and len(f2) == 2 and len(f3) == 2 and len(f4) == 2 :

            #Acá empezamos con las expresiones regulares
            # • Fecha
            match_fecha = re.findall('[0-3][0-9]/[0-1][0-9]/[0-9][0-9][0-9][0-9]', parte1) 
            # • Correos de los usuarios que reportaron el error
            match_correo1 = re.findall('[\w]+@[\w]*[.|\w]+', parte2) 
            # • Correos de los usuarios afectados por el error
            match_correo2 = re.findall('[\w]+@[\w]*[.|\w]+', parte3) 
            # • Código del error
            match_error = re.findall('[0-9]+', parte4)
            # • Palabras 
            match_palabra = re.findall('[\S]+', parte5)

            descripcion = ""
            for i in range(len(match_palabra)):
                if i > 0:
                    descripcion = descripcion + " " + match_palabra[i]
                else:
                    descripcion = match_palabra[i]

            if match_fecha and match_correo1 and match_correo2 and match_error and match_palabra:
                if len(match_fecha) == 1 and len(match_correo1) == 1 and len(match_error) == 1:

                    nuevo_evento = Evento(match_fecha[0], match_correo1[0], match_correo2, match_error[0], descripcion)
                    eventos.append(nuevo_evento)

                    if match_fecha[0] in fechas:
                        pass
                    else: 
                        fechas.append(match_fecha[0])

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def escribir_xml():
    estadisticas = ET.Element('ESTADISTICAS')
    fechas.sort()
    for i in range(len(fechas)):
        usuarios_con_mensaje = []
        usuarios_afectados = []
        errores_registrados = []
        mensajes = 0
        estadistica = ET.SubElement(estadisticas, 'ESTADISTICA')
        dato = ET.SubElement(estadistica, 'FECHA')
        dato.text= fechas[i]
        for e in range(len(eventos)):
            # Cantidad de mensajes
            if eventos[e].getFecha() == fechas[i]:
                mensajes += 1

                # Reportado por
                if len(usuarios_con_mensaje) == 0 :
                    datos_usuario = [str(eventos[e].getUsuario()) , 1]
                    usuarios_con_mensaje.append(datos_usuario)
                else:
                    usuario_registrado = False
                    for a in range(len(usuarios_con_mensaje)):
                        auxiliar = usuarios_con_mensaje[a]
                        if auxiliar[0] == eventos[e].getUsuario():
                            usuario_registrado = True
                            break

                    if usuario_registrado:
                        usuar = usuarios_con_mensaje[a]
                        usuar[1] = usuar[1] + 1
                    else:
                        datos_usuario = [str(eventos[e].getUsuario()) , 1]
                        usuarios_con_mensaje.append(datos_usuario)
        
                # Afectados
                aux2 = eventos[e].getAfectados()
                for u in range(len(aux2)):
                    if aux2[u] in usuarios_afectados:
                        pass
                    else:
                        usuarios_afectados.append(aux2[u])

                # Errores [codigo, cantidad]
                if len(errores_registrados) == 0 :
                    error = [str(eventos[e].getCodigo_error()) , 1]
                    errores_registrados.append(error)
                else:
                    err_registrado = False
                    for w in range(len(errores_registrados)):
                        aux_3 = errores_registrados[w]
                        if aux_3[0] == eventos[e].getCodigo_error():
                            err_registrado = True
                            break
                    if err_registrado:
                        error = errores_registrados[w]
                        error[1] = error[1] + 1
                    else:
                        error = [str(eventos[e].getCodigo_error()) , 1]
                        errores_registrados.append(error)

        # Escribiendo la info en el xml   
        cantidad_mensajes = ET.SubElement(estadistica, 'CANTIDAD_MENSAJES')
        cantidad_mensajes.text = str(mensajes)

        usuarios_reportando = ET.SubElement(estadistica, 'REPORTADO_POR')

        for o in range(len(usuarios_con_mensaje)):
            usuario = ET.SubElement(usuarios_reportando, 'USUARIO')
            user = usuarios_con_mensaje[o]
            correo = ET.SubElement(usuario, 'EMAIL')
            correo.text = str(user[0])
            cantidad = ET.SubElement(usuario, 'CANTIDAD_MENSAJES')
            cantidad.text = str(user[1])

        usuarios_afectados.sort()
        afectados = ET.SubElement(estadistica, 'AFECTADOS')
        for q in range(len(usuarios_afectados)):
            afectado = ET.SubElement(afectados, 'AFECTADO')
            afectado.text = str(usuarios_afectados[q])

        errores_ = ET.SubElement(estadistica, 'ERRORES')
        errores_registrados.sort()
        for r in range(len(errores_registrados)):
            aux4 = errores_registrados[r]
            err = ET.SubElement(errores_, 'ERROR')
            error_code = ET.SubElement(err, 'CODIGO')
            error_code.text = str(aux4[0])
            error_cantidad = ET.SubElement(err, 'CANTIDAD_MENSAJES')
            error_cantidad.text = str(aux4[1])

    mi_doc = prettify(estadisticas)        
    mi_doc_xml = open("salida.xml", "w")                    
    mi_doc_xml.write(str(mi_doc))
    return str(mi_doc)
        





#Variable = Flask(__name__) 
app = Flask(__name__)

#CORS(variable) habilita los CORS es para el FrontEnd
CORS(app)

@app.route('/Leer_Documento', methods=['POST'])
def Entrada():
    ruta = request.json['ruta']
    cadena = Leer_xml_original(ruta)

    if cadena == "Documento no válido" or cadena == "ERROR: Documento vacío":
        mensaje = {'message': 'Failed'}
        respuesta = jsonify(mensaje)

    else:

        mensaje = {'message': 'Success',
                    'cadena': cadena
                    }
        respuesta = jsonify(mensaje)
    
    return respuesta

        


@app.route('/Generar_Estadisticas', methods=['GET'])
def Leer_Documento():

    if leer_xml() == "Documento no válido":
        mensaje = {'message': 'Failed'}
        respuesta = jsonify(mensaje)

    else :    
        cadena = escribir_xml()
        if cadena == "":
            mensaje = {'message': 'Failed'}
            respuesta = jsonify(mensaje)
        else :
            mensaje = {'message': 'Success',
                        'cadena': cadena
            }
            respuesta = jsonify(mensaje)
            print(cadena)
    return respuesta





@app.route('/Filtro_error/<string:error_buscado>', methods=['GET'])

def filtar_fecha_error(error_buscado):

    archivo_valido = True 

    try:
        archivo_xml = ET.parse("salida.xml")
    except:
        archivo_valido = False
            
    if archivo_valido:

        Datos = []

    #Obtenemos raiz del xml, ese nos permitirá ubicarnos y obtener la info
    # del xml 
        raiz = archivo_xml.getroot()
        for elemento in raiz:
            errores = elemento[4]
            for error in errores:
                if error[0].text == error_buscado:

                    Dato = {
                    elemento[0].text : error[1].text
                    }
                    Datos.append(Dato)
                    break

        if len(Datos) == 0:
            mensaje = {'message': 'No encontrado'}
            respuesta = jsonify(mensaje)

        else:
            auxiliar3 = {
                'message': 'Success',
                'fechas' : Datos
            }
            respuesta = jsonify(auxiliar3)

        return (respuesta)

    else:
        mensaje = {'message': 'Failed'}
        respuesta = jsonify(mensaje)
        return respuesta
    

@app.route('/Filtro_fecha', methods=['POST'])

def filtar_fecha_usuario():
    fecha_buscada = request.json['fecha']
    archivo_valido = True 
    fechas = []
    try:
        archivo_xml = ET.parse("salida.xml")
    except:
        archivo_valido = False
            
    if archivo_valido:

        #Obtenemos raiz del xml, ese nos permitirá ubicarnos y obtener la info
        # del xml 
        raiz = archivo_xml.getroot()
        for elemento in raiz:
            fecha_actual = elemento[0].text
            if fecha_actual == fecha_buscada:
                usuarios = elemento[2]
                for usuario in usuarios:
                    fechas.append(usuario[0].text)
        if len(fechas) == 0:
            mensaje = {'message': 'No encontrado'}
            respuesta = jsonify(mensaje)
        else:
            auxiliar3 = {
                'message': 'Success',
                'fechas' : fechas
                }
            respuesta = jsonify(auxiliar3)


    else:
        mensaje = {'message': 'Failed'}
        respuesta = jsonify(mensaje)
    
    return respuesta

@app.route('/Reset', methods=['GET'])
def estado_inicial():
    eventos = []
    fechas = []
    salida = open("salida.xml", "w")                    
    salida.write("")
    entrada_leida = open("entrada_leida.xml", "w")                    
    entrada_leida.write("")

    mensaje = {'message': 'Success'}
    respuesta = jsonify(mensaje)
    
    return respuesta




if __name__ == "__main__":
    app.run( threaded=True, host="0.0.0.0", port=3000, debug=True)