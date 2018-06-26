# -*- coding: utf-8 -*-

from qgis.core import QGis, QgsVectorLayer, QgsVectorLayer, QgsMapLayerRegistry, QgsFeature, QgsField, QgsGeometry, QGis, QgsSimpleMarkerSymbolLayerV2, QgsLineSymbolV2, QgsMarkerSymbolV2, QgsMarkerLineSymbolLayerV2, QgsSimpleMarkerSymbolLayerBase, QgsSingleSymbolRendererV2
from PyQt4.QtGui import QIcon, QAction, QColor
from PyQt4.QtCore import QObject, SIGNAL, QVariant
from PyQt4.QtSql import QSqlDatabase, QSqlQuery
import resources_rc  
from qgis.gui import QgsMessageBar
from DsgTools.dsgEnums import DsgEnums

class StartOutofBoundsAngles:

    def __init__(self, iface):
        
        self.iface = iface

        self.Schema = 'edgv'
        self.geometryColumn = 'geom'
        self.keyColumn = 'id'

    def initGui(self): 
        # cria uma ação que iniciará a configuração do plugin 
        pai = self.iface.mainWindow()
        icon_path = ':/plugins/StartOutofBoundsAngles/icon.png'
        self.action = QAction (QIcon (icon_path),u"Acessa banco de dados para encontrar anglos fechados.", pai)
        self.action.setObjectName ("Start database")
        self.action.setStatusTip(None)
        self.action.setWhatsThis(None)
        self.action.triggered.connect(self.run)
        # Adicionar o botão icone
        self.iface.addToolBarIcon (self.action) 

    def unload(self):
        # remove o item de ícone do QGIS GUI.
        self.iface.removeToolBarIcon (self.action)
        
        
    def run(self):

    ##################################
    ###### PEGA A LAYER ATIVA ########
    ##################################

        layer = self.iface.activeLayer() 

        if not layer:
            self.iface.messageBar().pushMessage("Erro", u"Esperando uma Active Layer!", level=QgsMessageBar.CRITICAL, duration=4)
            return
        if layer.featureCount() == 0:
            self.iface.messageBar().pushMessage("Erro", u"a camada não possui feições!", level=QgsMessageBar.CRITICAL, duration=4)
            return

        parametros = layer.source().split(" ") # recebe todos os parametros em uma lista ( senha, porta, password etc..)

    ####################################
    ###### INICIANDO CONEXÃO DB ########
    ####################################

        # Outra opção para isso, seria usar ex: self.dbname.. self.host.. etc.. direto dentro do laço for.
        dbname = "" 
        host = ""
        port = 0
        user = ""
        password = ""

        for i in parametros:
            part = i.split("=")
            
        # Recebe os parametros guardados na própria Layer

            if "dbname" in part[0]:
                dbname = part[1].replace("'", "")

            elif "host" in part[0]:
                host = part[1].replace("'", "")

            elif "port" in part[0]:
                port = int(part[1].replace("'", ""))

            elif "user" in part[0]:
                user = part[1].replace("'", "")

            elif "password" in part[0]:
                password = part[1].split("|")[0].replace("'", "")

        print dbname, host, port, user, password



        def insertFrame(self,scale,mi,inom,frame,srid,geoSrid, paramDict = dict()):
        paramKeys = paramDict.keys()
        if 'tableSchema' not in paramKeys:
            tableSchema = 'public'
        else:
            tableSchema = paramDict['tableSchema']
        if 'tableName' not in paramKeys:
            tableName = 'aux_moldura_a'
        else:
            tableName = paramDict['tableName']
        if 'miAttr' not in paramKeys:
            miAttr = 'mi'
        else:
            miAttr = paramDict['miAttr']
        if 'inomAttr' not in paramKeys:
            inomAttr = 'inom'
        else:
            inomAttr = paramDict['inomAttr']
        if 'geom' not in paramKeys:
            geometryColumn = 'geom'
        else:
            geometryColumn = paramDict['geom']
        if 'geomType' not in paramKeys:
            geomType = 'MULTIPOLYGON'
        else:
            geomType = paramDict['geomType']

        if geomType == 'MULTIPOLYGON':
            sql = """INSERT INTO "{5}"."{6}" ({7},{8},{9}) VALUES ('{0}','{1}',ST_Transform(ST_SetSRID(ST_Multi('{2}'),{3}), {4}))""".format(mi, inom, frame, geoSrid, srid, tableSchema, tableName, miAttr, inomAttr, geometryColumn)
        else:
            sql = """INSERT INTO "{5}"."{6}" ({7},{8},{9}) VALUES ('{0}','{1}',ST_Transform((ST_SetSRID( (ST_Dump('{2}')).geom,{3})), {4}))""".format(mi, inom, frame, geoSrid, srid, tableSchema, tableName, miAttr, inomAttr, geometryColumn)
        return sql



        # Testa se os parametros receberam os valores pretendidos, caso não, apresenta a mensagem informando..
        if len(dbname) == 0 or len(host) == 0 or port == 0 or len(user) == 0 or len(password) == 0:
            self.iface.messageBar().pushMessage("Erro", u'Um dos parametros não foram devidamente recebidos!', level=QgsMessageBar.CRITICAL, duration=4)
            return

    ####################################
    #### SETA VALORES DE CONEXÃO DB ####
    ####################################

        connection = QSqlDatabase.addDatabase('QPSQL')
        connection.setHostName(host)
        connection.setPort(port)
        connection.setUserName(user)
        connection.setPassword(password)
        connection.setDatabaseName(dbname)

        if not connection.isOpen(): # Testa se a conexão esta recebendo os parametros adequadamente.
            if not connection.open():
                print 'Error connecting to database!'
                self.iface.messageBar().pushMessage("Erro", u'Error connecting to database!', level=QgsMessageBar.CRITICAL, duration=4)
                print connection.lastError().text()
                return

    ####################################
    ###### CRIAÇÃO DE MEMORY LAYER #####
    ####################################
        ProcessName, ClassName = range(2) # copiado do dsgEnums.py
        layerCrs = layer.crs().authid() # Passa o formato (epsg: numeros)

        flagsLayerName = layer.name() + "_flags"
        flagsLayerExists = False

        for l in QgsMapLayerRegistry.instance().mapLayers().values(): # Recebe todas as camadas que estão abertas
            if l.name() == flagsLayerName: # ao encontrar o nome pretendido..
                self.flagsLayer = l # flagslayer vai receber o nome..
                self.flagsLayerProvider = l.dataProvider()
                flagsLayerExists = True # se encontrado os parametros buscados, recebe True.
                break
        
        if flagsLayerExists == False: # se não encontrado os parametros buscados, recebe False.
            tempString = "Point?crs="
            tempString += str(layerCrs)

            self.flagsLayer = QgsVectorLayer(tempString, flagsLayerName, "memory")
            self.flagsLayerProvider = self.flagsLayer.dataProvider()
            self.flagsLayerProvider.addAttributes([QgsField("id", QVariant.Int), QgsField("motivo", QVariant.String)])
            self.flagsLayer.updateFields()

        self.flagsLayer.startEditing()
        ids = [feat.id() for feat in self.flagsLayer.getFeatures()]
        self.flagsLayer.deleteFeatures(ids)
        self.flagsLayer.commitChanges()
        
        lista_fid = [] # Iniciando lista
        for f in layer.getFeatures():
            lista_fid.append(str(f.id())) # Guarda na lista. A lista de Feature ids passa tipo "int", foi convertido e guardado como "str".

        source = layer.source().split(" ")
        self.tableName = "" # Inicia vazio
        layerExistsInDB = False
        
        for i in source:
                
            if "table=" in i or "layername=" in i: # Se encontrar os atributos pretendidos dentre todos do for
                self.tableName = source[source.index(i)].split(".")[1] # Faz split em ponto e pega a segunda parte.
                self.tableName = self.tableName.replace('"', '')
                layerExistsInDB = True
                break
             
        if layerExistsInDB == False:
            self.iface.messageBar().pushMessage("Erro", u"Provedor da camada corrente não provem do banco de dados!", level=QgsMessageBar.CRITICAL, duration=4)
            return

        
        
         
        if 'LINESTRING' in self.geomType:
            
        # Busca através do SQL 
            sql = """
            WITH result AS (SELECT points."{4}", points.anchor, (degrees
                                        (
                                            ST_Azimuth(points.anchor, points.pt1) - ST_Azimuth(points.anchor, points.pt2)
                                        )::decimal + 360) % 360 as angle
                        FROM
                        (SELECT
                              ST_PointN("{3}", generate_series(1, ST_NPoints("{3}")-2)) as pt1, 
                              ST_PointN("{3}", generate_series(2, ST_NPoints("{3}")-1)) as anchor,
                              ST_PointN("{3}", generate_series(3, ST_NPoints("{3}"))) as pt2,
                              linestrings."{4}" as "{4}"
                            FROM
                              (SELECT "{4}" as "{4}", (ST_Dump("{3}")).geom as "{3}"
                               FROM only "{0}"."{1}"
                               ) AS linestrings WHERE ST_NPoints(linestrings."{3}") > 2 ) as points)
            select distinct "{4}", anchor, angle from result where (result.angle % 360) < {2} or result.angle > (360.0 - ({2} % 360.0)) and {3} in ({5}) as {2}""".format( tableSchema, tableName, angle, geometryColumn, keyColumn,",".join(lista_fid))
        
        elif  'POLYGON' in geomType:
            sql = """
            WITH result AS (SELECT points."{4}", points.anchor, (degrees
                                        (
                                            ST_Azimuth(points.anchor, points.pt1) - ST_Azimuth(points.anchor, points.pt2)
                                        )::decimal + 360) % 360 as angle
                        FROM
                        (SELECT
                              ST_PointN("{3}", generate_series(1, ST_NPoints("{3}")-1)) as pt1,
                              ST_PointN("{3}", generate_series(1, ST_NPoints("{3}")-1) %  (ST_NPoints("{3}")-1)+1) as anchor,
                              ST_PointN("{3}", generate_series(2, ST_NPoints("{3}")) %  (ST_NPoints("{3}")-1)+1) as pt2,
                              linestrings."{4}" as "{4}"
                            FROM
                              (SELECT "{4}" as "{4}", (ST_Dump(ST_Boundary(ST_ForceRHR((ST_Dump("{3}")).geom)))).geom as "{3}"
                               FROM only "{0}"."{1}"
                               ) AS linestrings WHERE ST_NPoints(linestrings."{3}") > 2 ) as points)
            select distinct "{4}", anchor, angle from result where (result.angle % 360) < {2} or result.angle > (360.0 - ({2} % 360.0)) and {3} in ({5}) as {2}""".format( tableSchema, tableName, angle, geometryColumn, keyColumn,",".join(lista_fid) )
        return sql
        query = QSqlQuery(sql)
        
        self.flagsLayer.startEditing()
        flagCount = 0 # iniciando contador que será referência para os IDs da camada de memória.

        listaFeatures = []
        while query.next():
            motivo = query.value(0)
            local = query.value(1)
            flagId = flagCount

            flagFeat = QgsFeature()
            flagGeom = QgsGeometry.fromWkt(local) # passa o local onde foi localizado o erro.
            flagFeat.setGeometry(flagGeom)
            flagFeat.initAttributes(2)
            flagFeat.setAttribute(0,flagId) # insere o id definido para a coluna 0 da layer de memória.
            flagFeat.setAttribute(1, motivo) # insere o motivo/razão pré-definida para a coluna 1 da layer de memória.
        
        # TypeError: fromWkt(QString): argument 1 has unexpected type 'long' 
        #     Traceback (most recent call last):
        #     File "/home/piangers/.qgis2/python/plugins/StartDuplic/StartDuplic.py", line 177, in run
        #     flagGeom = QgsGeometry.fromWkt(local) # passa o local onde foi localizado o erro.

            listaFeatures.append(flagFeat)    

            flagCount += 1 # incrementando o contador a cada iteração

        self.flagsLayerProvider.addFeatures(listaFeatures)
        self.flagsLayer.commitChanges() # Aplica as alterações à camada.
        
        QgsMapLayerRegistry.instance().addMapLayer(self.flagsLayer) # Adicione a camada no mapa
        
        if flagCount == 0: 
            
            QgsMapLayerRegistry.instance().removeMapLayer(self.flagsLayer.id())
            self.iface.messageBar().pushMessage("Aviso", u"Não foi encontrado Flags em \"" + layer.name() + "\" !", level=QgsMessageBar.CRITICAL, duration=4)

            return
        if len(query.lastError().text()) == 1:
            self.iface.messageBar().pushMessage("Aviso", "foram geradas " + str(flagCount) + " flags para a camada \"" + layer.name() + "\" !", level=QgsMessageBar.INFO, duration=4)
        else:
            self.iface.messageBar().pushMessage("Erro", u"a geração de flags falhou!", level=QgsMessageBar.CRITICAL, duration=4)
            print query.lastError().text()
