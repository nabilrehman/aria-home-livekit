warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /transport/media/ingress-egress/ingress/transcode

LiveKit docs › WebRTC Transport › Media › Stream export & import › Ingress › Transcoding configuration

---

# Transcoding configuration

> Configure video and audio encoding settings for LiveKit Ingress, including presets and custom encoding options.

## Overview

The Ingress service can transcode the media being received. This is the only supported behavior for RTMP and URL inputs. WHIP ingresses are not transcoded by default, but transcoding can be enabled by setting the `enable_transcoding` parameter. When transcoding is enabled, the default settings enable [video simulcast](https://blog.livekit.io/an-introduction-to-webrtc-simulcast-6c5f1f6402eb/) to ensure media can be consumed by all viewers, and should be suitable for most use cases.

In some situations however, you may want to adjust these settings to match source content or the viewer conditions better. For this purpose, LiveKit Ingress defines several presets, both for audio and video. Presets define both the characteristics of the media (codec, dimensions, framerate, channel count, sample rate) and the bitrate. For video, a single preset defines the full set of simulcast layers.

## Using video presets

A preset can be chosen at Ingress creation time from the [constants in the Ingress protocol definition](https://github.com/livekit/protocol/blob/main/protobufs/livekit_ingress.proto):

**LiveKit CLI**:

Create a file at `ingress.json` with the following content:

```json
{
    "name": "Name of the egress goes here",
    "room_name": "Name of the room to connect to",
    "participant_identity": "Unique identity for the room participant the Ingress service will connect as",
    "participant_name": "Name displayed in the room for the participant"
    "video": {
        "name": "track name",
        "source": "SCREEN_SHARE",
        "preset": "Video preset enum value"
    },
    "audio": {
        "name": "track name",
        "source": "SCREEN_SHARE_AUDIO",
        "preset": "Audio preset enum value"
    }
}

```

Then create the ingress using `lk`:

```shell
lk ingress create ingress.json

```

---

**Node.js**:

```ts
import { IngressAudioOptions, IngressVideoOptions, LiveKitAPI } from 'livekit-server-sdk';
import {
  IngressAudioEncodingPreset,
  IngressInput,
  IngressVideoEncodingPreset,
  TrackSource,
} from '@livekit/protocol';

const api = new LiveKitAPI();

const ingress = {
  name: 'my-ingress',
  roomName: 'my-room',
  participantIdentity: 'my-participant',
  participantName: 'My Participant',
  video: new IngressVideoOptions({
    source: TrackSource.SCREEN_SHARE,
    encodingOptions: {
      case: 'preset',
      value: IngressVideoEncodingPreset.H264_1080P_30FPS_3_LAYERS,
    },
  }),
  audio: new IngressAudioOptions({
    source: TrackSource.SCREEN_SHARE_AUDIO,
    encodingOptions: {
      case: 'preset',
      value: IngressAudioEncodingPreset.OPUS_MONO_64KBS,
    },
  }),
};

await api.ingress.createIngress(IngressInput.RTMP_INPUT, ingress);

```

---

**Python**:

```python
from livekit import api

async with api.LiveKitAPI() as lkapi:
    info = await lkapi.ingress.create_ingress(
        api.CreateIngressRequest(
            input_type=api.IngressInput.RTMP_INPUT,
            name="my-ingress",
            room_name="my-room",
            participant_identity="my-participant",
            participant_name="My Participant",
            video=api.IngressVideoOptions(
                source=api.TrackSource.SCREEN_SHARE,
                preset=api.IngressVideoEncodingPreset.H264_1080P_30FPS_3_LAYERS,
            ),
            audio=api.IngressAudioOptions(
                source=api.TrackSource.SCREEN_SHARE_AUDIO,
                preset=api.IngressAudioEncodingPreset.OPUS_MONO_64KBS,
            ),
        )
    )
    print(info.ingress_id)

```

---

**Ruby**:

```ruby
require 'livekit'

lkapi = LiveKit::LiveKitAPI.new

video_options = LiveKit::Proto::IngressVideoOptions.new(
  name: "track name",
  source: :SCREEN_SHARE,
  preset: :H264_1080P_30FPS_3_LAYERS
)
audio_options = LiveKit::Proto::IngressAudioOptions.new(
  name: "track name",
  source: :SCREEN_SHARE_AUDIO,
  preset: :OPUS_STEREO_96KBPS
)
info = lkapi.ingress.create_ingress(:RTMP_INPUT,
  name: 'my-ingress',
  room_name: 'my-room',
  participant_identity: 'ingress',
  video: video_options,
  audio: audio_options,
)
puts info.ingress_id

```

---

**Go**:

```go
api, err := lksdk.NewLiveKitAPI()
if err != nil {
    panic(err)
}

ingressRequest := &livekit.CreateIngressRequest{
    Name:                "my-ingress",
    RoomName:            "my-room",
    ParticipantIdentity: "my-participant",
    ParticipantName:     "My Participant",
    Video: &livekit.IngressVideoOptions{
        EncodingOptions: &livekit.IngressVideoOptions_Preset{
            Preset: livekit.IngressVideoEncodingPreset_H264_1080P_30FPS_3_LAYERS,
        },
    },
    Audio: &livekit.IngressAudioOptions{
        EncodingOptions: &livekit.IngressAudioOptions_Preset{
            Preset: livekit.IngressAudioEncodingPreset_OPUS_MONO_64KBS,
        },
    },
}

info, err := api.Ingress().CreateIngress(ctx, ingressRequest)
ingressID := info.IngressId

```

---

**Kotlin**:

```kotlin
import io.livekit.server.LiveKitAPI
import livekit.LivekitIngress
import livekit.LivekitModels

val api = LiveKitAPI.createClient()

val videoOptions = LivekitIngress.IngressVideoOptions.newBuilder()
    .setSource(LivekitModels.TrackSource.SCREEN_SHARE)
    .setPreset(LivekitIngress.IngressVideoEncodingPreset.H264_1080P_30FPS_3_LAYERS)
    .build()
val audioOptions = LivekitIngress.IngressAudioOptions.newBuilder()
    .setSource(LivekitModels.TrackSource.SCREEN_SHARE_AUDIO)
    .setPreset(LivekitIngress.IngressAudioEncodingPreset.OPUS_MONO_64KBS)
    .build()

val info = api.ingress.createIngress(
    name = "my-ingress",
    roomName = "my-room",
    participantIdentity = "my-participant",
    participantName = "My Participant",
    inputType = LivekitIngress.IngressInput.RTMP_INPUT,
    videoOptions = videoOptions,
    audioOptions = audioOptions,
).execute().body()
val ingressId = info?.ingressId

```

---

**Rust**:

```rust
use livekit_api::services::ingress::CreateIngressOptions;
use livekit_api::services::LiveKitApi;
use livekit_protocol::{
    ingress_audio_options, ingress_video_options, IngressAudioEncodingPreset, IngressAudioOptions,
    IngressInput, IngressVideoEncodingPreset, IngressVideoOptions, TrackSource,
};

let api = LiveKitApi::new("https://my-livekit-host")?;
let info = api
    .ingress()
    .create_ingress(
        IngressInput::RtmpInput,
        CreateIngressOptions {
            name: "my-ingress".to_string(),
            room_name: "my-room".to_string(),
            participant_identity: "my-participant".to_string(),
            participant_name: "My Participant".to_string(),
            video: IngressVideoOptions {
                source: TrackSource::ScreenShare as i32,
                encoding_options: Some(ingress_video_options::EncodingOptions::Preset(
                    IngressVideoEncodingPreset::H2641080p30fps3Layers as i32,
                )),
                ..Default::default()
            },
            audio: IngressAudioOptions {
                source: TrackSource::ScreenShareAudio as i32,
                encoding_options: Some(ingress_audio_options::EncodingOptions::Preset(
                    IngressAudioEncodingPreset::OpusMono64kbs as i32,
                )),
                ..Default::default()
            },
            ..Default::default()
        },
    )
    .await?;
let ingress_id = info.ingress_id;

```

## Custom settings

For specialized use cases, it is also possible to specify fully custom encoding parameters. In this case, all video layers need to be defined if simulcast is desired.

**LiveKit CLI**:

Create a file at `ingress.json` with the following content:

```json
{
  "name": "Name of the egress goes here",
  "room_name": "Name of the room to connect to",
  "participant_identity": "Unique identity for the room participant the Ingress service will connect as",
  "participant_name": "Name displayed in the room for the participant",
  "video": {
    "options": {
"video_codec": "video codec ID from the [VideoCodec enum](https://github.com/livekit/protocol/blob/main/protobufs/livekit_models.proto)",
      "frame_rate": "desired framerate in frame per second",
      "layers": [
        {
          "quality": "ID for one of the LOW, MEDIUM or HIGH VideoQuality definitions",
          "width": "width of the layer in pixels",
          "height": "height of the layer in pixels",
          "bitrate": "video bitrate for the layer in bit per second"
        }
      ]
    }
  },
  "audio": {
    "options": {
"audio_codec": "audio codec ID from the [AudioCodec enum](https://github.com/livekit/protocol/blob/main/protobufs/livekit_models.proto)",
      "bitrate": "audio bitrate for the layer in bit per second",
      "channels": "audio channel count, 1 for mono, 2 for stereo",
      "disable_dtx": "whether to disable the [DTX feature](https://www.rfc-editor.org/rfc/rfc6716#section-2.1.9) for the OPUS codec"
    }
  }
}

```

Then create the ingress using `lk`:

```shell
lk ingress create ingress.json

```

---

**Node.js**:

```ts
import {
  IngressAudioOptions,
  IngressVideoOptions,
  IngressAudioEncodingOptions,
  IngressVideoEncodingOptions,
  LiveKitAPI,
} from 'livekit-server-sdk';
import { AudioCodec, IngressInput, TrackSource, VideoCodec, VideoQuality } from '@livekit/protocol';

const api = new LiveKitAPI();

const ingress = {
  name: 'my-ingress',
  roomName: 'my-room',
  participantIdentity: 'my-participant',
  participantName: 'My Participant',
  enableTranscoding: true,
  video: new IngressVideoOptions({
    name: 'my-video',
    source: TrackSource.CAMERA,
    encodingOptions: {
      case: 'options',
      value: new IngressVideoEncodingOptions({
        videoCodec: VideoCodec.H264_BASELINE,
        frameRate: 30,
        layers: [
          {
            quality: VideoQuality.HIGH,
            width: 1920,
            height: 1080,
            bitrate: 4500000,
          },
        ],
      }),
    },
  }),
  audio: new IngressAudioOptions({
    name: 'my-audio',
    source: TrackSource.MICROPHONE,
    encodingOptions: {
      case: 'options',
      value: new IngressAudioEncodingOptions({
        audioCodec: AudioCodec.OPUS,
        bitrate: 64000,
        channels: 1,
      }),
    },
  }),
};

await api.ingress.createIngress(IngressInput.RTMP_INPUT, ingress);

```

---

**Python**:

```python
from livekit import api

async with api.LiveKitAPI() as lkapi:
    info = await lkapi.ingress.create_ingress(
        api.CreateIngressRequest(
            input_type=api.IngressInput.RTMP_INPUT,
            name="my-ingress",
            room_name="my-room",
            participant_identity="my-participant",
            participant_name="My Participant",
            enable_transcoding=True,
            video=api.IngressVideoOptions(
                name="my-video",
                source=api.TrackSource.CAMERA,
                options=api.IngressVideoEncodingOptions(
                    video_codec=api.VideoCodec.H264_BASELINE,
                    frame_rate=30,
                    layers=[
                        api.VideoLayer(
                            quality=api.VideoQuality.HIGH,
                            width=1920,
                            height=1080,
                            bitrate=4_500_000,
                        ),
                    ],
                ),
            ),
            audio=api.IngressAudioOptions(
                name="my-audio",
                source=api.TrackSource.MICROPHONE,
                options=api.IngressAudioEncodingOptions(
                    audio_codec=api.AudioCodec.OPUS,
                    bitrate=64_000,
                    channels=1,
                ),
            ),
        )
    )
    print(info.ingress_id)

```

---

**Ruby**:

```ruby
require 'livekit'

lkapi = LiveKit::LiveKitAPI.new

video_encoding_opts = LiveKit::Proto::IngressVideoEncodingOptions.new(
  video_codec: :H264_BASELINE,
  frame_rate: 30,
)
# add layers as array
video_encoding_opts.layers += [
  LiveKit::Proto::VideoLayer.new(
    quality: :HIGH,
    width: 1920,
    height: 1080,
    bitrate: 4_500_000,
  )
]
video_options = LiveKit::Proto::IngressVideoOptions.new(
  name: "track name",
  source: :CAMERA,
  options: video_encoding_opts,
)
audio_options = LiveKit::Proto::IngressAudioOptions.new(
  name: "track name",
  source: :MICROPHONE,
  options: LiveKit::Proto::IngressAudioEncodingOptions.new(
    audio_codec: :OPUS,
    bitrate: 64000,
    channels: 1,
  )
)
info = lkapi.ingress.create_ingress(:RTMP_INPUT,
  name: 'my-ingress',
  room_name: 'my-room',
  participant_identity: 'ingress',
  enable_transcoding: true,
  video: video_options,
  audio: audio_options,
)
puts info.ingress_id

```

---

**Go**:

```go
api, err := lksdk.NewLiveKitAPI()
if err != nil {
    panic(err)
}

t := true
ingressRequest := &livekit.CreateIngressRequest{
    Name:                "my-ingress",
    RoomName:            "my-room",
    ParticipantIdentity: "my-participant",
    ParticipantName:     "My Participant",
    EnableTranscoding:   &t,
    Video: &livekit.IngressVideoOptions{
        EncodingOptions: &livekit.IngressVideoOptions_Options{
            Options: &livekit.IngressVideoEncodingOptions{
                VideoCodec: livekit.VideoCodec_H264_BASELINE,
                FrameRate:  30,
                Layers: []*livekit.VideoLayer{
                    {
                        Quality: livekit.VideoQuality_HIGH,
                        Width:   1920,
                        Height:  1080,
                        Bitrate: 4_500_000,
                    },
                },
            },
        },
    },
    Audio: &livekit.IngressAudioOptions{
        EncodingOptions: &livekit.IngressAudioOptions_Options{
            Options: &livekit.IngressAudioEncodingOptions{
                AudioCodec: livekit.AudioCodec_OPUS,
                Bitrate:    64_000,
                Channels:   1,
            },
        },
    },
}

info, err := api.Ingress().CreateIngress(ctx, ingressRequest)
ingressID := info.IngressId

```

---

**Kotlin**:

```kotlin
import io.livekit.server.LiveKitAPI
import livekit.LivekitIngress
import livekit.LivekitModels

val api = LiveKitAPI.createClient()

val videoOptions = LivekitIngress.IngressVideoOptions.newBuilder()
    .setName("my-video")
    .setSource(LivekitModels.TrackSource.CAMERA)
    .setOptions(
        LivekitIngress.IngressVideoEncodingOptions.newBuilder()
            .setVideoCodec(LivekitModels.VideoCodec.H264_BASELINE)
            .setFrameRate(30.0)
            .addLayers(
                LivekitModels.VideoLayer.newBuilder()
                    .setQuality(LivekitModels.VideoQuality.HIGH)
                    .setWidth(1920)
                    .setHeight(1080)
                    .setBitrate(4_500_000),
            ),
    )
    .build()
val audioOptions = LivekitIngress.IngressAudioOptions.newBuilder()
    .setName("my-audio")
    .setSource(LivekitModels.TrackSource.MICROPHONE)
    .setOptions(
        LivekitIngress.IngressAudioEncodingOptions.newBuilder()
            .setAudioCodec(LivekitModels.AudioCodec.OPUS)
            .setBitrate(64_000)
            .setChannels(1),
    )
    .build()

val info = api.ingress.createIngress(
    name = "my-ingress",
    roomName = "my-room",
    participantIdentity = "my-participant",
    participantName = "My Participant",
    inputType = LivekitIngress.IngressInput.RTMP_INPUT,
    enableTranscoding = true,
    videoOptions = videoOptions,
    audioOptions = audioOptions,
).execute().body()
val ingressId = info?.ingressId

```

---

**Rust**:

```rust
use livekit_api::services::ingress::CreateIngressOptions;
use livekit_api::services::LiveKitApi;
use livekit_protocol::{
    ingress_audio_options, ingress_video_options, AudioCodec, IngressAudioEncodingOptions,
    IngressAudioOptions, IngressInput, IngressVideoEncodingOptions, IngressVideoOptions,
    TrackSource, VideoCodec, VideoLayer, VideoQuality,
};

let api = LiveKitApi::new("https://my-livekit-host")?;
let info = api
    .ingress()
    .create_ingress(
        IngressInput::RtmpInput,
        CreateIngressOptions {
            name: "my-ingress".to_string(),
            room_name: "my-room".to_string(),
            participant_identity: "my-participant".to_string(),
            participant_name: "My Participant".to_string(),
            enable_transcoding: Some(true),
            video: IngressVideoOptions {
                name: "my-video".to_string(),
                source: TrackSource::Camera as i32,
                encoding_options: Some(ingress_video_options::EncodingOptions::Options(
                    IngressVideoEncodingOptions {
                        video_codec: VideoCodec::H264Baseline as i32,
                        frame_rate: 30.0,
                        layers: vec![VideoLayer {
                            quality: VideoQuality::High as i32,
                            width: 1920,
                            height: 1080,
                            bitrate: 4_500_000,
                            ..Default::default()
                        }],
                    },
                )),
            },
            audio: IngressAudioOptions {
                name: "my-audio".to_string(),
                source: TrackSource::Microphone as i32,
                encoding_options: Some(ingress_audio_options::EncodingOptions::Options(
                    IngressAudioEncodingOptions {
                        audio_codec: AudioCodec::Opus as i32,
                        bitrate: 64_000,
                        channels: 1,
                        ..Default::default()
                    },
                )),
            },
            ..Default::default()
        },
    )
    .await?;
let ingress_id = info.ingress_id;

```

## Enabling transcoding for WHIP sessions

By default, WHIP ingress sessions forward incoming audio and video media unmodified from the source to LiveKit clients. This behavior allows the lowest possible end to end latency between the media source and the viewers. This however requires the source encoder to be configured with settings that are compatible with all the subscribers, and ensure the right trade offs between quality and reach for clients with variable connection quality. This is best achieved when the source encoder is configured with simulcast enabled.

If the source encoder cannot be setup easily to achieve such tradeoffs, or if the available uplink bandwidth is insufficient to send all required simulcast layers, WHIP ingresses can be configured to transcode the source media similarly to other source types. This is done by setting the `enable_transcoding` option on the ingress. The encoder settings can then be configured in the `audio` and `video` settings in the same manner as for other inputs types.

**LiveKit CLI**:

Create a file at `ingress.json` with the following content:

```json
{
    "input_type": 1 (WHIP only)
    "name": "Name of the egress goes here",
    "room_name": "Name of the room to connect to",
    "participant_identity": "Unique identity for the room participant the Ingress service will connect as",
    "participant_name": "Name displayed in the room for the participant",
    "enable_transcoding": true
    "video": {
        "name": "track name",
        "source": "SCREEN_SHARE",
        "preset": "Video preset enum value"
    },
    "audio": {
        "name": "track name",
        "source": "SCREEN_SHARE_AUDIO",
        "preset": "Audio preset enum value"
    }
}

```

Then create the Ingress using `lk`:

```shell
lk ingress create ingress.json

```

---

**Node.js**:

```ts
import {
  IngressAudioOptions,
  IngressVideoOptions,
  IngressAudioEncodingOptions,
  IngressVideoEncodingOptions,
  LiveKitAPI,
} from 'livekit-server-sdk';
import { AudioCodec, IngressInput, TrackSource, VideoCodec, VideoQuality } from '@livekit/protocol';

const api = new LiveKitAPI();

const ingress = {
  name: 'my-ingress',
  roomName: 'my-room',
  participantIdentity: 'my-participant',
  participantName: 'My Participant',
  enableTranscoding: true,
  video: new IngressVideoOptions({
    source: TrackSource.SCREEN_SHARE,
    encodingOptions: {
      case: 'options',
      value: new IngressVideoEncodingOptions({
        videoCodec: VideoCodec.H264_BASELINE,
        frameRate: 30,
        layers: [
          {
            quality: VideoQuality.HIGH,
            width: 1920,
            height: 1080,
            bitrate: 4500000,
          },
        ],
      }),
    },
  }),
  audio: new IngressAudioOptions({
    source: TrackSource.MICROPHONE,
    encodingOptions: {
      case: 'options',
      value: new IngressAudioEncodingOptions({
        audioCodec: AudioCodec.OPUS,
        bitrate: 64000,
        channels: 1,
      }),
    },
  }),
};

await api.ingress.createIngress(IngressInput.WHIP_INPUT, ingress);

```

---

**Python**:

```python
from livekit import api

async with api.LiveKitAPI() as lkapi:
    info = await lkapi.ingress.create_ingress(
        api.CreateIngressRequest(
            input_type=api.IngressInput.WHIP_INPUT,
            name="my-ingress",
            room_name="my-room",
            participant_identity="my-participant",
            participant_name="My Participant",
            enable_transcoding=True,
            video=api.IngressVideoOptions(
                source=api.TrackSource.SCREEN_SHARE,
                options=api.IngressVideoEncodingOptions(
                    video_codec=api.VideoCodec.H264_BASELINE,
                    frame_rate=30,
                    layers=[
                        api.VideoLayer(
                            quality=api.VideoQuality.HIGH,
                            width=1920,
                            height=1080,
                            bitrate=4_500_000,
                        ),
                    ],
                ),
            ),
            audio=api.IngressAudioOptions(
                source=api.TrackSource.MICROPHONE,
                options=api.IngressAudioEncodingOptions(
                    audio_codec=api.AudioCodec.OPUS,
                    bitrate=64_000,
                    channels=1,
                ),
            ),
        )
    )
    print(info.ingress_id)

```

---

**Ruby**:

```ruby
require 'livekit'

lkapi = LiveKit::LiveKitAPI.new

video_encoding_opts = LiveKit::Proto::IngressVideoEncodingOptions.new(
  video_codec: :H264_BASELINE,
  frame_rate: 30,
)
# add layers as array
video_encoding_opts.layers += [
  LiveKit::Proto::VideoLayer.new(
    quality: :HIGH,
    width: 1920,
    height: 1080,
    bitrate: 4_500_000,
  )
]
video_options = LiveKit::Proto::IngressVideoOptions.new(
  name: "track name",
  source: :SCREEN_SHARE,
  options: video_encoding_opts,
)
audio_options = LiveKit::Proto::IngressAudioOptions.new(
  name: "track name",
  source: :MICROPHONE,
  options: LiveKit::Proto::IngressAudioEncodingOptions.new(
    audio_codec: :OPUS,
    bitrate: 64000,
    disable_dtx: true,
    channels: 1,
  )
)

info = lkapi.ingress.create_ingress(:WHIP_INPUT,
  name: 'my-ingress',
  room_name: 'my-room',
  participant_identity: 'ingress',
  enable_transcoding: true,
  video: video_options,
  audio: audio_options,
)
puts info.ingress_id

```

---

**Go**:

```go
api, err := lksdk.NewLiveKitAPI()
if err != nil {
    panic(err)
}

t := true
ingressRequest := &livekit.CreateIngressRequest{
    InputType:           livekit.IngressInput_WHIP_INPUT,
    Name:                "my-ingress",
    RoomName:            "my-room",
    ParticipantIdentity: "my-participant",
    ParticipantName:     "My Participant",
    EnableTranscoding:   &t,
    Video: &livekit.IngressVideoOptions{
        EncodingOptions: &livekit.IngressVideoOptions_Options{
            Options: &livekit.IngressVideoEncodingOptions{
                VideoCodec: livekit.VideoCodec_H264_BASELINE,
                FrameRate:  30,
                Layers: []*livekit.VideoLayer{
                    {
                        Quality: livekit.VideoQuality_HIGH,
                        Width:   1920,
                        Height:  1080,
                        Bitrate: 4_500_000,
                    },
                },
            },
        },
    },
    Audio: &livekit.IngressAudioOptions{
        EncodingOptions: &livekit.IngressAudioOptions_Options{
            Options: &livekit.IngressAudioEncodingOptions{
                AudioCodec: livekit.AudioCodec_OPUS,
                Bitrate:    64_000,
                Channels:   1,
            },
        },
    },
}

info, err := api.Ingress().CreateIngress(ctx, ingressRequest)
ingressID := info.IngressId

```

---

**Kotlin**:

```kotlin
import io.livekit.server.LiveKitAPI
import livekit.LivekitIngress
import livekit.LivekitModels

val api = LiveKitAPI.createClient()

val videoOptions = LivekitIngress.IngressVideoOptions.newBuilder()
    .setSource(LivekitModels.TrackSource.SCREEN_SHARE)
    .setOptions(
        LivekitIngress.IngressVideoEncodingOptions.newBuilder()
            .setVideoCodec(LivekitModels.VideoCodec.H264_BASELINE)
            .setFrameRate(30.0)
            .addLayers(
                LivekitModels.VideoLayer.newBuilder()
                    .setQuality(LivekitModels.VideoQuality.HIGH)
                    .setWidth(1920)
                    .setHeight(1080)
                    .setBitrate(4_500_000),
            ),
    )
    .build()
val audioOptions = LivekitIngress.IngressAudioOptions.newBuilder()
    .setSource(LivekitModels.TrackSource.MICROPHONE)
    .setOptions(
        LivekitIngress.IngressAudioEncodingOptions.newBuilder()
            .setAudioCodec(LivekitModels.AudioCodec.OPUS)
            .setBitrate(64_000)
            .setChannels(1),
    )
    .build()

val info = api.ingress.createIngress(
    name = "my-ingress",
    roomName = "my-room",
    participantIdentity = "my-participant",
    participantName = "My Participant",
    inputType = LivekitIngress.IngressInput.WHIP_INPUT,
    enableTranscoding = true,
    videoOptions = videoOptions,
    audioOptions = audioOptions,
).execute().body()
val ingressId = info?.ingressId

```

---

**Rust**:

```rust
use livekit_api::services::ingress::CreateIngressOptions;
use livekit_api::services::LiveKitApi;
use livekit_protocol::{
    ingress_audio_options, ingress_video_options, AudioCodec, IngressAudioEncodingOptions,
    IngressAudioOptions, IngressInput, IngressVideoEncodingOptions, IngressVideoOptions,
    TrackSource, VideoCodec, VideoLayer, VideoQuality,
};

let api = LiveKitApi::new("https://my-livekit-host")?;
let info = api
    .ingress()
    .create_ingress(
        IngressInput::WhipInput,
        CreateIngressOptions {
            name: "my-ingress".to_string(),
            room_name: "my-room".to_string(),
            participant_identity: "my-participant".to_string(),
            participant_name: "My Participant".to_string(),
            enable_transcoding: Some(true),
            video: IngressVideoOptions {
                source: TrackSource::ScreenShare as i32,
                encoding_options: Some(ingress_video_options::EncodingOptions::Options(
                    IngressVideoEncodingOptions {
                        video_codec: VideoCodec::H264Baseline as i32,
                        frame_rate: 30.0,
                        layers: vec![VideoLayer {
                            quality: VideoQuality::High as i32,
                            width: 1920,
                            height: 1080,
                            bitrate: 4_500_000,
                            ..Default::default()
                        }],
                    },
                )),
                ..Default::default()
            },
            audio: IngressAudioOptions {
                source: TrackSource::Microphone as i32,
                encoding_options: Some(ingress_audio_options::EncodingOptions::Options(
                    IngressAudioEncodingOptions {
                        audio_codec: AudioCodec::Opus as i32,
                        bitrate: 64_000,
                        channels: 1,
                        ..Default::default()
                    },
                )),
                ..Default::default()
            },
            ..Default::default()
        },
    )
    .await?;
let ingress_id = info.ingress_id;

```

---

This document was rendered at 2026-08-24T21:31:31.482Z.
For the latest version of this document, see [https://docs.livekit.io/transport/media/ingress-egress/ingress/transcode.md](https://docs.livekit.io/transport/media/ingress-egress/ingress/transcode.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).
