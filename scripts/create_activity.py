import argparse

from services import UserService, DocumentService, ConversationService

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

    def parse_args(self):
        return self.parser.parse_args()


def _main(total_users, total_documents):
    print("==> Creating users...")
    users = UserService().register_n_users(total_users)

    print("\n==> Uploading documents...")
    document_service = DocumentService()
    documents = document_service.upload_documents(users, total_documents)
    document_service.star_document(users, documents)

    print("\n==> Starting conversations...")
    ConversationService().initiate_conversations(users, documents)


if __name__ == "__main__":
    args = ArgumentParserService().parse_args()
    _main(args.users, args.documents)
    exit(0)
