from flask_sqlalchemy import SQLAlchemy

class SerializableAlchemy(SQLAlchemy):
    def apply_driver_hacks(self, app, info, options):
        if 'isolation_level' not in options:
            options['isolation_level'] = 'SERIALIZABLE'
        return super().apply_driver_hacks(app, info, options)

# Make sure to declare the connection to the database
db = SerializableAlchemy()

# Import models into here
from .member import TimeStampMixin, Member, Major, Minor
# from .studies import Major, Minor
