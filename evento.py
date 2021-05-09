class Evento:

    def __init__(self, fecha, usuario, afectados, codigo_error, descripcion):
        self.fecha = fecha
        self.usuario = usuario
        self.afectados = afectados
        self.codigo_error = codigo_error
        self.descripcion = descripcion

    def getFecha(self):
        return self.fecha

    def getUsuario(self):
        return self.usuario

    def getAfectados(self):
        return self.afectados
        
    def getCodigo_error(self):
        return self.codigo_error
        
    def getDescripcion(self):
        return self.descripcion