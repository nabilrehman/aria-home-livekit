warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /telephony/accepting-calls/inbound-twilio

LiveKit docs › Telephony › Accepting calls › Twilio Voice integration

---

# Twilio Voice integration

> How to use LiveKit SIP with TwiML and Twilio conferencing.

## Inbound calls with Twilio programmable voice

Accept inbound calls using Twilio programmable voice. You need an inbound trunk and a dispatch rule created using the LiveKit CLI (or SDK) to accept calls and route callers to LiveKit rooms. The following steps guide you through the process.

> ℹ️ **Unsupported features**
> 
> This method doesn't support [SIP REFER](https://docs.livekit.io/telephony/features/transfers/cold.md) or outbound calls. To use these features, switch to Elastic SIP Trunking. For details, see the [Configuring Twilio SIP trunks](https://docs.livekit.io/telephony/start/providers/twilio.md) quickstart.

### Step 1. Purchase a phone number from Twilio

If you don't already have a phone number, see [How to Search for and Buy a Twilio Phone Number From Console](https://help.twilio.com/articles/223135247-How-to-Search-for-and-Buy-a-Twilio-Phone-Number-from-Console).

### Step 2. Set up a TwiML Bin

> ℹ️ **Other approaches**
> 
> This guide uses TwiML Bins, but you can also return TwiML via another mechanism, such as a webhook.

TwiML Bins are a simple way to test TwiML responses. Use a TwiML Bin to redirect an inbound call to LiveKit.

To create a TwiML Bin, follow these steps:

