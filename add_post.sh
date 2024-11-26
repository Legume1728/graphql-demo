#!/bin/bash

http post localhost:5000/graphql query=@add_post.graphql \
  AUTH-USER:"user123" \
  variables:='{"post_content": "Something new happened!"}'