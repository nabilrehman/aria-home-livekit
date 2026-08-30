warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /telephony/start/providers/plivo

LiveKit docs › Telephony › Get Started › Provider-specific quickstarts › Plivo

---

# Create and configure a Plivo SIP trunk

> Step-by-step instructions for creating inbound and outbound SIP trunks using Plivo.

Connect [Plivo's](https://plivo.com) SIP trunking with LiveKit for inbound and outbound calls. You can configure Plivo using the [Plivo SIP Trunking (Zentrunk) API](https://www.plivo.com/docs/sip-trunking/api/overview) or the [Plivo Console](https://cx.plivo.com/). Each step in this guide includes both options.

## Prerequisites

The following are required to complete the steps in this guide:

- [Plivo account](https://cx.plivo.com/)
- [LiveKit Cloud project](https://cloud.livekit.io/projects/p_/settings/project)

If you're using the Plivo API, you also need your Plivo **Auth ID** and **Auth Token**, available on the [Plivo Console home page](https://cx.plivo.com/home). The Plivo API uses HTTP Basic authentication. Export your credentials as environment variables to use with the code samples in this guide:

```shell
export PLIVO_AUTH_ID="<your_auth_id>"
export PLIVO_AUTH_TOKEN="<your_auth_token>"

```

## Inbound calling

To accept inbound calls with Plivo and LiveKit, complete the steps in the following sections.

### Create a SIP trunk

Create an inbound trunk in Plivo, setting your LiveKit SIP endpoint as the primary URI.

**API**:

1. Create an [origination URI](https://www.plivo.com/docs/sip-trunking/api/origination-uris) that points to your LiveKit [SIP endpoint](https://docs.livekit.io/telephony/start/sip-trunk-setup.md#sip-endpoint). Include `;transport=tcp` in the URI:

**cURL**:

```shell
curl "https://api.plivo.com/v1/Account/$PLIVO_AUTH_ID/Zentrunk/URI/" \
-u "$PLIVO_AUTH_ID:$PLIVO_AUTH_TOKEN" \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-d '{
  "name": "LiveKit SIP endpoint",
  "uri": "%{sipHost}%;transport=tcp"
}'

```

---

**Python**:

```python
import os
import requests

auth_id = os.environ["PLIVO_AUTH_ID"]
auth_token = os.environ["PLIVO_AUTH_TOKEN"]

response = requests.post(
    f"https://api.plivo.com/v1/Account/{auth_id}/Zentrunk/URI/",
    auth=(auth_id, auth_token),
    json={
        "name": "LiveKit SIP endpoint",
        "uri": "%{sipHost}%;transport=tcp",
    },
)
print(response.json())

```

---

**Node.js**:

```javascript
const authId = process.env.PLIVO_AUTH_ID;
const authToken = process.env.PLIVO_AUTH_TOKEN;
const authHeader = 'Basic ' + Buffer.from(`${authId}:${authToken}`).toString('base64');

const response = await fetch(`https://api.plivo.com/v1/Account/${authId}/Zentrunk/URI/`, {
  method: 'POST',
  headers: {
    'Authorization': authHeader,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: 'LiveKit SIP endpoint',
    uri: '%{sipHost}%;transport=tcp',
  }),
});
console.log(await response.json());

```

> ℹ️ **Secure trunking**
> 
> If you're setting up [secure trunking](https://docs.livekit.io/telephony/features/secure-trunking.md), use `;transport=tls` instead of `;transport=tcp`.

> ℹ️ **Region-based endpoints**
> 
> To restrict calls to a specific region, replace your global LiveKit SIP endpoint with a [region-based endpoint](https://docs.livekit.io/telephony/features/region-pinning.md).

Copy the `uri_uuid` from the output of the command for the next step:

```json
{
  "api_id": "<api_id>",
  "message": "Origination URI created successfully",
  "uri_uuid": "<uri_uuid>"
}

```
2. Create an [inbound trunk](https://www.plivo.com/docs/sip-trunking/api/trunks) using the origination URI as the primary URI:

**cURL**:

```shell
curl "https://api.plivo.com/v1/Account/$PLIVO_AUTH_ID/Zentrunk/Trunk/" \
-u "$PLIVO_AUTH_ID:$PLIVO_AUTH_TOKEN" \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-d '{
  "name": "My LiveKit inbound trunk",
  "trunk_direction": "inbound",
  "primary_uri_uuid": "<uri_uuid>"
}'

