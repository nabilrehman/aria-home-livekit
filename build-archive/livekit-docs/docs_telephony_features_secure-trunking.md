warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /telephony/features/secure-trunking

LiveKit docs › Telephony › Features › Secure trunking

---

# Secure trunking

> How to enable secure trunking for LiveKit SIP.

LiveKit SIP supports secure trunking using Transport Layer Security (TLS) to encrypt signaling traffic, and Secure Real-time Transport (SRTP) to encrypt media traffic. Encryption ensures that an Internet Service Provider (ISP) or an eavesdropping attacker (man-in-the-middle) cannot listen in on the conversation.

## Configure secure trunking for SIP calls

Setting up secure trunking requires multiple steps and includes enabling SRTP and TLS on your SIP trunking provider side, and enabling media encryption on your LiveKit trunks or on a per-call basis. The following sections provide instructions for enabling secure trunking with Twilio, Telnyx, and Plivo and setting up your LiveKit SIP trunks.

To secure calls you must complete all of the following steps:

1. Enable secure trunking with your SIP trunking provider.
2. Update your SIP URIs to use TLS for transport.
3. Enable media encryption for your LiveKit SIP trunks.

## Prerequisites

The following instructions assume you have already configured trunking with your SIP provider. If you haven't, see the [SIP trunk setup](https://docs.livekit.io/telephony/start/sip-trunk-setup.md) quickstart or select your provider-specific instructions from the navigation menu.

## Step 1: Enable secure trunking with your SIP trunking provider

Depending on your SIP trunking provider, you might need to explicitly enable secure trunking.

### Enable secure trunking with Twilio, Telnyx, and Plivo

**Twilio**:

