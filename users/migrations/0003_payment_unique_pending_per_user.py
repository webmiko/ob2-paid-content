"""Partial unique constraint: один PENDING-платёж на пользователя."""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_payment_subscription"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="payment",
            constraint=models.UniqueConstraint(
                condition=models.Q(("status", "pending")),
                fields=("user",),
                name="unique_pending_payment_per_user",
            ),
        ),
    ]
