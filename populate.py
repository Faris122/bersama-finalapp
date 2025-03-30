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
from fundraiser.models import *
from django.utils.timezone import make_aware
from datetime import datetime, timedelta


# This python file intends to populate the web app with dummy and placeholder data

def create_users_and_profiles():
    users_data = [
        {'username': 'user1', 'email': 'user1@mail.com', 'password': 'password123', 'role': 'Public', 'needs_help': True},
        {'username': 'user2', 'email': 'user2@mail.com', 'password': 'password123', 'role': 'Public', 'needs_help': False},
        {'username': 'orguser', 'email': 'user3@mail.com', 'password': 'password123', 'role': 'Organisation', 'needs_help': False},
        {'username': 'jackdaniels', 'email': 'jackdaniels@mail.com', 'password': 'password123', 'role': 'Public', 'needs_help': True}
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
            role=data['role'],
            bio=f"This is the bio of {data['username']}.",
            needs_help=data['needs_help']
        )
        # Create Financial Profile ONLY IF the user needs help
        if data['needs_help'] == True:
            FinancialProfile.objects.get_or_create(profile=profile)
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
    category_names = ['Education', 'Voucher', 'Subsidy','Housing', 'Families','Students']
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
         'author': users[0], 'categories': ['Families', 'Housing'],'link': 'https://www.hdb.gov.sg/residential/renting-a-flat/renting-from-hdb/public-rental-scheme/'},
        {'title': 'Student Care Fee Assistance (SCFA)', 'content': 'Provides fee assistance for children from lower-income working families enrolled in Student Care Centres (SCCs) registered with MSF.', 
         'author': users[0], 'categories': ['Students','Education'],'link': 'https://supportgowhere.life.gov.sg/schemes/SCFA/student-care-fee-assistance-scfa','max_income_pc':1125,'max_income_gross':4500}
    ]
    bursaries_data = [
        {'title': 'Government Bursaries for Higher Education', 'content': 'Provides financial assistance for Singapore Citizen students from lower- and middle-income families studying in MOE-subsidised full-time and part-time Nitec, Higher Nitec, diploma and undergraduate courses at publicly funded post-secondary education institutions.', 
         'author': users[0], 'level': 'tertiary','link': 'https://www.moe.gov.sg/financial-matters/financial-assistance/financial-assistance-information-for-pseis'},
         {'title': 'MOE Financial Assistance Scheme', 'content': 'For primary, secondary and pre-university Singapore Citizen students studying in Government and government-aided schools', 
         'author': users[0], 'level': 'primary','link': 'https://www.moe.gov.sg/financial-matters/financial-assistance','max_income_pc':750,'max_income_gross':3000}
    ]

    resources = []
    bursaries = []
    for data in resources_data:
        resource = Resource.objects.create(
            title=data['title'],
            content=data['content'],
            author=data['author'],
            link=data['link'],
            max_income_pc = data.get('max_income_pc', None),
            max_income_gross = data.get('max_income_gross',None)
        )
        resource.categories.set([category for category in categories if category.name in data['categories']])
        resources.append(resource)
    for data in bursaries_data:
        bursary = Bursary.objects.create(
            title=data['title'],
            content=data['content'],
            author=data['author'],
            link=data['link'],
            level=data['level'],
            max_income_pc = data.get('max_income_pc', None),
            max_income_gross = data.get('max_income_gross',None)
        )
        bursaries.append(bursary)
    return resources, bursaries

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
    category_names = ['Free Wifi', 'Free Clinic','Free Food','Government Social Services','Non-Profit Orgs','Charities']
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

def create_event_categories():
    category_names = ['Fundraiser', 'Food Drive','Donation','Volunteering']
    categories = []
    for name in category_names:
        category, created = EventCategory.objects.get_or_create(name=name)
        categories.append(category)
    return categories

