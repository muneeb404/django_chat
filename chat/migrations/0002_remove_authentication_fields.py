from django.db import migrations


def remove_legacy_user_columns(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        cursor.execute('PRAGMA table_info(chat_chatroom)')
        room_columns = {row[1] for row in cursor.fetchall()}
        cursor.execute('PRAGMA table_info(chat_message)')
        message_columns = {row[1] for row in cursor.fetchall()}

    if 'created_by_id' in room_columns:
        schema_editor.execute('DROP INDEX IF EXISTS chat_chatroom_created_by_id_238a1e37')
        schema_editor.execute('ALTER TABLE chat_chatroom DROP COLUMN created_by_id')
    if 'sender_id' in message_columns:
        schema_editor.execute('DROP INDEX IF EXISTS chat_message_sender_id_991c686c')
        schema_editor.execute('ALTER TABLE chat_message DROP COLUMN sender_id')
    if 'username' not in message_columns:
        schema_editor.execute(
            "ALTER TABLE chat_message ADD COLUMN username varchar(50) NOT NULL DEFAULT 'guest'"
        )


class Migration(migrations.Migration):
    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(remove_legacy_user_columns, migrations.RunPython.noop),
    ]
