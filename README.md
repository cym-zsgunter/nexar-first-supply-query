# nexar-first-supply-query
[nexar.com]: https://nexar.com/
Simple console app which looks up supplier parts by MPN

## Prerequisites

You need an application at [nexar.com] with the Supply scope.
Use the application client ID and secret and set environment variables `NEXAR_CLIENT_ID` and `NEXAR_CLIENT_SECRET`.

## Understanding these Examples

Each of these examples are using a "nexarClient" or "supplyClient" class. This class provides the necessary functionality to retrieve tokens and then use them to query the API. Then there are example runnable files that use this client to perform a given query and then display the data.
##
### Information: Use of Community-Created Java API Client

We are excited to share a Java-based API client that was developed by a member of our community. It has not undergone any formal testing or validation by the Nexar API team. As such, we cannot guarantee the client's functionality, performance, or security at this time.

We encourage you to review the code, conducting your own tests, and ensuring it meets your needs before using it in a production environment.
