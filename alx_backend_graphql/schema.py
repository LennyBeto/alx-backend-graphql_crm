import graphene
from crm.schema import Query, Mutation


class Query(graphene.ObjectType):
  
    hello = graphene.String(default_value="Hello, GraphQL!")

# Create the final schema by passing the Query class to graphene.Schema.
schema = graphene.Schema(query=Query, mutation=Mutation)
