"""
Tests for common/api/response.py - Unified response format.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from common.api.response import Result


class ResultTestCase(TestCase):
    """Test cases for Result class"""
    
    def test_success_response(self):
        """Test successful response format"""
        response = Result.success(data={'key': 'value'}, message='Operation successful')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(response.data['message'], 'Operation successful')
        self.assertEqual(response.data['data'], {'key': 'value'})
    
    def test_success_response_default_message(self):
        """Test successful response with default message"""
        response = Result.success(data={'key': 'value'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(response.data['message'], 'success')
        self.assertEqual(response.data['data'], {'key': 'value'})
    
    def test_success_response_no_data(self):
        """Test successful response without data"""
        response = Result.success()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(response.data['message'], 'success')
        self.assertIsNone(response.data['data'])
    
    def test_error_response(self):
        """Test error response format"""
        response = Result.error(message='Operation failed', code=400)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 400)
        self.assertEqual(response.data['message'], 'Operation failed')
        self.assertIsNone(response.data['data'])
    
    def test_error_response_default(self):
        """Test error response with default values"""
        response = Result.error()
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['code'], 500)
        self.assertEqual(response.data['message'], 'error')
        self.assertIsNone(response.data['data'])
    
    def test_error_response_with_data(self):
        """Test error response with additional data"""
        error_data = {'field': 'error details'}
        response = Result.error(message='Validation failed', code=400, data=error_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 400)
        self.assertEqual(response.data['message'], 'Validation failed')
        self.assertEqual(response.data['data'], error_data)
    
    def test_created_response(self):
        """Test created response (201)"""
        response = Result.created(data={'id': 1}, message='Resource created')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], 201)
        self.assertEqual(response.data['message'], 'Resource created')
        self.assertEqual(response.data['data'], {'id': 1})
    
    def test_no_content_response(self):
        """Test no content response (204)"""
        response = Result.no_content(message='Deleted successfully')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['code'], 204)
        self.assertEqual(response.data['message'], 'Deleted successfully')
        self.assertIsNone(response.data['data'])
    
    def test_bad_request_response(self):
        """Test bad request response (400)"""
        response = Result.bad_request(message='Invalid input')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 400)
        self.assertEqual(response.data['message'], 'Invalid input')
    
    def test_unauthorized_response(self):
        """Test unauthorized response (401)"""
        response = Result.unauthorized(message='Authentication required')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['code'], 401)
        self.assertEqual(response.data['message'], 'Authentication required')
    
    def test_forbidden_response(self):
        """Test forbidden response (403)"""
        response = Result.forbidden(message='Access denied')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['code'], 403)
        self.assertEqual(response.data['message'], 'Access denied')
    
    def test_not_found_response(self):
        """Test not found response (404)"""
        response = Result.not_found(message='Resource not found')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['code'], 404)
        self.assertEqual(response.data['message'], 'Resource not found')











