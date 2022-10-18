from datetime import datetime

import factory

from app.models import User


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    id = factory.Sequence(lambda x: f"{x}")
    email = factory.Faker("email")
    full_name = factory.Faker("name")
    is_active = True
    hashed_password = ""
    time_created = factory.LazyFunction(datetime.now)

    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"