1. Sign in to the [Twilio Console](https://console.twilio.com/).
2. Select **Develop** tab → **Elastic SIP Trunking** → **Manage** → **Trunks**.
3. Select the trunk you want to edit.
4. On the **General Settings** page, under **Features**, enable **Secure Trunking**.
5. Save your changes.

---

**Telnyx**:

1. Sign in to the [Telnyx Portal](https://portal.telnyx.com/).
2. Select **Real-Time Communications** → **Voice** → **SIP Trunking**.
3. Select the trunk you want to edit.
4. Select the **Inbound** tab.
5. For **SIP transport protocol**, select **TLS**.
6. For **Encrypted media**, select **SRTP**.
7. Save your changes.

---

**Plivo**:

1. Sign in to the [Plivo Console](https://cx.plivo.com/).
2. Navigate to **SIP Trunking** → [**Outbound Trunks**](https://cx.plivo.com/zentrunk/outbound-trunks/).
3. Select the trunk you want to edit.
4. For secure trunking, select the switch next to **Secure Trunking**.
5. Save your changes.

### Enable secure trunking for other providers

If you're using a different provider, check with them to see if you need to enable secure trunking.

## Step 2: Update your SIP URIs to use TLS

Enable TLS to encrypt signaling traffic.

### Update the origination URI in Twilio, Telnyx, or Plivo

The following instructions apply to inbound calls for Twilio, Telnyx, or Plivo.

**Twilio**:

1. Sign in to the [Twilio Console](https://console.twilio.com/).
2. Select the **Develop** tab → **Elastic SIP Trunking** → **Manage** → **Trunks**.
3. Select the trunk you want to edit → **Origination**.
4. Update the **Origination URI** to include `;transport=tls`.
5. Save your changes.

---

**Telnyx**:

1. Sign in to the [Telnyx Portal](https://portal.telnyx.com/).
2. Select **Real-Time Communications** → **Voice** → **SIP Trunking**.
3. Select the edit icon for your trunk → **Inbound settings**.
4. Select **Authentication and routing**.
5. In the **FQDN** section, select **Add FQDN**.
6. Add your SIP domain and port `5061` for TLS and save.
7. In the **Inbound calls routing** section, select the option you just added with port `5061`.
8. Save your changes.

---

**Plivo**:

1. Sign in to the [Plivo Console](https://cx.plivo.com/).
2. Navigate to **SIP Trunking** → [**Inbound Trunks**](https://cx.plivo.com/sip-trunking/inbound).
3. Select your inbound (origination) trunk.
4. Update the origination URI to use `;transport=tls` instead of `;transport=tcp`.
5. Save your changes.

### Update the origination URI for other providers

For other providers, set the origination URI to your SIP URI with `;transport=tls` appended to it. For example, if your SIP URI is:

`sip:bwwn08a2m4o.sip.livekit.cloud`

Set the origination URI to:

`sip:bwwn08a2m4o.sip.livekit.cloud;transport=tls`.

You can find your SIP URI on your LiveKit Cloud [project settings](https://cloud.livekit.io/projects/p_/settings) page.

If your provider doesn't support a SIP URI with URI parameters, you must enable TLS another way:

- Enable TLS in the trunk settings (required).
- If supported, set the port to `5061`, the default port for SIP over TLS.

> ℹ️ **TLS must be enabled**
> 
> Changing only the port number without enabling TLS is not enough. Some providers might treat port `5061` as a non-standard port for insecure UDP or TCP traffic.

Check your provider's documentation for exact steps.

## Step 3: Enable media encryption for your SIP trunks

Set the `media_encryption` parameter for your inbound or outbound trunks to either allow or require encryption. Valid values are as follows:

- `SIP_MEDIA_ENCRYPT_ALLOW`: Use media encryption if available.
- `SIP_MEDIA_ENCRYPT_REQUIRE`: Require media encryption.

By default, media encryption is turned off. To see all options, see the [API reference](https://docs.livekit.io/reference/telephony/sip-api.md#sipmediaencryption).

### Create an inbound trunk

Create an inbound trunk with media encryption enabled. To edit a trunk instead, see [Edit an existing trunk](#edit-trunk).

1. Sign in to your [Telephony → SIP trunks](https://cloud.livekit.io/projects/p_/telephony/trunks) dashboard.
2. Select **Create new trunk**.
3. Select the **JSON editor** tab and copy and paste the following contents. Replace the phone number with the one purchased from your SIP trunking provider.

```json
{
    "name": "My trunk",
    "numbers": [
      "+15105550100"
    ],
    "mediaEncryption": "SIP_MEDIA_ENCRYPT_ALLOW"
}

```
4. Select **Create**.

### Create an outbound trunk

For outbound calls, you can create a stored outbound trunk with media encryption enabled and [transport](https://docs.livekit.io/reference/telephony/sip-api.md#siptransport) protocol set to `SIP_TRANSPORT_TLS`. All calls made using this trunk use TLS and SRTP. You can also pass trunk configuration [inline](https://docs.livekit.io/telephony/making-calls/outbound-calls.md#inline-trunk) with each call or enable media encryption on a [call-by-call basis](#per-call-encryption).

Use the following instructions to create a new wildcard outbound trunk with SRTP and TLS enabled. The wildcard allows all calls to be routed to the same trunk. To edit a trunk instead, see [Edit an existing trunk](#edit-trunk).

1. Sign in to your [Telephony → SIP trunks](https://cloud.livekit.io/projects/p_/telephony/trunks) dashboard.
2. Select **Create new trunk**.
3. Select the **JSON editor** → select **Outbound** for **Trunk direction**.
4. Copy and paste the following contents. Replace the SIP trunking provider endpoint, and username and password for authentication.

```json
{
"name": "My outbound trunk",
"address": "<sip-trunking-provider-endpoint>",
"transport": "SIP_TRANSPORT_TLS",
"numbers": [
   "*"
],
"authUsername": "<username>",
"authPassword": "<password>",
"mediaEncryption": "SIP_MEDIA_ENCRYPT_ALLOW"
}

```
5. Select **Create**.

### Edit an existing trunk

Edit an existing inbound or outbound trunk to enable media encryption using the LiveKit Cloud dashboard.

- Sign in to your [Telephony → SIP trunks](https://cloud.livekit.io/projects/p_/telephony/trunks) dashboard.
- Navigate to the **Inbound** or **Outbound** section on the page.
- Select the more menu (**⋮**) next to the trunk you want to edit → **Configure trunk**.
- For _outbound_ trunks, for **Transport** select **TLS**.
- Expand the **Optional settings** section. Select either **Media encryption enabled** or **Media encryption required**.
- Select **Update**.

### Enable media encryption per call

You can enable media encryption on a per-call basis by setting the `media_encryption` parameter in the `CreateSIPParticipant` request. Valid values are as follows:

- `SIP_MEDIA_ENCRYPT_ALLOW`: Use media encryption if available.
- `SIP_MEDIA_ENCRYPT_REQUIRE`: Require media encryption.

> ℹ️ **SRTP must be enabled**
> 
> You must also enable SRTP on the SIP trunking provider side. If you haven't already enabled this, see [Step 1: Enable secure trunking with your SIP trunking provider](#enable-secure-trunking).

1. Create a `sip-participant.json` file with the following participant details:

```json
{
  "trunk": {
    "hostname": "<SIP server>",
    "auth_username": "<username>",
    "auth_password": "<password>",
    "transport": "SIP_TRANSPORT_TLS"
  },
  "sip_number": "<SIP provider number>",
  "sip_call_to": "<phone-number-to-dial>",
  "room_name": "my-sip-room",
  "participant_identity": "sip-test",
  "participant_name": "Test Caller",
  "wait_until_answered": true,
  "media_encryption": "SIP_MEDIA_ENCRYPT_ALLOW"
}

```

> ℹ️ **Stored outbound trunk**
> 
> You can also use a stored outbound trunk by passing `sip_trunk_id` instead of `trunk`. For details, see [Outbound trunk](https://docs.livekit.io/telephony/making-calls/outbound-trunk.md).
2. Create the SIP participant using the CLI. After you run this command, a call is made to the `<phone-number-to-dial>` number.

```shell
lk sip participant create sip-participant.json

```

## Supported cipher suites

A _cipher suite_ is a set of cryptographic algorithms used to secure network connections. Each cipher suite defines how data is encrypted, how message integrity is verified, and how keys are exchanged between parties. When establishing a secure connection, both sides negotiate which cipher suite to use based on mutual support and security preferences.

The following sections describe the TLS and SRTP cipher suites supported by LiveKit.

### Supported TLS cipher suites

All secure suites listed in [Go's crypto/tls package](https://go.dev/src/crypto/tls/cipher_suites.go).

### Supported SRTP cipher suites

The following SRTP cipher suites are supported:

- AES_CM_128_HMAC_SHA1_80
- AES_CM_128_HMAC_SHA1_32
- AES_256_CM_HMAC_SHA1_80
- AES_256_CM_HMAC_SHA1_32

---

This document was rendered at 2026-08-24T21:31:24.529Z.
For the latest version of this document, see [https://docs.livekit.io/telephony/features/secure-trunking.md](https://docs.livekit.io/telephony/features/secure-trunking.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).
