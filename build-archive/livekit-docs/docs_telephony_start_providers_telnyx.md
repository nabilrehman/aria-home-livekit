warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /telephony/start/providers/telnyx

LiveKit docs › Telephony › Get Started › Provider-specific quickstarts › Telnyx

---

# Create and configure Telnyx SIP trunk

> Step-by-step instructions for creating inbound and outbound SIP trunks using Telnyx.

## Creating a Telnyx SIP trunk using the API

> ❗ **Paid account required**
> 
> Using Telnyx with LiveKit requires a paid Telnyx account. For details on trial account limitations, see [Trial account privileges & limitations](https://developers.telnyx.com/docs/account-setup/levels-and-capabilities/trial) in the Telnyx developer documentation.

You can use `curl` command to make calls to the Telnyx API V2. The commands in the steps below use the example phone number, `+15105550100`. To use the Telnyx console, see [Creating a SIP trunk using the Telnyx UI](#creating-a-sip-trunk-using-the-telnyx-ui).

### Prerequisite

Purchase a [Telnyx phone number](https://telnyx.com/products/phone-numbers).

### Step 1: Create an environment variable for API key

If you don't have a Telnyx API V2 key, see the [Telnyx guide to create one](https://support.telnyx.com/en/articles/4305158-api-keys-and-how-to-use-them).

```shell
export TELNYX_API_KEY="<your_api_v2_key>"

```

### Step 2: Create an FQDN connection

The following inbound and outbound commands include the required configuration settings if you plan on using only an inbound or outbound trunk for your LiveKit telephony app. However, by default, an [FQDN connection](https://developers.telnyx.com/api-reference/fqdn-connections/create-an-fqdn-connection) creates both an inbound and outbound trunk.

1. Creating an FQDN connection. Depending on your use case, select **Inbound**, **Outbound**, or **Inbound and outbound** to accept calls, make calls, or both:

**Inbound**:

Set the caller's number format to `+E.164` for inbound calls (this identifies the caller's number with a leading `+`):

```shell
curl -L 'https://api.telnyx.com/v2/fqdn_connections' \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-H "Authorization: Bearer $TELNYX_API_KEY" \
-d '{
  "active": true,
  "anchorsite_override": "Latency",
  "connection_name": "My LiveKit trunk",
  "inbound": {
    "ani_number_format": "+E.164",
    "dnis_number_format": "+e164"
  },
  "transport_protocol": "TCP"
}'

```

---

**Outbound**:

For outbound trunks, complete the following items:

- Create a voice profile for outbound calls.
- Configure credential authentication with a username and password.
1. Creating a [voice profile](https://developers.telnyx.com/api-reference/outbound-voice-profiles/create-an-outbound-voice-profile):

```shell
curl -L 'https://api.telnyx.com/v2/outbound_voice_profiles' \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-H "Authorization: Bearer $TELNYX_API_KEY" \
-d '{
  "name": "My LiveKit outbound voice profile",
  "traffic_type": "conversational",
  "service_plan": "global"
}'

```
2. Creating an outbound FQDN connection:

```shell
curl -L 'https://api.telnyx.com/v2/fqdn_connections' \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-H "Authorization: Bearer $TELNYX_API_KEY" \
-d '{
  "active": true,
  "anchorsite_override": "Latency",
  "connection_name": "My LiveKit trunk",
  "user_name": "<username>",
  "password": "<password>",
  "outbound": {
    "outbound_voice_profile_id": "<voice_profile_id>"
  },
  "transport_protocol": "TCP"
}'

```

---

**Inbound and Outbound**:

To configure an FQDN trunk for both inbound and outbound calls:

- Create a voice profile for outbound calls.
- Set the caller's number format to `+E.164`.
- Configure credential authentication with a username and password.
1. Create a [voice profile](https://developers.telnyx.com/api-reference/outbound-voice-profiles/create-an-outbound-voice-profile):

```shell
curl -L 'https://api.telnyx.com/v2/outbound_voice_profiles' \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-H "Authorization: Bearer $TELNYX_API_KEY" \
-d '{
  "name": "My LiveKit outbound voice profile",
  "traffic_type": "conversational",
  "service_plan": "global"
}'

```
2. Create an inbound and outbound FQDN connection:

```shell
curl -L 'https://api.telnyx.com/v2/fqdn_connections' \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-H "Authorization: Bearer $TELNYX_API_KEY" \
-d '{
  "active": true,
  "anchorsite_override": "Latency",
  "connection_name": "My LiveKit trunk",
  "user_name": "<username>",
  "password": "<password>",
  "inbound": {
    "ani_number_format": "+E.164",
    "dnis_number_format": "+e164"
  },
  "outbound": {
    "outbound_voice_profile_id": "<voice_profile_id>"
  },
  "transport_protocol": "TCP"
}'

```
2. Copy the FQDN connection ID from the output:

```json
{
  "data": {
    "id":"<connection_id>",
    ...
  }
}

```
3. Create an FQDN with your [LiveKit SIP endpoint](https://docs.livekit.io/telephony/start/sip-trunk-setup.md#sip-endpoint) and your FQDN connection ID:

```shell
curl -L 'https://api.telnyx.com/v2/fqdns' \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-H "Authorization: Bearer $TELNYX_API_KEY" \
-d '{
  "connection_id": "<connection_id>",
  "fqdn": "%{sipHost}%",
  "port": 5060,
  "dns_record_type": "a"
}'

```

> ℹ️ **Region-based endpoints**
> 
> To restrict calls to a specific region, replace your global LiveKit SIP endpoint with a [region-based endpoint](https://docs.livekit.io/telephony/features/region-pinning.md).

### Step 3: Associate phone number and trunk

1. Get the phone number ID for phone number `5105550100`:

```shell
curl -L -g 'https://api.telnyx.com/v2/phone_numbers?filter[phone_number]=5105550100' \
-H 'Accept: application/json' \
-H "Authorization: Bearer $TELNYX_API_KEY"

```

Copy the phone number ID from the output:

```json
{
  "meta": {
    "total_pages": 1,
    "total_results": 1,
    "page_number": 1,
    "page_size": 100
  },
  "data": [
    {
      "id": "<phone_number_id>",
      ...
    }
  ]
}

```
2. Add the FQDN connection to the phone number:

```shell
curl -L -X PATCH 'https://api.telnyx.com/v2/phone_numbers/<phone_number_id>' \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-H "Authorization: Bearer $TELNYX_API_KEY" \
-d '{
  "id": "<phone_number_id>",
  "connection_id": "<connection_id>"
}'

```

### Step 4: Set custom headers in SIP INVITE

This step ensures outbound calls from LiveKit to Telnyx are properly authenticated.

Telnyx uses [SIP digest authentication](https://docs.livekit.io/reference/telephony/sip-handshake.md#optional-authentication-challenge):

1. LiveKit sends an INVITE to Telnyx with the username.
2. Telnyx responds with a `407 Proxy Authentication Required` and an encryption key.
3. LiveKit sends a second INVITE with the username and encrypted password.
4. Telnyx validates the username and decrypted password to authenticate the request.

To make this work reliably, LiveKit must include the username in the first INVITE message as a custom SIP header.

By default, LiveKit _doesn't_ include the username in the initial INVITE. When this happens, Telnyx normally returns a `407 Proxy Authentication Required` response. However, if Telnyx finds any existing SIP IP connection from the same source IP, it uses that connection as the authenticated user and skips the `407`. Because this lookup is based only on the source IP, the matched connection could belong to a different customer.

Configuring LiveKit to send the username in the first INVITE ensures Telnyx always replies with a `407` challenge to initiate SIP digest authentication.

To include a custom SIP header in INVITE messages, use the `headers_to_attributes` field for your outbound trunk. Add the key `X-Telnyx-Username` to the mapping with your username as the value:

```json
{
  "trunk": {
    "name": "My outbound trunk",
    "address": "sip.telnyx.com",
    "numbers": ["+15555555555"],
    "authUsername": "<username>",
    "authPassword": "<password>",

    "headers_to_attributes": {
      "X-Telnyx-Username": "<username>"
    }
  }
}

```

## Creating a SIP trunk using the Telnyx UI

Optionally, you can also create the Telnyx SIP trunk using the Telnyx Portal UI:

1. Sign in to the [Telnyx portal](https://portal.telnyx.com/).
2. [Purchase a phone number](https://portal.telnyx.com/#/numbers/buy-numbers).
3. Navigate to **Real-time Communications** » **Voice** » [**SIP Trunking**](https://portal.telnyx.com/#/voice/connections).
4. Select **Create SIP connection**:

- Enter a descriptive name for your SIP trunk.
- Select **FQDN** → select **Next**.
- Select **+ Add FQDN** and enter your [LiveKit SIP endpoint](https://docs.livekit.io/telephony/start/sip-trunk-setup.md#sip-endpoint) into the **FQDN** field and save.

For example, `vjnxecm0tjk.sip.livekit.cloud`.

> ℹ️ **Region-based endpoints**
> 
> To restrict calls to a specific region, replace your global LiveKit SIP endpoint with a [region-based endpoint](https://docs.livekit.io/telephony/features/region-pinning.md).
- In the **Outbound calls authentication** section, complete the **Username** and **Password** fields.
- Select **Next**.
- Select **Next** on the following page to skip the **Configuration** section.
- On the **Inbound settings** page, complete the following settings:

- For **Destination number format**, select `+E.164`.
- For **Origination number format**, select `+E.164`.
- For **SIP transport protocol**, select either **TCP** or **UDP**. **TCP** is recommended.
- For **SIP region**, select your region.
- Select **Next**.
- On the **Outbound settings** page, select a profile for the **Outbound voice profile** field.

If you don't have a profile, create one by navigating to **Real-Time Communications** » **Voice** » [**Settings**](https://portal.telnyx.com/#/outbound-profiles) and select **Create Profile**.
- Select **Next**.
- Select a phone number to associate with the SIP trunk by selecting the link icon.
- Select **Complete**.

## Configure HD voice

Telnyx supports [HD voice](https://docs.livekit.io/telephony/features/hd-voice.md) for customers in the US. To enable HD voice, configure the following settings in the Telnyx portal:

### Enable HD voice for a phone number

You must enable HD voice for the phone number before you can use it with HD voice:

1. Sign in to the [Telnyx portal](https://portal.telnyx.com/).
2. Navigate to **Real-Time Communications** » **Numbers** » [**Manage Numbers**](https://portal.telnyx.com/#/numbers/my-numbers).
3. Select the edit icon for the phone number you want to use.
4. Select the **Voice** tab and navigate to the **Services** section. Select **Enable HD Voice**.
5. Save your changes.

### Enable codecs for the SIP trunk

You must enable the _G.722_ codec for the SIP trunk associated with the phone number from the previous step:

1. Navigate to **Real-Time Communications** » **Voice** » [**SIP Trunking**](https://portal.telnyx.com/#/voice/connections).
2. Select the edit icon for the SIP trunk associated with the phone number.
3. Select the **Inbound** tab.
4. In the **Codecs** list, select **G.722**. Leave **G.711U** selected for compatibility.
5. Save your changes.

> ℹ️ **AMR-WB support**
> 
> In addition to G.722, LiveKit SIP also supports the AMR-WB codec for HD voice. To use it, select **AMR-WB** in the Telnyx **Codecs** list and enable it on the LiveKit side by adding it to the trunk's media configuration. AMR-WB must be enabled on both sides to take effect. To learn more, see [Configuring codecs](https://docs.livekit.io/reference/telephony/codecs-negotiation.md#configuring-codecs).

## Configure inbound fallbacks

> ℹ️ **When to configure fallbacks**
> 
> LiveKit Cloud already fails over between regions automatically. Provider-side fallbacks are an advanced option. To learn when to use them, see [Inbound call fallbacks](https://docs.livekit.io/telephony/features/region-pinning.md#inbound-fallbacks).

To add redundancy, associate more than one FQDN with your connection and let Telnyx fail over between them. Add a [region-based endpoint](https://docs.livekit.io/telephony/features/region-pinning.md#region-based-endpoint) as a fallback FQDN behind your global endpoint, then configure the connection to try them in order.

1. Add a region-based endpoint as a second FQDN on your connection. Copy the new FQDN `id` from the output. You also need the `id` of the global FQDN you [created in Step 2](#step-2-create-an-fqdn-connection):

```shell
curl -L 'https://api.telnyx.com/v2/fqdns' \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-H "Authorization: Bearer $TELNYX_API_KEY" \
-d '{
  "connection_id": "<connection_id>",
  "fqdn": "%{regionalEndpointSubdomain}%.us.sip.livekit.cloud",
  "port": 5060,
  "dns_record_type": "a"
}'

```
2. Configure the connection to try FQDNs in order, using your global endpoint as the primary and the region endpoint as the secondary:

```shell
curl -L -X PATCH 'https://api.telnyx.com/v2/fqdn_connections/<connection_id>' \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-H "Authorization: Bearer $TELNYX_API_KEY" \
-d '{
  "inbound": {
    "default_routing_method": "sequential",
    "default_primary_fqdn_id": "<global_fqdn_id>",
    "default_secondary_fqdn_id": "<region_fqdn_id>"
  }
}'

```

## Next steps

Head back to the main setup documentation to finish connecting your SIP trunk to LiveKit.

- **[SIP trunk setup](https://docs.livekit.io/telephony/start/sip-trunk-setup.md#livekit-setup)**: Configure your Telnyx trunk in LiveKit.

---

This document was rendered at 2026-08-24T21:31:35.350Z.
For the latest version of this document, see [https://docs.livekit.io/telephony/start/providers/telnyx.md](https://docs.livekit.io/telephony/start/providers/telnyx.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).
