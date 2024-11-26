from models import Base, User, Post, Comment, SessionLocal, engine

USERS = [
    {
        "id": "user123",
        "name": "john",
        "email": "john@example.com"
    },
    {
        "id": "user234",
        "name": "emily",
        "email": "emily@example.com"
    },
]

POSTS = [
    {
        "id": "1",
        "content": "This is my first post!",
        "user_id": "user123"
    },
    {
        "id": "2",
        "content": "This is another post with more info.",
        "user_id": "user123"
    },
]

COMMENTS = {
    "1": [{
        "id": "1",
        "text": "Great post!",
        "commenter_id": "user234"
    }, {
        "id": "2",
        "text": "Very informative.",
        "commenter_id": "user234"
    }],
    "2": [{
        "id": "3",
        "text": "Nice explanation!",
        "commenter_id": "user234"
    }]
}

# Create tables
Base.metadata.create_all(engine)

def populate_posts():
    with SessionLocal() as session:
        try:
            for user_data in USERS:
                user = User(**user_data)
                session.add(user)

            for post_data in POSTS:
                post = Post(**post_data)
                session.add(post)
            
            for post_id, comments in COMMENTS.items():
                for comment_data in comments:
                    comment = Comment(**comment_data, post_id=post_id)
                    session.add(comment)
            session.commit()
            print("Posts populated successfully!")
        except Exception as e:
            session.rollback()
            print(f"Error: {e}")

if __name__ == "__main__":
    populate_posts()