warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /telephony/start/providers/twilio

LiveKit docs › Telephony › Get Started › Provider-specific quickstarts › Twilio

---

# Create and configure a Twilio SIP trunk

> Step-by-step instructions for creating inbound and outbound SIP trunks using Twilio.

## Creating a SIP trunk for inbound and outbound calls

Create a Twilio SIP trunk for incoming or outgoing calls, or both, using the following steps. To use the Twilio console, see [Configure a SIP trunk using the Twilio UI](#configure-a-sip-trunk-using-the-twilio-ui).

> ℹ️ **Note**
> 
> For inbound calls, you can use TwiML for Programmable Voice instead of setting up Elastic SIP Trunking. To learn more, see [Inbound calls with Twilio Voice](https://docs.livekit.io/telephony/accepting-calls/inbound-twilio.md).

### Prerequisites

- [Purchase phone number](https://help.twilio.com/articles/223135247-How-to-Search-for-and-Buy-a-Twilio-Phone-Number-from-Console).
- [Install the Twilio CLI](https://www.twilio.com/docs/twilio-cli/getting-started/install).
- Create a [Twilio profile](https://www.twilio.com/docs/twilio-cli/general-usage/profiles) to use the CLI.

### Step 1. Create a SIP trunk

The domain name for your SIP trunk must end in `pstn.twilio.com`. For example, to create a trunk named `My test trunk` with the domain name `my-test-trunk.pstn.twilio.com`, run the following command:

```shell
twilio api trunking v1 trunks create \
--friendly-name "My test trunk" \
--domain-name "my-test-trunk.pstn.twilio.com"

```

The output includes the trunk SID. Copy it for use in the following steps.

### Step 2: Configure your trunk

Configure the trunk for inbound calls or outbound calls or both. To create a SIP trunk for both inbound and outbound calls, follow the steps in both tabs:

**Inbound**:

For inbound trunks, configure an [origination URI](https://www.twilio.com/docs/sip-trunking#origination).

```shell
twilio api trunking v1 trunks origination-urls create \
--trunk-sid <twilio_trunk_sid> \
--friendly-name "LiveKit SIP URI" \
--sip-url "sip:%{sipHost}%;transport=tcp" \
--weight 1 --priority 1 --enabled

```

> ℹ️ **Region-based endpoints**
> 
> To restrict calls to a specific region, replace your global LiveKit SIP endpoint with a [region-based endpoint](https://docs.livekit.io/telephony/features/region-pinning.md).

---

**Outbound**:

For outbound trunks, configure username and password authentication using a credentials list. Complete the following steps using the Twilio console.

**Step 1: Create a credential list**

1. Sign in to the [Twilio console](https://console.twilio.com).
2. Select **Voice** » **Credential lists**.
3. Create a new credential list with the username and password of your choice.

**Step 2: Associate the credential list with your SIP trunk**

1. Select **Elastic SIP Trunking** » **Manage** » **Trunks** and select the outbound trunk created in the previous steps.
2. Select **Termination** » **Authentication** » **Credential Lists** and select the credential list you just created.
3. Select **Save**.

### Step 3: Associate phone number and trunk

The Twilio trunk SID and phone number SID are included in the output of previous steps. If you didn't copy the SIDs, you can list them using the following commands:

- To list phone numbers: `twilio phone-numbers list`
- To list trunks: `twilio api trunking v1 trunks list`

```shell
twilio api trunking v1 trunks phone-numbers create \
--trunk-sid <twilio_trunk_sid> \
--phone-number-sid <twilio_phone_number_sid>

```

## Configure a SIP trunk using the Twilio UI

1. Sign in to the [Twilio console](https://console.twilio.com/).
2. [Purchase a phone number](https://help.twilio.com/articles/223135247-How-to-Search-for-and-Buy-a-Twilio-Phone-Number-from-Console).
3. [Create SIP Trunk](https://www.twilio.com/docs/sip-trunking#create-a-trunk) on Twilio:

- Select **Products & Services** » **Elastic SIP Trunking** » **Trunks**.
- Select **Create new SIP trunk**, enter a name for your trunk, and select **Create**.
4. For inbound calls:

- Select the **Origination** tab.
- In the **Origination URIs** section, select **Add new Origination URI**.
- In the **Origination SIP URI** field, enter your LiveKit SIP URI with `;transport=tcp` appended. For example, `sip:vjnxecm0tjk.sip.livekit.cloud;transport=tcp`. You can find your SIP URI on the [**Project settings**](https://cloud.livekit.io/projects/p_/settings/project) page or [generate it from the CLI](https://docs.livekit.io/telephony/start/sip-trunk-setup.md#find-sip-uri).

> ℹ️ **Region-based endpoints**
> 
> To restrict calls to a specific region, replace your global LiveKit SIP endpoint with a [region-based endpoint](https://docs.livekit.io/telephony/features/region-pinning.md).
- Select **Add**.
5. For outbound calls, configure termination and authentication:

- Select the **Termination** tab.
- For the **Termination SIP URI** field, enter a unique domain name to identify your termination URI for the trunk.

Copy this [Termination SIP URI](https://www.twilio.com/docs/sip-trunking#termination-uri) to use when you create an [outbound trunk](https://docs.livekit.io/telephony/making-calls/outbound-trunk.md) for LiveKit.
- Configure [Authentication](https://www.twilio.com/docs/sip-trunking#authentication):

Select or create a **Credential List** with a username and password of your choice. The username and password must match the username and password you use for your LiveKit outbound trunk.
6. Select **Save**.

## Configure inbound fallbacks

> ℹ️ **When to configure fallbacks**
> 
> LiveKit Cloud already fails over between regions automatically. Provider-side fallbacks are an advanced option. To learn when to use them, see [Inbound call fallbacks](https://docs.livekit.io/telephony/features/region-pinning.md#inbound-fallbacks).

To add redundancy, configure more than one origination URI on your trunk and let Twilio fail over between them. Twilio tries the URI with the lowest `priority` value first, then fails over to a higher-value URI if the first doesn't respond. The `weight` value only distributes load across URIs that share the same `priority`, so use `priority` (not `weight`) to control fallback order. To learn more about these properties, see [OriginationUrl Resource](https://www.twilio.com/docs/sip-trunking/api/originationurl-resource).

The following example adds a [region-based endpoint](https://docs.livekit.io/telephony/features/region-pinning.md#region-based-endpoint) as a fallback behind the global endpoint created in [Step 2](#step-2-configure-your-trunk). The global endpoint uses `priority 1` and the region endpoint uses `priority 2`, so Twilio tries the global endpoint first and falls back to the US region if it doesn't respond:

```shell
twilio api trunking v1 trunks origination-urls create \
--trunk-sid <twilio_trunk_sid> \
--friendly-name "LiveKit US region fallback" \
--sip-url "sip:%{regionalEndpointSubdomain}%.us.sip.livekit.cloud;transport=tcp" \
--weight 1 --priority 2 --enabled

```

To add more fallbacks, create additional origination URIs with higher `priority` values.

## Next steps

Head back to the main setup documentation to finish connecting your SIP trunk to LiveKit.

- **[SIP trunk setup](https://docs.livekit.io/telephony/start/sip-trunk-setup.md#livekit-setup)**: Configure your Twilio trunk in LiveKit.

---

This document was rendered at 2026-08-24T21:31:34.764Z.
For the latest version of this document, see [https://docs.livekit.io/telephony/start/providers/twilio.md](https://docs.livekit.io/telephony/start/providers/twilio.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).
