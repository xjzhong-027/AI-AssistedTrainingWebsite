"""
Unified response format for API.
"""
from rest_framework.response import Response
from rest_framework import status


class Result:
    """
    Unified response format class.
    
    Usage:
        return Result.success(data={'key': 'value'}, message='Operation successful')
        return Result.error(message='Operation failed', code=400)
    """
    
    @staticmethod
    def success(data=None, message="success"):
        """
        Return a successful response.
        
        Args:
            data: Response data (optional)
            message: Success message (default: "success")
            
        Returns:
            Response with format:
            {
                'code': 200,
                'message': str,
                'data': any
            }
        """
        return Response({
            'code': 200,
            'message': message,
            'data': data
        }, status=status.HTTP_200_OK)
    
    @staticmethod
    def error(message="error", code=500, data=None):
        """
        Return an error response.
        
        Args:
            message: Error message (default: "error")
            code: Error code (default: 500)
            data: Additional error data (optional)
            
        Returns:
            Response with format:
            {
                'code': int,
                'message': str,
                'data': any
            }
        """
        # Map common HTTP status codes
        http_status = code if 100 <= code < 600 else status.HTTP_500_INTERNAL_SERVER_ERROR
        
        return Response({
            'code': code,
            'message': message,
            'data': data
        }, status=http_status)
    
    @staticmethod
    def created(data=None, message="created"):
        """
        Return a created response (201).
        
        Args:
            data: Response data (optional)
            message: Success message (default: "created")
            
        Returns:
            Response with status 201
        """
        return Response({
            'code': 201,
            'message': message,
            'data': data
        }, status=status.HTTP_201_CREATED)
    
    @staticmethod
    def no_content(message="no content"):
        """
        Return a no content response (204).
        
        Args:
            message: Message (default: "no content")
            
        Returns:
            Response with status 204
        """
        return Response({
            'code': 204,
            'message': message,
            'data': None
        }, status=status.HTTP_204_NO_CONTENT)
    
    @staticmethod
    def bad_request(message="bad request", data=None):
        """
        Return a bad request response (400).
        
        Args:
            message: Error message (default: "bad request")
            data: Additional error data (optional)
            
        Returns:
            Response with status 400
        """
        return Result.error(message=message, code=400, data=data)
    
    @staticmethod
    def unauthorized(message="unauthorized", data=None):
        """
        Return an unauthorized response (401).
        
        Args:
            message: Error message (default: "unauthorized")
            data: Additional error data (optional)
            
        Returns:
            Response with status 401
        """
        return Result.error(message=message, code=401, data=data)
    
    @staticmethod
    def forbidden(message="forbidden", data=None):
        """
        Return a forbidden response (403).
        
        Args:
            message: Error message (default: "forbidden")
            data: Additional error data (optional)
            
        Returns:
            Response with status 403
        """
        return Result.error(message=message, code=403, data=data)
    
    @staticmethod
    def invalid(message="invalid", data=None):
        """参数无效 (400)。"""
        return Result.error(message=message, code=400, data=data)

    @staticmethod
    def not_found(message="not found", data=None):
        """
        Return a not found response (404).
        
        Args:
            message: Error message (default: "not found")
            data: Additional error data (optional)
            
        Returns:
            Response with status 404
        """
        return Result.error(message=message, code=404, data=data)











