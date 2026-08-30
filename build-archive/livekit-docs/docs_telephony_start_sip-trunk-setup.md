warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /telephony/start/sip-trunk-setup

LiveKit docs › Telephony › Get Started › SIP trunk setup

---

# SIP trunk setup

> Guide to integrating SIP trunks with LiveKit telephony.

## Overview

LiveKit's telephony features support integration with third-party SIP trunking providers (for example, Telnyx, Twilio, Plivo). When linked, these trunks allow you to route calls between traditional phone networks and LiveKit rooms for processing, recording, or interaction with agents and voice AI apps.

This guide walks you through configuring a SIP trunk and associating it with your LiveKit Cloud project to enable inbound and outbound calls.

## External provider setup

The usual steps to create a SIP trunk are as follows:

1. Create a SIP trunk with your provider.
2. Add authentication or limit trunk usage by phone numbers or IP addresses.
3. Purchase a phone number and associate it with your SIP trunk.
4. Add your [LiveKit SIP endpoint](#sip-endpoint) to the SIP trunk.

### SIP endpoint

Depending on your SIP trunking provider, you might need to use a _SIP endpoint_ to configure inbound calls instead of your SIP URI. The SIP endpoint is your LiveKit SIP URI without the `sip:` prefix. You can find your SIP URI on the [**Project settings**](https://cloud.livekit.io/projects/p_/settings/project) page or generate it from the CLI.

For example, if your SIP URI is `sip:vjnxecm0tjk.sip.livekit.cloud`, your SIP endpoint is `vjnxecm0tjk.sip.livekit.cloud`.

#### Find your SIP URI using the CLI

Your SIP URI is based on your project ID. To find it, list your projects with the LiveKit CLI:

```shell
lk project list --json

```

The output includes a `ProjectId` field for each project (for example, `p_vjnxecm0tjk`). Remove the `p_` prefix to get your SIP subdomain, then construct the SIP URI:

```
sip:{subdomain}.sip.livekit.cloud

```

For example, a project with ID `p_vjnxecm0tjk` has the SIP URI `sip:vjnxecm0tjk.sip.livekit.cloud`.

> ℹ️ **Region-based endpoints**
> 
> To restrict calls to a specific region, replace your global LiveKit SIP endpoint with a [region-based endpoint](https://docs.livekit.io/telephony/features/region-pinning.md).

## Provider-specific instructions

For step-by-step instructions for Telnyx, Twilio, Plivo, or Wavix, see the following quickstarts:

- **[Twilio Setup](https://docs.livekit.io/sip/quickstarts/configuring-twilio-trunk.md)**: Step-by-step instructions for setting up a SIP trunk with Twilio.

- **[Telnyx Setup](https://docs.livekit.io/sip/quickstarts/configuring-telnyx-trunk.md)**: Step-by-step instructions for setting up a SIP trunk with Telnyx.

- **[Plivo Setup](https://docs.livekit.io/sip/quickstarts/configuring-plivo-trunk.md)**: Step-by-step instructions for setting up a SIP trunk with Plivo.

- **[Wavix Setup](https://docs.livekit.io/sip/quickstarts/configuring-wavix-trunk.md)**: Step-by-step instructions for setting up a SIP trunk with Wavix.

## LiveKit setup

Now you are ready to configure your LiveKit Cloud project to use the SIP trunk.

The following steps are common to all SIP trunking providers.

> ℹ️ **LiveKit CLI**
> 
> These examples use the [LiveKit Cloud](https://cloud.livekit.io/). For additional examples and full documentation, see the linked documentation for each component.

### Inbound trunk setup

An [inbound trunk](https://docs.livekit.io/telephony/accepting-calls/inbound-trunk.md) allows you to accept incoming phone calls.

Create an inbound trunk using the LiveKit Cloud dashboard.

1. Sign in to the **Telephony** → [**SIP trunks**](https://cloud.livekit.io/projects/p_/telephony/trunks) page.
2. Select **Create new trunk**.
3. Select the **JSON editor** tab.
4. Select **Inbound** for **Trunk direction**.
5. Copy and paste the following text into the editor, replacing the phone number with the number you purchased from your SIP trunk provider:

```json
{
  "name": "My inbound trunk",
  "numbers": ["+15105550123"]
}

```
6. Select **Create**.

### Create a dispatch rule

You must set up at least one [dispatch rule](https://docs.livekit.io/telephony/accepting-calls/dispatch-rule.md) to accept incoming calls into a LiveKit room.

This example creates a dispatch rule that puts each caller into a randomly generated unique room using the name prefix `call-`. For many applications, this is the only configuration you need.

1. Sign in to the **Telephony** → [**Dispatch rules**](https://cloud.livekit.io/projects/p_/telephony/dispatch) page.
2. Select **Create new dispatch rule**.
3. Select the **JSON editor** tab.
4. Copy and paste the following text into the editor:

```json
{
   "name": "My dispatch rule",
   "rule": {
      "dispatchRuleIndividual": {
         "roomPrefix": "call-"
      }
   }
}

```
5. Select **Create**.

After you create an inbound trunk and dispatch rule, you can create an agent to answer incoming calls. To learn more, see the resources in the [Next steps](#next-steps) section.

### Create an outbound trunk

Create an [outbound trunk](https://docs.livekit.io/telephony/making-calls/outbound-trunk.md) to make outgoing phone calls with LiveKit.

This example creates a username and password authenticated outbound trunk with the phone number `+15105550123` and the trunk domain name `my-trunk-domain-name`.

1. Sign in to the **Telephony** → [**SIP trunks**](https://cloud.livekit.io/projects/p_/telephony/trunks) page.
2. Select **Create new trunk**.
3. Select the **JSON editor** tab.
4. Select **Outbound** for **Trunk direction**.
5. Copy and paste the following text into the editor:

```json
{
  "name": "My outbound trunk",
  "address": "<my-trunk-domain-name>",
  "numbers": [
    "+15105550123"
  ],
  "authUsername": "<username>",
  "authPassword": "<password>"
}

```
6. Select **Create**.

Now you are ready to [place outgoing calls](https://docs.livekit.io/telephony/making-calls/outbound-calls.md).

## Next steps

See the following guides to continue building your telephony app.

- **[Voice AI quickstart](https://docs.livekit.io/agents/start/voice-ai.md)**: Build an agent for your telephony-based voice AI app.

- **[Make outbound calls](https://docs.livekit.io/sip/outbound-calls.md)**: Detailed instructions for making outbound calls.

## Additional documentation

See the following documentation for more details on the topics covered in this guide.

- **[Inbound trunk](https://docs.livekit.io/sip/trunk-inbound.md)**: Detailed instructions for setting up inbound trunks.

- **[Dispatch rule](https://docs.livekit.io/telephony/accepting-calls/dispatch-rule.md)**: Detailed instructions for setting up dispatch rules.

- **[Outbound trunk](https://docs.livekit.io/sip/trunk-outbound.md)**: Detailed instructions for setting up outbound trunks.

- **[Testing your telephony setup](https://docs.livekit.io/telephony/testing.md)**: Validate the setup with a test call and verify the resulting room, SIP participant, and logs.

---

This document was rendered at 2026-08-24T21:31:16.135Z.
For the latest version of this document, see [https://docs.livekit.io/telephony/start/sip-trunk-setup.md](https://docs.livekit.io/telephony/start/sip-trunk-setup.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).
