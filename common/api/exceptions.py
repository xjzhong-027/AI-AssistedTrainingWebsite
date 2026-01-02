"""
Custom exception handlers for DRF.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns a consistent response format.
    
    Returns:
        Response with format:
        {
            'code': int,
            'message': str,
            'data': None
        }
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize the response format
        custom_response_data = {
            'code': response.status_code,
            'message': str(exc.detail) if hasattr(exc, 'detail') else str(exc),
            'data': None
        }
        
        # If response.data is a dict, try to extract more details
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                custom_response_data['message'] = str(response.data['detail'])
            elif 'non_field_errors' in response.data:
                custom_response_data['message'] = ', '.join(response.data['non_field_errors'])
            else:
                # Include field errors in message
                error_messages = []
                for field, errors in response.data.items():
                    if isinstance(errors, list):
                        error_messages.append(f"{field}: {', '.join(str(e) for e in errors)}")
                    else:
                        error_messages.append(f"{field}: {str(errors)}")
                if error_messages:
                    custom_response_data['message'] = '; '.join(error_messages)
        
        response.data = custom_response_data
    else:
        # Handle unexpected exceptions
        logger.exception(f"Unhandled exception: {exc}")
        custom_response_data = {
            'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': 'Internal server error',
            'data': None
        }
        response = Response(custom_response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response







