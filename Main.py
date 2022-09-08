from array import array
from email import message
from fastapi import FastAPI, File, UploadFile, HTTPException # HTTPException para los errores.
from typing import Optional
from typing import List
from enum import Enum
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware # Evitar problemas CORS importando con ajax.
import pyodbc #Libreria para BD.
import datetime

app = FastAPI()

# ------------ Necesario para evitar el CORS ------------ #

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------ Modelo ------------ #

class Informe(BaseModel):
    empresa: str
    resultado_usuarios: int
    resultado_expedientes: int
    resultado_sesiones: int

# ------------ Sentencias SQL ------------ #

sql_usuario = "select count(USUARIO) from lvicario.USUARIOS"
sql_siniestro = "select count(EJERCICIO) from lvicario.SINIESTROS"
sql_sesiones =  "select count(CODIGO) from lvicario.SESIONES"

#////////////////////////////// PRIMER GET /////////////////////////////////////#

@app.get("/Clientes/")
async def Cliente_Tiempo(temporalidad: str, fecha: Optional[str] = None):

    # Definir BD
    server = '' #Dirección IP de BD.
    database = 'empresas' #Nombre de la BD.
    username = '' #Usuario de BD.
    password = '' #Contraseña de BD.

    # Declarar objeto vacio para posteriormente insertar los resultados.
    Todos_los_resultados = []


    # Accedemos primero a PERIGESgeneral para sacar los nombres de las empresas que queremos a traves de la columna "CODIGO".
    try:
        cnxn = pyodbc.connect ('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)    
        cursor = cnxn.cursor()
    except:
        #Si no consigue entrar... este error.
        raise HTTPException(status_code=512, detail="La base de datos es inaccesible desde el segundo get") 


    #/////////////////////////// Temporalidad TOTAL ////////////////////////////#

    if (temporalidad == "total"):
        cursor.execute("SELECT CODIGO FROM EMPRESAS") # Location -> PERIGESgeneral/EMPRESAS/CÓDIGO (Empresas a recorrer).
        empresas = cursor.fetchone()

        while empresas:
            database = 'PERIGES'+empresas[0] # Cada empresa tiene su BD, todas empiezan con extensión PERIGES.

            # Llamando a cada BD: PERIGES + EMPRESA.
            cnxn = pyodbc.connect ('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
            recorre_bd = cnxn.cursor()

            # Ejecuta sentencias SQL en cada vuelta de bucle.
            recorre_bd.execute(sql_usuario) # Columna "USUARIOS".
            resultado_usuarios = recorre_bd.fetchone()

            recorre_bd.execute(sql_siniestro) # Columna "EJERCICIO".
            resultado_expedientes = recorre_bd.fetchone()

            recorre_bd.execute(sql_sesiones) # Columna "CODIGO".
            resultado_sesiones = recorre_bd.fetchone()

            # Insertar los resultados en el objeto vacio
            Todos_los_resultados.append({
                "nombre_empresa": empresas[0],
                "numero_usuarios":resultado_usuarios[0],
                "numero_expedientes":resultado_expedientes[0],
                "numero_sesiones":resultado_sesiones[0],
            })

            empresas = cursor.fetchone() # Fin del buble.


    #/////////////////////////// Temporalidad MENSUALES //////////////////////////#

    if (temporalidad == "mensuales" and fecha == fecha):
        cursor.execute("SELECT CODIGO FROM EMPRESAS") 
        empresas = cursor.fetchone()

        while empresas:
            database = 'PERIGES'+empresas[0] 

            cnxn = pyodbc.connect ('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
            recorre_bd = cnxn.cursor()

            recorre_bd.execute(sql_usuario)
            resultado_usuarios = recorre_bd.fetchone()

            recorre_bd.execute( sql_siniestro + " WHERE YEAR(FECHA_ENTRADA) = YEAR(""'" +fecha+ "'"") AND MONTH(FECHA_ENTRADA) = MONTH(""'" +fecha+ "'"");")
            resultado_expedientes = recorre_bd.fetchone()

            recorre_bd.execute(sql_sesiones + " WHERE YEAR(FECHA) = YEAR(""'" +fecha+ "'"") AND MONTH(FECHA) = MONTH(""'" +fecha+ "'"");") 
            resultado_sesiones = recorre_bd.fetchone()

            Todos_los_resultados.append({
                "nombre_empresa": empresas[0],
                "numero_usuarios":resultado_usuarios[0],
                "numero_expedientes":resultado_expedientes[0],
                "numero_sesiones":resultado_sesiones[0],
            })
            
            empresas = cursor.fetchone()

    #/////////////////////////// Temporalidad DIARIA ////////////////////////////#

    if (temporalidad == "diarios" and fecha == fecha):
        cursor.execute("SELECT CODIGO FROM EMPRESAS") 
        empresas = cursor.fetchone()

        while empresas:
            database = 'PERIGES'+empresas[0]

            cnxn = pyodbc.connect ('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
            recorre_bd = cnxn.cursor()

            recorre_bd.execute(sql_usuario)
            resultado_usuarios = recorre_bd.fetchone()

            recorre_bd.execute(sql_siniestro + " WHERE FECHA_ENTRADA = (""'" +fecha+ "'"");")
            resultado_expedientes = recorre_bd.fetchone()

            recorre_bd.execute("select count(CONVERT(DATE, FECHA)) from lvicario.SESIONES where CONVERT(DATE, FECHA) = (""'" +fecha+ "'"");")
            resultado_sesiones = recorre_bd.fetchone()

            Todos_los_resultados.append({
                "nombre_empresa": empresas[0],
                "numero_usuarios":resultado_usuarios[0],
                "numero_expedientes":resultado_expedientes[0],
                "numero_sesiones":resultado_sesiones[0],
            })

            empresas = cursor.fetchone()

    return Todos_los_resultados