from app.config import settings

class PaginationConstants:
    USERS_PER_PAGE = 10
    DOCUMENTS_PER_PAGE = 20

class FreeTierLimitations:
    MAX_UPLOAD_DOCUMENTS = 3
    DOCUMENT_TOKEN_LIMIT = 100,000

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
