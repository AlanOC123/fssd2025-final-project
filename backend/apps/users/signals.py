from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ClientProfile, CustomUser, TrainerProfile


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """Signal receiver to handle user activation and profile creation.

    When a new CustomUser is created, this function ensures the user is
    marked as active and automatically instantiates the appropriate profile
    (Trainer or Client) based on the user's role flags.

    Args:
        sender: The model class (CustomUser) that sent the signal.
        instance: The actual instance of the user being saved.
        created: A boolean indicating whether a new record was created.
        **kwargs: Additional keyword arguments passed by the signal.
    """
    if created:
        # Force activation for new users to bypass template-based verification
        # flows in this headless API setup.
        if not instance.is_active:
            CustomUser.objects.filter(pk=instance.pk).update(is_active=True)
            instance.is_active = True

        # Trigger automatic profile creation based on the assigned role.
        if instance.is_trainer:
            TrainerProfile.objects.create(user=instance)
        elif instance.is_client:
            ClientProfile.objects.create(user=instance)
