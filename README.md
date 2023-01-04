# patreon-post-webhook-to-discord
Get a webhook from patreon and ship it to discord


## Setting up discord Webhooks

* Go to your server | Integrations
* Choose "New Webhook"
* Configure the webhook bot with a name and channel.
* Copy webhook url (Save as a github secret BBS TODO)
* Test the webhook 

## Setting up Patreon
* Get a creator acess token
  * Create a client at [https://www.patreon.com/portal/registration/register-clients]. For the return URL use https://example.com What we need is the access token. You will get the token after registering the oauth return. (We will not be using OAuth)
* Get your campaign ID
  * `export TOKEN=<yourToken>`
  * `curl -H "Accept: application/json" -H "Authorization: Bearer $TOKEN" https://patreon.com/api/oauth2/v2/campaigns`
  * Response will be something like `{"data":[{"attributes":{},"id":"9758323","type":"campaign"}],"meta":{"pagination":{"total":1}}}` (We care about the id attribute.)  
  * Validate the ID by `curl -H "Accept: application/json" -H "Authorization: Bearer $TOKEN" "https://patreon.com/api/oauth2/v2/campaigns/{campaignID}?fields%5Bcampaign%5D=creation_name"`
    * You will see something like `{"data":{"attributes":{"creation_name":"Just testing out an API interaction"},"id":"9758323","type":"campaign"},"links":{"self":"https://www.patreon.com/api/oauth2/v2/campaigns/9758323"}}`
    * n.b. (The necessity of urlencoding of the brackets is a noted error https://docs.patreon.com/#more-data-paging-and-sorting)

` 


