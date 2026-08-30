warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /reference/telephony/phone-numbers-api

LiveKit docs › Reference › Telephony › Phone Numbers API

---

# Phone Numbers APIs

> Use LiveKit's Phone Number APIs to manage phone numbers for your telephony apps.

## Overview

LiveKit provides Phone Numbers APIs that let you search for, purchase, and manage [phone numbers](https://docs.livekit.io/telephony/start/phone-numbers.md) for your telephony apps. These APIs are available with LiveKit server SDKs and CLI:

- [Go phone number client](https://pkg.go.dev/github.com/livekit/server-sdk-go/v2#PhoneNumberClient)
- [CLI](https://github.com/livekit/livekit-cli/blob/main/cmd/lk/phone_number.go)

To learn more about additional APIs, see [SIP APIs](https://docs.livekit.io/reference/telephony/sip-api.md) and [Server APIs](https://docs.livekit.io/reference/server/server-apis.md).

### Using endpoints

The Phone Number API is accessible via `/twirp/livekit.PhoneNumberService/<MethodName>`. For example, if you're using LiveKit Cloud the following URL is for the [SearchPhoneNumbers](#searchphonenumbers) API endpoint:

```shell
https://%{projectDomain}%/twirp/livekit.PhoneNumberService/SearchPhoneNumbers

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

Search available phone numbers using [SearchPhoneNumbers](#searchphonenumbers) API endpoint:

```shell
curl -X POST https://%{projectDomain}%/twirp/livekit.PhoneNumberService/SearchPhoneNumbers \
	-H "Authorization: Bearer <token-with-sip-admin>" \
	-H 'Content-Type: application/json' \
	-d '{ "country_code": "US", "area_code": "415", "limit": 10 }'

```

Purchase a phone number using [PurchasePhoneNumber](#purchasephonenumber) API endpoint:

```shell
curl -X POST https://%{projectDomain}%/twirp/livekit.PhoneNumberService/PurchasePhoneNumber \
	-H "Authorization: Bearer <token-with-sip-admin>" \
	-H 'Content-Type: application/json' \
	-d '{ "phone_numbers": ["+14155551234"] }'

```

## PhoneNumberService APIs

The PhoneNumberService APIs allow you to manage phone numbers for your LiveKit project, including searching, purchasing, and releasing phone numbers.

> 💡 **Tip**
> 
> All RPC definitions and options can be found [here](https://github.com/livekit/protocol/blob/main/protobufs/livekit_phone_number.proto).

### SearchPhoneNumbers

Search available phone numbers in inventory.

Returns [SearchPhoneNumbersResponse](#searchphonenumbersresponse).

| Parameter | Type | Required | Description |
| country_code | string | yes | Filter by country code (for example, "US", "CA"). |
| area_code | string |  | Filter by area code (for example, "415"). |
| limit | int32 |  | Maximum number of results (default: 50). |

### PurchasePhoneNumber

Purchase a phone number from inventory.

Returns [PurchasePhoneNumberResponse](#purchasephonenumberresponse).

| Parameter | Type | Required | Description |
| phone_numbers | string | yes | Phone numbers to purchase (for example, "+16505550010"). |
| sip_dispatch_rule_id | string |  | SIP dispatch rule ID to apply to all purchased numbers. |

### ListPhoneNumbers

List phone numbers for a project.

Returns [ListPhoneNumbersResponse](#listphonenumbersresponse).

| Parameter | Type | Required | Description |
| limit | int32 |  | Maximum number of results (default: 50). |
| statuses | [PhoneNumberStatus](#phonenumberstatus) |  | Filter by status. Multiple statuses can be specified. Valid values are:

- `active`
- `pending`
- `released`
- `offline` |
| sip_dispatch_rule_id | string |  | Filter by SIP dispatch rule ID. |

### GetPhoneNumber

Get a phone number from a project by ID or phone number string.

Returns [GetPhoneNumberResponse](#getphonenumberresponse).

| Parameter | Type | Required | Description |
| id | string |  | Use phone number ID for direct lookup. Required if `phone_number` is not provided. |
| phone_number | string |  | Use phone number string for lookup. (for example, "+16505550010"). Required if `id` is not provided. |

### UpdatePhoneNumber

Update the SIP dispatch rule ID for a phone number in a project.

Returns [UpdatePhoneNumberResponse](#updatephonenumberresponse).

| Parameter | Type | Required | Description |
| id | string |  | Use phone number ID for direct lookup. Required if `phone_number` is not provided. |
| phone_number | string |  | Use phone number string for lookup (for example, "+16505550010"). Required if `id` is not provided. |
| sip_dispatch_rule_id | string |  | SIP dispatch rule ID to assign to the phone number. |

### ReleasePhoneNumbers

Release phone numbers by ID or phone number string.

Returns [ReleasePhoneNumbersResponse](#releasephonenumbersresponse).

| Parameter | Type | Required | Description |
| ids | array<string> |  | Use phone number IDs for direct lookup. Required if `phone_numbers` is not provided. |
| phone_numbers | array<string> |  | Use phone number strings for lookup (for example, "+16505550010"). Required if `ids` is not provided. |

## Types

The Phone Number service includes the following types.

### PhoneNumber

This type is returned in the response types for multiple API endpoints. Some fields are only returned by certain endpoints. See the descriptions for specific response types for more information.

| Field | Type | Description |
| id | string | Unique identifier. |
| e164_format | string | Phone number in E.164 format (for example, "+14155552671"). |
| country_code | string | Country code (for example, "US"). |
| area_code | string | Area code (for example, "415"). |
| number_type | [PhoneNumberType](#phonenumbertype) | Number type (mobile, local, toll-free, unknown). |
| locality | string | City/locality (for example, "San Francisco"). |
| region | string | State/region (for example, "CA"). |
| capabilities | array<string> | Available capabilities (for example, "voice", "sms"). |
| status | [PhoneNumberStatus](#phonenumberstatus) | Current status. |
| assigned_at | google.protobuf.Timestamp | Assignment timestamp. |
| released_at | google.protobuf.Timestamp | Release timestamp (if applicable). |
| sip_dispatch_rule_id | string | **Deprecated.** Use `sip_dispatch_rule_ids` instead. Associated SIP dispatch rule ID. |
| sip_dispatch_rule_ids | array<string> | Associated SIP dispatch rule IDs. |

### PhoneNumberStatus

Enum. Valid values are as follows:

| Name | Value | Description |
| PHONE_NUMBER_STATUS_UNSPECIFIED | 0 | Default value. |
| PHONE_NUMBER_STATUS_ACTIVE | 1 | Number is active and ready for use. |
| PHONE_NUMBER_STATUS_PENDING | 2 | Number is being provisioned. |
| PHONE_NUMBER_STATUS_RELEASED | 3 | Number has been released. |
| PHONE_NUMBER_STATUS_OFFLINE | 4 | Number is offline (not associated with any dispatch rule). |

### PhoneNumberType

Enum. Valid values are as follows:

| Name | Value | Description |
| PHONE_NUMBER_TYPE_UNKNOWN | 0 | Default value - unknown or parsing error. |
| PHONE_NUMBER_TYPE_MOBILE | 1 | Mobile phone number. |
| PHONE_NUMBER_TYPE_LOCAL | 2 | Local/fixed line number. |
| PHONE_NUMBER_TYPE_TOLL_FREE | 3 | Toll-free number. |

### SearchPhoneNumbersResponse

| Field | Type | Description |
| items | array<[PhoneNumber](#phonenumber)> | List of available phone numbers. |

### PurchasePhoneNumberResponse

| Field | Type | Description |
| phone_numbers | array<[PhoneNumber](#phonenumber)> | Details of the purchased phone numbers. Only the following fields of `PhoneNumber` type are returned:

- `id`
- `e164_format`
- `status` |

### ListPhoneNumbersResponse

| Field | Type | Description |
| items | array<[PhoneNumber](#phonenumber)> | List of phone numbers. The following fields of `PhoneNumber` type are returned:

- `id`
- `e164_format`
- `country_code`
- `area_code`
- `number_type`
- `locality`
- `region`
- `capabilities`
- `status`
- `sip_dispatch_rule_id`
- `sip_dispatch_rule_ids`
- `released_at` (if applicable) |
| total_count | int32 | Total number of phone numbers. |
| offline_count | int32 | Total number of offline phone numbers. |

### GetPhoneNumberResponse

| Field | Type | Description |
| phone_number | [PhoneNumber](#phonenumber) | The phone number details. The following fields of `PhoneNumber` type are returned:

- `id`
- `e164_format`
- `country_code`
- `area_code`
- `number_type`
- `locality`
- `region`
- `capabilities`
- `status`
- `sip_dispatch_rule_id`
- `sip_dispatch_rule_ids`
- `released_at` (if applicable) |

### UpdatePhoneNumberResponse

| Field | Type | Description |
| phone_number | [PhoneNumber](#phonenumber) | The updated phone number details. The following fields of `PhoneNumber` type are returned:

- `id`
- `e164_format`
- `status`
- `sip_dispatch_rule_id`
- `sip_dispatch_rule_ids` |

### ReleasePhoneNumbersResponse

| Field | Type | Description |
|  |  | Empty response - operation completed successfully. |

---

This document was rendered at 2026-08-24T21:31:32.180Z.
For the latest version of this document, see [https://docs.livekit.io/reference/telephony/phone-numbers-api.md](https://docs.livekit.io/reference/telephony/phone-numbers-api.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).