```

---

**Python**:

```python
import os
import requests

auth_id = os.environ["PLIVO_AUTH_ID"]
auth_token = os.environ["PLIVO_AUTH_TOKEN"]

response = requests.post(
    f"https://api.plivo.com/v1/Account/{auth_id}/Zentrunk/Trunk/",
    auth=(auth_id, auth_token),
    json={
        "name": "My LiveKit inbound trunk",
        "trunk_direction": "inbound",
        "primary_uri_uuid": "<uri_uuid>",
    },
)
print(response.json())

```

---

**Node.js**:

```javascript
const authId = process.env.PLIVO_AUTH_ID;
const authToken = process.env.PLIVO_AUTH_TOKEN;
const authHeader = 'Basic ' + Buffer.from(`${authId}:${authToken}`).toString('base64');

const response = await fetch(`https://api.plivo.com/v1/Account/${authId}/Zentrunk/Trunk/`, {
  method: 'POST',
  headers: {
    'Authorization': authHeader,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: 'My LiveKit inbound trunk',
    trunk_direction: 'inbound',
    primary_uri_uuid: '<uri_uuid>',
  }),
});
console.log(await response.json());

```

Copy the `trunk_id` from the output of the command. Use it to connect your phone number in the next step:

```json
{
  "api_id": "<api_id>",
  "message": "Trunk created successfully.",
  "trunk_id": "<trunk_id>"
}

```

---

**Console**:

1. Sign in to the [Plivo Console](https://cx.plivo.com/).
2. Navigate to **SIP Trunking** → [**Inbound Trunks**](https://cx.plivo.com/sip-trunking/inbound).
3. Select **Create Trunk** and provide a descriptive name for your trunk.
4. For **Primary URI**, select **Add New URI** and enter your LiveKit [SIP endpoint](https://docs.livekit.io/telephony/start/sip-trunk-setup.md#sip-endpoint). Include `;transport=tcp` in the URI. For example, `vjnxecm0tjk.sip.livekit.cloud;transport=tcp`.

> ℹ️ **Secure trunking**
> 
> If you're setting up [secure trunking](https://docs.livekit.io/telephony/features/secure-trunking.md), use `;transport=tls` instead of `;transport=tcp`.

> ℹ️ **Region-based endpoints**
> 
> To restrict calls to a specific region, replace your global LiveKit SIP endpoint with a [region-based endpoint](https://docs.livekit.io/telephony/features/region-pinning.md).
5. For **Link Numbers**, select your phone number from the dropdown menu. Or connect your phone number in the next step.
6. Select **Create Trunk**.

### Connect your phone number

Connect your Plivo phone number to the inbound trunk. You can skip this step if you connected your phone number when you created the inbound trunk.

**API**:

Assign the inbound trunk to your phone number using the [update a number](https://www.plivo.com/docs/numbers/api/account-phone-number#update-a-number) endpoint. In the endpoint URL, replace the example number with your Plivo phone number in E.164 format, without the leading `+`. For example, `15105550100`. Set the `app_id` field to the **trunk ID** of your inbound trunk:

**cURL**:

```shell
curl "https://api.plivo.com/v1/Account/$PLIVO_AUTH_ID/Number/15105550100/" \
-u "$PLIVO_AUTH_ID:$PLIVO_AUTH_TOKEN" \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-d '{
  "app_id": "<trunk_id>"
}'

```

---

**Python**:

```python
import os
import requests

auth_id = os.environ["PLIVO_AUTH_ID"]
auth_token = os.environ["PLIVO_AUTH_TOKEN"]
phone_number = "15105550100"

response = requests.post(
    f"https://api.plivo.com/v1/Account/{auth_id}/Number/{phone_number}/",
    auth=(auth_id, auth_token),
    json={
        "app_id": "<trunk_id>",
    },
)
print(response.json())

```

---

**Node.js**:

```javascript
const authId = process.env.PLIVO_AUTH_ID;
const authToken = process.env.PLIVO_AUTH_TOKEN;
const authHeader = 'Basic ' + Buffer.from(`${authId}:${authToken}`).toString('base64');
const phoneNumber = '15105550100';

