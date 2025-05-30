import random
from faker import Faker
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from app.config import settings

API_BASE_URL = f"{settings.API_URL}/api/{settings.API_VERSION}"

@dataclass
class User:
    id: Optional[int] = None
    username: Optional[str] = None
    fullname: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    account_type: str = 'BASIC'

    token: str = ""
    ingestions: int = 0

    @classmethod
    def spawn(cls, fake: Faker) -> "User":
        first = fake.first_name()
        last = fake.last_name()

        fullname = f"{first} {last}"
        first_last = [first, last]
        random.shuffle(first_last)
        email = random.choice(list('_.')).join(first_last) \
            + random.choice([str(random.randrange(2000))] + [''] * 3) \
            + '@' + random.choice([fake.free_email_domain()] * 2 + [fake.domain_name()] * 1)

        random.shuffle(first_last)
        username = random.choice(list('_.')).join(
            random.sample([first, last], k=random.randint(1, 2))) \
            + random.choice([str(random.randrange(2000))] + [''] * 3)

        return cls(
            username=username.lower(),
            fullname=fullname,
            email=email.lower(),
            password=fake.password(10)
        )

    def _update_profile(self, request):
        response = request("GET", "users/profile", headers = self.get_auth_header())
        if response and response.status_code == 200:
            profile = response.json()
            self.id = profile['id']

    def get_auth_header(self):
        return {"Authorization": f"Bearer {self.token}"}

    def upgrade_to_premium(self, request, account_type='PREMIUM'):
        self.account_type = account_type
        request("POST", "users/profile/account/update-account-type", json=dict(
            account_type = self.account_type
        ), headers = self.get_auth_header())


@dataclass
class Document:
    id: Optional[int] = None
    user_id: Optional[int] = None
    document_key: Optional[str] = None
    title: Optional[str] = None
    local_path: str = None
    is_private: bool = False

    @classmethod
    def spawn(cls, fake: Faker):
        path = f"/tmp/{fake.uuid4()}.txt"
        content = fake.text(max_nb_chars=1500)
        Path(path).write_text(content)

        return cls(
            title = fake.sentence(nb_words=random.randrange(1,4)),
            is_private = random.choice([True, False, False]),
            local_path = path,
        )
