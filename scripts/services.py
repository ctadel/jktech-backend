import os
import sys
import random
import requests
from faker import Faker
from typing import List

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.common.constants import FreeTierLimitations
from assets import User, Document, API_BASE_URL


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
        self.fake = Faker()

    def _register_user(self, user):
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
            print(f"[OK] Registered: {user.username}")

        return user

    def register_n_users(self, count: int):
        users = []
        for _ in range(count):
            user = User.spawn(self.fake)
            self._register_user(user)
            users.append(user)
        return users

    def register_users(self, users: List[User]):
        for user in users:
            self._register_user(user)
        return users


class DocumentService(APIService):
    def __init__(self):
        super().__init__()
        self.documents = []
        self.fake = Faker()

    def upload_documents(self, users: List[User], total_docs: int, preserve_account_type = False):
        for _ in range(total_docs):
            user = random.choice(users)

            if user.ingestions >= FreeTierLimitations.MAX_UPLOAD_DOCUMENTS \
                    and user.account_type == 'BASIC' \
                    and not preserve_account_type:
                user.upgrade_to_premium(self._request)

            document = Document.spawn(self.fake)
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

    def __init__(self):
        super().__init__()
        self.fake = Faker()

    def initiate_conversations(self, users: List[User], documents: List[Document]):
        for user in users:
            interactable_documents = [
                    document for document in documents
                    if (document.user_id == user.id or not document.is_private)
                ]
            total_interacted_documents = min(random.randrange(10), len(interactable_documents))

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
                        message = self.fake.sentence(nb_words=random.randint(3, 12))
                        msg_response = self._request("POST", f"/conversations/{convo_id}", json=dict(
                                role = 'user',
                                content = message
                            ), headers = user.get_auth_header())

                        if msg_response and msg_response.status_code == 200:
                            print(f" - [OK] Sent message: {message}")
