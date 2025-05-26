from services import APIService, UserService, DocumentService, ConversationService
from assets import User

def _main():
    basic_user = User(
            username = 'basic', fullname = 'Basic User',
            email = 'basic@example.com', password = 'password',
            account_type = 'BASIC'
        )

    premium_user = User(
            username = 'premium', fullname = 'Premium User',
            email = 'premium@example.com', password = 'password',
            account_type = 'PREMIUM'
        )

    moderator = User(
            username = 'moderator', fullname = 'Moderator User',
            email = 'moderator@example.com', password = 'password',
            account_type = 'MODERATOR'
        )

    requests_di = APIService()._request

    print("==> Creating users...")
    users = UserService().register_users(
            [basic_user, premium_user, moderator])

    for user in users:
        user.upgrade_to_premium(requests_di, user.account_type)

    print("\n==> Uploading documents...")
    documents = DocumentService().upload_documents(users, 15, preserve_account_type=True)

    print("\n==> Starting conversations...")
    ConversationService().initiate_conversations(users, documents)


if __name__ == "__main__":
    _main()
    exit(0)
