import graphene
import logging
import uuid
import graphene
import logging
import traceback

from flask import g, request
from graphql_server.flask import GraphQLView
from models import User, Post, Comment
from sqlalchemy.orm import joinedload
from graphql import GraphQLError
from models import Post, Comment, SessionLocal
from flask import Flask, g
from models import SessionLocal
from graphql import GraphQLError



# Set up logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
logger = logging.getLogger(__name__)


# Define GraphQL types
class CommentType(graphene.ObjectType):
    id = graphene.ID()
    text = graphene.String(required=True)
    commenter = graphene.Field(lambda: UserType)


class PostType(graphene.ObjectType):
    id = graphene.ID()
    title = graphene.String()
    content = graphene.String()
    comments = graphene.List(CommentType)

    def resolve_comments(self, info):
        if self.comments is not None:
            return self.comments

        print('fetching comments')

        # Retrieve comments from "database" based on post ID
        db = info.context['db']
        return [
            build_comment_response(comment)
            for comment in db.query(Comment).filter_by(post_id=self.id).all()
        ]


class UserType(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    email = graphene.String()
    posts = graphene.List(PostType)

    def resolve_posts(self, info):
        if self.posts is not None:
            return self.posts

        print('fetching posts')
        db = info.context['db']  # Access the database session

        # Dynamically fetch posts from "database" by filtering on `user_id`
        return [
            PostType(id=post.id, content=post.content)
            for post in db.query(Post).filter_by(user_id=self.id).all()
        ]


def build_comment_response(comment_data):
    return CommentType(id=comment_data.id,
                       text=comment_data.text,
                       commenter=UserType(id=comment_data.commenter.id,
                                          name=comment_data.commenter.name,
                                          email=comment_data.commenter.email))


def build_post_response(post_data):
    return PostType(id=post_data.id,
                    content=post_data.content,
                    comments=[
                        build_comment_response(comment)
                        for comment in post_data.comments
                    ])


# Define the Query class
class Query(graphene.ObjectType):
    user = graphene.Field(UserType, user_id=graphene.ID(required=True))
    joined_user = graphene.Field(UserType, user_id=graphene.ID(required=True))
    example_error = graphene.String()
    posts_with_error = graphene.List(PostType, user_id=graphene.ID(required=True))

    def resolve_user(self, info, user_id):
        db = info.context['db']  # Access the database session

        # Fetch the user from "database"
        user_data = db.query(User).get(user_id)
        if user_data:
            return UserType(id=user_data.id,
                            name=user_data.name,
                            email=user_data.email)
        return None

    def resolve_joined_user(self, info, user_id):
        db = info.context['db']  # Access the database session

        # Fetch the user from "database"
        user_data = (db.query(User).options(
            joinedload(User.posts).joinedload(
                Post.comments)).filter(User.id == user_id).first())

        if not user_data:
            return None

        return UserType(
            id=user_data.id,
            name=user_data.name,
            email=user_data.email,
            posts=[build_post_response(post) for post in user_data.posts])

    def resolve_example_error(self, info):
        raise GraphQLError("This is a custom error message",
                           extensions={"code": "CUSTOM_ERROR"})

    
    def resolve_posts_with_error(self, info, user_id):
        db = info.context['db']
        posts_data = db.query(Post).filter(Post.user_id == user_id).all()
        posts_response = [
            PostType(id=post.id, content=post.content)
            for post in posts_data
        ]
        posts_response.append({
            'random': 'field'
        })
        return posts_response


class AddPost(graphene.Mutation):

    class Arguments:
        content = graphene.String()

    post = graphene.Field(PostType)

    def mutate(self, info, content):
        user_id = info.context['user_id']

        if not user_id:
            raise GraphQLError("Unauthorized access to field: {}".format(
                info.field_name),
                               extensions={"code": "UNAUTHENTICATED"})

        db = info.context['db']
        post = Post(id=uuid.uuid4().hex, content=content, user_id=user_id)
        db.add(post)
        db.commit()
        return AddPost(post=post)


class AddComment(graphene.Mutation):

    class Arguments:
        text = graphene.String()
        post_id = graphene.ID()
        commenter_id = graphene.ID()

    comment = graphene.Field(CommentType)

    def mutate(self, info, text, post_id):
        commenter_id = info.context['user_id']
        if not commenter_id:
            raise GraphQLError("Unauthorized access to field: {}".format(
                info.field_name),
                               extensions={"code": "UNAUTHENTICATED"})

        db = info.context['db']
        comment = Comment(id=uuid.uuid4().hex,
                          text=text,
                          post_id=post_id,
                          commenter_id=commenter_id)
        db.add(comment)
        db.commit()
        return AddComment(comment=comment)


class Mutation(graphene.ObjectType):
    add_post = AddPost.Field()
    add_comment = AddComment.Field()


logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.before_request
def before_request():
    g.db = SessionLocal()


@app.teardown_request
def teardown_request(exception=None):
    db_session = g.pop('db', None)
    if db_session:
        db_session.close()


class ErrorLoggingMiddleware:

    def resolve(self, next, root, info, **args):
        try:
            # Call the next resolver
            return next(root, info, **args)
        except Exception as e:
            # Log full stack trace
            logger.error("Exception in resolver '%s': %s", info.field_name,
                         traceback.format_exc())
            raise


# Set up the schema
schema = graphene.Schema(query=Query, mutation=Mutation)


@app.route('/graphql', methods=['GET', 'POST'])
def graphql():

    # Add the `db` session to the context
    print(f'{request.headers=}')
    context = {"db": g.db, 'user_id': request.headers.get('Auth-User')}
    return GraphQLView.as_view(
        "graphql",
        schema=schema,
        graphiql=True,  # Enable GraphiQL interface
        context=context,  # Add custom context
        debug=True,
        middleware=[ErrorLoggingMiddleware()])()


if __name__ == "__main__":
    app.run(debug=True)
