import factory

from app.models import ToDo

from .user_factory import UserFactory


class ToDoFactory(factory.alchemy.SQLAlchemyModelFactory):
    id = factory.Sequence(lambda x: f"{x}")
    title = factory.Faker("sentence")
    description = factory.Faker("paragraph")

    user = factory.SubFactory(UserFactory)

    class Meta:
        model = ToDo
        sqlalchemy_session_persistence = "commit"
