from django.db import models
from django.contrib.auth.models import User

# Create your models here

opcionesEstadoProyecto =[
     ('PL', 'Planeación'),
     ('P', 'En Proceso'),
     ('C', 'Completado')
    ]

class Project(models.Model):    #Para llamar a la clase modelo y usar sus metodos(CharField)
    nombre = models.TextField(
        "Nombre", #verbose_name (nombre que se ve en el texfield antes de escribir) 
        max_length= 255, 
        blank= False, #que no acepte en blanco
        null= False, #que no acepte nulo
        help_text= "Nombre del Proyecto a crear" #texto de ayuda
    )
    descripcion = models.TextField(
        "Descripcion",#Ya se toma por defecto que es el verbose_name
        max_length= 255,
        blank= False,
        null= False,
        help_text= "Descripcion del Proyecto a crear"
    )
    estado = models.CharField(
        "Estado",
        max_length= 2,
        choices=opcionesEstadoProyecto,
        default= 'PL',
    )
    #llave foranea con usuario
    usuario = models.ForeignKey (
        User,
        on_delete= models.CASCADE, #Si el usuario es eliminado se eliminaran todos los proyectos del usuario
        related_name= 'usuarioProyecto' #Nos permite acceder a todos los proyectos de un usuario
        )

    def __str__(self):
        return f"Proyecto {self.descripcion[:35]}..." # Muestra una parte de la descripcion del proyecta
    tecnico = models.ForeignKey (
        User,
        on_delete= models.CASCADE, #Si el usuario es eliminado se eliminaran todos los proyectos del usuario
        related_name= 'tecnicoProyecto' #Nos permite acceder a todos los proyectos de un usuario
        )

    def __str__(self):
        return f"Proyecto {self.descripcion[:35]}..."


