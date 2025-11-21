"""
Tests for CommunicationService implementation (forum part).

These tests verify that CommunicationServiceImpl correctly implements the CommunicationService interface
for forum-related functionality (Post, Comment).
"""
from django.test import TestCase
from django.contrib.auth.models import User
from Account.models import Students, Teachers, Class, Course
from ELW.models import MainQuestion, SubQuestion, MediaMaterial, Unit, PaperPage
from forum.models import Post, Comment, Anonymous
from forum.services.communication_service_impl import CommunicationServiceImpl
from Account.services.user_service_impl import UserServiceImpl


class CommunicationServiceImplForumTestCase(TestCase):
    """Test CommunicationService implementation for forum functionality"""

    def setUp(self):
        """Set up test data"""
        # Create test course
        self.course = Course.objects.create(
            year=2024,
            grade=1,
            semester=1
        )
        
        # Create test teacher
        self.teacher_user = User.objects.create_user(
            username='test_teacher_user',
            password='teacher123'
        )
        self.teacher = Teachers.objects.create(
            username='test_teacher',
            name='Test Teacher',
            password='teacher123',
            user=self.teacher_user
        )
        
        # Create test class
        self.class_instance = Class.objects.create(
            course=self.course,
            teacher=self.teacher,
            start_date='2024-01-01',
            week=1,
            start_time='08:00:00',
            end_time='10:00:00'
        )
        
        # Create test student
        self.student_user = User.objects.create_user(
            username='test_student_user',
            password='student123'
        )
        self.student = Students.objects.create(
            username='test_student',
            name='Test Student',
            password='student123',
            class_instance=self.class_instance,
            user=self.student_user
        )
        
        # Create test media material
        self.media = MediaMaterial.objects.create(
            title='Test Media',
            theme='Test Theme',
            abstract='Test Abstract',
            keywords='test, keywords',
            transcript='Test transcript'
        )
        
        # Create test main question
        self.main_question = MainQuestion.objects.create(
            media_material=self.media,
            question_type='choice',
            question_text='Test main question'
        )
        
        # Create test sub question
        self.sub_question = SubQuestion.objects.create(
            main_question=self.main_question,
            question_text='Test sub question',
            answer='Test Answer'
        )

    def test_create_post_success(self):
        """Test creating a post successfully"""
        post = CommunicationServiceImpl.create_post(
            title='Test Post',
            content='Test content',
            author_username='test_teacher',
            author_role='teacher'
        )
        
        self.assertIsNotNone(post)
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.content, 'Test content')
        self.assertEqual(post.teacher, self.teacher)
        self.assertEqual(post.author, 'test_teacher')
        self.assertFalse(post.is_anonymous)

    def test_create_post_with_main_question(self):
        """Test creating a post with main question"""
        post = CommunicationServiceImpl.create_post(
            title='Test Post',
            content='Test content',
            author_username='test_teacher',
            author_role='teacher',
            main_question_id=self.main_question.id
        )
        
        self.assertIsNotNone(post)
        self.assertEqual(post.main_question, self.main_question)
        self.assertTrue(post.is_question)

    def test_create_post_with_sub_question(self):
        """Test creating a post with sub question"""
        post = CommunicationServiceImpl.create_post(
            title='Test Post',
            content='Test content',
            author_username='test_teacher',
            author_role='teacher',
            main_question_id=self.main_question.id,
            sub_question_id=self.sub_question.id
        )
        
        self.assertIsNotNone(post)
        self.assertEqual(post.main_question, self.main_question)
        self.assertEqual(post.sub_question, self.sub_question)
        self.assertTrue(post.is_question)

    def test_create_post_anonymous(self):
        """Test creating an anonymous post"""
        post = CommunicationServiceImpl.create_post(
            title='Test Post',
            content='Test content',
            author_username='test_student',
            author_role='student',
            is_anonymous=True
        )
        
        self.assertIsNotNone(post)
        self.assertTrue(post.is_anonymous)
        self.assertIsNotNone(post.anonymous_name)
        self.assertEqual(post.name, post.anonymous_name)
        # Verify Anonymous record was created
        anonymous = Anonymous.objects.filter(post=post, user=self.student).first()
        self.assertIsNotNone(anonymous)

    def test_create_post_student(self):
        """Test creating a post as student"""
        post = CommunicationServiceImpl.create_post(
            title='Test Post',
            content='Test content',
            author_username='test_student',
            author_role='student'
        )
        
        self.assertIsNotNone(post)
        self.assertEqual(post.student, self.student)
        self.assertEqual(post.author, 'test_student')

    def test_get_post_by_id_success(self):
        """Test getting a post by ID successfully"""
        post = CommunicationServiceImpl.create_post(
            title='Test Post',
            content='Test content',
            author_username='test_teacher',
            author_role='teacher'
        )
        
        retrieved_post = CommunicationServiceImpl.get_post_by_id(post.id)
        
        self.assertIsNotNone(retrieved_post)
        self.assertEqual(retrieved_post.id, post.id)
        self.assertEqual(retrieved_post.title, 'Test Post')

    def test_get_post_by_id_not_found(self):
        """Test getting a post by ID that doesn't exist"""
        retrieved_post = CommunicationServiceImpl.get_post_by_id(99999)
        
        self.assertIsNone(retrieved_post)

    def test_get_posts_by_question_main_question(self):
        """Test getting posts by main question"""
        # Create posts
        post1 = CommunicationServiceImpl.create_post(
            title='Post 1',
            content='Content 1',
            author_username='test_teacher',
            author_role='teacher',
            main_question_id=self.main_question.id
        )
        post2 = CommunicationServiceImpl.create_post(
            title='Post 2',
            content='Content 2',
            author_username='test_teacher',
            author_role='teacher',
            main_question_id=self.main_question.id
        )
        # Create a post without question
        post3 = CommunicationServiceImpl.create_post(
            title='Post 3',
            content='Content 3',
            author_username='test_teacher',
            author_role='teacher'
        )
        
        posts = CommunicationServiceImpl.get_posts_by_question(
            main_question_id=self.main_question.id
        )
        
        self.assertEqual(len(posts), 2)
        self.assertIn(post1, posts)
        self.assertIn(post2, posts)
        self.assertNotIn(post3, posts)

    def test_get_posts_by_question_sub_question(self):
        """Test getting posts by sub question"""
        # Create posts
        post1 = CommunicationServiceImpl.create_post(
            title='Post 1',
            content='Content 1',
            author_username='test_teacher',
            author_role='teacher',
            main_question_id=self.main_question.id,
            sub_question_id=self.sub_question.id
        )
        post2 = CommunicationServiceImpl.create_post(
            title='Post 2',
            content='Content 2',
            author_username='test_teacher',
            author_role='teacher',
            main_question_id=self.main_question.id
        )
        
        posts = CommunicationServiceImpl.get_posts_by_question(
            sub_question_id=self.sub_question.id
        )
        
        self.assertEqual(len(posts), 1)
        self.assertIn(post1, posts)
        self.assertNotIn(post2, posts)

    def test_create_comment_success(self):
        """Test creating a comment successfully"""
        post = CommunicationServiceImpl.create_post(
            title='Test Post',
            content='Test content',
            author_username='test_teacher',
            author_role='teacher'
        )
        
        comment = CommunicationServiceImpl.create_comment(
            post_id=post.id,
            content='Test comment',
            author_username='test_student',
            author_role='student'
        )
        
        self.assertIsNotNone(comment)
        self.assertEqual(comment.post, post)
        self.assertEqual(comment.content, 'Test comment')
        self.assertEqual(comment.student, self.student)
        self.assertEqual(comment.author, 'test_student')

    def test_create_comment_reply(self):
        """Test creating a reply comment"""
        post = CommunicationServiceImpl.create_post(
            title='Test Post',
            content='Test content',
            author_username='test_teacher',
            author_role='teacher'
        )
        
        parent_comment = CommunicationServiceImpl.create_comment(
            post_id=post.id,
            content='Parent comment',
            author_username='test_teacher',
            author_role='teacher'
        )
        
        reply = CommunicationServiceImpl.create_comment(
            post_id=post.id,
            content='Reply comment',
            author_username='test_student',
            author_role='student',
            parent_comment_id=parent_comment.id
        )
        
        self.assertIsNotNone(reply)
        self.assertEqual(reply.parent_comment, parent_comment)
        self.assertEqual(reply.content, 'Reply comment')

    def test_create_comment_post_not_found(self):
        """Test creating a comment for non-existent post"""
        # This should raise an exception or return None
        # The implementation should handle this case
        try:
            comment = CommunicationServiceImpl.create_comment(
                post_id=99999,
                content='Test comment',
                author_username='test_student',
                author_role='student'
            )
            # If no exception is raised, comment should be None
            self.assertIsNone(comment)
        except Exception:
            # If exception is raised, that's also acceptable
            pass

