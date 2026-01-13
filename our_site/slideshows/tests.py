from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from .models import SlideshowProgress
import json

@override_settings(DEBUG_TOOLBAR_CONFIG={'SHOW_TOOLBAR_CALLBACK': lambda request: False})
class SlideshowProgressTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()
        self.client.login(username='testuser', password='password')
        self.slug = 'test-slideshow'

    def test_save_progress_new(self):
        response = self.client.post(
            '/slideshows/save_progress/',
            data=json.dumps({
                'slideshow_slug': self.slug,
                'current_h': 1,
                'current_v': 2,
                'max_percentage': 10
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        progress = SlideshowProgress.objects.get(user=self.user, slideshow_slug=self.slug)
        self.assertEqual(progress.current_h, 1)
        self.assertEqual(progress.current_v, 2)
        self.assertEqual(progress.max_percentage, 10)

    def test_save_progress_update(self):
        SlideshowProgress.objects.create(
            user=self.user, 
            slideshow_slug=self.slug,
            max_percentage=50
        )
        
        response = self.client.post(
            '/slideshows/save_progress/',
            data=json.dumps({
                'slideshow_slug': self.slug,
                'current_h': 5,
                'current_v': 0,
                'max_percentage': 60
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        progress = SlideshowProgress.objects.get(user=self.user, slideshow_slug=self.slug)
        self.assertEqual(progress.max_percentage, 60)

    def test_get_progress_existing(self):
        SlideshowProgress.objects.create(
            user=self.user, 
            slideshow_slug=self.slug,
            current_h=2,
            max_percentage=20
        )
        
        response = self.client.get(f'/slideshows/get_progress/?slideshow_slug={self.slug}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['current_h'], 2)
        self.assertEqual(data['max_percentage'], 20)

    def test_get_progress_non_existent(self):
        response = self.client.get('/slideshows/get_progress/?slideshow_slug=unknown-slug')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['current_h'], 0)
        self.assertEqual(data['max_percentage'], 0)
        
    def test_save_progress_null_values(self):
        """Test that missing or null values don't cause 500 errors."""
        # Test with missing current_v
        response = self.client.post(
            '/slideshows/save_progress/',
            data=json.dumps({
                'slideshow_slug': self.slug,
                'current_h': 1,
                # current_v missing
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        progress = SlideshowProgress.objects.get(user=self.user, slideshow_slug=self.slug)
        self.assertEqual(progress.current_v, 0)
        
        # Test with explicit nulls
        response = self.client.post(
            '/slideshows/save_progress/',
            data=json.dumps({
                'slideshow_slug': self.slug,
                'current_h': None,
                'current_v': None
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        progress.refresh_from_db()
        self.assertEqual(progress.current_h, 0)
        self.assertEqual(progress.current_v, 0)

    def test_unauthenticated_access(self):
        self.client.logout()
        response = self.client.post('/slideshows/save_progress/', {}, content_type='application/json')
        self.assertNotEqual(response.status_code, 200)
