import factory
from datetime import datetime

from app.models import User


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    id = factory.Sequence(lambda x: f"{x}")
    email = factory.Faker("email")
    full_name = factory.Faker("name")
    is_active = True
    hashed_password = ""
    # created_at = factory.LazyFunction(datetime.now)


    class Meta:
        model = User
        sqlalchemy_session_persistence = 'commit'
