from bloggy import mongo

# -------------------------------------- #
#    Database filtering/query helpers    #
# -------------------------------------- #
all_posts = list(mongo.db.posts.find())  # Fetch all posts from the database


def check_username(username):
    '''Helper for checking is username already exists
    Checks the user input against the database using .lower method
    '''
    return mongo.db.users.find_one({"username": username.lower()})


def check_email(email):
    '''Helper for checking is email address is already in use
    Checks the user input against the database
    '''
    return mongo.db.users.find_one({"email": email})


def check_existing_blog(blog_name):
    '''Helper for checking is blog with such name already exists
    Checks the user input against the database using the slug
    to avoid blogs with different capitalisation being permitted
    '''
    return mongo.db.blogs.find_one({"title-slug": blog_name})


def get_user_id_from_username(username):
    '''Helper for getting users id using their username'''
    return mongo.db.users.find_one({"username": username})["_id"]


def get_users_posts(user_id):
    '''Helper for getting all users' posts using their id'''
    return mongo.db.posts.find({"user_id": user_id})


def get_user_from_id(user_id):
    '''Helper for getting user based on their ID'''
    return mongo.db.users.find_one({"_id": user_id})


def get_blog_from_user_id(user_id):
    '''Helper for getting blogs using creators id'''
    return mongo.db.blogs.find_one({"owner_id": user_id})

def get_user_from_username(username):
    '''Helper for getting user based on their username'''
    return mongo.db.users.find_one({"username": username})