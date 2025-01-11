import os
import django
# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finalapp.settings')
django.setup()
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from home.models import *
from account.models import *
from discussion.models import *
from resource.models import *
from service.models import *

def create_users_and_profiles():
    users_data = [
        {'username': 'user1', 'email': 'user1@mail.com', 'password': 'password123', 'role': 'Public'},
        {'username': 'user2', 'email': 'user2@mail.com', 'password': 'password123', 'role': 'Low-Income User'},
        {'username': 'user3', 'email': 'user3@mail.com', 'password': 'password123', 'role': 'Organisation'},
        {'username': 'jackdaniels', 'email': 'jackdaniels@mail.com', 'password': 'password123', 'role': 'Low-Income User'}
    ]

    users = []
    for data in users_data:
        user, created = User.objects.get_or_create(username=data['username'], email=data['email'])
        if created:
            user.set_password(data['password'])
            user.save()
        
        # Create Profile
        profile, _ = Profile.objects.get_or_create(
            user=user,
            defaults={
                'role': data['role'],
                'bio': f"This is the bio of {user.username}.",
                'phone_number': '1234567890',
                'is_phone_public': True,
                'is_verified': True if data['role'] == 'Organisation' else False,
            }
        )
        users.append(user)
    return users

def create_discussion_categories():
    category_names = ['General', 'Announcements', 'Emergency', 'Question']
    categories = []
    for name in category_names:
        category, created = DiscussionCategory.objects.get_or_create(name=name)
        categories.append(category)
    return categories

def create_resource_categories():
    category_names = ['Education', 'Bursary', 'Voucher', 'Subsidy','Scheme', 'Families','Students']
    categories = []
    for name in category_names:
        category, created = ResourceCategory.objects.get_or_create(name=name)
        categories.append(category)
    return categories

def create_discussions(users, categories):
    discussions_data = [
        {'title': 'Welcome to Bersama Discussion Forum', 'content': 'This is a test post', 'author': users[0], 'categories': ['General', 'Announcements']},
        {'title': 'How does this work?', 'content': 'How does this website work?', 'author': users[1], 'categories': ['Question']},
        {'title': 'I might no longer be receiving aid! Help', 'content': 'Please help me', 'author': users[2], 'categories': ['Emergency']},
    ]

    discussions = []
    for data in discussions_data:
        discussion = Discussion.objects.create(
            title=data['title'],
            content=data['content'],
            author=data['author']
        )
        discussion.categories.set([category for category in categories if category.name in data['categories']])
        discussions.append(discussion)
    return discussions


def create_resources(users, categories):
    resources_data = [
        {'title': 'Public Rental Scheme - Family Scheme', 'content': 'Provides heavily subsidised rental flats for Singaporean households with no other housing options and no family support.', 
         'author': users[0], 'categories': ['Families', 'Scheme'],'link': 'https://www.hdb.gov.sg/residential/renting-a-flat/renting-from-hdb/public-rental-scheme/'},
        {'title': 'Government Bursaries for Higher Education', 'content': 'Provides financial assistance for Singapore Citizen students from lower- and middle-income families studying in MOE-subsidised full-time and part-time Nitec, Higher Nitec, diploma and undergraduate courses at publicly funded post-secondary education institutions.', 
         'author': users[0], 'categories': ['Students', 'Bursary'],'link': 'https://www.moe.gov.sg/financial-matters/financial-assistance/financial-assistance-information-for-pseis'}
    ]

    resources = []
    for data in resources_data:
        resource = Resource.objects.create(
            title=data['title'],
            content=data['content'],
            author=data['author'],
            link=data['link']
        )
        resource.categories.set([category for category in categories if category.name in data['categories']])
        resources.append(resource)
    return resources

def create_comments_and_replies(users, discussions,resources):
    disc_comments_data = [
        {'post': discussions[0], 'author': users[1], 'content': 'Thanks for the welcome!'},
        {'post': discussions[0], 'author': users[2], 'content': 'Looking forward to contributing here.'},
        {'post': discussions[1], 'author': users[0], 'content': 'You make a post'},
    ]

    disc_replies_data = [
        {'parent_content': 'Thanks for the welcome!', 'post': discussions[0], 'author': users[0], 'content': 'No problem'},
        {'parent_content': 'Looking forward to contributing here.', 'post': discussions[0], 'author': users[1], 'content': 'Glad to have you here'},
        {'parent_content': 'You make a post', 'post': discussions[1], 'author': users[1], 'content': 'Yes, but what post?'},
    ]
    res_comments_data = [
        {'post': resources[0], 'author': users[1], 'content': 'Thanks'},
    ]

    res_replies_data = [
        {'parent_content': 'Thanks', 'post': resources[0], 'author': users[0], 'content': 'No problem'},
    ]

    # Create comments
    comments = []
    for data in disc_comments_data:
        comment = DiscussionComment.objects.create(
            post=data['post'],
            author=data['author'],
            content=data['content']
        )
        comments.append(comment)

    # Create replies
    for data in disc_replies_data:
        parent_comment = DiscussionComment.objects.get(content=data['parent_content'], post=data['post'])
        reply = DiscussionComment.objects.create(
            post=data['post'],
            author=data['author'],
            content=data['content'],
            parent=parent_comment
        )
    
    # Create comments
    comments = []
    for data in res_comments_data:
        comment = ResourceComment.objects.create(
            post=data['post'],
            author=data['author'],
            content=data['content']
        )
        comments.append(comment)

    # Create replies
    for data in res_replies_data:
        parent_comment = ResourceComment.objects.get(content=data['parent_content'], post=data['post'])
        reply = ResourceComment.objects.create(
            post=data['post'],
            author=data['author'],
            content=data['content'],
            parent=parent_comment
        )

def create_service_categories():
    category_names = ['Free Wifi', 'Free Clinic','Free Food']
    categories = []
    for name in category_names:
        category, created = ServiceCategory.objects.get_or_create(name=name)
        categories.append(category)
    return categories

def create_services(categories):
    service_data = [
        {'title': 'Free Wifi Hotspot @ Kreta Ayer Community Club', 'content': 'Community Club free wifi', 'categories': ['Free Wifi'],
         'address': '28 Kreta Ayer Rd, Singapore 088995', 'latitude':1.2809086384687445,'longitude':103.84284061964121},
        {'title': 'Free Lunches at Buddha Tooth Relic Temple', 'content': 'On Tuesdays only', 'categories': ['Free Food'],
         'address': '288 South Bridge Rd, Singapore 058840', 'latitude':1.2815049095409599,'longitude':103.84424067732014}
    ]
    services = []
    for data in service_data:
        service = Service.objects.create(
            title=data['title'],
            content=data['content'],
            address=data['address'],
            latitude=data['latitude'],
            longitude=data['longitude']
        )
        service.categories.set([category for category in categories if category.name in data['categories']])
        services.append(service)
    return services


def populate():
    users = create_users_and_profiles()
    disc_categories = create_discussion_categories()
    resc_categories = create_resource_categories()
    discussions = create_discussions(users, disc_categories)
    resources = create_resources(users, resc_categories)
    create_comments_and_replies(users, discussions, resources)
    svc_categories = create_service_categories()
    services = create_services(svc_categories)

if __name__ == '__main__':
    populate()