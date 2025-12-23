from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Check the structure of the users table'
    
    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("DESCRIBE users")
            columns = cursor.fetchall()
            self.stdout.write(self.style.SUCCESS('Users table structure:'))
            for column in columns:
                self.stdout.write(f"  {column[0]}: {column[1]}")