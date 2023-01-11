# patreon-post-webhook-to-discord
Get a webhook from patreon and ship it to discord


## Setting up discord Webhooks

* Go to your server | Integrations
* Choose "New Webhook"
* Configure the webhook bot with a name and channel.
* Copy webhook url (Save as a github secret BBS TODO)
* Test the webhook 

## Setting up a webhook laundry

Github, correctly, [requires an access token](https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#create-a-repository-dispatch-event) to call its repository_dispatch webhook call. Thus, we need to launder the webhook call through an appropriate proxy. 

### Webhook relay

* Sign up for [webhookrelay](https://my.webhookrelay.com/) -- The free service should be acceptable.
* For testing, set up a basic webhook relay. For destination, use the Discord webhook integration url set up above. Lock the path.
* Create the configuration.
* Use the `./testDiscordWebhookPOST.sh` script with the url provided to test basic routing.


### Didn't work, but might work for you. Testing the proxy IFTTT -> Discord (No github) 

Using IFTTT, we can proxy webhooks. Use the "Recieve a web request with JSON payload", then authenticate the IFTTT bot to Discord and have it post the full json payload in a testing channel of your choice. Title should automagically be: "If Maker Event "Patreon Webhook", then post a message to a channel"

Note the Event ID at the bottom in light grey on white text. 

Ensure that the IFTTT bot has been added to the channel assigned (especially if the test channel is locked)

Then, following the [IFTTT docs on webhooks](https://help.ifttt.com/hc/en-us/articles/115010230347-Webhooks-service-FAQ) go to the [webhooks service page](https://ifttt.com/maker_webhooks) and click "Documentation"

Get the url from arbitrary JSON payload, which should look like: `curl -X POST -H "Content-Type: application/json" -d '{"this":[{"is":{"some":["test","data"]}}]}' https://maker.ifttt.com/trigger/$IFTTT_EVENT/json/with/key/$IFTTT_TOKEN`

Test with:

```{.bash}
export IFTTT_KEY=<your key>
export IFTTT_EVENT=<your event ID>
curl -X POST -H "Content-Type: application/json" -d '{"this":[{"is":{"some":["test","data"]}}]}' https://maker.ifttt.com/trigger/$IFTTT_EVENT/json/with/key/$IFTTT_TOKEN
```

Even if the IFTTT bot is offline, we can still test the webhook by going to the IFTTT event page

## Setting up Patreon
* Get a creator acess token
  * Create a client at [https://www.patreon.com/portal/registration/register-clients]. For the return URL use https://example.com What we need is the access token. You will get the token after registering the oauth return. (We will not be using OAuth)
* Get your campaign ID
  * `export PATREON_TOKEN=<yourToken>`
  * `curl -H "Accept: application/json" -H "Authorization: Bearer $PATREON_TOKEN" https://patreon.com/api/oauth2/v2/campaigns`
  * Response will be something like `{"data":[{"attributes":{},"id":"9758323","type":"campaign"}],"meta":{"pagination":{"total":1}}}` (We care about the id attribute.)  
  * Validate the ID by `curl -H "Accept: application/json" -H "Authorization: Bearer $PATREON_TOKEN" "https://patreon.com/api/oauth2/v2/campaigns/{campaignID}?fields%5Bcampaign%5D=creation_name"`
    * You will see something like `{"data":{"attributes":{"creation_name":"Just testing out an API interaction"},"id":"9758323","type":"campaign"},"links":{"self":"https://www.patreon.com/api/oauth2/v2/campaigns/9758323"}}`
    * n.b. (The necessity of urlencoding of the brackets is a noted error https://docs.patreon.com/#more-data-paging-and-sorting)

* Invoke the webhook-making-api call
  * make `patreonCreateWebhook.json` from `patreonCreateWebhook.json.dist`
    * Edit URL, edit campaign. No shell variables.
  * `curl -H "Content-Type:application/json" -H "Accept: application/json" -H "Authorization: Bearer $PATREON_TOKEN" -d '@patreonCreateWebhook.json' "https://patreon.com/api/oauth2/v2/webhooks"`




