from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_default_superuser(sender, **kwargs):
    User = get_user_model()

    if not User.objects.filter(username='developer').exists():
        User.objects.create_superuser(
            username='developer',
            email='admin@example.com',
            password='default'
        )
        print("Superusuario creado automáticamente.")
