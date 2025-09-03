# Importamos las clases necesarias de Django
from django.db import models                     # Contiene todos los tipos de campos (CharField, TextField, etc.)
from django.contrib.auth.models import User      # Importamos el modelo de usuarios que ya viene con Django

# Definimos las opciones que podrá tener el campo "estado" del proyecto
# Cada tupla tiene (valor_guardado, valor_mostrado)
# - 'PL' se guarda en la BD y "Planeación" es lo que se muestra al usuario
# - 'P' se guarda y se muestra como "En Proceso"
# - 'C' se guarda y se muestra como "Completado"
opcionesEstadoProyecto = [
    ('PL', 'Planeación'),
    ('P', 'En Proceso'),
    ('C', 'Completado'),
]

# Definimos la clase Project, que hereda de models.Model
# Esto significa que será una tabla en la base de datos
class Project(models.Model):

    # Campo "nombre" del proyecto
    # Usamos TextField porque puede tener textos largos, aunque también se podría usar CharField
    # - verbose_name = texto descriptivo que verá el usuario en formularios
    # - max_length = cantidad máxima de caracteres
    # - blank y null = indican que este campo es obligatorio (False)
    # - help_text = texto de ayuda que aparece en formularios
    nombre = models.CharField(
        "Nombre",
        max_length=255,
        blank=False,
        null=False,
        help_text="Nombre del Proyecto a crear"
    )

    # Campo "descripcion" del proyecto
    # Similar a "nombre", pero aquí se describe el proyecto con más detalle
    # También es obligatorio y con un máximo de 255 caracteres
    descripcion = models.CharField(
        "Descripción",
        max_length=255,
        blank=False,
        null=False,
        help_text="Descripción del Proyecto a crear"
    )

    # Campo "estado" del proyecto
    # Es un CharField (cadena corta), con máximo 2 caracteres
    # Se restringe a las opciones definidas en "opcionesEstadoProyecto"
    # Tiene un valor por defecto: 'PL' (Planeación)
    estado = models.CharField(
        "Estado",
        max_length=2,
        choices=opcionesEstadoProyecto,
        default='PL',
    )

    # Relación con el modelo User (usuario dueño del proyecto)
    # - ForeignKey crea una relación de muchos proyectos → un solo usuario
    # - on_delete=models.CASCADE significa que si el usuario se borra, también se borran sus proyectos
    # - related_name nos da un nombre más claro para acceder desde User (user.usuarioProyecto.all())
    usuario = models.ForeignKey(
        User,
        on_delete= models.CASCADE, #Si el usuario es eliminado se eliminaran todos los proyectos del usuario
        related_name= 'usuarioProyecto' #Nos permite acceder a todos los proyectos de un usuario
        )

    def __str__(self):
        return f"Proyecto {self.descripcion[:35]}..." # Muestra una parte de la descripcion del proyecta
    tecnico = models.ForeignKey (
        User,
        on_delete=models.CASCADE,
        related_name='tecnicoProyecto'
    )

    # Método que devuelve una representación en texto del objeto
    # Esto es útil al imprimir un proyecto en consola o en el admin de Django
    # Mostramos solo los primeros 35 caracteres de la descripción para no saturar
    def __str__(self):
        return f"Proyecto {self.descripcion[:35]}..."
