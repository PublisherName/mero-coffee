from django.db import migrations
from django.db import connection


def assign_users_to_groups(apps, schema_editor):
    """Assign users to groups based on their roles using bulk SQL."""

    User = apps.get_model('accounts', 'User')
    Group = apps.get_model('auth', 'Group')

    ROLE_GROUP_MAP = {
        'super_admin': 'super_admin',
        'admin': 'admin',
        'manager': 'manager',
        'merchant': 'merchant',
        'support': 'support',
        'creator': 'creator',
        'supporter': 'supporter',
    }

    auth_user_groups_table = 'accounts_user_groups'

    with connection.cursor() as cursor:
        # Clear existing assignments (consider if you want to preserve some)
        cursor.execute(f"DELETE FROM {auth_user_groups_table}")

        for role, group_name in ROLE_GROUP_MAP.items():
            try:
                # Get group using historical model
                group = Group.objects.get(name=group_name)
                group_id = group.id
            except Group.DoesNotExist:
                print(f"\nWarning: Group '{group_name}' does not exist. Skipping.")
                continue

            # Check if there are users with this role
            count = User.objects.filter(role=role).count()
            if count == 0:
                print(f"\nNo users found with role '{role}'. Skipping.")
                continue

            # Insert users into group
            insert_sql = """
                INSERT INTO {} (user_id, group_id)
                SELECT id, %s FROM accounts_user WHERE role = %s
            """.format(auth_user_groups_table)

            cursor.execute(insert_sql, [group_id, role])

            print(f"\nAssigned {count} users with role '{role}' to group '{group_name}'")


def reverse_assignment(apps, schema_editor):
    """Reverse by clearing all group assignments."""

    # Get the actual table name using the model
    User = apps.get_model('accounts', 'User')
    auth_user_groups_table = User.groups.through._meta.db_table

    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM {auth_user_groups_table}")
    print("Cleared all user-group assignments.")


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0016_alter_user_managers'),
    ]

    operations = [
        migrations.RunPython(assign_users_to_groups, reverse_assignment),
    ]