const response = await fetch(`https://api.plivo.com/v1/Account/${authId}/Number/${phoneNumber}/`, {
  method: 'POST',
  headers: {
    'Authorization': authHeader,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    app_id: '<trunk_id>',
  }),
});
console.log(await response.json());

```

A successful response returns HTTP `202`:

```json
{
  "api_id": "<api_id>",
  "message": "changed"
}

```

To list your purchased numbers, run the following command:

**cURL**:

```shell
curl "https://api.plivo.com/v1/Account/$PLIVO_AUTH_ID/Number/" \
-u "$PLIVO_AUTH_ID:$PLIVO_AUTH_TOKEN" \
-H 'Accept: application/json'

```

---

**Python**:

```python
import os
import requests

auth_id = os.environ["PLIVO_AUTH_ID"]
auth_token = os.environ["PLIVO_AUTH_TOKEN"]

response = requests.get(
    f"https://api.plivo.com/v1/Account/{auth_id}/Number/",
    auth=(auth_id, auth_token),
)
print(response.json())

```

---

**Node.js**:

```javascript
const authId = process.env.PLIVO_AUTH_ID;
const authToken = process.env.PLIVO_AUTH_TOKEN;
const authHeader = 'Basic ' + Buffer.from(`${authId}:${authToken}`).toString('base64');

const response = await fetch(`https://api.plivo.com/v1/Account/${authId}/Number/`, {
  headers: { 'Authorization': authHeader },
});
console.log(await response.json());

```

---

**Console**:

1. Navigate to **Phone Numbers** → [**Purchased Numbers**](https://cx.plivo.com/phone-numbers/list).
2. Select the phone number to connect to the trunk.
3. For **Application Type**, select **SIP Trunk**.
4. For **Trunk**, select the trunk you created in the previous step.
5. Select **Save changes**.

### Configure LiveKit to accept calls

Set up an [inbound trunk](https://docs.livekit.io/telephony/accepting-calls/inbound-trunk.md) and [dispatch rule](https://docs.livekit.io/telephony/accepting-calls/dispatch-rule.md) in LiveKit to accept calls to your Plivo phone number.

### Test incoming calls

Start your LiveKit agent and call your Plivo phone number. Your agent should answer the call. If you don't have an agent, see the [Voice AI quickstart](https://docs.livekit.io/agents/start/voice-ai.md) to create one.

### Troubleshooting

For help troubleshooting inbound calls, check the following logs:

- First check the [Plivo logs](https://cx.plivo.com/logs/zentrunk).
- Then check the [call logs](https://cloud.livekit.io/projects/p_/telephony) in your LiveKit Cloud dashboard.

## Outbound calling

To make outbound calls with Plivo and LiveKit, complete the steps in the following sections.

### Create an outbound trunk in Plivo

Set up an outbound trunk with username and password authentication in Plivo.

**API**:

1. Create a [credential](https://www.plivo.com/docs/sip-trunking/api/credentials) with a username and strong password for outbound call authentication. The username must be 5 to 20 alphanumeric characters. The password must be 5 to 20 characters, using only alphanumeric characters and the special characters `~!@#$%^&*()_+`, and must include at least one special character. Make sure these values match the username and password you use for your LiveKit outbound trunk:

**cURL**:

```shell
curl "https://api.plivo.com/v1/Account/$PLIVO_AUTH_ID/Zentrunk/Credential/" \
-u "$PLIVO_AUTH_ID:$PLIVO_AUTH_TOKEN" \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-d '{
  "name": "LiveKit outbound credential",
  "username": "<username>",
  "password": "<password>"
}'

```

---

**Python**:

```python
import os
import requests

auth_id = os.environ["PLIVO_AUTH_ID"]
auth_token = os.environ["PLIVO_AUTH_TOKEN"]

response = requests.post(
    f"https://api.plivo.com/v1/Account/{auth_id}/Zentrunk/Credential/",
    auth=(auth_id, auth_token),
    json={
        "name": "LiveKit outbound credential",
        "username": "<username>",
        "password": "<password>",
    },
)
print(response.json())

```

---

**Node.js**:

