from app.config import settings

def create_endpoints(base_class: type, parent_prefix: str = ""):
    obj = base_class()
    if hasattr(base_class, 'PREFIX'):
        current_prefix = parent_prefix + obj.PREFIX
    obj.FULL_ROUTE = current_prefix

    for attr_name, attr_value in base_class.__dict__.items():
        if isinstance(attr_value, type):
            child_instance = create_endpoints(attr_value, current_prefix)
            setattr(obj, attr_name, child_instance)
    return obj

class Endpoints:
    BASE_PREFIX = '/api/'
    PREFIX = BASE_PREFIX + settings.API_VERSION


    class Users:
        PREFIX = '/users'

        class Auth:
            PREFIX = '/auth'

            LOGIN = '/login'
            REGISTER = '/register'

        class Profile:
            PREFIX = '/profile'

            GET_USER_PROFILE = ''
            UPDATE_PROFILE = '/update'
            GET_PROFILE = '/user/{username}'
            LIST_USERS = '/users'
            UPDATE_PASSWORD = '/account/update-password'
            UPDATE_ACCOUNT_TYPE = '/account/update-account-type'
            ACTIVATE_PROFILE = '/account/activate'
            DEACTIVATE_PROFILE = '/account/deactivate'

        class SuperAdmin:
            PREFIX = '/admin'

            DEACTIVATE_USER = '/deactivate/{user_id}'
            DELETE_USER = '/delete/{user_id}'

    class Documents:
        PREFIX = '/documents'

        UPLOAD_DOCUMENT = ''
        REUPLOAD_DOCUMENT = ''
        VIEW_DOCUMENT = '/{document_key}'
        DELETE_DOCUMENT = '/{document_key}'

        class PublicDocuments:
            PREFIX = '/document/public'

            LIST_USER_DOCUMENTS = '/user/{username}'
            EXPLORE_DOCUMENTS = '/explore'
            TRENDING_DOCUMENTS = '/explore/trending'
            LATEST_DOCUMENTS = '/explore/latest'

    class LLM:
        PREFIX = '/llm'

        GET_DOCUMENT_STATUS = '/ingestion_status/{document_id}'
        STOP_DOCUMENT_INGESTION = '/cancel_ingestion/{document_id}'


    class Conversations:
        PREFIX = '/conversations'

        LIST_USER_CONVERSATIONS = ''
        START_NEW_CONVERSATION = ''
        GET_CONVERSATION = '/{convo_id}'
        ADD_MESSAGE = '/{convo_id}'
        DELETE_CONVERSATION = '/{convo_id}'
        ARCHIVE_CONVERSATION = '/{convo_id}/archive'

BASE_ENDPOINT = create_endpoints(Endpoints)
