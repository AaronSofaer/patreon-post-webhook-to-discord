# patreon-post-webhook-to-discord
Get a webhook from patreon and ship it to discord


## Setting up discord Webhooks

* Go to your server | Integrations
* Choose "New Webhook"
* Configure the webhook bot with a name and channel.
* Copy webhook url
* Use the `./testDiscordWebhookPOST.sh $WEBHOOK_URL` script with the url provided to test basic routing.

## Setting up github

* Fork this repository.
* Edit the github action env files for the static metadata.
* Make a [fine-grained personal access token.](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token#creating-a-fine-grained-personal-access-token). Don't forget a reasonable expiry (1 year) and to provide it only repo scope on only the one repo that you need.
* In the repository settings > security > Secrets and variables > actions , you will need to make a number of variables and secrets
  * Variables: 
    * DISCORD_MESSAGE = "Hwaet! A new chapter is out: "
    * EPUB_LANGUAGE = "en"
    * EPUB_AUTHOR = "Test Author"
    * EPUB_TITLE_PREFIX = "Test prefix: "
  * Secrets (when you know them):
    * DISCORD_WEBHOOK_URL
    * PATREON_CREATOR_ACCESS_TOKEN


## Setting up a webhook laundry

Github, correctly, [requires an access token](https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#create-a-repository-dispatch-event) to call its repository_dispatch webhook call. Thus, we need to launder the webhook call through an appropriate proxy. 


### Setting up webhook relay



* Sign up for [webhookrelay](https://my.webhookrelay.com/) -- The free service should be acceptable.

* Under the request forwarding dropdown, select Functions and then create a new function, called `Patreon-to-github`
* In editor, open composer, paste the following:

```{.lua}
local json = require("json")

local request_payload, err = json.decode(r.RequestBody)
if err then error(err) end

local new_payload = {
    event_type= "generate_epub",
    client_payload= {
    url= request_payload.data.attributes.url, 
    title= request_payload.data.attributes.title,
    content= request_payload.data.attributes.content,
    }
}

-- encoding
local encoded_payload, err = json.encode(new_payload)
if err then error(err) end

r:SetRequestBody(encoded_payload)

-- set header
r:SetRequestHeader("Content-Type", "application/json")
r:SetRequestHeader("Accept", "application/vnd.github+json")
r:SetRequestHeader("Authorization", "Bearer " .. cfg:GetValue("github token"))
r:SetRequestHeader("X-GitHub-Api-Version", "2022-11-28")

```
* In config variables, make a variable `github token` and paste your github token as the value.
* In "Request forwarding"
  * Choose "New", public endpoint, default input domain
  * Do not run a function on the incoming request
  * Route the request to: `https://api.github.com/repos/$GITHUB_REPO_OWNER/$GITHUB_REPO_NAME/dispatches`  (Note owner *and* name should be of your fork)
  * *Do* Run a function before forwarding to destination. Choose the function you made above

* Test the proxy url `./testGithubAction.py`


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
    * Edit attributes uri, edit campaign id. No shell variables.
  * `curl -H "Content-Type:application/json" -H "Accept: application/json" -H "Authorization: Bearer $PATREON_TOKEN" -d '@patreonCreateWebhook.json' "https://patreon.com/api/oauth2/v2/webhooks"`
  * If you run it more than once, a get on the above without the post data will show how many, and `-X DELETE` on `/webhooks/{id}` will remove extras. a GET to the above, without the -d will show all viable webhooks.