```javascript
const authId = process.env.PLIVO_AUTH_ID;
const authToken = process.env.PLIVO_AUTH_TOKEN;
const authHeader = 'Basic ' + Buffer.from(`${authId}:${authToken}`).toString('base64');

const response = await fetch(`https://api.plivo.com/v1/Account/${authId}/Zentrunk/Credential/`, {
  method: 'POST',
  headers: {
    'Authorization': authHeader,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: 'LiveKit outbound credential',
    username: '<username>',
    password: '<password>',
  }),
});
console.log(await response.json());

```

Copy the `credential_uuid` from the output for the next step:

```json
{
  "api_id": "<api_id>",
  "message": "Credential created successfully",
  "credential_uuid": "<credential_uuid>"
}

```
2. Create an [outbound trunk](https://www.plivo.com/docs/sip-trunking/api/trunks) using the credential:

**cURL**:

```shell
curl "https://api.plivo.com/v1/Account/$PLIVO_AUTH_ID/Zentrunk/Trunk/" \
-u "$PLIVO_AUTH_ID:$PLIVO_AUTH_TOKEN" \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-d '{
  "name": "My LiveKit outbound trunk",
  "trunk_direction": "outbound",
  "credential_uuid": "<credential_uuid>",
  "secure": true
}'

```

---

**Python**:

```python
import os
import requests

auth_id = os.environ["PLIVO_AUTH_ID"]
auth_token = os.environ["PLIVO_AUTH_TOKEN"]

response = requests.post(
    f"https://api.plivo.com/v1/Account/{auth_id}/Zentrunk/Trunk/",
    auth=(auth_id, auth_token),
    json={
        "name": "My LiveKit outbound trunk",
        "trunk_direction": "outbound",
        "credential_uuid": "<credential_uuid>",
        "secure": True,
    },
)
print(response.json())

```

---

**Node.js**:

```javascript
const authId = process.env.PLIVO_AUTH_ID;
const authToken = process.env.PLIVO_AUTH_TOKEN;
const authHeader = 'Basic ' + Buffer.from(`${authId}:${authToken}`).toString('base64');

const response = await fetch(`https://api.plivo.com/v1/Account/${authId}/Zentrunk/Trunk/`, {
  method: 'POST',
  headers: {
    'Authorization': authHeader,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: 'My LiveKit outbound trunk',
    trunk_direction: 'outbound',
    credential_uuid: '<credential_uuid>',
    secure: true,
  }),
});
console.log(await response.json());

```

> 💡 **Secure trunking**
> 
> If you enable secure trunking in Plivo (`"secure": true`), you must also enable secure trunking in LiveKit. To learn more, see [Secure trunking](https://docs.livekit.io/telephony/features/secure-trunking.md).

Copy the `trunk_id` from the output:

```json
{
  "api_id": "<api_id>",
  "message": "Trunk created successfully.",
  "trunk_id": "<trunk_id>"
}

```
3. Retrieve the trunk to get your **Termination SIP Domain**. In the endpoint URL, replace `<trunk_id>` with the trunk ID from the previous step. The domain is returned in the `trunk_domain` field of the response. For example, `21784177241578.zt.plivo.com`:

**cURL**:

```shell
curl "https://api.plivo.com/v1/Account/$PLIVO_AUTH_ID/Zentrunk/Trunk/<trunk_id>/" \
-u "$PLIVO_AUTH_ID:$PLIVO_AUTH_TOKEN" \
-H 'Accept: application/json'

```

---

**Python**:

```python
import os
import requests

auth_id = os.environ["PLIVO_AUTH_ID"]
auth_token = os.environ["PLIVO_AUTH_TOKEN"]
trunk_id = "<trunk_id>"

response = requests.get(
    f"https://api.plivo.com/v1/Account/{auth_id}/Zentrunk/Trunk/{trunk_id}/",
    auth=(auth_id, auth_token),
)
print(response.json())

```

---

**Node.js**:

```javascript
const authId = process.env.PLIVO_AUTH_ID;
const authToken = process.env.PLIVO_AUTH_TOKEN;
const authHeader = 'Basic ' + Buffer.from(`${authId}:${authToken}`).toString('base64');
const trunkId = '<trunk_id>';

const response = await fetch(`https://api.plivo.com/v1/Account/${authId}/Zentrunk/Trunk/${trunkId}/`, {
  headers: { 'Authorization': authHeader },
});
console.log(await response.json());

