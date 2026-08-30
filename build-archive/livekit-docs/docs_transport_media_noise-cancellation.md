warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /transport/media/noise-cancellation

LiveKit docs › WebRTC Transport › Media › Noise & echo cancellation

---

# Noise & echo cancellation

> Achieve crystal-clear audio for video conferencing and voice AI.

## Overview

User microphones can capture unwanted audio such as background noise (traffic, music) and even echoes from their own speakers. This degrades the experience for other participants in a call. In voice AI apps, it can also interfere with turn detection and reduce transcription quality.

**LiveKit Cloud** includes access to advanced noise cancellation models (Krisp and ai-coustics) so agents receive crystal-clear audio. Audio sent through LiveKit Cloud can use these models regardless of where your agent runs. See [Agents](#agents) for setup. For pricing details, see the [AI voice and video agents](https://livekit.com/pricing#agents) and [Media transport](https://livekit.com/pricing#media-transport) sections of the pricing page.

**LiveKit SDKs** support WebRTC noise and echo cancellation for conferencing apps via [`echoCancellation`](https://developer.mozilla.org/en-US/docs/Web/API/MediaTrackSettings/echoCancellation) and [`noiseSuppression`](https://developer.mozilla.org/en-US/docs/Web/API/MediaTrackSettings/noiseSuppression) in any deployment. WebRTC cancellation runs in the client only, so it applies to conferencing. For agents and telephony (where there is no browser frontend), use the LiveKit Cloud models above. Adjust WebRTC settings with the `AudioCaptureOptions` type during connection. See [WebRTC noise and echo cancellation](#webrtc-noise-and-echo-cancellation) in the Frontend section for more information.

To hear the effect of enhanced noise cancellation, play the samples below:

**Audio comparison** (audio-only, not available in text):

- Original
- [LiveKit Cloud enhanced (Krisp)](/transport/media/noise-cancellation#agents)

## Agents

Enhanced noise cancellation is available when you use LiveKit Cloud for realtime transport. This applies noise cancellation to inbound audio and is the recommended approach for most voice AI use cases. There are two types of noise cancellation:

- [Voice isolation](#agents-voice-isolation): Emphasizes the primary speaker and reduces competing speech or noise.
- [Background noise suppression](#agents-background-noise-suppression): Reduces non-speech noise like traffic, fans, and music.

Voice isolation works well when there is a single speaker, while background noise suppression is better for multiple speakers and [diarization](https://docs.livekit.io/agents/models/stt.md#speaker-diarization). LiveKit supports two providers for enhanced noise cancellation: Krisp and ai-coustics.

> 💡 **Tip**
> 
> The ai-coustics plugin is built for use in the Python and Node.js agents SDK only, and is not supported on clients for video conferencing.

Try the free [noise canceller tool](https://github.com/livekit-examples/noise-canceller) with your LiveKit Cloud account to test your own audio samples.

> 💡 **Tip**
> 
> When using noise or background voice cancellation in the agent code, do not enable noise cancellation models in the frontend. Noise cancellation models are trained on raw audio and might produce unexpected results if the input has already been processed by a noise cancellation model in the frontend.
> 
> Standard noise cancellation and the separate echo cancellation feature can be left enabled.

### Installation

Install the package for your chosen provider (Krisp or ai-coustics):

**Python**:

```shell
# Krisp voice isolation (VIVA)
uv add "livekit-plugins-krisp"

# Krisp background noise suppression (NC)
uv add "livekit-plugins-noise-cancellation~=0.2"

# ai-coustics
uv add "livekit-plugins-ai-coustics"

```

---

**Node.js**:

```shell
# Krisp voice isolation (VIVA)
pnpm add @livekit/agents-plugin-krisp

# Krisp background noise suppression (NC)
pnpm add @livekit/noise-cancellation-node

# ai-coustics
pnpm add @livekit/plugins-ai-coustics

```

### Voice isolation

Voice isolation emphasizes the primary speaker and suppresses competing speech and background noise. It improves clarity for the agent when multiple people or noise are present.

#### Available models

All voice isolation models incur an additional cost. See the [Voice isolation row](https://livekit.com/pricing#speaker-isolation) on the pricing page for details.

| Model | Additional cost | Description |
| Krisp VIVA | [Yes](https://livekit.com/pricing#speaker-isolation) | Removes competing voices and background noise, emphasizing the primary speaker. Optimized for single-speaker scenarios where cross-talk from nearby people could confuse transcriptions or turn detection. Exposes a [runtime-adjustable noise suppression level](#noise-suppression-level). In Python, use `krisp.voice_isolation()`, and in Node.js, `krisp.voiceIsolation()`. |
| Krisp VIVA (telephony) | [Yes](https://livekit.com/pricing#speaker-isolation) | Voice isolation tuned for telephony audio. Use for SIP participants. In Python, use `krisp.voice_isolation_telephony()` or a [selector](#selectors) to apply the telephony variant per participant. In Node.js, use `krisp.voiceIsolationTelephony()`. |
| ai-coustics Voice Focus 2.1 S (QUAIL_VF_S) | [Yes](https://livekit.com/pricing#speaker-isolation) | Voice Focus mode with realtime audio enhancement and speaker isolation. Optimized for agent pipelines to improve STT accuracy and turn detection, and tuned for near-field microphones such as headsets or earbuds where the speaker's voice is the dominant signal. Lightweight variant for compute-constrained deployments. |
| ai-coustics Voice Focus 2.1 L (QUAIL_VF_L) | [Yes](https://livekit.com/pricing#speaker-isolation) | Voice Focus mode with realtime audio enhancement and speaker isolation. Optimized for agent pipelines to improve STT accuracy and turn detection, and tuned for near-field microphones such as headsets or earbuds where the speaker's voice is the dominant signal. More compute-intensive variant. |

Listen to the same gym membership sample with original audio, Krisp VIVA, and ai-coustics Voice Focus 2.1 (S and L). Transcripts are from [Deepgram Nova 3](https://docs.livekit.io/agents/models/stt/deepgram.md). Segments marked with a strikethrough indicate unwanted content that would confuse the agent.

**Audio comparison:**

- Original: [Can I get you the] How peaceful [Okay? Did you catch the halftime show? I think about that it was a Spanish] Yes. I've just received an email that my gym membership is canceled.
- Krisp VIVA: How peaceful. Okay. Yes. I've just received an email that my gym membership is canceled.
- ai-coustics Voice Focus 2.1 S (QUAIL_VF_S): How peaceful. Okay. I've just received an email that my gym membership is canceled.
- ai-coustics Voice Focus 2.1 L (QUAIL_VF_L): How peaceful Okay. Yes. I just received an email that my gym membership is canceled.

The following table compares word error rate (WER) for the original audio and each model. WER is the percentage of errors (insertions, deletions, and substitutions) relative to the total words in a reference transcript:

| Model | WER |
| Original | 117.6% |
| Krisp VIVA | 11.8% |
| ai-coustics Voice Focus 2.1 S (QUAIL_VF_S) | 7.1% |
| ai-coustics Voice Focus 2.1 L (QUAIL_VF_L) | 14.3% |

#### Basic implementation

Include the filter in the room input options when starting your agent session:

**Python**:

```python
from livekit.agents import room_io
from livekit.plugins import ai_coustics  # or krisp

# ...
await session.start(
    # ...,
    room_options=room_io.RoomOptions(
        audio_input=room_io.AudioInputOptions(
            noise_cancellation=ai_coustics.audio_enhancement(model=ai_coustics.EnhancerModel.QUAIL_VF_S),
            # or ai_coustics.audio_enhancement(model=ai_coustics.EnhancerModel.QUAIL_VF_L)
            # or krisp.voice_isolation()
            # or krisp.voice_isolation_telephony()  # tuned for SIP participants
        ),
    ),
)
# ...

```

---

**Node.js**:

```typescript
import * as aiCoustics from '@livekit/plugins-ai-coustics';
// import * as krisp from '@livekit/agents-plugin-krisp';

// ...
await session.start({
  // ...,
  inputOptions: {
    noiseCancellation: aiCoustics.audioEnhancement({ model: 'quailVfS' }),
    // or aiCoustics.audioEnhancement({ model: 'quailVfL' })
    // or krisp.voiceIsolation()
    // or krisp.voiceIsolationTelephony() // tuned for SIP participants
  },
});
// ...

```

#### Custom implementation

Use this when you create an `AudioStream` from a track yourself. Apply the filter when constructing the stream so that the frames you read are already filtered:

**Python**:

```python
from livekit.rtc import AudioStream
from livekit.plugins import ai_coustics  # or krisp

stream = AudioStream.from_track(
    track=track,
    noise_cancellation=ai_coustics.audio_enhancement(model=ai_coustics.EnhancerModel.QUAIL_VF_S),
    # or ai_coustics.audio_enhancement(model=ai_coustics.EnhancerModel.QUAIL_VF_L)
    # or krisp.voice_isolation()
    # or krisp.voice_isolation_telephony()  # tuned for SIP participants
)

```

---

**Node.js**:

```typescript
import { AudioStream } from '@livekit/rtc-node';
import * as aiCoustics from '@livekit/plugins-ai-coustics';
// import * as krisp from '@livekit/agents-plugin-krisp';

const stream = new AudioStream(track, {
  noiseCancellation: aiCoustics.audioEnhancement({ model: 'quailVfS' }),
  // or aiCoustics.audioEnhancement({ model: 'quailVfL' })
  // or krisp.voiceIsolation()
  // or krisp.voiceIsolationTelephony()  // tuned for SIP participants
});

```

### Background noise suppression

Background noise suppression reduces non-speech noise such as traffic, fans, and music. Use it when the main challenge is environmental noise rather than competing speakers. For voice removal, see [Voice isolation](#agents-voice-isolation).

#### Available models

Background noise suppression models are included with LiveKit Cloud. See the [Background noise suppression row](https://livekit.com/pricing#audio-enhancement) on the pricing page for details.

| Model | Additional cost | Description |
| Krisp NC | None | Removes environmental background noise such as traffic, fans, and music while preserving all speech. |
| ai-coustics QUAIL_L | None | Machine-optimized audio enhancement for agent performance. |

Listen to the same gym membership sample with original audio, Krisp NC, and ai-coustics Quail (QUAIL_L). Transcripts are from [Deepgram Nova 3](https://docs.livekit.io/agents/models/stt/deepgram.md). Segments marked with a strikethrough indicate unwanted content that would confuse the agent.

**Audio comparison:**

- Original: [Can I get you the] How peaceful [Okay? Did you catch the halftime show? I think about that it was a Spanish] Yes. I've just received an email that my gym membership is canceled.
- Krisp NC: [Oh,] peaceful. Okay. [That's an off time show? I just] received an email that my gym membership is canceled.
- ai-coustics Quail (QUAIL_L): How peaceful? [Okay. I buy that with] Yes. I've just received an email that my gym membership is canceled.

#### Basic implementation

Include the filter in the room input options when starting your agent session:

**Python**:

```python
from livekit.agents import room_io
from livekit.plugins import ai_coustics  # or noise_cancellation

# ...
await session.start(
    # ...,
    room_options=room_io.RoomOptions(
        audio_input=room_io.AudioInputOptions(
            noise_cancellation=ai_coustics.audio_enhancement(model=ai_coustics.EnhancerModel.QUAIL_L),
            # or noise_cancellation.NC()
        ),
    ),
)
# ...

```

---

**Node.js**:

```typescript
import * as aiCoustics from '@livekit/plugins-ai-coustics';
// or NoiseCancellation from '@livekit/noise-cancellation-node'

// ...
await session.start({
  // ...,
  inputOptions: {
    noiseCancellation: aiCoustics.audioEnhancement({ model: 'quailL' }),
  },
});
// ...

```

#### Custom implementation

Use this when you create an `AudioStream` from a track yourself. Apply the filter when constructing the stream so that the frames you read are already filtered:

**Python**:

```python
from livekit.rtc import AudioStream
from livekit.plugins import ai_coustics  # or noise_cancellation

stream = AudioStream.from_track(
    track=track,
    noise_cancellation=ai_coustics.audio_enhancement(model=ai_coustics.EnhancerModel.QUAIL_L),
    # or noise_cancellation.NC()
)

```

---

**Node.js**:

```typescript
import { AudioStream } from '@livekit/rtc-node';
import * as aiCoustics from '@livekit/plugins-ai-coustics';
// or NoiseCancellation from '@livekit/noise-cancellation-node'

const stream = new AudioStream(track, {
  noiseCancellation: aiCoustics.audioEnhancement({ model: 'quailL' }),
});

```

### Additional options

The following options apply on top of the voice isolation or background noise suppression setup above.

#### Selectors

Available in:
- [ ] Node.js
- [x] Python

When you pass a fixed model, every participant in the session receives the same noise cancellation. A selector lets the SDK call your function for each new participant and track, so different participants can receive different models in the same session without additional routing logic.

The following example applies ai-coustics enhancement to human participants and skips it for other agents in the room.

```python
from livekit import rtc
from livekit.plugins import ai_coustics

# Pass as the noise_cancellation argument in AudioInputOptions:
noise_cancellation=lambda params: None
    if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_AGENT
    else ai_coustics.audio_enhancement(
        model=ai_coustics.EnhancerModel.QUAIL_L
    ),

```

#### Noise suppression level (Krisp)

The Krisp VIVA plugin exposes a noise suppression level parameter (`noise_suppression_level` in Python, `noiseSuppressionLevel` in Node.js) that controls how aggressively the model reduces noise. The value ranges from `0` (minimal processing) to `100` (maximum suppression). When omitted, it defaults to `75`.

You can adjust the level after the processor starts. This is useful for responding to changes in the conversation, such as raising it when background noise increases. In Python, set the `noise_suppression_level` property, and in Node.js, call `setNoiseSuppressionLevel`:

**Python**:

```python
from livekit.plugins import krisp

processor = krisp.voice_isolation()

# ...

processor.noise_suppression_level = 100

```

---

**Node.js**:

```typescript
import * as krisp from '@livekit/agents-plugin-krisp';

const noiseCancellation = krisp.voiceIsolation();

// ...

noiseCancellation.setNoiseSuppressionLevel(100);

```

#### Enhancement level (ai-coustics)

The ai-coustics plugin exposes an enhancement level parameter (`enhancement_level` in Python, `enhancementLevel` in Node.js) to control how aggressively the model processes audio. The value ranges from `0.0` (minimal processing) to `1.0` (maximum enhancement). When omitted, the model applies its built-in default.

The ai-coustics audio samples on this page use an enhancement level of 0.8.

**Python**:

```python
from livekit.plugins import ai_coustics

ai_coustics.audio_enhancement(
    model=ai_coustics.EnhancerModel.QUAIL_L,
    model_parameters=ai_coustics.ModelParameters(
        enhancement_level=0.8,
    ),
)

```

---

**Node.js**:

```typescript
import * as aiCoustics from '@livekit/plugins-ai-coustics';

aiCoustics.audioEnhancement({
  model: 'quailL',
  modelParameters: {
    enhancementLevel: 0.8,
  },
})

```

You can also adjust the enhancement level after the plugin starts by calling `update_model_parameters` (Python) or `updateModelParameters` (Node.js) on the plugin instance. This is useful when you want to respond to changes in the conversation, such as raising the level when background noise increases.

**Python**:

```python
aic.update_model_parameters(ai_coustics.ModelParameters(enhancement_level=1.0))

```

---

**Node.js**:

```typescript
aic.updateModelParameters({ enhancementLevel: 1.0 });

```

#### VAD adapter (ai-coustics)

The ai-coustics plugin includes a built-in VAD adapter for turn detection. Because VAD runs inside the ai-coustics model, you can skip running a separate VAD (such as Silero) entirely. Pass `VAD()` to `AgentSession` and the noise cancellation filter in `room_options` (Python) or `inputOptions` (Node.js) when calling `session.start()`:

**Python**:

```python
from livekit.agents import AgentSession, room_io
from livekit.plugins.ai_coustics import audio_enhancement, VAD, EnhancerModel

session = AgentSession(
    vad=VAD(),
    # ...
)

await session.start(
    # ...,
    room_options=room_io.RoomOptions(
        audio_input=room_io.AudioInputOptions(
            noise_cancellation=audio_enhancement(model=EnhancerModel.QUAIL_L),
        ),
    ),
)

```

---

**Node.js**:

```typescript
import { voice } from '@livekit/agents';
import * as aic from '@livekit/plugins-ai-coustics';

const session = new voice.AgentSession({
  vad: aic.vad(),
  // ...
});

await session.start({
  // ...,
  inputOptions: {
    noiseCancellation: aic.audioEnhancement(),
  },
});

```

#### Self-hosted authentication (ai-coustics)

By default the ai-coustics plugin authenticates and meters usage through LiveKit Cloud. If you self-host your SFU instead of using LiveKit Cloud, you can authenticate directly against ai-coustics by passing your own license key with the `auth` parameter. Usage is then billed by ai-coustics, not LiveKit. Generate an ai-coustics API key at [developers.ai-coustics.io](https://developers.ai-coustics.io).

**Python**:

```python
import os
from livekit.plugins.ai_coustics import audio_enhancement, Auth, EnhancerModel

audio_enhancement(
    model=EnhancerModel.QUAIL_VF_S,
    auth=Auth.ai_coustics_api(
        license_key=os.environ["AI_COUSTICS_API_KEY"],
    ),
)

```

---

**Node.js**:

```typescript
import { Auth, audioEnhancement } from '@livekit/plugins-ai-coustics';

audioEnhancement({
  model: 'quailVfS',
  auth: Auth.aiCousticsApi(process.env.AI_COUSTICS_API_KEY!),
});

```

## Telephony

Krisp noise cancellation can be applied directly at your SIP trunk for inbound or outbound calls. This uses the standard Krisp noise cancellation (NC) model. Other models are not available for SIP.

> 💡 **Tip**
> 
> If a LiveKit Agent handles the call, we recommend applying noise cancellation on the [agent](#agents) instead of the SIP trunk. Agent-side cancellation gives you access to more models—including Krisp's enhanced models and [ai-coustics](#agents)—and keeps noise cancellation configuration alongside your agent logic.

### Inbound

Include `krisp_enabled: true` in the inbound trunk configuration.

```json
{
  "trunk": {
    "name": "My trunk",
    "numbers": ["+15105550100"],
    "krisp_enabled": true
  }
}

```

See the full [inbound trunk docs](https://docs.livekit.io/telephony/accepting-calls/inbound-trunk.md) for more information.

### Outbound

Include `krisp_enabled: true` in the [`CreateSipParticipant`](https://docs.livekit.io/reference/telephony/sip-api.md#createsipparticipant) request.

```python
request = CreateSIPParticipantRequest(
  sip_trunk_id = "<trunk_id>",
  sip_call_to = "<phone_number>",
  room_name = "my-sip-room",
  participant_identity = "sip-test",
  participant_name = "Test Caller",
  krisp_enabled = True,
  wait_until_answered = True
)

```

See the full [outbound call docs](https://docs.livekit.io/telephony/making-calls.md) for more information.

## Frontend

Noise cancellation in the frontend applies to outbound audio before it is sent to the room.

### Krisp

The following examples show how to set up noise cancellation in the frontend using Krisp. This applies noise cancellation to outbound audio. The BVC model is available in the JavaScript frontend; other frontend SDKs support the NC model only.

| Platform | Outbound | BVC | Package |
| Web | ✅ | ✅ | [@livekit/krisp-noise-filter](https://www.npmjs.com/package/@livekit/krisp-noise-filter) |
| Swift | ✅ | ❌ | [LiveKitKrispNoiseFilter](https://github.com/livekit/swift-krisp-noise-filter) |
| Android | ✅ | ❌ | [io.livekit:krisp-noise-filter](https://central.sonatype.com/artifact/io.livekit/krisp-noise-filter) |
| Flutter | ✅ | ❌ | [livekit_noise_filter](https://pub.dev/packages/livekit_noise_filter) |
| React Native | ✅ | ❌ | [@livekit/react-native-krisp-noise-filter](https://www.npmjs.com/package/@livekit/react-native-krisp-noise-filter) |
| Unity | ❌ | ❌ | N/A |

> 💡 **Tip**
> 
> When using noise or background voice cancellation in the frontend, do not enable Krisp noise cancellation in the agent code. Standard noise cancellation and the separate echo cancellation feature can be left enabled.

**JavaScript**:

#### Installation

```shell
npm install @livekit/krisp-noise-filter

```

This package includes the Krisp SDK but not the models, which download at runtime to minimize the impact on your application's bundle size.

#### React components usage

LiveKit Components includes a convenient [`useKrispNoiseFilter`](https://docs.livekit.io/reference/components/react/hook/usekrispnoisefilter.md) hook to easily integrate Krisp into your React app:

```tsx
import { useKrispNoiseFilter } from '@livekit/components-react/krisp';

function MyKrispSetting() {
  const krisp = useKrispNoiseFilter();
  return (
    <input
      type="checkbox"
      onChange={(ev) => krisp.setNoiseFilterEnabled(ev.target.checked)}
      checked={krisp.isNoiseFilterEnabled}
      disabled={krisp.isNoiseFilterPending}
    />
  );
}

```

#### Base JS SDK usage

For other frameworks or advanced use cases, use the `KrispNoiseFilter` class directly:

```ts
import { type LocalAudioTrack, Room, RoomEvent, Track } from 'livekit-client';

const room = new Room();

// We recommend a dynamic import to only load the required resources when you enable the plugin
const { KrispNoiseFilter } = await import('@livekit/krisp-noise-filter');

room.on(RoomEvent.LocalTrackPublished, async (trackPublication) => {
  if (
    trackPublication.source === Track.Source.Microphone &&
    trackPublication.track instanceof LocalAudioTrack
  ) {
    if (!isKrispNoiseFilterSupported()) {
      console.warn('Krisp noise filter is currently not supported on this browser');
      return;
    }
    // Once instantiated, the filter will begin initializing and will download additional resources
    const krispProcessor = KrispNoiseFilter();
    console.log('Enabling LiveKit Krisp noise filter');
    await trackPublication.track.setProcessor(krispProcessor);

    // To enable/disable the noise filter, use setEnabled()
    await krispProcessor.setEnabled(true);

    // To check the current status use:
    // krispProcessor.isEnabled()

    // To stop and dispose of the Krisp processor, simply call:
    // await trackPublication.track.stopProcessor()
  }
});

```

#### Available models

The JavaScript noise filter supports the standard Krisp noise cancellation (NC) and background voice cancellation (BVC) models.

#### Compatibility

Not all browsers support the underlying Krisp SDK (including Safari <`17.4`). Use `isKrispNoiseFilterSupported()` to check if the current browser is supported.

---

**Android**:

#### Installation

Add the package to your `build.gradle` file:

```groovy
dependencies {
  implementation "io.livekit:krisp-noise-filter:0.0.10"
}

```

Get the latest SDK version number from [Maven Central](https://central.sonatype.com/artifact/io.livekit/krisp-noise-filter).

#### Usage

```kotlin
val krisp = KrispAudioProcessor.getInstance(getApplication())

coroutineScope.launch(Dispatchers.IO) {
    // Only needs to be done once.
    // This should be executed on the background thread to avoid UI freezes.
    krisp.init()
}

// Pass the KrispAudioProcessor into the Room creation
room = LiveKit.create(
    getApplication(),
    overrides = LiveKitOverrides(
        audioOptions = AudioOptions(
            audioProcessorOptions = AudioProcessorOptions(
                capturePostProcessor = krisp,
            )
        ),
    ),
)

// Or to set after Room creation
room.audioProcessingController.setCapturePostProcessing(krisp)

```

#### Available models

The Android noise filter supports only the standard Krisp noise cancellation (NC) model.

---

**Swift**:

#### Installation

Add a new [package dependency](https://developer.apple.com/documentation/xcode/adding-package-dependencies-to-your-app) to your app by URL:

```
https://github.com/livekit/swift-krisp-noise-filter

```

Or in your `Package.swift` file:

```swift
.package(url: "https://github.com/livekit/swift-krisp-noise-filter.git", from: "0.0.7"),

```

#### Usage

Here is a simple example of a SwiftUI app that uses Krisp in its root view:

```swift
import LiveKit
import SwiftUI
import LiveKitKrispNoiseFilter

// Keep this as a global variable or somewhere that won't be deallocated
let krispProcessor = LiveKitKrispNoiseFilter()

struct ContentView: View {
    @StateObject private var room = Room()

    var body: some View {
        MyOtherView()
        .environmentObject(room)
        .onAppear {
            // Attach the processor
            AudioManager.shared.capturePostProcessingDelegate = krispProcessor
            // This must be done before calling `room.connect()`
            room.add(delegate: krispProcessor)

            // You are now ready to connect to the room from this view or any child view
        }
    }
}

```

For a complete example, view the [Krisp sample project](https://github.com/livekit-examples/swift-example-collection/tree/main/krisp-minimal).

#### Available models

The Swift noise filter supports only the standard Krisp noise cancellation (NC) model.

#### Compatibility

- The Krisp SDK requires iOS 13+ or macOS 10.15+.
- If your app also targets visionOS or tvOS, you'll need to wrap your Krisp code in `#if os(iOS) || os(macOS)` and [add a filter to the library linking step in Xcode](https://developer.apple.com/documentation/xcode/customizing-the-build-phases-of-a-target#Link-against-additional-frameworks-and-libraries).

---

**React Native**:

#### Installation

```shell
npm install @livekit/react-native-krisp-noise-filter

```

This package includes both the Krisp SDK and the required models.

#### Usage

```tsx
import { KrispNoiseFilter } from '@livekit/react-native-krisp-noise-filter';
import { useLocalParticipant } from '@livekit/components-react';
import { useMemo, useEffect } from 'react';

function MyComponent() {
  let { microphoneTrack } = useLocalParticipant();
  const krisp = useMemo(() => KrispNoiseFilter(), []);

  useEffect(() => {
    const localAudioTrack = microphoneTrack?.audioTrack;
    if (!localAudioTrack) {
      return;
    }
    localAudioTrack?.setProcessor(krisp);
  }, [microphoneTrack, krisp]);
}

```

#### Available models

The React Native noise filter supports only the standard Krisp noise cancellation (NC) model.

---

**Flutter**:

#### Installation

Add the package to your `pubspec.yaml` file:

```yaml
dependencies:
  livekit_noise_filter: ^0.1.0

```

#### Usage

```dart
import 'package:livekit_client/livekit_client.dart';
import 'package:livekit_noise_filter/livekit_noise_filter.dart';

// Create the noise filter instance
final liveKitNoiseFilter = LiveKitNoiseFilter();

// Configure room with the noise filter
final room = Room(
  roomOptions: RoomOptions(
    defaultAudioCaptureOptions: AudioCaptureOptions(
      processor: liveKitNoiseFilter,
    ),
  ),
);

// Connect to room and enable microphone
await room.connect(url, token);
await room.localParticipant?.setMicrophoneEnabled(true);

// You can also enable/disable the filter at runtime
// liveKitNoiseFilter.setBypass(true);  // Disables noise cancellation
// liveKitNoiseFilter.setBypass(false); // Enables noise cancellation

```

#### Available models

The Flutter noise filter supports only the standard Krisp noise cancellation (NC) model.

#### Compatibility

The Flutter noise filter is currently supported only on iOS, macOS, and Android platforms.

### WebRTC noise and echo cancellation

As an alternative to Krisp, the LiveKit SDKs support built-in outbound noise and echo cancellation based on the WebRTC implementations of [`echoCancellation`](https://developer.mozilla.org/en-US/docs/Web/API/MediaTrackSettings/echoCancellation) and [`noiseSuppression`](https://developer.mozilla.org/en-US/docs/Web/API/MediaTrackSettings/noiseSuppression). You can adjust these settings with the `AudioCaptureOptions` type in the LiveKit SDKs during connection. Leaving these WebRTC settings on is strongly recommended when you are not using enhanced noise cancellation (Krisp or ai-coustics).

**Audio comparison** (audio-only, not available in text):

- Original
- WebRTC noiseSuppression

---

This document was rendered at 2026-08-24T21:31:38.382Z.
For the latest version of this document, see [https://docs.livekit.io/transport/media/noise-cancellation.md](https://docs.livekit.io/transport/media/noise-cancellation.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).
