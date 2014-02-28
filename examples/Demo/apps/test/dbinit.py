import uliweb
from uliweb.orm import get_model
from uliweb import settings

# Generate test data

User = get_model('user')
Role = get_model('role')
items = settings.get_var('TEST_DATA/USERS', [])

user_default = {'is_superuser': False, 'password': '1', 'roles': []}

for item in items:

    for key in user_default.keys():
        if not item.has_key(key):
            item[key] = user_default[key]

    username = item['username']
    if not User.get(User.c.username == item['username']):

        # add user
        user = User(username=username, nickname=item['nickname'])
        user.set_password(item['password'])
        user.is_superuser = item['is_superuser']
        user.save()

        # set roles
        for role in item['roles']:
            role = Role.get(Role.c.name == role)
            if not role:
                continue
            if not role.users.has(user):
                role.users.add(user)






