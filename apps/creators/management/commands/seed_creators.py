from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker

from apps.accounts.models import KYC
from apps.creators.models import CreatorProfile

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = "Load 25 verified creators with fake data"

    def handle(self, *args, **options):
        self.stdout.write("Creating 25 verified creators...")

        for i in range(25):
            username = fake.user_name() + str(i)
            email = f"{username}@example.com"

            user = User.objects.create_user(
                username=username,
                email=email,
                password="testpass123",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                verified=True,
            )

            KYC.objects.create(user=user, status="approved")

            profile = CreatorProfile.objects.get(user=user)
            profile.display_name = fake.name()
            profile.bio = fake.text(max_nb_chars=200)
            profile.coffee_price = fake.random_int(min=50, max=500, step=50)
            profile.save()

            if (i + 1) % 10 == 0:
                self.stdout.write(f"Created {i + 1} creators...")

        self.stdout.write(self.style.SUCCESS("Successfully created 25 verified creators"))