def create_events(categories):
    now = make_aware(datetime.now())
    event_data = [
        {'title': 'Fundraising Event at Kreta Ayer CC', 'content': 'Community Club Fundraising for poor families.', 'categories': ['Fundraiser','Volunteering'], 'host':'Kreta Ayer CC',
         'address': '28 Kreta Ayer Rd, Singapore 088995', 'latitude':1.2809086384687445,'longitude':103.84284061964121, 'datetime_start': now,  'datetime_end': now + timedelta(hours=1)},
        {'title': 'Food Distribution Buddha Tooth Relic Temple', 'content': 'Bring food.', 'categories': ['Food Drive','Volunteering'], 'host':'Buddha Tooth Temple',
         'address': '288 South Bridge Rd, Singapore 058840', 'latitude':1.2815049095409599,'longitude':103.84424067732014,'datetime_start': now,  'datetime_end': now + timedelta(days=30, hours=12)},
         {'title': 'Gala Dinner to Help Sick Children', 'content': 'Feel free to volunteer!', 'categories': ['Volunteering'], 'host':'Singapore General Hospital',
         'address': 'Singapore General Hospital, Outram Rd, Singapore 169608', 'latitude':1.279350220123578,'longitude':103.83519416155283,'datetime_start': now + timedelta(days=30),  'datetime_end': now + timedelta(days=31, hours=12)}
    ]
    events = []
    for data in event_data:
        event = Event.objects.create(
            title=data['title'],
            content=data['content'],
            address=data['address'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            host=data['host'],
            datetime_start=data['datetime_start'],
            datetime_end=data['datetime_end']
        )
        event.categories.set([category for category in categories if category.name in data['categories']])
        events.append(event)
    return events

def create_fundraisers(users):
    now = make_aware(datetime.now())
    fundraiser_data = [
        {'user': users[0], 'title': 'Help My Mother Recover from Surgery', 'description': 'My mother is recovering from a major surgery and needs financial support', 
         'goal_amount': 500.00, 'end_date': now + timedelta(days=30)},
        {'user': users[2], 'title': 'Support Our Client with Housing', 'description': 'Jack is in need of temporary rental support', 
         'goal_amount': 1500.00, 'end_date': now + timedelta(hours=1)},
        {'user': users[2], 'title': 'Family Food Drive, support us', 'description': 'Helping families in need with essential food supplies', 
         'goal_amount': 1000.00, 'end_date': now + timedelta(days=60)}
    ]
    fundraisers = []
    for data in fundraiser_data:
        fundraiser = Fundraiser.objects.create(
            user=data['user'],
            title=data['title'],
            description=data['description'],
            goal_amount=data['goal_amount'],
            end_date=data['end_date']
        )
        fundraisers.append(fundraiser)
    return fundraisers

def create_payments(users, fundraisers):
    payment_data = [
        {'user': users[1], 'fundraiser': fundraisers[0], 'amount': 100.00, 'message': 'Wishing you a speedy recovery!'},
        {'user': None, 'anon_name': 'Anonymous Donor', 'fundraiser': fundraisers[0], 'amount': 200.00, 'message': 'Stay strong!'},
        {'user': users[0], 'fundraiser': fundraisers[1], 'amount': 1500.00, 'message': 'Hope this helps!'},
        {'user': users[1], 'fundraiser': fundraisers[2], 'amount': 300.00, 'message': 'Great initiative!'},
        {'user': None, 'anon_name': 'Kind Soul', 'fundraiser': fundraisers[2], 'amount': 500.00, 'message': 'Keep up the good work!'}
    ]
    payments = []
    for data in payment_data:
        payment = Payment.objects.create(
            user=data['user'],
            anon_name=data.get('anon_name', None),
            fundraiser=data['fundraiser'],
            amount=data['amount'],
            message=data['message']
        )
        payments.append(payment)
    return payments

def populate():
    users = create_users_and_profiles()
    disc_categories = create_discussion_categories()
    resc_categories = create_resource_categories()
    discussions = create_discussions(users, disc_categories)
    resources, bursaries = create_resources(users, resc_categories)
    create_comments_and_replies(users, discussions, resources)
    svc_categories = create_service_categories()
    services = create_services(svc_categories)
    event_categories = create_event_categories()
    events = create_events(event_categories)
    fundraisers = create_fundraisers(users)
    payments = create_payments(users,fundraisers)

if __name__ == '__main__':
    populate()