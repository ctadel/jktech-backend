from fastapi import HTTPException, status

class UserAlreadyExistsException(HTTPException):
    def __init__(self, username=None, email=None):
        message = 'User already exists'
        if email:
            message = 'Email is alredy registered'
        if username:
            message = f'Username ({username}) is alredy taken'
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=message)

class InvalidUserParameters(HTTPException):
    def __init__(self, parameter):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid user parameter: {parameter}")

class InvalidAuthToken(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid Token")

class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

class InvalidCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

class FreeTierException(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=f"Tier Limit Reached: {message}")

class InvalidDocumentException(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Document error: {message}")

class DocumentMissingException(HTTPException):
    def __init__(self, document_name):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document not found: {document_name}")

class DocumentIngestionException(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=f"Document Ingestion Error: {message}")

class InvalidConversationException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Conversation ID")

