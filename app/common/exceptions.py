from fastapi import HTTPException, status

class UserAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

class InvalidUserParameters(HTTPException):
    def __init__(self, parameter):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid user parameter: {parameter}")

class InvalidAuthToken(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid Token")

class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

class InvalidCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

class FreeTierException(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Tier Limit Reached: {message}")

class InvalidDocumentException(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=f"Document error: {message}")

class DocumentMissingException(HTTPException):
    def __init__(self, document_name):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document not found: {document_name}")

class DocumentIngestionException(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=f"Document Ingestion Error: {message}")
