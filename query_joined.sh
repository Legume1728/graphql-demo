#!/bin/bash

http get localhost:5000/graphql query=@query_joined.graphql variables:='{"user_id": "user123"}'