1. Sign in to the [Twilio console](https://console.twilio.com/).
2. Select **Develop** » **TwiML Bins**.
3. Create a TwiML Bin and add the following contents:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Dial>
    <Sip username="<sip_trunk_username>" password="<sip_trunk_password>">
      sip:<your_phone_number>@%{sipHost}%;transport=tcp
    </Sip>
  </Dial>
</Response>

```

### Step 3. Direct phone number to the TwiML Bin

Configure incoming calls to a specific phone number to use the TwiML Bin you just created:

1. Sign in to the [Twilio console](https://console.twilio.com/).
2. Select **Products & Services** » **Numbers & Senders** » **Overview**.
3. In the **Phone Numbers** section, select the purchased phone number.
4. In the **Configuration details** section, select **Voice and emergency calling** » select **Edit voice configuration**.
5. In the **How do you want to configur this number?** section, for **Select a method**, select **Webhook, TwiML Bin, Function, Studio Flow, Proxy Service**.
6. In the **How do you want to set up your primary method?**, for **Select your primary method**, select **Use TwiML Bins**.
7. Select the TwiML Bin you just created for **Select a TwiML Bin**.
8. Select **Save**.

### Step 4. Create a LiveKit inbound trunk

Use the LiveKit CLI to create an [inbound trunk](https://docs.livekit.io/telephony/accepting-calls/inbound-trunk.md) for the purchased phone number.

1. Create an `inbound-trunk.json` file with the following contents. Replace the phone number with the one purchased from Twilio:

```json
{
  "trunk": {
    "name": "My inbound trunk",
    "numbers": ["<your_phone_number>"]
  }
}

```
2. Use the CLI to create an inbound trunk. Pass the same username and password that you specified in the TwiML Bin using the `--auth-user` and `--auth-pass` flags:

```shell
lk sip inbound create inbound-trunk.json \
  --auth-user <sip_trunk_username> \
  --auth-pass <sip_trunk_password>

```

### Step 5. Create a dispatch rule to place each caller into their own room.

Use the LiveKit CLI to create a [dispatch rule](https://docs.livekit.io/telephony/accepting-calls/dispatch-rule.md) that places each caller into individual rooms named with the prefix `call`.

1. Create a `dispatch-rule.json` file with the following contents:

```json
{
  "dispatch_rule":
   {
     "rule": {
       "dispatchRuleIndividual": {
         "roomPrefix": "call-"
       }
     }
   }
}

```
2. Create the dispatch rule using the CLI:

```shell
lk sip dispatch create dispatch-rule.json

```

If you already have a default [caller dispatch rule](https://docs.livekit.io/telephony/accepting-calls/dispatch-rule.md#individual-dispatch-rule) and want to match a specific trunk, create the dispatch rule using the `trunks` flag with the ID of the trunk you just created:

```shell
lk sip dispatch create dispatch-rule.json --trunks "<trunk-id>"

```

### Testing with an agent

Follow the [Voice AI quickstart](https://docs.livekit.io/agents/start/voice-ai.md) to create an agent that responds to incoming calls. Add the prebuilt [EndCallTool](https://docs.livekit.io/agents/prebuilt/tools/end-call-tool.md) to your agent's tools so the agent can hang up the call when the conversation is complete. For a custom implementation, see [Hang up](https://docs.livekit.io/telephony/accepting-calls/workflow-setup.md#hangup). Then call the phone number and your agent should pick up the call.

After your agent answers, validate the setup end to end by following the [Testing your telephony setup](https://docs.livekit.io/telephony/testing.md) checklist to confirm the room, SIP participant attributes, and agent dispatch all match what you expect.

## Multi-number routing

To route calls from different phone numbers to different agents (for example, one number for English support and another for Spanish), create a separate inbound trunk and dispatch rule for each number.

### Step 1. Set up a TwiML Bin for each number

Create a [TwiML Bin](#step-2-set-up-a-twiml-bin) for each phone number. Each TwiML Bin uses the same LiveKit SIP host but includes the specific phone number in the SIP URI.

> ℹ️ **Differentiating trunks**
> 
> Each TwiML Bin uses a different phone number, username, and password.

**English number TwiML Bin:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Dial>
    <Sip username="<english_trunk_username>" password="<english_trunk_password>">
      sip:<english_phone_number>@%{sipHost}%;transport=tcp
    </Sip>
  </Dial>
</Response>

```

**Spanish number TwiML Bin:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Dial>
    <Sip username="<spanish_trunk_username>" password="<spanish_trunk_password>">
      sip:<spanish_phone_number>@%{sipHost}%;transport=tcp
    </Sip>
  </Dial>
</Response>

```

[Direct each Twilio phone number](#step-3-direct-phone-number-to-the-twiml-bin) to its corresponding TwiML Bin.

### Step 2. Create a LiveKit inbound trunk for each number

Create an [inbound trunk](https://docs.livekit.io/telephony/accepting-calls/inbound-trunk.md) for each phone number. Use the credentials from the corresponding TwiML Bin.

**english-trunk.json:**

```json
{
  "trunk": {
    "name": "English support trunk",
    "numbers": ["<english_phone_number>"]
  }
}

```

**spanish-trunk.json:**

```json
{
  "trunk": {
    "name": "Spanish support trunk",
    "numbers": ["<spanish_phone_number>"]
  }
}

```

Create both trunks using the CLI. Pass the credentials from each TwiML Bin using the `--auth-user` and `--auth-pass` flags:

```shell
lk sip inbound create english-trunk.json \
  --auth-user <english_trunk_username> \
  --auth-pass <english_trunk_password>
lk sip inbound create spanish-trunk.json \
  --auth-user <spanish_trunk_username> \
  --auth-pass <spanish_trunk_password>

```

Note the trunk IDs returned by each command.

### Step 3. Create a dispatch rule for each trunk

Create a [dispatch rule](https://docs.livekit.io/telephony/accepting-calls/dispatch-rule.md) for each trunk. Use the `trunks` flag to bind each rule to a specific trunk, and use `roomConfig` to [dispatch a different agent](https://docs.livekit.io/agents/server/agent-dispatch.md) for each number:

**english-dispatch.json:**

```json
{
  "dispatch_rule": {
    "rule": {
      "dispatchRuleIndividual": {
        "roomPrefix": "english-"
      }
    },
    "name": "English dispatch rule",
    "roomConfig": {
      "agents": [{
        "agentName": "english-agent"
      }]
    }
  }
}

```

**spanish-dispatch.json:**

```json
{
  "dispatch_rule": {
    "rule": {
      "dispatchRuleIndividual": {
        "roomPrefix": "spanish-"
      }
    },
    "name": "Spanish dispatch rule",
    "roomConfig": {
      "agents": [{
        "agentName": "spanish-agent"
      }]
    }
  }
}

```

Create both dispatch rules with their corresponding trunk IDs:

```shell
lk sip dispatch create english-dispatch.json --trunks "<english-trunk-id>"
lk sip dispatch create spanish-dispatch.json --trunks "<spanish-trunk-id>"

```

Now calls to the English number route to the `english-agent` and calls to the Spanish number route to the `spanish-agent`.

## Connecting to a Twilio phone conference

You can bridge Twilio conferencing to LiveKit via SIP, allowing you to add agents and other LiveKit clients to an existing Twilio conference. This requires the following setup:

- [Twilio conferencing](https://www.twilio.com/docs/voice/conference).
- LiveKit [inbound trunk](https://docs.livekit.io/telephony/accepting-calls/inbound-trunk.md).
- LiveKit [voice AI agent](https://docs.livekit.io/agents/start/voice-ai.md).

The example in this section uses [Node](https://nodejs.org) and the [Twilio Node SDK](https://www.twilio.com/docs/libraries).

### Step 1. Set Twilio environment variables

You can find these values in your [Twilio Console](https://console.twilio.com/):

```shell
export TWILIO_ACCOUNT_SID=<twilio_account_sid>
export TWILIO_AUTH_TOKEN=<twilio_auth_token>

```

### Step 2. Bridge a Twilio conference and LiveKit SIP

Create a `bridge.js` file and update the `twilioPhoneNumber`, `conferenceSid`, `sipHost`, and `from` field for the API call in the following code:

```typescript
import twilio from 'twilio';

const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;

const twilioClient = twilio(accountSid, authToken);

/**
 * Phone number bought from Twilio that is associated with a LiveKit trunk.
 * For example, +14155550100.
 * See https://docs.livekit.io/sip/quickstarts/configuring-twilio-trunk/
 */
const twilioPhoneNumber = '<sip_trunk_phone_number>';

/**
 * SIP host is available in your LiveKit Cloud project settings.
 * This is your project domain without the leading "sip:".
 */
const sipHost = '%{sipHost}%';

/**
 * The conference SID from Twilio that you want to add the agent to. You
 * likely want to obtain this from your conference status callback webhook handler.
 * The from field must contain the phone number, client identifier, or username
 * portion of the SIP address that made this call.
 * See https://www.twilio.com/docs/voice/api/conference-participant-resource#request-body-parameters
 */
const conferenceSid = '<twilio_conference_sid>';
await twilioClient.conferences(conferenceSid).participants.create({
    from: '<valid_from_value>',
    to: `sip:${twilioPhoneNumber}@${sipHost};transport=tcp`,
});

```

### Step 3. Execute the file

When you run the file, it bridges the Twilio conference to a new LiveKit session using the previously configured dispatch rule. This allows you to automatically [dispatch an agent](https://docs.livekit.io/agents/server/agent-dispatch.md) to the Twilio conference.

```shell
node bridge.js

```

---

This document was rendered at 2026-08-24T21:31:19.705Z.
For the latest version of this document, see [https://docs.livekit.io/telephony/accepting-calls/inbound-twilio.md](https://docs.livekit.io/telephony/accepting-calls/inbound-twilio.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).
