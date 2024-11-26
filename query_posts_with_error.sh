http get localhost:5000/graphql \
  query=@query_posts_with_error.graphql \
  variables:='{"user_id": "user123"}'