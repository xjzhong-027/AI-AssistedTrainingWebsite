"""
Tests for common/api/exceptions.py - Custom exception handler.
"""
from django.test import TestCase
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import status
from rest_framework.exceptions import (
    ValidationError,
    NotFound,
    PermissionDenied,
    AuthenticationFailed,
    APIException
)
from common.api.exceptions import custom_exception_handler


class CustomExceptionHandlerTestCase(TestCase):
    """Test cases for custom exception handler"""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.context = {'request': self.factory.get('/')}
    
    def test_validation_error_handler(self):
        """Test handling of ValidationError"""
        exc = ValidationError({'field': ['This field is required.']})
        response = custom_exception_handler(exc, self.context)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 400)
        self.assertIn('field', response.data['message'].lower())
    
    def test_not_found_error_handler(self):
        """Test handling of NotFound exception"""
        exc = NotFound('Resource not found')
        response = custom_exception_handler(exc, self.context)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['code'], 404)
        self.assertEqual(response.data['message'], 'Resource not found')
    
    def test_permission_denied_handler(self):
        """Test handling of PermissionDenied exception"""
        exc = PermissionDenied('You do not have permission')
        response = custom_exception_handler(exc, self.context)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['code'], 403)
        self.assertEqual(response.data['message'], 'You do not have permission')
    
    def test_authentication_failed_handler(self):
        """Test handling of AuthenticationFailed exception"""
        exc = AuthenticationFailed('Authentication credentials were not provided')
        response = custom_exception_handler(exc, self.context)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['code'], 401)
        self.assertIn('authentication', response.data['message'].lower())
    
    def test_generic_api_exception_handler(self):
        """Test handling of generic APIException"""
        exc = APIException('Generic API error')
        response = custom_exception_handler(exc, self.context)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.data['code'], response.status_code)
        self.assertEqual(response.data['message'], 'Generic API error')
    
    def test_validation_error_with_multiple_fields(self):
        """Test handling of ValidationError with multiple fields"""
        exc = ValidationError({
            'field1': ['Error 1'],
            'field2': ['Error 2']
        })
        response = custom_exception_handler(exc, self.context)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('field1', response.data['message'].lower())
        self.assertIn('field2', response.data['message'].lower())
    
    def test_validation_error_with_non_field_errors(self):
        """Test handling of ValidationError with non_field_errors"""
        exc = ValidationError({'non_field_errors': ['General error message']})
        response = custom_exception_handler(exc, self.context)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'General error message')
    
    def test_unhandled_exception(self):
        """Test handling of unhandled exceptions"""
        exc = ValueError('Unexpected error')
        response = custom_exception_handler(exc, self.context)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['code'], 500)
        self.assertEqual(response.data['message'], 'Internal server error')







