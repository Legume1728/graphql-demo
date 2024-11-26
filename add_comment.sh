#!/bin/bash

http post localhost:5000/graphql \
  Auth-User:user234 \
  query=@add_comment.graphql \
  variables:='{"comment_text": "I don't like it", "post_id": "1"}'