```

A successful response returns the following output including the `trunk_domain` field:

```json
{
  "api_id": "<api_id>",
  "object": {
    "trunk_id": "<trunk_id>",
    "name": "My LiveKit outbound trunk",
    "trunk_status": "enabled",
    "secure": true,
    "trunk_domain": "<trunk_id>.zt.plivo.com",
    "trunk_direction": "outbound",
    "ipacl_uuid": null,
    "credential_uuid": "<credential_uuid>",
    "primary_uri_uuid": null,
    "fallback_uri_uuid": null
  }
}

```

Copy the **Termination SIP Domain** (`trunk_domain`) for the next step.

---

**Console**:

1. Sign in to the [Plivo Console](https://cx.plivo.com/).
2. Navigate to **SIP Trunking** → [**Outbound Trunks**](https://cx.plivo.com/zentrunk/outbound-trunks/).
3. Select **Create Trunk** and provide a descriptive name for your trunk.
4. In the **Trunk Authentication** section → **Credential**, select **Create new credential**.
5. Add a credential name, and a username and strong password for outbound call authentication. Make sure these values match the username and password you use for your LiveKit outbound trunk. Select **Create credential**.
6. For **Authentication**, select the credential you created in the previous step.
7. For secure trunking, select the switch next to **Secure Trunking**.

> 💡 **Secure trunking**
> 
> If you enable secure trunking in Plivo, you must also enable secure trunking in LiveKit. To learn more, see [Secure trunking](https://docs.livekit.io/telephony/features/secure-trunking.md).
8. Select **Create Trunk** to complete your outbound trunk configuration.

Copy the **Termination SIP Domain** for the next step.

### Configure LiveKit to make outbound calls

Create an [outbound trunk](https://docs.livekit.io/telephony/making-calls/outbound-trunk.md) in LiveKit using the **Termination SIP Domain**, and username and password from the previous section.

### Place an outbound call

Test your configuration by placing an outbound call with LiveKit using the `CreateSIPParticipant` API. To learn more, see [Creating a SIP participant](https://docs.livekit.io/telephony/making-calls/outbound-calls.md#creating-a-sip-participant).

### Troubleshooting

If the call fails to connect, check the following common issues:

- Verify your SIP URI. It must include `;transport=tcp`.
- Verify your Plivo phone number is associated with the correct trunk.

For outbound calls, check the following logs:

- First check the [call logs](https://cloud.livekit.io/projects/p_/telephony) in your LiveKit Cloud dashboard.
- Then check the [Plivo logs](https://cx.plivo.com/logs/zentrunk/).

For error codes, see the [Plivo hangup codes](https://www.plivo.com/docs/voice/troubleshooting/hangup-causes) reference.

## Regional restrictions

If your calls are made from a Plivo India phone number, or you're dialing numbers in India, you must enable [region pinning](https://docs.livekit.io/telephony/features/region-pinning.md) for your LiveKit project. This restricts calls to India to comply with local telephony regulations. Your calls will fail to connect if region pinning is not enabled.

For other countries, select the region closest to the location of your call traffic for optimal performance.

## Next steps

The following guides provide next steps for building your LiveKit telephony app.

- **[Voice AI quickstart](https://docs.livekit.io/agents/start/voice-ai.md)**: A quickstart guide to build a voice AI agent to answer incoming calls.

- **[Agents telephony integration](https://docs.livekit.io/agents/start/telephony.md)**: Learn how to receive and make calls with a voice AI agent

- **[Call forwarding using SIP REFER](https://docs.livekit.io/telephony/features/transfers/cold.md)**: How to forward calls to another number or SIP endpoint with SIP REFER.

- **[Agent-assisted warm transfer](https://docs.livekit.io/telephony/features/transfers/warm.md)**: A comprehensive guide to transferring calls using an AI agent to provide context.

- **[Secure trunking for SIP calls](https://docs.livekit.io/telephony/features/secure-trunking.md)**: How to enable secure trunking for LiveKit SIP.

- **[Region pinning for SIP](https://docs.livekit.io/telephony/features/region-pinning.md)**: Use region pinning to restrict calls to a specific region.

---

This document was rendered at 2026-08-24T21:31:35.992Z.
For the latest version of this document, see [https://docs.livekit.io/telephony/start/providers/plivo.md](https://docs.livekit.io/telephony/start/providers/plivo.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).
