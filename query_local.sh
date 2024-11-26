#!/bin/bash

http get localhost:5000/graphql query=@query_local.graphql variables:='{"user_id": "user123"}'