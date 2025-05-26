import os
import argparse
import random
import requests
from faker import Faker
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

from app.common.constants import FreeTierLimitations
from app.config import settings

fake = Faker()
API_BASE_URL = f"http://localhost:8000/api/{settings.API_VERSION}"

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

    def upgrade_to_premium(self, request):
        self.account_type = 'PREMIUM'
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

class APIService:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip('/')

    def _request(self, method: str, endpoint: str, expect:int = 200, **kwargs):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.request(method=method.upper(), url=url, **kwargs)
            assert response.status_code == expect
            return response
        except requests.RequestException as e:
            print(f"[EXCEPTION] {method.upper()} {url} failed: {e}")
            return None
        except AssertionError:
            print(f"Expected StatusCode<{expect}> but got StatusCode<{response.status_code}>")
            print(response.json())
            return response


class UserService(APIService):
    def __init__(self):
        super().__init__()
        self.users: List[User] = []

    def create_users(self, count: int):
        for _ in range(count):
            user = User.spawn(fake)

            registration = self._request("POST", "/users/auth/register", json=dict(
                username  = user.username,
                full_name = user.fullname,
                email     = user.email,
                password  = user.password
            ))

            if registration and registration.status_code == 200:
                user_data = registration.json()
                user.token = user_data['access_token']
                user._update_profile(self._request)

                self.users.append(user)
                print(f"[OK] Registered: {user.username}")

        return self.users


class DocumentService(APIService):
    def __init__(self):
        super().__init__()
        self.documents = []

    def upload_documents(self, users: List[User], total_docs: int):
        for _ in range(total_docs):
            user = random.choice(users)

            if user.ingestions >= FreeTierLimitations.MAX_UPLOAD_DOCUMENTS \
                    and user.account_type == 'BASIC':
                user.upgrade_to_premium(self._request)

            document = Document.spawn(fake)
            with open(document.local_path, 'rb') as stream:
                response = self._request("POST", "/documents", headers=user.get_auth_header(),
                        files={"file": (document.local_path, stream)}, data=dict(
                            title      = document.title,
                            is_private = str(document.is_private).lower()
                        ))

            if response and response.status_code == 200:
                user.ingestions += 1

                response_data = response.json()
                document.id = response_data['id']
                print(f"[OK] Uploaded doc '{document.id}' for {user.username}")
                self.documents.append(document)

            if os.path.exists(document.local_path):
                os.remove(document.local_path)

        return self.documents


class ConversationService(APIService):
    def initiate_conversations(self, users: List[User], documents: List[Document]):
        for user in users:
            interactable_documents = [
                    document for document in documents
                    if (document.user_id == user.id or not document.is_private)
                ]
            total_interacted_documents = random.randrange(10)

            for _ in range(total_interacted_documents):
                document = random.choice(interactable_documents)

                response = self._request("POST", "/conversations", json=dict(
                        document_id = document.id,
                        title = document.title
                    ), headers=user.get_auth_header())

                if response and response.status_code == 200:
                    response_data = response.json()
                    convo_id = response_data["id"]
                    print(f"[OK] Conversation {convo_id} started for {user.username} with document: {document.title}")

                    for _ in range(random.randrange(15)):
                        message = fake.sentence(nb_words=random.randint(3, 12))
                        msg_response = self._request("POST", f"/conversations/{convo_id}", json=dict(
                                role = 'user',
                                content = message
                            ), headers = user.get_auth_header())

                        if msg_response and msg_response.status_code == 200:
                            print(f" - [OK] Sent message: {message}")

class ArgumentParserService:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Create fake activity in this lonely just started application"
        )
        self._add_arguments()

    def _add_arguments(self):
        self.parser.add_argument(
            "--users", "-u",
            type=int,
            required=False,
            default=20,
            help="Total number of users participating"
        )
        self.parser.add_argument(
            "--documents", "-d",
            type=int,
            required=False,
            default=100,
            help="Total number of documents to ingest"
        )

    def parse(self):
        return self.parser.parse_args()

def create(total_users, total_documents):
    print("==> Creating users...")
    users = UserService().create_users(total_users)

    print("\n==> Uploading documents...")
    documents = DocumentService().upload_documents(users, total_documents)

    print("\n==> Starting conversations...")
    ConversationService().initiate_conversations(users, documents)


if __name__ == "__main__":
    args = ArgumentParserService().parse()
    create(args.users, args.documents)
    exit(0)
