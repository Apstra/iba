# Graph queries

## Introduction

This directory has a list of sample graph queries that you can use in IBA probes. The
goal is to help probe authors get familiar with graph queries in the process of
creating probes.

Refer to AOS documentation on [graph queries](
https://files.apstra.com/docs/database_concepts.html#query-specification) for more
information about the query syntax. These queries are sometimes categorically
referred to as "qe" queries, in contrast to [GraphQL](https://graphql.org/) queries,
that are also supported by AOS, but not used in the probes

Each example is presented in a YAML file, simply for better organization and
readability. These YAML documents are __not__ consumed by AOS or any other software
component.

## Disclaimer

Exact graph query to use depends a lot on the specific use case in question. The
queries stated here are only for illustration and not meant to be used "as is".

Each query has a lot of choices to make and it's very important for you to understand
your exact requirement and come up with the right graph query(ies) to be used in
probes. You can certainly use these samples as starting points but it's unlikely for
any of these to be an accurate match for your specific requirements.

## Interactive query execution

Apstra Operating System GUI has 'GraphQL API Explorer' accessible from the blueprint
details view. You can execute the queries in this directory in the explorer
and examine the results. Be sure to change the Action dropdown from the default value
of ql to qe. You can also tweak the query and see the results interactively. Use the
explorer as an aid to arrive at the final queries that work for your specific
requirements.
