warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /reference/other/ingress/api

LiveKit docs › Reference › Other › Ingress › Ingress API

---

# Ingress API

> Use LiveKit's ingress service to import live streams from non-WebRTC sources into LiveKit rooms.

## API

The Ingress API is available within the server SDKs and the CLI:

- [Go Ingress Client](https://pkg.go.dev/github.com/livekit/server-sdk-go/v2#IngressClient)
- [JS Ingress Client](https://docs.livekit.io/reference/server-sdk-js/classes/IngressClient.html.md)
- [Ruby Ingress Client](https://github.com/livekit/server-sdk-ruby/blob/main/lib/livekit/ingress_service_client.rb)
- [Python Ingress Client](https://docs.livekit.io/reference/python/livekit/api/ingress_service.html.md)
- [Java Ingress Client](https://github.com/livekit/server-sdk-kotlin/blob/main/src/main/kotlin/io/livekit/server/IngressServiceClient.kt)
- [CLI](https://github.com/livekit/livekit-cli/blob/main/cmd/lk/ingress.go)

### CreateIngress

#### WHIP / RTMP example

To provision an ingress with the Ingress service, use the `CreateIngress` API. It returns an `IngressInfo` object that describes the created ingress, along with connection settings. These parameters can also be queried at any time using the `ListIngress` API

**LiveKit CLI**:

Create a file at `ingress.json` with the following content:

```json
{
    "input_type": 0 for RTMP, 1 for WHIP
    "name": "Name of the ingress goes here",
    "room_name": "Name of the room to connect to",
    "participant_identity": "Unique identity for the room participant the Ingress service will connect as",
    "participant_name": "Name displayed in the room for the participant",
    "enable_transcoding": true // Transcode the input stream. Can only be false for WHIP,
}

```

Then create the ingress using `lk`:

```shell
export LIVEKIT_URL=https://my-livekit-host
export LIVEKIT_API_KEY=livekit-api-key
export LIVEKIT_API_SECRET=livekit-api-secret

lk ingress create ingress.json

```

---

**Node.js**:

```typescript
import { LiveKitAPI, IngressInput } from 'livekit-server-sdk';

const api = new LiveKitAPI();

const ingress = {
  name: 'my-ingress',
  roomName: 'my-room',
  participantIdentity: 'my-participant',
  participantName: 'My Participant',
  // Transcode the input stream. Can only be false for WHIP.
  enableTranscoding: false,
};

// Use IngressInput.WHIP_INPUT to create a WHIP endpoint
const info = await api.ingress.createIngress(IngressInput.RTMP_INPUT, ingress);

```

---

**Python**:

```python
from livekit import api

async with api.LiveKitAPI() as lkapi:
    info = await lkapi.ingress.create_ingress(
        api.CreateIngressRequest(
            input_type=api.IngressInput.RTMP_INPUT,  # or api.IngressInput.WHIP_INPUT
            name="my-ingress",
            room_name="my-room",
            participant_identity="my-participant",
            participant_name="My Participant",
            # Transcode the input stream. Can only be false for WHIP.
            enable_transcoding=True,
        )
    )
    print(info.ingress_id)

```

---

**Ruby**:

```ruby
require 'livekit'

lkapi = LiveKit::LiveKitAPI.new
info = lkapi.ingress.create_ingress(
  :RTMP_INPUT, # Or WHIP_INPUT
  name: "my-ingress",
  room_name: "my-room",
  participant_identity: "my-participant",
  participant_name: "My Participant",
  enable_transcoding: true
)
puts info.ingress_id

```

---

**Go**:

```go
import lksdk "github.com/livekit/server-sdk-go/v2"

ctx := context.Background()
api, err := lksdk.NewLiveKitAPI()

t := true

ingressRequest := &livekit.CreateIngressRequest{
    InputType:           livekit.IngressInput_RTMP_INPUT, // Or livekit.IngressInput_WHIP_INPUT
    Name:                "my-ingress",
    RoomName:            "my-room",
    ParticipantIdentity: "my-participant",
    ParticipantName:     "My Participant",
    // Transcode the input stream. Can only be false for WHIP.
    EnableTranscoding: &t,
}

info, err := api.Ingress().CreateIngress(ctx, ingressRequest)
ingressID := info.IngressId

```

---

**Kotlin**:

```kotlin
import io.livekit.server.LiveKitAPI
import livekit.LivekitIngress

val api = LiveKitAPI.createClient(host, apiKey, secret)
val info = api.ingress.createIngress(
    "my-ingress",
    roomName = "my-room",
    participantIdentity = "my-participant",
    participantName = "My Participant",
    // Or LivekitIngress.IngressInput.WHIP_INPUT
    inputType = LivekitIngress.IngressInput.RTMP_INPUT,
    // Transcode the input stream. Can only be false for WHIP.
    enableTranscoding = true,
).execute().body()

```

---

**Rust**:

```rust
use livekit_api::services::ingress::CreateIngressOptions;
use livekit_api::services::LiveKitApi;
use livekit_protocol as proto;

let api = LiveKitApi::with_api_key(host, api_key, api_secret);
let info = api
    .ingress()
    .create_ingress(
        proto::IngressInput::RtmpInput, // or proto::IngressInput::WhipInput
        CreateIngressOptions {
            name: "my-ingress".to_string(),
            room_name: "my-room".to_string(),
            participant_identity: "my-participant".to_string(),
            participant_name: "My Participant".to_string(),
            // Transcode the input stream. Can only be false for WHIP.
            enable_transcoding: Some(true),
            ..Default::default()
        },
    )
    .await?;

```

#### URL Input example

With URL Input, ingress will begin immediately after `CreateIngress` is called. `URL_INPUT` ingress can't be reused.

**LiveKit CLI**:

Create a file at `ingress.json` with the following content:

```json
{
  "input_type": "URL_INPUT", // or 2
  "name": "Name of the ingress goes here",
  "room_name": "Name of the room to connect to",
  "participant_identity": "Unique identity for the room participant the Ingress service will connect as",
  "participant_name": "Name displayed in the room for the participant",
  "url": "HTTP(S) or SRT url to the file or stream"
}

```

Then create the ingress using `lk`:

```shell
export LIVEKIT_URL=https://my-livekit-host
export LIVEKIT_API_KEY=livekit-api-key
export LIVEKIT_API_SECRET=livekit-api-secret

lk ingress create ingress.json

```

---

**Node.js**:

```typescript
import { LiveKitAPI, IngressInput } from 'livekit-server-sdk';

const api = new LiveKitAPI();

const ingress = {
  name: 'my-ingress',
  roomName: 'my-room',
  participantIdentity: 'my-participant',
  participantName: 'My Participant',
  url: 'https://domain.com/video.m3u8', // or 'srt://domain.com:7001'
};

const info = await api.ingress.createIngress(IngressInput.URL_INPUT, ingress);

```

---

**Python**:

```python
from livekit import api

async with api.LiveKitAPI() as lkapi:
    info = await lkapi.ingress.create_ingress(
        api.CreateIngressRequest(
            input_type=api.IngressInput.URL_INPUT,
            name="my-ingress",
            room_name="my-room",
            participant_identity="my-participant",
            participant_name="My Participant",
            url="https://domain.com/video.m3u8",  # or 'srt://domain.com:7001'
        )
    )
    print(info.ingress_id)

```

---

**Ruby**:

```ruby
require 'livekit'

lkapi = LiveKit::LiveKitAPI.new
info = lkapi.ingress.create_ingress(
  :URL_INPUT,
  name: "my-ingress",
  room_name: "my-room",
  participant_identity: "my-participant",
  participant_name: "My Participant",
  url: "https://domain.com/video.m3u8", # or 'srt://domain.com:7001'
)
puts info.ingress_id

```

---

**Go**:

```go
import lksdk "github.com/livekit/server-sdk-go/v2"

ctx := context.Background()
api, err := lksdk.NewLiveKitAPI()

ingressRequest := &livekit.CreateIngressRequest{
    InputType:           livekit.IngressInput_URL_INPUT,
    Name:                "my-ingress",
    RoomName:            "my-room",
    ParticipantIdentity: "my-participant",
    ParticipantName:     "My Participant",
    Url:                 "https://domain.com/video.m3u8", // or 'srt://domain.com:7001'
}

info, err := api.Ingress().CreateIngress(ctx, ingressRequest)
ingressID := info.IngressId

```

---

**Kotlin**:

```kotlin
import io.livekit.server.LiveKitAPI
import livekit.LivekitIngress

val api = LiveKitAPI.createClient(host, apiKey, secret)
val info = api.ingress.createIngress(
    "my-ingress",
    roomName = "my-room",
    participantIdentity = "my-participant",
    participantName = "My Participant",
    inputType = LivekitIngress.IngressInput.URL_INPUT,
    url = "https://domain.com/video.m3u8", // or "srt://domain.com:7001"
).execute().body()

```

---

**Rust**:

```rust
use livekit_api::services::ingress::CreateIngressOptions;
use livekit_api::services::LiveKitApi;
use livekit_protocol as proto;

let api = LiveKitApi::with_api_key(host, api_key, api_secret);
let info = api
    .ingress()
    .create_ingress(
        proto::IngressInput::UrlInput,
        CreateIngressOptions {
            name: "my-ingress".to_string(),
            room_name: "my-room".to_string(),
            participant_identity: "my-participant".to_string(),
            participant_name: "My Participant".to_string(),
            url: "https://domain.com/video.m3u8".to_string(), // or "srt://domain.com:7001"
            ..Default::default()
        },
    )
    .await?;

```

### ListIngress

**LiveKit CLI**:

```shell
lk ingress list

```

The optional `--room` option allows to restrict the output to the Ingress associated to a given room. The `--id` option can check if a specific ingress is active.

---

**Node.js**:

```typescript
import { LiveKitAPI } from 'livekit-server-sdk';

const api = new LiveKitAPI();
await api.ingress.listIngress({ roomName: 'my-room' });

```

The `roomName` parameter can be left empty to list all Ingress.

---

**Python**:

```python
from livekit import api

async with api.LiveKitAPI() as lkapi:
    # room_name is optional; leave empty to list all Ingress.
    res = await lkapi.ingress.list_ingress(api.ListIngressRequest(room_name="my-room"))

```

---

**Ruby**:

```ruby
require 'livekit'

lkapi = LiveKit::LiveKitAPI.new
puts lkapi.ingress.list_ingress(
  # optional
  room_name: "my-room"
)

```

---

**Go**:

```go
import lksdk "github.com/livekit/server-sdk-go/v2"

api, err := lksdk.NewLiveKitAPI()
listRequest := &livekit.ListIngressRequest{
    RoomName: "my-room", // Optional parameter to restrict the list to only one room. Leave empty to list all Ingress.
}

infoArray, err := api.Ingress().ListIngress(context.Background(), listRequest)

```

---

**Kotlin**:

```kotlin
import io.livekit.server.LiveKitAPI

val api = LiveKitAPI.createClient(host, apiKey, secret)
// roomName is optional; leave empty to list all Ingress.
val infos = api.ingress.listIngress(roomName = "my-room").execute().body()

```

---

**Rust**:

```rust
use livekit_api::services::ingress::IngressListFilter;
use livekit_api::services::LiveKitApi;

let api = LiveKitApi::with_api_key(host, api_key, api_secret);
// Use IngressListFilter::All to list every ingress.
let infos = api.ingress().list_ingress(IngressListFilter::Room("my-room".to_string())).await?;

```

### UpdateIngress

The ingress configuration can be updated using the `UpdateIngress` API. This enables the ability to reuse the same ingress URL to publish to different rooms. Only reusable ingresses, such as RTMP or WHIP, can be updated.

**LiveKit CLI**:

Create a file at `ingress.json` with the fields to be updated.

```json
{
  "ingress_id": "Ingress ID of the ingress to update",
  "name": "Name of the ingress goes here",
  "room_name": "Name of the room to connect to",
  "participant_identity": "Unique identity for the room participant the Ingress service will connect as",
  "participant_name": "Name displayed in the room for the participant"
}

```

The only required field is `ingress_id`. Non-provided fields are left unchanged.

```shell
lk ingress update ingress.json

```

---

**Node.js**:

```typescript
import { LiveKitAPI } from 'livekit-server-sdk';

const api = new LiveKitAPI();
const update = {
  name: 'my-other-ingress',
  roomName: 'my-other-room',
  participantIdentity: 'my-other-participant',
  participantName: 'My Other Participant',
};

await api.ingress.updateIngress(ingressId, update);

```

Parameters left empty in the update object are left unchanged.

---

**Python**:

```python
from livekit import api

async with api.LiveKitAPI() as lkapi:
    # non-specified fields are left unchanged
    info = await lkapi.ingress.update_ingress(
        api.UpdateIngressRequest(
            ingress_id="ingress-id",
            name="my-other-ingress",
            room_name="my-other-room",
            participant_identity="my-other-participant",
            participant_name="My Other Participant",
        )
    )

```

---

**Ruby**:

```ruby
require 'livekit'

lkapi = LiveKit::LiveKitAPI.new
# only specified fields are updated, all fields are optional
puts lkapi.ingress.update_ingress(
  "ingress-id",
  name: "ingress-name",
  room_name: "my-room",
  participant_identity: "my-participant",
  participant_name: "My Participant"
)

```

---

**Go**:

```go
import lksdk "github.com/livekit/server-sdk-go/v2"

api, err := lksdk.NewLiveKitAPI()
updateRequest := &livekit.UpdateIngressRequest{
    IngressId:           "ingressID", // required parameter indicating what Ingress to update
    Name:                "my-other-ingress",
    RoomName:            "my-other-room",
    ParticipantIdentity: "my-other-participant",
    ParticipantName:     "My Other Participant",
}

info, err := api.Ingress().UpdateIngress(context.Background(), updateRequest)

```

Non specified fields are left unchanged.

---

**Kotlin**:

```kotlin
import io.livekit.server.LiveKitAPI

val api = LiveKitAPI.createClient(host, apiKey, secret)
// non-specified fields are left unchanged
val info = api.ingress.updateIngress(
    "ingress-id",
    name = "my-other-ingress",
    roomName = "my-other-room",
    participantIdentity = "my-other-participant",
    participantName = "My Other Participant",
).execute().body()

```

---

**Rust**:

```rust
use livekit_api::services::ingress::UpdateIngressOptions;
use livekit_api::services::LiveKitApi;

let api = LiveKitApi::with_api_key(host, api_key, api_secret);
let info = api
    .ingress()
    .update_ingress(
        "ingress-id",
        UpdateIngressOptions {
            name: "my-other-ingress".to_string(),
            room_name: "my-other-room".to_string(),
            participant_identity: "my-other-participant".to_string(),
            participant_name: "My Other Participant".to_string(),
            ..Default::default()
        },
    )
    .await?;

```

### DeleteIngress

An ingress can be reused multiple times. When not needed anymore, it can be deleted using the `DeleteIngress` API:

**LiveKit CLI**:

```shell
lk ingress delete <INGRESS_ID>

```

---

**Node.js**:

```typescript
import { LiveKitAPI } from 'livekit-server-sdk';

const api = new LiveKitAPI();
await api.ingress.deleteIngress('ingress-id');

```

---

**Python**:

```python
from livekit import api

async with api.LiveKitAPI() as lkapi:
    info = await lkapi.ingress.delete_ingress(
        api.DeleteIngressRequest(ingress_id="ingress-id")
    )

```

---

**Ruby**:

```ruby
require 'livekit'

lkapi = LiveKit::LiveKitAPI.new
puts lkapi.ingress.delete_ingress("ingress-id")

```

---

**Go**:

```go
import lksdk "github.com/livekit/server-sdk-go/v2"

api, err := lksdk.NewLiveKitAPI()
deleteRequest := &livekit.DeleteIngressRequest{
    IngressId: "ingress-id",
}

info, err := api.Ingress().DeleteIngress(context.Background(), deleteRequest)

```

---

**Kotlin**:

```kotlin
import io.livekit.server.LiveKitAPI

val api = LiveKitAPI.createClient(host, apiKey, secret)
val info = api.ingress.deleteIngress("ingress-id").execute().body()

```

---

**Rust**:

```rust
use livekit_api::services::LiveKitApi;

let api = LiveKitApi::with_api_key(host, api_key, api_secret);
let info = api.ingress().delete_ingress("ingress-id").await?;

```

## Types

The Ingress service includes the following types.

### ListIngressResponse

| Field | Type | Description |
| items | array<[IngressInfo](#ingressinfo)> | List of ingress endpoints. |
| next_page_token | TokenPagination | Token for the next page of results. |

### IngressInfo

Describes the ingress and its connection settings.

| Field | Type | Description |
| ingress_id | string | Unique ingress ID. |
| name | string | User-provided identifier for the ingress. |
| stream_key | string | Stream key for the encoder (RTMP). |
| url | string | URL for the encoder (RTMP, WHIP) or source to pull from (URL input). Format depends on input type: `rtmp://` for RTMP, `http://` for URL. |
| input_type | [IngressInput](#ingressinput) | Type of input. |
| enable_transcoding | bool | Whether transcoding is enabled. |
| audio | [IngressAudioOptions](#ingressaudiooptions) | Audio options. |
| video | [IngressVideoOptions](#ingressvideooptions) | Video options. |
| room_name | string | Room the ingress publishes to. |
| participant_identity | string | Identity of the publishing participant. |
| participant_name | string | Display name of the publishing participant. |
| participant_metadata | string | Metadata associated with the publishing participant. |
| reusable | bool | Whether the ingress can be reused (e.g. for another room). |
| state | [IngressState](#ingressstate) | Current state, including error or debug info (bitrate, resolution, bandwidth). |
| enabled | bool | When false, new connection attempts are rejected. Default is true. |

### IngressState

Describes current endpoint status, errors, and input media state.

| Field | Type | Description |
| status | [IngressState.Status](#ingressstatestatus) | Endpoint status. |
| error | string | Error or non-compliance description, if any. |
| video | [InputVideoState](#inputvideostate) | Incoming video state. |
| audio | [InputAudioState](#inputaudiostate) | Incoming audio state. |
| room_id | string | ID of the current or previous room published to. |
| started_at | int64 | When the endpoint started publishing. |
| ended_at | int64 | When the endpoint stopped publishing. |
| updated_at | int64 | Last update timestamp. |
| resource_id | string | Resource identifier. |
| tracks | array<TrackInfo> | Published track info. |

### IngressState.Status

Enum. Endpoint status values:

| Name | Value | Description |
| ENDPOINT_INACTIVE | 0 | Endpoint is inactive. |
| ENDPOINT_BUFFERING | 1 | Endpoint is buffering. |
| ENDPOINT_PUBLISHING | 2 | Endpoint is publishing. |
| ENDPOINT_ERROR | 3 | Endpoint encountered an error. |
| ENDPOINT_COMPLETE | 4 | Endpoint finished (e.g. stream ended). |

### InputVideoState

State of the incoming video input.

| Field | Type | Description |
| mime_type | string | MIME type of the video. |
| average_bitrate | uint32 | Average bitrate in bps. |
| width | uint32 | Frame width in pixels. |
| height | uint32 | Frame height in pixels. |
| framerate | double | Frame rate. |

### InputAudioState

State of the incoming audio input.

| Field | Type | Description |
| mime_type | string | MIME type of the audio. |
| average_bitrate | uint32 | Average bitrate in bps. |
| channels | uint32 | Number of audio channels. |
| sample_rate | uint32 | Sample rate in Hz. |

### IngressInput

Enum. Type of ingress input:

| Name | Value | Description |
| RTMP_INPUT | 0 | RTMP push input. |
| WHIP_INPUT | 1 | WHIP push input. |
| URL_INPUT | 2 | Pull from a URL. Only HTTP URLs supported (single media file or HLS stream). |

### IngressAudioOptions

| Field | Type | Description |
| name | string | Track name. |
| source | TrackSource | Track source. |
| encoding_options | [IngressAudioEncodingPreset](#ingressaudioencodingpreset) or [IngressAudioEncodingOptions](#ingressaudioencodingoptions) | Preset or custom encoding options. |

### IngressVideoOptions

| Field | Type | Description |
| name | string | Track name. |
| source | TrackSource | Track source. |
| encoding_options | [IngressVideoEncodingPreset](#ingressvideoencodingpreset) or [IngressVideoEncodingOptions](#ingressvideoencodingoptions) | Preset or custom encoding options. |

### IngressAudioEncodingPreset

Enum. Audio encoding presets:

| Name | Value | Description |
| OPUS_STEREO_96KBPS | 0 | OPUS, 2 channels, 96 kbps. |
| OPUS_MONO_64KBS | 1 | OPUS, 1 channel, 64 kbps. |

### IngressVideoEncodingPreset

Enum. Video encoding presets:

| Name | Value | Description |
| H264_720P_30FPS_3_LAYERS | 0 | 1280×720, 30 fps, 1900 kbps main layer, 3 layers total. |
| H264_1080P_30FPS_3_LAYERS | 1 | 1920×1080, 30 fps, 3500 kbps main layer, 3 layers total. |
| H264_540P_25FPS_2_LAYERS | 2 | 960×540, 25 fps, 1000 kbps main layer, 2 layers total. |
| H264_720P_30FPS_1_LAYER | 3 | 1280×720, 30 fps, 1900 kbps, no simulcast. |
| H264_1080P_30FPS_1_LAYER | 4 | 1920×1080, 30 fps, 3500 kbps, no simulcast. |
| H264_720P_30FPS_3_LAYERS_HIGH_MOTION | 5 | 1280×720, 30 fps, 2500 kbps main layer, 3 layers, higher bitrate for high motion. |
| H264_1080P_30FPS_3_LAYERS_HIGH_MOTION | 6 | 1920×1080, 30 fps, 4500 kbps main layer, 3 layers, higher bitrate for high motion. |
| H264_540P_25FPS_2_LAYERS_HIGH_MOTION | 7 | 960×540, 25 fps, 1300 kbps main layer, 2 layers, higher bitrate for high motion. |
| H264_720P_30FPS_1_LAYER_HIGH_MOTION | 8 | 1280×720, 30 fps, 2500 kbps, no simulcast, higher bitrate for high motion. |
| H264_1080P_30FPS_1_LAYER_HIGH_MOTION | 9 | 1920×1080, 30 fps, 4500 kbps, no simulcast, higher bitrate for high motion. |

### IngressAudioEncodingOptions

Custom audio encoding options.

| Field | Type | Description |
| audio_codec | AudioCodec | Desired audio codec to publish to the room. |
| bitrate | uint32 | Bitrate in bps. |
| disable_dtx | bool | Whether to disable DTX. |
| channels | uint32 | Number of channels. |

### IngressVideoEncodingOptions

Custom video encoding options.

| Field | Type | Description |
| video_codec | VideoCodec | Desired video codec to publish to the room. |
| frame_rate | double | Frame rate. |
| layers | array<VideoLayer> | Simulcast layers. When empty, layers are typically set to 1/2 and 1/4 of dimensions. |

---

This document was rendered at 2026-08-24T21:34:39.661Z.
For the latest version of this document, see [https://docs.livekit.io/reference/other/ingress/api.md](https://docs.livekit.io/reference/other/ingress/api.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).
