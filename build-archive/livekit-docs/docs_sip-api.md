warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /reference/telephony/sip-api

LiveKit docs › Reference › Telephony › SIP API

---

# SIP APIs

> Use LiveKit's built-in SIP APIs to manage your SIP-based apps.

## Overview

LiveKit has built-in APIs that let you manage SIP trunks, dispatch rules, and SIP participants. These APIs are available with LiveKit server SDKs and CLI:

- [Go SIP client](https://pkg.go.dev/github.com/livekit/server-sdk-go/v2#SIPClient)
- [JS SIP client](https://docs.livekit.io/reference/server-sdk-js/classes/SipClient.html.md)
- [Ruby SIP client](https://github.com/livekit/server-sdk-ruby/blob/main/lib/livekit/sip_service_client.rb)
- [Python SIP client](https://docs.livekit.io/reference/python/livekit/api/sip_service.html.md)
- [Java SIP client](https://github.com/livekit/server-sdk-kotlin/blob/main/src/main/kotlin/io/livekit/server/SipServiceClient.kt)
- [CLI](https://github.com/livekit/livekit-cli/blob/main/cmd/lk/sip.go)

> ❗ **Important**
> 
> Requests to the SIP API require the SIP `admin` permission unless otherwise noted. To create a token with the appropriate grant, see [SIP grant](https://docs.livekit.io/frontends/authentication/tokens.md#sip-grant).

For phone number management APIs, see [Phone Number APIs](https://docs.livekit.io/reference/telephony/phone-numbers-api.md).

To learn more about additional APIs, see [Server APIs](https://docs.livekit.io/reference/server/server-apis.md).

### Using endpoints

The SIP API is accessible via `/twirp/livekit.SIP/<MethodName>`. For example, if you're using LiveKit Cloud the following URL is for the [CreateSIPInboundTrunk](#createsipinboundtrunk) API endpoint:

```shell
https://%{projectDomain}%/twirp/livekit.SIP/CreateSIPInboundTrunk

```

#### Authorization header

All endpoints require a signed access token. This token should be set via HTTP header:

```
Authorization: Bearer <token>

```

LiveKit server SDKs automatically include the above header.

#### Post body

Twirp expects an HTTP POST request. The body of the request must be a JSON object (`application/json`) containing parameters specific to that request. Use an empty `{}` body for requests that don't require parameters.

#### Examples

For example, create an inbound trunk using [CreateSIPInboundTrunk](#createsipinboundtrunk):

```shell
curl -X POST https://%{projectDomain}%/twirp/livekit.SIP/CreateSIPInboundTrunk \
	-H "Authorization: Bearer <token-with-sip-admin>" \
	-H 'Content-Type: application/json' \
	-d '{ "name": "My trunk", "numbers": ["+15105550100"] }'

```

Use the [ListSIPInboundTrunk](#listsipinboundtrunk) API endpoint to list inbound trunks:

```shell
curl -X POST https://%{projectDomain}%/twirp/livekit.SIP/ListSIPInboundTrunk \
	-H "Authorization: Bearer <token-with-sip-admin>" \
	-H 'Content-Type: application/json' \
	-d '{}'

```

## SIPService APIs

The SIPService APIs allow you to manage trunks, dispatch rules, and SIP participants.

> 💡 **Tip**
> 
> All RPC definitions and options can be found [here](https://github.com/livekit/protocol/blob/main/protobufs/livekit_sip.proto).

### CreateSIPInboundTrunk

Create an inbound trunk with the specified settings.

Returns [SIPInboundTrunkInfo](#sipinboundtrunkinfo).

| Parameter | Type | Required | Description |
| name | string | yes | Name of the trunk. |
| metadata | string |  | Initial metadata to assign to the trunk. This metadata is added to every SIP participant that uses the trunk. |
| numbers | array<string> | yes | Array of provider phone numbers associated with the trunk. |
| allowed_addresses | array<string> |  | List of IP addresses that are allowed to use the trunk. Each item in the list can be an individual IP address or a Classless Inter-Domain Routing notation representing a CIDR block. This field must be enabled for your project before you can use it. Contact LiveKit support to request access. |
| allowed_numbers | array<string> |  | List of phone numbers that are allowed to use the trunk. If this [list is empty](https://docs.livekit.io/telephony/accepting-calls/inbound-trunk.md#accepting-calls-to-any-phone-number), trunk access must be limited by using one of the following options:

- Set `auth_username` and `auth_password` _or_
- Set `allowed_addresses` |
| auth_username | string |  | If configured, the username for authorized use of the provider's SIP trunk. |
| auth_password | string |  | If configured, the password for authorized use of the provider's SIP trunk. |
| headers | map<string, string> |  | SIP X-* headers for INVITE request. These headers are sent as-is and may help identify this call as coming from LiveKit for the other SIP endpoint. |
| headers_to_attributes | map<string, string> |  | Key-value mapping of SIP X-* header names to participant attribute names. |
| attributes_to_headers | map<string, string> |  | Map SIP headers from INVITE request to `sip.h.*` participant attributes. If the names of the required headers is known, use `headers_to_attributes` instead. |
| include_headers | [SIPHeaderOptions](#sipheaderoptions) |  | Specify how SIP headers should be mapped to attributes. |
| ringing_timeout | [google.protobuf.Duration](https://github.com/protocolbuffers/protobuf/blob/main/src/google/protobuf/duration.proto) |  | Maximum time for the call to ring. |
| max_call_duration | google.protobuf.Duration |  | Maximum call duration. |
| krisp_enabled | bool |  | True to enable [Krisp noise cancellation](https://docs.livekit.io/transport/media/noise-cancellation.md#telephony) for the caller. |
| media | [SIPMediaConfig](#sipmediaconfig) |  | Media configuration for calls on this trunk, including codecs, encryption, and media timeout. |
| media_encryption | [SIPMediaEncryption](#sipmediaencryption) |  | Deprecated. Use the `encryption` field in [`media`](#sipmediaconfig) instead. Whether or not to encrypt media. |

### CreateSIPOutboundTrunk

Create an outbound trunk with the specified settings.

Returns [SIPOutboundTrunkInfo](#sipoutboundtrunkinfo).

| Parameter | Type | Required | Description |
| name | string | yes | Name of the trunk. |
| metadata | string |  | User-defined metadata for the trunk. This metadata is added to every SIP participant that uses the trunk. |
| address | string | yes | Hostname or IP the SIP INVITE is sent to. This is _not_ a SIP URI and shouldn't contain the `sip:` protocol. |
| destination_country | string | yes | Two-letter [country code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) for the country the call terminates in. LiveKit uses the country code to route calls. To learn more, see [Outbound calls](https://docs.livekit.io/telephony/features/region-pinning.md#outbound-calls). |
| numbers | array<string> | yes | List of provider phone numbers associated with the trunk that can be used as a caller id. |
| transport | [SIPTransport](#siptransport) |  | Protocol to use for SIP transport: auto, TCP, or UDP. |
| auth_username | string |  | If configured, the username for authorized use of the provider's SIP trunk. |
| auth_password | string |  | If configured, the password for authorized use of the provider's SIP trunk. |
| headers | map<string, string> |  | SIP X-* headers for INVITE request. These headers are sent as-is and may help identify this call as coming from LiveKit for the other SIP endpoint. |
| headers_to_attributes | map<string, string> |  | Key-value mapping of SIP X-* header names to participant attribute names. |
| media | [SIPMediaConfig](#sipmediaconfig) |  | Media configuration for calls on this trunk, including codecs, encryption, and media timeout. |
| media_encryption | [SIPMediaEncryption](#sipmediaencryption) |  | Deprecated. Use the `encryption` field in [`media`](#sipmediaconfig) instead. Whether or not to encrypt media. |

### CreateSIPDispatchRule

Create dispatch rule.

Returns [SIPDispatchRuleInfo](#sipdispatchruleinfo).

| Parameter | Type | Required | Description |
| dispatch_rule | [SIPDispatchRuleInfo](#sipdispatchruleinfo) | yes | Dispatch rule to create. |
| trunk_ids | array<string> |  | List of associated trunk IDs. If empty, all trunks match this dispatch rule. |
| hide_phone_number | bool |  | If true, use a random value for participant identity and phone number omitted from attributes. By default, the participant identity is created using the phone number (if the participant identity isn't explicitly set). |
| inbound_numbers | array<string> |  | If this list is populated, the dispatch rule only accepts calls made _from_ numbers in the list. If a caller's phone number is not in the list, the call is rejected. |
| name | string | yes | Human-readable name for the dispatch rule. |
| metadata | string |  | Optional metadata for the dispatch rule. If defined, participants created by the rule inherit this metadata. |
| attributes | map<string, string> |  | Key-value mapping of user-defined attributes. Participants created by this rule inherit these attributes. |
| room_preset | string |  | Only for LiveKit Cloud: Config preset to use. |
| room_config | [RoomConfiguration](https://docs.livekit.io/reference/server/server-apis.md#roomconfiguration) |  | Room configuration to use if the participant initiates the room. |

### CreateSIPParticipant

> ℹ️ **Note**
> 
> Requires SIP `call` grant on authorization token.

Create a SIP participant to make outgoing calls.

Returns [SIPParticipantInfo](#sipparticipantinfo)

| Parameter | Type | Required | Description |
| sip_trunk_id | string |  | ID for SIP trunk used to dial user. Required if `trunk` is not set. |
| trunk | [SIPOutboundConfig](#sipoutboundconfig) |  | Inline outbound trunk configuration. Required if `sip_trunk_id` is not set. When using this parameter, `sip_number` must also be set. |
| sip_call_to | string | yes | Phone number to call. |
| sip_number | string |  | SIP number to call from. Required if using an [inline trunk configuration](https://docs.livekit.io/telephony/making-calls/outbound-calls.md#inline-trunk). If `sip_trunk_id` is set, this defaults to the number associated with the stored trunk. |
| room_name | string | yes | Name of the room to connect the participant to. |
| participant_identity | string |  | Identity of the participant. |
| participant_name | string |  | Name of the participant. |
| participant_metadata | string |  | User-defined metadata that is attached to created participant. |
| participant_attributes | map<string, string> |  | Key-value mapping of user-defined attributes to attach to created participant. |
| dtmf | string |  | DTMF digits (extension codes) to use when making the call. Use character `w` to add a 0.5 second delay. |
| play_dialtone | bool |  | Optionally play dial tone in the room as an audible indicator for existing participants. |
| hide_phone_number | bool |  | If true, use a random value for participant identity and phone number omitted from attributes. By default, the participant identity is created using the phone number (if the participant identity isn't explicitly set). |
| headers | map<string, string> |  | SIP X-* headers for INVITE request. These headers are sent as-is and may help identify this call as coming from LiveKit. |
| include_headers | [SIPHeaderOptions](#sipheaderoptions) |  | Specify how SIP headers should be mapped to attributes. |
| ringing_timeout | google.protobuf.Duration |  | Maximum time for the callee to answer the call. The upper limit is 80 seconds. |
| max_call_duration | google.protobuf.Duration |  | Maximum call duration. |
| krisp_enabled | bool |  | True to enable [Krisp noise cancellation](https://docs.livekit.io/transport/media/noise-cancellation.md#telephony) for the callee. |
| media | [SIPMediaConfig](#sipmediaconfig) |  | Media configuration for the call, including codecs, encryption, and media timeout. |
| media_encryption | [SIPMediaEncryption](#sipmediaencryption) |  | Deprecated. Use the `encryption` field in [`media`](#sipmediaconfig) instead. Whether or not to encrypt media. |
| wait_until_answered | bool |  | If true, return after the call is answered — including if it goes to voicemail. |
| display_name | string |  | Optional display name for the caller's number. If empty, results in a CNAM lookup by destination carrier. If omitted, defaults to caller's number. For more information, see [Custom caller ID](https://docs.livekit.io/telephony/making-calls/outbound-calls.md#custom-caller-id). |

### DeleteSIPDispatchRule

Delete a dispatch rule.

Returns [SIPDispatchRuleInfo](#sipdispatchruleinfo).

| Parameter | Type | Required | Description |
| sip_dispatch_rule_id | string |  | ID of dispatch rule. |

### DeleteSIPTrunk

Delete a trunk.

Returns [SIPTrunkInfo](#siptrunkinfo).

| Parameter | Type | Required | Description |
| sip_trunk_id | string | yes | ID of trunk. |

### GetSIPInboundTrunk

Get inbound trunk.

Returns [GetSIPInboundTrunkResponse](#getsipinboundtrunkresponse).

| Parameter | Type | Required | Description |
| sip_trunk_id | string | yes | ID of trunk. |

### GetSIPOutboundTrunk

Get outbound trunk.

Returns [GetSIPOutboundTrunkResponse](#getsipoutboundtrunkresponse).

| Parameter | Type | Required | Description |
| sip_trunk_id | string | yes | ID of trunk. |

### ListSIPDispatchRule

List dispatch rules.

Returns array<[SIPDispatchRuleInfo](#sipdispatchruleinfo)>.

| Parameter | Type | Required | Description |
| page | [Pagination](#pagination) |  | Pagination options. |
| dispatch_rule_ids | array<string> |  | Dispatch rule IDs to list. If set, the response contains rules in the same order. If any rule is missing, the response includes a nil item in its position. |
| trunk_ids | array<string> |  | Only list rules that contain one of these trunk IDs, including wildcard rules. |

### ListSIPInboundTrunk

List inbound trunks.

Returns array<[SIPInboundTrunkInfo](#sipinboundtrunkinfo)>.

| Parameter | Type | Required | Description |
| page | [Pagination](#pagination) |  | Pagination options. |
| trunk_ids | array<string> |  | Trunk IDs to list. If set, the response contains trunks in the same order. If any trunk is missing, the response includes a nil item in its position. |
| numbers | array<string> |  | Only list trunks that contain one of these numbers, including wildcard trunks. |

### ListSIPOutboundTrunk

List outbound trunks.

Returns array<[SIPOutboundTrunkInfo](#sipoutboundtrunkinfo)>.

| Parameter | Type | Required | Description |
| page | [Pagination](#pagination) |  | Pagination options. |
| trunk_ids | array<string> |  | Trunk IDs to list. If set, the response contains trunks in the same order. If any trunk is missing, the response includes a nil item in its position. |
| numbers | array<string> |  | Only list trunks that contain one of these numbers, including wildcard trunks. |

### TransferSIPParticipant

> ℹ️ **Note**
> 
> Requires SIP `call` grant on authorization token.

Transfer call to another number or SIP endpoint.

Returns [google.protobuf.Empty](https://github.com/protocolbuffers/protobuf/blob/main/src/google/protobuf/empty.proto).

| Parameter | Type | Required | Description |
| participant_identity | string | yes | Identity of the participant to transfer. |
| room_name | string | yes | Name of the room the participant is currently in. |
| transfer_to | string | yes | Phone number or SIP endpoint to transfer participant to. This value can either be a valid telephone number or a SIP URI. The following examples are valid values:

- `tel:+15105550100`
- `sip:+15105550100@sip.telnyx.com`
- `sip:+15105550100@my-livekit-demo.pstn.twilio.com` |
| play_dialtone | bool |  | Optionally play dial tone during the transfer. By default, the room audio is played during the transfer. |
| ringing_timeout | [google.protobuf.Duration](https://github.com/protocolbuffers/protobuf/blob/main/src/google/protobuf/duration.proto) |  | Maximum time to wait for the transfer destination to answer. If the timeout expires before the destination answers, the request returns an error and the caller stays in the room. To learn more, see [Control transfer timeout](https://docs.livekit.io/telephony/features/transfers/cold.md#ringing_timeout). |

### UpdateSIPDispatchRule

Update a dispatch rule.

Returns [SIPDispatchRuleInfo](#sipdispatchruleinfo).

| Parameter | Type | Required | Description |
| req | [UpdateSIPDispatchRuleRequest](#updatesipdispatchrulerequest) | yes | Update or replace request. |

### UpdateSIPInboundTrunk

Update an inbound trunk.

Returns [SIPInboundTrunkInfo](#sipinboundtrunkinfo).

| Parameter | Type | Required | Description |
| req | [UpdateSIPInboundTrunkRequest](#updatesipinboundtrunkrequest) | yes | Update or replace request. |

### UpdateSIPOutboundTrunk

Update an outbound trunk.

Returns [SIPOutboundTrunkInfo](#sipoutboundtrunkinfo).

| Parameter | Type | Required | Description |
| req | [UpdateSIPOutboundTrunkRequest](#updatesipoutboundtrunkrequest) | yes | Update or replace request. |

## Types

The SIP service includes the following types.

### GetSIPInboundTrunkResponse

| Field | Type | Description |
| trunk | [SIPInboundTrunkInfo](#sipinboundtrunkinfo) | Inbound trunk. |

### GetSIPOutboundTrunkResponse

| Field | Type | Description |
| trunk | [SIPOutboundTrunkInfo](#sipoutboundtrunkinfo) | Outbound trunk. |

### ListUpdate

| Field | Type | Description |
| add | array<string> | Optional set of items to add. |
| set | array<string> | Optional set of items to set. If this field is present, it replaces the existing list. |
| remove | array<string> | Optional set of items to remove. |

### Pagination

| Field | Type | Description |
| after_id | string | List entities with IDs greater than this value. |
| limit | int32 | Maximum number of entities to return. |

### SIPCodec

A single audio codec entry for [SIPMediaConfig](#sipmediaconfig). To learn more, see [Configuring codecs](https://docs.livekit.io/reference/telephony/codecs-negotiation.md#configuring-codecs).

| Field | Type | Description |
| name | string | Codec name. Must exactly match the codec name used in Session Description Protocol (SDP). Supported values are `PCMU`, `PCMA`, `G722`, and `AMR-WB`. To learn more, see [SDP offer and answer](https://docs.livekit.io/reference/telephony/codecs-negotiation.md#sdp-offer-and-answer). |
| rate | uint32 | Sample rate in Hz. If unset, the default rate for the codec is used. Each currently supported codec uses a single sample rate, so this field can be omitted. To learn more, see [Codec sample rate](https://docs.livekit.io/reference/telephony/codecs-negotiation.md#codec-sample-rate). |

### SIPDispatchRule

Valid values include:

| Name | Type | Value | Description |
| dispatch_rule_direct | SIPDispatchRuleDirect | 1 | Dispatches callers into an existing room. You can optionally require a pin before caller enters the room. |
| dispatch_rule_individual | SIPDispatchRuleIndividual | 2 | Creates a new room for each caller. |
| dispatch_rule_callee | SIPDispatchRuleCallee | 3 | Creates a new room for each callee. |

### SIPDispatchRuleCallee

| Field | Type | Description |
| room_prefix | string | Prefix added to the generated room name. When set, the room name is `<room_prefix>_<called_number>`; when empty, the room name is the called number. |
| pin | string | Optional pin a caller must enter to join the room. |
| randomize | bool | If true, append a random suffix to the room name so each caller gets a unique room. Defaults to false, which places callers to the same number in the same room. |

### SIPDispatchRuleDirect

| Field | Type | Description |
| room_name | string | Name of the room that callers join. |
| pin | string | Optional pin a caller must enter to join the room. |

### SIPDispatchRuleIndividual

| Field | Type | Description |
| room_prefix | string | Prefix added to the generated room name. When set, the room name is `<room_prefix>_<caller_number>`; when empty, the room name is the caller's number. |
| pin | string | Optional pin a caller must enter to join the room. |

### SIPDispatchRuleInfo

| Field | Type | Description |
| sip_dispatch_rule_id | string | Dispatch rule ID. |
| rule | [SIPDispatchRule](#sipdispatchrule) | Type of dispatch rule. |
| trunk_ids | array<string> | List of associated trunk IDs. |
| hide_phone_number | bool | If true, hides phone number. |
| inbound_numbers | array<string> | If this list is populated, the dispatch rule only accepts calls made _from_ numbers in the list. If a caller's phone number is not in the list, the call is rejected. |
| name | string | Human-readable name for the dispatch rule. |
| metadata | string | User-defined metadata for the dispatch rule. Participants created by this rule inherit this metadata. |
| headers | map<string, string> | Custom SIP X-* headers to include in the 200 OK response. |
| attributes | map<string, string> | Key-value mapping of user-defined attributes. Participants created by this rule inherit these attributes. |
| room_preset | string | Only for LiveKit Cloud: Config preset to use. |
| room_config | [RoomConfiguration](https://docs.livekit.io/reference/server/server-apis.md#roomconfiguration) | Room configuration object associated with the dispatch rule. |
| media | [SIPMediaConfig](#sipmediaconfig) | Media configuration for calls handled by this dispatch rule, including codecs, encryption, and media timeout. |

### SIPDispatchRuleUpdate

| Field | Type | Description |
| trunk_ids | array<string> | [ListUpdate](#listupdate) | List of trunk IDs to associate with the dispatch rule. |
| rule | [SIPDispatchRule](#sipdispatchrule) | Type of dispatch rule. |
| name | string | Human-readable name for the dispatch rule. |
| metadata | string | User-defined metadata for the dispatch rule. Participants created by this rule inherit this metadata. |
| attributes | map<string, string> | Key-value mapping of user-defined attributes. Participants created by this rule inherit these attributes. |
| media | [SIPMediaConfig](#sipmediaconfig) | Media configuration for calls handled by this dispatch rule, including codecs, encryption, and media timeout. |
| media_encryption | [SIPMediaEncryption](#sipmediaencryption) | Deprecated. Use the `encryption` field in [`media`](#sipmediaconfig) instead. Whether or not to encrypt media. |

### SIPHeaderOptions

Enum. Valid values are as follows:

| Name | Value | Description |
| SIP_NO_HEADERS | 0 | Don't map any headers except those mapped explicitly. |
| SIP_X_HEADERS | 1 | Map all `X-*` headers to `sip.h.*` attributes. |
| SIP_ALL_HEADERS | 2 | Map all headers to `sip.h.*` attributes. |

### SIPInboundTrunkInfo

| Field | Type | Description |
| sip_trunk_id | string | Trunk ID |
| name | string | Human-readable name for the trunk. |
| numbers | array<string> | [ListUpdate](#listupdate) | Phone numbers associated with the trunk. The trunk only accepts calls made to the phone numbers in the list. |
| allowed_addresses | array<string> | IP addresses or CIDR blocks that are allowed to use the trunk. If this list is populated, the trunk only accepts traffic from the IP addresses in the list. |
| allowed_numbers | array<string> | Phone numbers that are allowed to dial in. If this list is populated, the trunk only accepts calls from the numbers in the list. |
| auth_username | string | Username used to authenticate inbound SIP invites. |
| auth_password | string | Password used to authenticate inbound SIP invites. |
| headers | map<string, string> | Custom SIP X-* headers to include in the 200 OK response. |
| headers_to_attributes | map<string, string> | Custom SIP X-* headers that map to SIP participant attributes. |
| ringing_timeout | [google.protobuf.Duration](https://github.com/protocolbuffers/protobuf/blob/main/src/google/protobuf/duration.proto) | Maximum time for the caller to wait for track subscription (that is, for the call to be picked up). |
| max_call_duration | google.protobuf.Duration | Maximum call duration. |
| krisp_enabled | Boolean | True if Krisp noise cancellation is enabled for the call. |
| media | [SIPMediaConfig](#sipmediaconfig) | Media configuration for calls on this trunk, including codecs, encryption, and media timeout. |

### SIPInboundTrunkUpdate

| Field | Type | Description |
| numbers | array<string> | [ListUpdate](#listupdate) | List of phone numbers associated with the trunk. |
| allowed_addresses | array<string> | [ListUpdate](#listupdate) | List of IP addresses or CIDR blocks that are allowed to use the trunk. This field must be enabled for your project before you can use it. Contact LiveKit support to request access. |
| allowed_numbers | array<string> | [ListUpdate](#listupdate) | List of phone numbers that are allowed to use the trunk. |
| auth_username | string | Username used to authenticate inbound SIP invites. |
| auth_password | string | Password used to authenticate inbound SIP invites. |
| name | string | Human-readable name for the trunk. |
| metadata | string | User-defined metadata for the trunk. |
| media | [SIPMediaConfig](#sipmediaconfig) | Media configuration for calls on this trunk, including codecs, encryption, and media timeout. |
| media_encryption | [SIPMediaEncryption](#sipmediaencryption) | Deprecated. Use the `encryption` field in [`media`](#sipmediaconfig) instead. Whether or not to encrypt media. |

### SIPMediaConfig

Encapsulates the media configuration for a call, including codecs, encryption, and media timeout. Set this object using the `media` field on inbound trunks, outbound trunks, dispatch rules, and `CreateSIPParticipant` requests.

> ℹ️ **Media configuration precedence**
> 
> When media configuration is set at more than one level, LiveKit resolves each value in the following order, from highest to lowest priority:
> 
> - **Inbound calls**: dispatch rule, then inbound trunk, then defaults.
> - **Outbound calls**: `CreateSIPParticipant` request, then outbound trunk, then defaults.
> 
> The `encryption` and `media_timeout` fields fall through independently: if either is unset at a higher-priority level, the next level's value stays in effect. Codecs are resolved as a pair: if the higher-priority level lists no `codecs`, both `codecs` and `only_listed_codecs` are inherited from the next level down.

| Field | Type | Description |
| codecs | array<[SIPCodec](#sipcodec)> | Extra codecs to enable for the call, in addition to the default codecs. If `only_listed_codecs` is true, the default codecs are cleared and only the codecs in this list are used. To learn more, see [Configuring codecs](https://docs.livekit.io/reference/telephony/codecs-negotiation.md#configuring-codecs). |
| only_listed_codecs | bool | If true, ignore the default codecs and use only the codecs listed in `codecs`. Defaults to false. |
| encryption | [SIPMediaEncryption](#sipmediaencryption) | Whether or not to encrypt media. Replaces the deprecated top-level `media_encryption` field. |
| media_timeout | [google.protobuf.Duration](https://github.com/protocolbuffers/protobuf/blob/main/src/google/protobuf/duration.proto) | Custom media timeout for the call. If zero or unset, a default timeout is used. |

### SIPMediaEncryption

Enum. Valid values are as follows:

| Name | Value | Description |
| SIP_MEDIA_ENCRYPT_DISABLE | 0 | Don't turn on encryption. |
| SIP_MEDIA_ENCRYPT_ALLOW | 1 | Use encryption if available. |
| SIP_MEDIA_ENCRYPT_REQUIRE | 2 | Require encryption. |

### SIPOutboundConfig

Inline outbound trunk configuration for use with [`CreateSIPParticipant`](#createsipparticipant). For more information, see [Inline trunk configuration](https://docs.livekit.io/telephony/making-calls/outbound-calls.md#inline-trunk).

| Field | Type | Description |
| hostname | string | SIP server address (for example, `<my-trunk>.pstn.twilio.com` or `sip.telnyx.com`). |
| destination_country | string | Two-letter [country code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) for the country the call terminates in. LiveKit uses the country code to route calls. To learn more, see [Outbound calls](https://docs.livekit.io/telephony/features/region-pinning.md#outbound-calls). |
| transport | [SIPTransport](#siptransport) | SIP transport used for the outbound call. |
| auth_username | string | Username for authenticated use of the SIP trunk. Can be empty for unauthenticated trunks. |
| auth_password | string | Password for authenticated use of the SIP trunk. Can be empty for unauthenticated trunks. |
| headers_to_attributes | map<string, string> | Map of SIP X-* headers from a `200 OK` response to SIP participant attributes. Keys are header names and values are the participant attribute names they map to. |
| attributes_to_headers | map<string, string> | Map of LiveKit attributes to SIP X-* headers when sending BYE or REFER requests. Keys are attribute names and values are the X-* header names they map to. |
| from_host | string | Optional custom hostname for the `From` SIP header. When set, outbound calls use this host instead of the default project SIP domain. |

### SIPOutboundTrunkInfo

| Field | Type | Description |
| sip_trunk_id | string | Trunk ID. |
| name | string | Trunk name. |
| metadata | string | User-defined metadata for trunk. |
| address | string | Hostname or IP address the SIP request message (SIP INVITE) is sent to. |
| destination_country | string | Two-letter [country code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) for the country the call terminates in. LiveKit uses the country code to route calls. To learn more, see [Outbound calls](https://docs.livekit.io/telephony/features/region-pinning.md#outbound-calls). |
| transport | [SIPTransport](#siptransport) | Protocol to use for SIP transport: auto, TCP, or UDP. |
| numbers | array<string> | Phone numbers used to make calls. A random number in the list is selected whenever a call is made. |
| auth_username | string | Username used to authenticate with the SIP server. |
| auth_password | string | Password used to authenticate with the SIP server. |
| headers | map<string, string> | Custom SIP X-* headers to include in the 200 OK response. |
| headers_to_attributes | map<string, string> | Custom SIP X-* headers that map to SIP participant attributes. |
| media | [SIPMediaConfig](#sipmediaconfig) | Media configuration for calls on this trunk, including codecs, encryption, and media timeout. |

### SIPOutboundTrunkUpdate

| Field | Type | Description |
| address | string | Hostname or IP address the SIP request message (SIP INVITE) is sent to. |
| transport | [SIPTransport](#siptransport) | Protocol to use for SIP transport: auto, TCP, or UDP. |
| destination_country | string | Two-letter [country code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) for the country the call terminates in. LiveKit uses the country code to route calls. To learn more, see [Outbound calls](https://docs.livekit.io/telephony/features/region-pinning.md#outbound-calls). |
| numbers | array<string> | [ListUpdate](#listupdate) | Phone numbers used to make calls. A random number in the list is selected whenever a call is made. |
| auth_username | string | Username used to authenticate with the SIP server. |
| auth_password | string | Password used to authenticate with the SIP server. |
| name | string | Human-readable name for the trunk. |
| metadata | string | User-defined metadata for the trunk. |
| media | [SIPMediaConfig](#sipmediaconfig) | Media configuration for calls on this trunk, including codecs, encryption, and media timeout. |
| media_encryption | [SIPMediaEncryption](#sipmediaencryption) | Deprecated. Use the `encryption` field in [`media`](#sipmediaconfig) instead. Whether or not to encrypt media. |

### SIPParticipantInfo

| Field | Type | Description |
| participant_id | string | Participant ID. |
| participant_identity | string | Participant name. |
| room_name | string | Name of the room. |
| sip_call_id | string | SIP call ID. |

### SIPTransport

Enum. Valid values are as follows:

| Name | Value | Description |
| SIP_TRANSPORT_AUTO | 0 | Detect automatically. |
| SIP_TRANSPORT_UDP | 1 | UDP |
| SIP_TRANSPORT_TCP | 2 | TCP |
| SIP_TRANSPORT_TLS | 3 | TLS |

### SIPTrunkInfo

> ℹ️ **Note**
> 
> This type is deprecated. See [SIPInboundTrunkInfo](#sipinboundtrunkinfo) and [SIPOutboundTrunkInfo](#sipoutboundtrunkinfo).

| Field | Type | Description |
| sip_trunk_id | string | Trunk ID. |
| kind | [TrunkKind](#trunkkind) | Type of trunk. |
| inbound_addresses | array<string> | IP addresses or CIDR blocks that are allowed to use the trunk. If this list is populated, the trunk only accepts traffic from the IP addresses in the list. |
| outbound_address | string | IP address that the SIP INVITE is sent to. |
| outbound_number | string | Phone number used to make outbound calls. |
| transport | [SIPTransport](#siptransport) | Protocol to use for SIP transport: auto, TCP, or UDP. |
| inbound_numbers | array<string> | List of provider phone numbers this trunk is associated with. Only applies to inbound trunks. If this list is populated, the trunk only accepts calls to numbers in this list. |
| inbound_username | string | Username used to authenticate inbound SIP invites. |
| inbound_password | string | Password used to authenticate inbound SIP invites. |
| outbound_username | string | Username used to authenticate outbound SIP invites. |
| outbound_password | string | Password used to authenticate outbound SIP invites. |
| name | string | Trunk name. |
| metadata | string | Initial metadata to assign to the trunk. This metadata is added to every SIP participant that uses the trunk. |

### TrunkKind

Enum. Valid values are as follows:

| Name | Value | Description |
| TRUNK_LEGACY | 0 | Legacy trunk. |
| TRUNK_INBOUND | 1 | [Inbound trunk](https://docs.livekit.io/telephony/accepting-calls/inbound-trunk.md). |
| TRUNK_OUTBOUND | 2 | [Outbound trunk](https://docs.livekit.io/telephony/making-calls/outbound-trunk.md). |

### UpdateSIPDispatchRuleRequest

| Field | Type | Description |
| sip_dispatch_rule_id | string | Dispatch rule ID. |
| action | [SIPDispatchRule](#sipdispatchrule) | [SIPDispatchRuleUpdate](#sipdispatchruleupdate) | Dispatch rule for replacement or update. |

### UpdateSIPInboundTrunkRequest

| Field | Type | Description |
| sip_trunk_id | string | Trunk ID. |
| action | [SIPInboundTrunkInfo](#sipinboundtrunkinfo) | [SIPInboundTrunkUpdate](#sipinboundtrunkupdate) | Trunk info for replacement or update. |

### UpdateSIPOutboundTrunkRequest

| Field | Type | Description |
| sip_trunk_id | string | Trunk ID. |
| action | [SIPOutboundTrunkInfo](#sipoutboundtrunkinfo) | [SIPOutboundTrunkUpdate](#sipoutboundtrunkupdate) | Trunk info for replacement or update. |

---

This document was rendered at 2026-08-24T21:35:00.844Z.
For the latest version of this document, see [https://docs.livekit.io/reference/telephony/sip-api.md](https://docs.livekit.io/reference/telephony/sip-api.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).
