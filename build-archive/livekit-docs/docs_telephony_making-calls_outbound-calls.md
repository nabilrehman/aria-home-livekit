warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /telephony/making-calls/outbound-calls

LiveKit docs › Telephony › Making calls › Outbound calls

---

# Make outbound calls

> Create a LiveKit SIP participant to make outbound calls.

## Overview

Make outbound calls from LiveKit rooms to phone numbers by creating SIP participants. When you create a SIP participant, LiveKit uses an outbound trunk to initiate a call to the specified phone number and connects the callee to the room as a SIP participant. Once connected, the callee can interact with other participants in the room, including AI agents and regular participants.

You can configure the trunk in two ways:

- **Inline trunk configuration:** Pass trunk settings directly in the `CreateSIPParticipant` request.
- **Stored outbound trunk:** [Create an outbound trunk](https://docs.livekit.io/telephony/making-calls/outbound-trunk.md) ahead of time and reference it by ID.

You can customize outbound calls with features like custom caller ID, DTMF tones for extension codes, and dial tone playback while the call connects.

To create an AI agent to make outbound calls on your behalf, see the [Voice AI quickstart](https://docs.livekit.io/agents/start/voice-ai.md).

## Creating a SIP participant

To make outbound calls with SIP Service, create a SIP participant with the [`CreateSIPParticipant`](https://docs.livekit.io/reference/telephony/sip-api.md#createsipparticipant) API. It returns an `SIPParticipantInfo` object that describes the participant.

### Inline trunk configuration

Use inline configuration when each call needs different trunk settings, for example with multi-tenant platforms that have a separate SIP provider per customer or when routing to arbitrary SIP endpoints. Pass the trunk configuration directly in the `CreateSIPParticipant` request using the `trunk` parameter.

When using inline trunk configuration, set the following required parameters:

- `trunk.hostname`: SIP provider hostname or IP address (for example, `<my-trunk>.pstn.twilio.com`, `sip.telnyx.com`, or `<trunk-id>.zt.plivo.com`).
- `sip_number`: The phone number to call from. This is required because inline trunk configuration has no `numbers[]` field to pick a default from.

For a full list of trunk configuration fields, see [`SIPOutboundConfig`](https://docs.livekit.io/reference/telephony/sip-api.md#sipoutboundconfig).

**LiveKit CLI**:

1. Create a `sip-participant.json` file with the following participant details:

```json
{
  "trunk": {
    "hostname": "<SIP server>",
    "destination_country": "US",
    "auth_username": "<username>",
    "auth_password": "<password>"
  },
  "sip_number": "<SIP provider number>",
  "sip_call_to": "<phone-number-to-dial>",
  "room_name": "my-sip-room",
  "participant_identity": "sip-test",
  "participant_name": "Test Caller",
  "wait_until_answered": true
}

```
2. Create the SIP participant using the CLI:

```shell
lk sip participant create sip-participant.json

```

---

**Node.js**:

```typescript
import { LiveKitAPI } from 'livekit-server-sdk';
import { SIPOutboundConfig } from '@livekit/protocol';

const api = new LiveKitAPI({
  host: process.env.LIVEKIT_URL,
  apiKey: process.env.LIVEKIT_API_KEY,
  secret: process.env.LIVEKIT_API_SECRET,
});

const trunkConfig = new SIPOutboundConfig({
  hostname: process.env.SIP_TRUNK_HOSTNAME, // For example, <my-trunk>.pstn.twilio.com or <trunk-id>.zt.plivo.com
  destinationCountry: 'US',
  authUsername: process.env.SIP_AUTH_USERNAME,
  authPassword: process.env.SIP_AUTH_PASSWORD,
});

const participant = await api.sip.createSipParticipant(
  '', // Empty string when using inline trunk config
  '<phone-number-to-dial>',
  'my-sip-room',
  {
    participantIdentity: 'sip-test',
    participantName: 'Test Caller',
    fromNumber: '<SIP provider number>', // Required when using inline trunk config
    waitUntilAnswered: true,
  },
  trunkConfig, // SIPOutboundConfig as 5th parameter
);

```

---

**Python**:

```python
import asyncio
import os

from livekit import api
from livekit.protocol.sip import CreateSIPParticipantRequest, SIPOutboundConfig

async def main():
    livekit_api = api.LiveKitAPI()

    trunk_config = SIPOutboundConfig(
        hostname=os.getenv("SIP_TRUNK_HOSTNAME"), # For example, <my-trunk>.pstn.twilio.com, sip.telnyx.com, or <trunk-id>.zt.plivo.com
        destination_country="US",
        auth_username=os.getenv("SIP_AUTH_USERNAME"),
        auth_password=os.getenv("SIP_AUTH_PASSWORD"),
    )

    request = CreateSIPParticipantRequest(
        trunk=trunk_config,
        sip_number="<SIP provider number>", # Required when using inline trunk config
        sip_call_to="<phone-number-to-dial>",
        room_name="my-sip-room",
        participant_identity="sip-test",
        participant_name="Test Caller",
        wait_until_answered=True,
    )

    try:
        participant = await livekit_api.sip.create_sip_participant(request)
        print(f"Successfully created {participant}")
    except Exception as e:
        print(f"Error creating SIP participant: {e}")
    finally:
        await livekit_api.aclose()

asyncio.run(main())

```

---

**Ruby**:

```ruby
require 'livekit'

# Reads LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET from the environment.
lkapi = LiveKit::LiveKitAPI.new

trunk = LiveKit::Proto::SIPOutboundConfig.new(
  hostname: ENV['SIP_TRUNK_HOSTNAME'], # For example, <my-trunk>.pstn.twilio.com or <trunk-id>.zt.plivo.com
  destination_country: 'US',
  auth_username: ENV['SIP_AUTH_USERNAME'],
  auth_password: ENV['SIP_AUTH_PASSWORD']
)

lkapi.sip.create_sip_participant(
  '', # Empty when using inline trunk config
  '<phone-number-to-dial>',
  'my-sip-room',
  trunk: trunk,
  from_number: '<SIP provider number>', # Required when using inline trunk config
  participant_identity: 'sip-test',
  participant_name: 'Test Caller',
  wait_until_answered: true
)

```

---

**Go**:

```go
package main

import (
  "context"
  "fmt"
  "os"

  lksdk "github.com/livekit/server-sdk-go/v2"
  "github.com/livekit/protocol/livekit"
)

func main() {
  request := &livekit.CreateSIPParticipantRequest{
    Trunk: &livekit.SIPOutboundConfig{
      Hostname:           os.Getenv("SIP_TRUNK_HOSTNAME"), // For example, <my-trunk>.pstn.twilio.com, sip.telnyx.com, or <trunk-id>.zt.plivo.com
      DestinationCountry: "US",
      AuthUsername:       os.Getenv("SIP_AUTH_USERNAME"),
      AuthPassword:       os.Getenv("SIP_AUTH_PASSWORD"),
    },
    SipNumber:           "<SIP provider number>", // Required when using inline trunk config
    SipCallTo:           "<phone-number-to-dial>",
    RoomName:            "my-sip-room",
    ParticipantIdentity: "sip-test",
    ParticipantName:     "Test Caller",
    WaitUntilAnswered:   true,
  }

  api, err := lksdk.NewLiveKitAPI(lksdk.WithURL(os.Getenv("LIVEKIT_URL")),
    lksdk.WithAPIKey(os.Getenv("LIVEKIT_API_KEY"), os.Getenv("LIVEKIT_API_SECRET")))
  if err != nil {
    fmt.Println(err)
    return
  }

  participant, err := api.SIP().CreateSIPParticipant(context.Background(), request)

  if err != nil {
    fmt.Println(err)
  } else {
    fmt.Println(participant)
  }
}

```

---

**Kotlin**:

```kotlin
import io.livekit.server.CreateSipParticipantOptions
import io.livekit.server.LiveKitAPI
import livekit.LivekitSip.SIPOutboundConfig

val api = LiveKitAPI.createClient(
    System.getenv("LIVEKIT_URL") ?: "",
    System.getenv("LIVEKIT_API_KEY") ?: "",
    System.getenv("LIVEKIT_API_SECRET") ?: ""
)

val trunk = SIPOutboundConfig.newBuilder()
    .setHostname(System.getenv("SIP_TRUNK_HOSTNAME")) // For example, <my-trunk>.pstn.twilio.com or <trunk-id>.zt.plivo.com
    .setDestinationCountry("US")
    .setAuthUsername(System.getenv("SIP_AUTH_USERNAME"))
    .setAuthPassword(System.getenv("SIP_AUTH_PASSWORD"))
    .build()

val options = CreateSipParticipantOptions(
    participantIdentity = "sip-test",
    participantName = "Test Caller",
    outboundConfig = trunk,
    fromNumber = "<SIP provider number>", // Required when using inline trunk config
    waitUntilAnswered = true,
)

api.sip.createSipParticipant("", "<phone-number-to-dial>", "my-sip-room", options).execute()

```

---

**Rust**:

```rust
use livekit_api::services::sip::CreateSIPParticipantOptions;
use livekit_api::services::LiveKitApi;
use livekit_protocol::SipOutboundConfig;

let api = LiveKitApi::with_api_key(
    &std::env::var("LIVEKIT_URL")?,
    &std::env::var("LIVEKIT_API_KEY")?,
    &std::env::var("LIVEKIT_API_SECRET")?,
);

let trunk_config = SipOutboundConfig {
    hostname: std::env::var("SIP_TRUNK_HOSTNAME")?, // For example, <my-trunk>.pstn.twilio.com or <trunk-id>.zt.plivo.com
    destination_country: "US".to_owned(),
    auth_username: std::env::var("SIP_AUTH_USERNAME")?,
    auth_password: std::env::var("SIP_AUTH_PASSWORD")?,
    ..Default::default()
};

let participant = api
    .sip()
    .create_sip_participant(
        "".to_owned(), // Empty when using inline trunk config
        "<phone-number-to-dial>".to_owned(),
        "my-sip-room".to_owned(),
        CreateSIPParticipantOptions {
            participant_identity: "sip-test".to_owned(),
            participant_name: Some("Test Caller".to_owned()),
            sip_number: Some("<SIP provider number>".to_owned()), // Required with inline trunk config
            wait_until_answered: Some(true),
            ..Default::default()
        },
        Some(trunk_config), // SipOutboundConfig as the 5th argument
    )
    .await?;

```

Once the user picks up, they are connected to `my-sip-room`.

### Stored outbound trunk

If you use the same trunk configuration across multiple calls, you can [create an outbound trunk](https://docs.livekit.io/telephony/making-calls/outbound-trunk.md) ahead of time and reference it by ID. This avoids repeating the trunk configuration in every request.

**LiveKit CLI**:

1. Create a `sip-participant.json` file with the following participant details:

```json
{
  "sip_trunk_id": "<your-trunk-id>",
  "sip_call_to": "<phone-number-to-dial>",
  "room_name": "my-sip-room",
  "participant_identity": "sip-test",
  "participant_name": "Test Caller",
  "wait_until_answered": true
}

```
2. Create the SIP Participant using the CLI. After you run this command, the participant makes a call to the `sip_call_to` number configured in your outbound trunk. When you set `wait_until_answered` to `true`, the command waits until the callee picks up the call before returning. You can also monitor the call status using the [SIP participant attributes](https://docs.livekit.io/reference/telephony/sip-participant.md#sip-attributes). When the callee picks up the call, the `sip.callStatus` attribute is `active`.

```shell
lk sip participant create sip-participant.json

```

---

**Node.js**:

```typescript
import { LiveKitAPI, SipCallError } from 'livekit-server-sdk';

const api = new LiveKitAPI({
  host: process.env.LIVEKIT_URL,
  apiKey: process.env.LIVEKIT_API_KEY,
  secret: process.env.LIVEKIT_API_SECRET,
});

// Outbound trunk to use for the call
const trunkId = '<your-trunk-id>';

// Phone number to dial
const phoneNumber = '<phone-number-to-dial>';

// Name of the room to attach the call to
const roomName = 'my-sip-room';

const sipParticipantOptions = {
  participantIdentity: 'sip-test',
  participantName: 'Test Caller',
  // Block until the callee picks up; throws a SipCallError if the call fails.
  waitUntilAnswered: true,
};

async function main() {
  try {
    const participant = await api.sip.createSipParticipant(
      trunkId,
      phoneNumber,
      roomName,
      sipParticipantOptions,
    );

    console.log('Participant created:', participant);
  } catch (error) {
    if (error instanceof SipCallError) {
      // sipStatusCode / sipStatus carry the status from the upstream carrier
      console.error(`SIP call failed: ${error.sipStatusCode} ${error.sipStatus}`);
    } else {
      console.error('Error creating SIP participant:', error);
    }
  }
}

main();

```

---

**Python**:

```python
import asyncio

from livekit import api
from livekit.protocol.sip import CreateSIPParticipantRequest

async def main():
    lkapi = api.LiveKitAPI()

    request = CreateSIPParticipantRequest(
        sip_trunk_id = "<trunk_id>",
        sip_call_to = "<phone_number>",
        room_name = "my-sip-room",
        participant_identity = "sip-test",
        participant_name = "Test Caller",
        # Block until the callee picks up; raises a SipCallError if the call fails.
        wait_until_answered = True
    )

    try:
        participant = await lkapi.sip.create_sip_participant(request)
        print(f"Successfully created {participant}")
    except api.SipCallError as e:
        # sip_status_code / sip_status carry the status from the upstream carrier
        print(f"SIP call failed: {e.sip_status_code} {e.sip_status}")
    finally:
        await lkapi.aclose()

asyncio.run(main())

```

---

**Ruby**:

```ruby
require 'livekit'

lkapi = LiveKit::LiveKitAPI.new(
  ENV['LIVEKIT_URL'],
  api_key: ENV['LIVEKIT_API_KEY'],
  api_secret: ENV['LIVEKIT_API_SECRET']
)

begin
  participant = lkapi.sip.create_sip_participant(
    '<trunk_id>',
    '<phone_number>',
    'my-sip-room',
    participant_identity: 'sip-test',
    participant_name: 'Test Caller',
    # Block until the callee picks up; raises a SipCallError if the call fails.
    wait_until_answered: true
  )
  puts participant
rescue LiveKit::SipCallError => e
  puts "SIP call failed: #{e.sip_status_code} #{e.sip_status}"
end

```

---

**Go**:

```go
package main

import (
  "context"
  "fmt"
  "os"

  lksdk "github.com/livekit/server-sdk-go/v2"
  "github.com/livekit/protocol/livekit"
)

func main() {
  request := &livekit.CreateSIPParticipantRequest{
    SipTrunkId:          "<trunk_id>",
    SipCallTo:           "<phone_number>",
    RoomName:            "my-sip-room",
    ParticipantIdentity: "sip-test",
    ParticipantName:     "Test Caller",
    // Block until the callee picks up.
    WaitUntilAnswered:   true,
  }

  api, err := lksdk.NewLiveKitAPI(lksdk.WithURL(os.Getenv("LIVEKIT_URL")),
    lksdk.WithAPIKey(os.Getenv("LIVEKIT_API_KEY"), os.Getenv("LIVEKIT_API_SECRET")))
  if err != nil {
    fmt.Println(err)
    return
  }

  participant, err := api.SIP().CreateSIPParticipant(context.Background(), request)
  if err != nil {
    // SIPStatusFrom extracts the upstream carrier's SIP status, if any.
    if status := lksdk.SIPStatusFrom(err); status != nil {
      fmt.Printf("SIP call failed: %d %s\n", status.Code, status.Status)
    } else {
      fmt.Println(err)
    }
    return
  }
  fmt.Println(participant)
}

```

---

**Kotlin**:

```kotlin
import io.livekit.server.CreateSipParticipantOptions
import io.livekit.server.LiveKitAPI
import io.livekit.server.SipCallError

val api = LiveKitAPI.createClient(
    System.getenv("LIVEKIT_URL") ?: "",
    System.getenv("LIVEKIT_API_KEY") ?: "",
    System.getenv("LIVEKIT_API_SECRET") ?: ""
)

val options = CreateSipParticipantOptions(
    participantIdentity = "sip-test",
    participantName = "Test Caller",
    // Block until the callee picks up.
    waitUntilAnswered = true
)

val response = api.sip.createSipParticipant("<trunk_id>", "<phone_number>", "my-sip-room", options).execute()
if (response.isSuccessful) {
    println(response.body())
} else {
    // A SIP dial failure decodes to a SipCallError with the carrier's status.
    val error = SipCallError.from(response)
    println("SIP call failed: ${error?.sipStatusCode} ${error?.sipStatus}")
}

```

---

**Rust**:

```rust
use livekit_api::services::sip::CreateSIPParticipantOptions;
use livekit_api::services::{LiveKitApi, SipCallError};

let api = LiveKitApi::with_api_key(
    &std::env::var("LIVEKIT_URL")?,
    &std::env::var("LIVEKIT_API_KEY")?,
    &std::env::var("LIVEKIT_API_SECRET")?,
);

let result = api
    .sip()
    .create_sip_participant(
        "<trunk_id>".to_owned(),
        "<phone_number>".to_owned(),
        "my-sip-room".to_owned(),
        CreateSIPParticipantOptions {
            participant_identity: "sip-test".to_owned(),
            participant_name: Some("Test Caller".to_owned()),
            // Block until the callee picks up.
            wait_until_answered: Some(true),
            ..Default::default()
        },
        None,
    )
    .await;

match result {
    Ok(participant) => println!("{participant:?}"),
    Err(e) => match SipCallError::from_error(&e) {
        // sip_status_code / sip_status carry the status from the upstream carrier
        Some(sip) => println!("SIP call failed: {:?} {:?}", sip.sip_status_code(), sip.sip_status()),
        None => eprintln!("{e}"),
    },
}

```

Once the user picks up, they are connected to `my-sip-room`.

### Agent initiated outbound calls

To have your agent make an outbound call, dispatch the agent and then create a SIP participant. This section describes how to modify the [voice AI quickstart](https://docs.livekit.io/agents/start/voice-ai.md) for outbound calling. Alternatively, see the following complete example on GitHub:

- **[Outbound caller example](https://github.com/livekit-examples/outbound-caller-python)**: Complete example of an outbound calling agent.

#### Dialing a number

Add the following code to the agent code from the [voice AI quickstart](https://docs.livekit.io/agents/start/voice-ai.md). Your agent reads the phone number passed in the `metadata` field of the agent dispatch request and places an outbound call by creating a SIP participant.

You should also remove the initial greeting or place it behind an `if` statement to ensure the agent waits for the user to speak first when placing an outbound call.

> ℹ️ **SIP trunk ID**
> 
> You must add a valid [outbound trunk](https://docs.livekit.io/telephony/making-calls/outbound-trunk.md) ID to successfully make a phone call. To see a list of your outbound trunks use the LiveKit CLI: `lk sip outbound list`.

**Python**:

Add the following code to the `agent.py` file from the Voice AI quickstart:

```python
# add these imports at the top of your file
from livekit import agents, api
import json

# ... AgentServer, Assistant class, and AgentSession config from the voice AI quickstart ...

@server.rtc_session(agent_name="my-telephony-agent")
async def my_agent(ctx: agents.JobContext):
    # If a phone number was provided, then place an outbound call
    # By having a condition like this, you can use the same agent for inbound/outbound telephony as well as web/mobile/etc.
    dial_info = json.loads(ctx.job.metadata)
    phone_number = dial_info.get("phone_number")

    # The participant's identity can be anything you want, but this example uses the phone number itself
    sip_participant_identity = phone_number
    if phone_number is not None:
        # The outbound call will be placed after this method is executed
        try:
            await ctx.api.sip.create_sip_participant(api.CreateSIPParticipantRequest(
                # This ensures the participant joins the correct room
                room_name=ctx.room.name,

                # This is the outbound trunk ID to use
                # You can get this from LiveKit CLI with `lk sip outbound list`
                sip_trunk_id='ST_xxxx',

                # The outbound phone number to dial and identity to use
                sip_call_to=phone_number,
                participant_identity=sip_participant_identity,

                # This waits until the call is answered before returning
                wait_until_answered=True,
            ))

            print("call picked up successfully")
        except api.SipCallError as e:
            # sip_status_code / sip_status carry the status from the upstream carrier
            print(f"call failed: {e.sip_status_code} {e.sip_status}")
            ctx.shutdown()
            return

    # Wait for the SIP participant to fully join the room before starting the session
    participant = await ctx.wait_for_participant(identity=sip_participant_identity)

    # Create and start your AgentSession
    # session = AgentSession(...)
    # await session.start(room=ctx.room, participant=participant, agent=Assistant(), ...)

    # When placing an outbound call, let the callee speak first.
    if phone_number is None:
        await session.generate_reply(
            instructions="Greet the user and offer your assistance."
        )

```

---

**Node.js**:

Install `livekit-server-sdk`:

```
pnpm add livekit-server-sdk

```

Then, edit the `main.ts` file from the [voice AI quickstart](https://docs.livekit.io/agents/start/voice-ai.md). Add the outbound dial logic at the top of `entry`, before creating the session. Make sure to use a valid ID for the `outboundTrunkId`. Run `lk sip outbound list` to get a list of outbound trunks.

```typescript
import { LiveKitAPI, SipCallError } from 'livekit-server-sdk';
// ... any existing code / imports ...

const outboundTrunkId = '<outbound-trunk-id>';
const sipRoom = 'new-room';

export default defineAgent({
  entry: async (ctx: JobContext) => {
    // If a phone number was provided, place an outbound call.
    const dialInfo = JSON.parse(ctx.job.metadata || '{}');
    const phoneNumber = dialInfo.phone_number;

    if (phoneNumber) {
      const api = new LiveKitAPI({
        host: process.env.LIVEKIT_URL,
        apiKey: process.env.LIVEKIT_API_KEY,
        secret: process.env.LIVEKIT_API_SECRET,
      });
      try {
        await api.sip.createSipParticipant(
          outboundTrunkId,
          phoneNumber,
          sipRoom,
          {
            participantIdentity: phoneNumber,
            participantName: 'Test callee',
            waitUntilAnswered: true,
          },
        );
        console.log('Call picked up successfully');
      } catch (error) {
        if (error instanceof SipCallError) {
          console.error(`Call failed: ${error.sipStatusCode} ${error.sipStatus}`);
        }
        ctx.shutdown();
        return;
      }
    }

    // Wait for the SIP participant to fully join the room before starting the session
    const participant = await ctx.waitForParticipant({ identity: phoneNumber });

    // Create and start your AgentSession (use your existing STT, LLM, TTS config from the quickstart)

    // Only greet first on inbound; on outbound, the recipient speaks first and the agent responds after their turn.
    if (!phoneNumber) {
      session.generateReply({
        instructions: 'Greet the user and offer your assistance.',
      });
    }
  },
});

// Update the agentName from the quickstart to "my-telephony-agent"
cli.runApp(new ServerOptions({ agent: fileURLToPath(import.meta.url), agentName: 'my-telephony-agent' }));

```

> 🔥 **Wait for the callee to answer**
> 
> Call `session.start()` _after_ the callee picks up. If the session starts while the call is still ringing, the initial greeting plays before the callee joins the room. When they answer, they hear the tail end of the greeting or silence.

Start the agent and follow the instructions in the next section to call your agent.

#### Make a call with your agent

Use either the LiveKit CLI or the Python API to instruct your agent to place an outbound phone call.

In this example, the job's metadata includes the phone number to call. You can extend this to include more information if needed for your use case.

The agent name must match the name you assigned to your agent. If you set it earlier in the [agent dispatch](#agent-dispatch) section, this is `my-telephony-agent`.

> ❗ **Verify values to dispatch agents**
> 
> Make sure to verify or update the values in the following examples:
> 
> - Room name: The examples use `new-room`.
> - Agent name: Must match the name you assigned to your agent.
> - Phone number: Provide a valid phone number to dial.

**LiveKit CLI**:

The following command creates a new room and dispatches your agent to it with the phone number to call.

```shell
lk dispatch create \
    --new-room \
    --agent-name my-telephony-agent \
    --metadata '{"phone_number": "+15105550123"}' # insert your own phone number here

```

---

**Node.js**:

```typescript
import { LiveKitAPI } from 'livekit-server-sdk';

// Reads LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET from the environment.
const api = new LiveKitAPI();

// Use the agent name you set in ServerOptions.agentName. Room must match the name used for CreateSIPParticipant (e.g. new-room).
await api.agentDispatch.createDispatch(
  'new-room', // must match the room name used when creating the SIP participant
  'my-telephony-agent',
  { metadata: '{"phone_number": "+15105550123"}' },
);

```

---

**Python**:

```python
from livekit import api

# Reads LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET from the environment.
async with api.LiveKitAPI() as lkapi:
    await lkapi.agent_dispatch.create_dispatch(
        api.CreateAgentDispatchRequest(
            agent_name="my-telephony-agent",  # matches the rtc_session decorator
            room="new-room",
            metadata='{"phone_number": "+15105550123"}',
        )
    )

```

---

**Ruby**:

```ruby
require 'livekit'

# Reads LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET from the environment.
lkapi = LiveKit::LiveKitAPI.new

lkapi.agent_dispatch.create_dispatch(
  'new-room',
  'my-telephony-agent',
  metadata: '{"phone_number": "+15105550123"}'
)

```

---

**Go**:

```go
import (
  "context"
  "fmt"

  lksdk "github.com/livekit/server-sdk-go/v2"
  "github.com/livekit/protocol/livekit"
)

// Reads LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET from the environment.
api, err := lksdk.NewLiveKitAPI()
if err != nil {
  fmt.Println(err)
  return
}

_, err = api.AgentDispatch().CreateDispatch(context.Background(), &livekit.CreateAgentDispatchRequest{
  Room:      "new-room",
  AgentName: "my-telephony-agent",
  Metadata:  `{"phone_number": "+15105550123"}`,
})

```

---

**Kotlin**:

```kotlin
import io.livekit.server.LiveKitAPI

val api = LiveKitAPI.createClient(
    System.getenv("LIVEKIT_URL") ?: "",
    System.getenv("LIVEKIT_API_KEY") ?: "",
    System.getenv("LIVEKIT_API_SECRET") ?: ""
)

api.agentDispatch.createDispatch(
    room = "new-room",
    agentName = "my-telephony-agent",
    metadata = """{"phone_number": "+15105550123"}""",
).execute()

```

---

**Rust**:

```rust
use livekit_api::services::LiveKitApi;
use livekit_protocol::CreateAgentDispatchRequest;

// Reads LIVEKIT_API_KEY and LIVEKIT_API_SECRET from the environment.
let api = LiveKitApi::new(&std::env::var("LIVEKIT_URL")?)?;

api.agent_dispatch()
    .create_dispatch(CreateAgentDispatchRequest {
        room: "new-room".to_owned(),
        agent_name: "my-telephony-agent".to_owned(),
        metadata: r#"{"phone_number": "+15105550123"}"#.to_owned(),
        ..Default::default()
    })
    .await?;

```

#### Answering machine detection

Use [answering machine detection](https://docs.livekit.io/telephony/features/answering-machine-detection.md) to classify whether a real person, voicemail, or IVR system answered the call, and respond appropriately.

## Handling call outcomes

A successful call outcome means either the callee is speaking with your agent or an automated system (like voicemail) answered. A failure occurs when the callee doesn't answer or rejects the call. This section covers how to handle each scenario.

Use `wait_until_answered` to catch failures early. After the call connects, confirm the SIP participant joined using `JobContext.wait_for_participant`. For details, see [Catching call failures](#catch-failures).

To handle mid-call disconnections, listen for the `participant_disconnected` event. For details, see [Handling mid-call disconnections](#mid-call-disconnections).

The following table describes possible call outcomes and how to identify them:

| Outcome | SIP codes | Behavior | Indicators |
| Call answered | `200 OK` | `wait_until_answered` returns successfully. | `sip.callStatus = active` |
| Call rejected | `486 Busy Here`, `603 Decline` | `wait_until_answered` raises `SipCallError`. | `USER_REJECTED` in `disconnect_reason` |
| No answer / timeout | `408 Request Timeout`, `480 Temporarily Unavailable` | `wait_until_answered` raises `SipCallError`. | `USER_UNAVAILABLE` in `disconnect_reason` |
| SIP protocol failure | `5xx` Server Failure Responses | `wait_until_answered` raises `SipCallError`. | `SIP_TRUNK_FAILURE` in `disconnect_reason` |
| Voicemail | `200 OK` | Call answered | `sip.callStatus = active`, agent speaks to voicemail |

> 🔥 **Voicemail is not a failure**
> 
> Voicemail systems answer the call at the SIP layer with a `200 OK`, so `wait_until_answered` returns successfully and no `SipCallError` is raised. To handle voicemail, use [answering machine detection](https://docs.livekit.io/telephony/features/answering-machine-detection.md) instead of error handling.

### Catching call failures

To catch failures early, use the `CreateSIPParticipant` API with the `wait_until_answered` option. When a failure occurs, a `SipCallError` is raised exposing the SIP status code and reason from the upstream carrier. Use this information to determine the cause and handle it accordingly (for example, retry the call or notify the user).

The dial can run inside an agent or from any backend. The following example catches failures early with `wait_until_answered` and inspects the SIP status code to determine the cause:

**Node.js**:

```typescript
import { LiveKitAPI, SipCallError } from 'livekit-server-sdk';

const api = new LiveKitAPI();

try {
  await api.sip.createSipParticipant('ST_xxxx', phoneNumber, roomName, {
    participantIdentity: phoneNumber,
    waitUntilAnswered: true,
  });
} catch (error) {
  if (error instanceof SipCallError) {
    // 486 = Busy Here, 603 = Decline — user actively rejected the call
    // 408/480 = no answer or unavailable
    // 5xx = SIP trunk/protocol failure
    console.error(`Call failed: ${error.sipStatusCode} ${error.sipStatus}`);
  }
}

```

---

**Python**:

```python
from livekit import api

async with api.LiveKitAPI() as lkapi:
    try:
        await lkapi.sip.create_sip_participant(api.CreateSIPParticipantRequest(
            sip_trunk_id="ST_xxxx",
            sip_call_to=phone_number,
            room_name=room_name,
            participant_identity=phone_number,
            wait_until_answered=True,
        ))
    except api.SipCallError as e:
        # 486 = Busy Here, 603 = Decline — user actively rejected the call
        # 408/480 = no answer or unavailable
        # 5xx = SIP trunk/protocol failure
        print(f"Call failed: {e.sip_status_code} {e.sip_status}")

```

---

**Ruby**:

```ruby
require 'livekit'

lkapi = LiveKit::LiveKitAPI.new

begin
  lkapi.sip.create_sip_participant(
    'ST_xxxx', phone_number, room_name,
    participant_identity: phone_number,
    wait_until_answered: true
  )
rescue LiveKit::SipCallError => e
  # 486 = Busy Here, 603 = Decline — user actively rejected the call
  # 408/480 = no answer or unavailable; 5xx = SIP trunk/protocol failure
  puts "Call failed: #{e.sip_status_code} #{e.sip_status}"
end

```

---

**Go**:

```go
api, err := lksdk.NewLiveKitAPI()
if err != nil {
  fmt.Println(err)
  return
}

_, err = api.SIP().CreateSIPParticipant(context.Background(), &livekit.CreateSIPParticipantRequest{
  SipTrunkId:          "ST_xxxx",
  SipCallTo:           phoneNumber,
  RoomName:            roomName,
  ParticipantIdentity: phoneNumber,
  WaitUntilAnswered:   true,
})
if err != nil {
  // 486 = Busy Here, 603 = Decline — user actively rejected the call
  // 408/480 = no answer or unavailable; 5xx = SIP trunk/protocol failure
  if status := lksdk.SIPStatusFrom(err); status != nil {
    fmt.Printf("Call failed: %d %s\n", status.Code, status.Status)
  }
}

```

---

**Kotlin**:

```kotlin
import io.livekit.server.CreateSipParticipantOptions
import io.livekit.server.LiveKitAPI
import io.livekit.server.SipCallError

val api = LiveKitAPI.createClient(
    System.getenv("LIVEKIT_URL") ?: "",
    System.getenv("LIVEKIT_API_KEY") ?: "",
    System.getenv("LIVEKIT_API_SECRET") ?: ""
)

val options = CreateSipParticipantOptions(
    participantIdentity = phoneNumber,
    waitUntilAnswered = true,
)
val response = api.sip.createSipParticipant("ST_xxxx", phoneNumber, roomName, options).execute()
if (!response.isSuccessful) {
    // 486 = Busy Here, 603 = Decline — user actively rejected the call
    // 408/480 = no answer or unavailable; 5xx = SIP trunk/protocol failure
    val error = SipCallError.from(response)
    println("Call failed: ${error?.sipStatusCode} ${error?.sipStatus}")
}

```

---

**Rust**:

```rust
use livekit_api::services::sip::CreateSIPParticipantOptions;
use livekit_api::services::{LiveKitApi, SipCallError};

let api = LiveKitApi::new(&std::env::var("LIVEKIT_URL")?)?;

let result = api
    .sip()
    .create_sip_participant(
        "ST_xxxx".to_owned(),
        phone_number.clone(),
        room_name,
        CreateSIPParticipantOptions {
            participant_identity: phone_number,
            wait_until_answered: Some(true),
            ..Default::default()
        },
        None,
    )
    .await;

if let Err(e) = result {
    // 486 = Busy Here, 603 = Decline — user actively rejected the call
    // 408/480 = no answer or unavailable; 5xx = SIP trunk/protocol failure
    if let Some(sip) = SipCallError::from_error(&e) {
        eprintln!("Call failed: {:?} {:?}", sip.sip_status_code(), sip.sip_status());
    }
}

```

In an agent, dial through `ctx.api.sip` and, after the call is answered, confirm the SIP participant joined with `JobContext.wait_for_participant` (see [Agent initiated outbound calls](#agent-calls)). Call `ctx.shutdown()` on failure to release the job.

> ℹ️ **When ctx.shutdown() is required**
> 
> `AgentSession` automatically closes the session when a SIP participant disconnects with `USER_REJECTED`. If the disconnect reason is `USER_UNAVAILABLE` or `SIP_TRUNK_FAILURE`, you must explicitly call `ctx.shutdown()` to release the job. For more details, see [Disconnect reasons](https://docs.livekit.io/reference/telephony/sip-participant.md#disconnect-reasons).

### Handling mid-call disconnections

After a call connects, the callee might hang up or the connection might drop. Most mid-call hangups (either side ends the call cleanly with a SIP BYE) surface as `CLIENT_INITIATED`. The SIP-specific reasons (`USER_REJECTED`, `USER_UNAVAILABLE`, `SIP_TRUNK_FAILURE`) describe **outbound dial failures**: they are set during the dial attempt, not after a successful answer.

By default, `AgentSession` (via `RoomIO`) automatically closes the session when the SIP participant disconnects with `CLIENT_INITIATED`, `ROOM_DELETED`, or `USER_REJECTED`. For other reasons or for custom logic (for example, logging, metrics, follow-up actions), listen for the `participant_disconnected` event and inspect `disconnect_reason`:

**Python**:

```python
from livekit import rtc

@ctx.room.on("participant_disconnected")
def on_participant_disconnected(participant: rtc.RemoteParticipant):
    if participant.identity != sip_participant_identity:
        return
    reason = participant.disconnect_reason
    if reason == rtc.DisconnectReason.CLIENT_INITIATED:
        print("Callee hung up after the call was answered")
    elif reason == rtc.DisconnectReason.USER_REJECTED:
        print("Callee rejected the call before answering")
    elif reason == rtc.DisconnectReason.USER_UNAVAILABLE:
        print("Callee was unavailable")
    elif reason == rtc.DisconnectReason.SIP_TRUNK_FAILURE:
        print("SIP trunk or protocol failure")
    else:
        print(f"Callee disconnected: {rtc.DisconnectReason.Name(reason)}")

```

---

**Node.js**:

Install `@livekit/rtc-node` to get access to disconnect reasons:

```bash
pnpm add '@livekit/rtc-node'

```

Add a listener for the `participant_disconnected` event and inspect the `disconnectReason` property:

```typescript
import { DisconnectReason } from '@livekit/rtc-node';

ctx.room.on('participantDisconnected', (participant) => {
  if (participant.identity !== phoneNumber) return;

  switch (participant.disconnectReason) {
    case DisconnectReason.CLIENT_INITIATED:
      console.log('Callee hung up after the call was answered');
      break;
    case DisconnectReason.USER_REJECTED:
      console.log('Callee rejected the call before answering');
      break;
    case DisconnectReason.USER_UNAVAILABLE:
      console.log('Callee was unavailable');
      break;
    case DisconnectReason.SIP_TRUNK_FAILURE:
      console.log('SIP trunk or protocol failure');
      break;
    default:
      console.log(`Callee disconnected: ${DisconnectReason[participant.disconnectReason]}`);
  }
});

```

For more information on disconnect reasons, see [SIP participant attributes](https://docs.livekit.io/reference/telephony/sip-participant.md#sip-attributes).

## Custom caller ID

You can set a custom caller ID for outbound calls using the `display_name` field in the `CreateSIPParticipant` request. By default, if this field isn't included in the request, the phone number is used as the display name. If this field is set to an empty string, most SIP trunking providers issue a Caller ID Name (CNAM) lookup and use the result as the display name.

> ℹ️ **SIP provider support**
> 
> Your SIP provider must support custom caller ID for the `display_name` value to be used. Confirm with your specific provider to verify support.

**LiveKit CLI**:

```json
{
  "sip_trunk_id": "<your-trunk-id>",
  "sip_call_to": "<phone-number-to-dial>",
  "room_name": "my-sip-room",
  "participant_identity": "sip-test",
  "participant_name": "Test Caller",
  "display_name": "My Custom Display Name"
}

```

---

**Node.js**:

```typescript
const sipParticipantOptions = {
  participantIdentity: 'sip-test',
  participantName: 'Test Caller',
  displayName: 'My Custom Display Name'
};

```

---

**Python**:

```python
  request = CreateSIPParticipantRequest(
    sip_trunk_id = "<trunk_id>",
    sip_call_to = "<phone_number>",
    room_name = "my-sip-room",
    participant_identity = "sip-test",
    participant_name = "Test Caller",
    display_name = "My Custom Display Name"
  )

```

---

**Ruby**:

```ruby
lkapi.sip.create_sip_participant(
  trunk_id,
  number,
  room_name,
  participant_identity: 'sip-test',
  participant_name: 'Test Caller',
  display_name: 'My Custom Display Name'
)

```

---

**Go**:

```go
displayName := "My Custom Display Name"

request := &livekit.CreateSIPParticipantRequest {
  SipTrunkId: trunkId,
  SipCallTo: phoneNumber,
  RoomName: roomName,
  ParticipantIdentity: participantIdentity,
  ParticipantName: participantName,
  WaitUntilAnswered: true,
  DisplayName: &displayName,
}

```

---

**Kotlin**:

```kotlin
val options = CreateSipParticipantOptions(
    participantIdentity = "sip-test",
    participantName = "Test Caller",
    displayName = "My Custom Display Name"
)

```

---

**Rust**:

```rust
let options = CreateSIPParticipantOptions {
    participant_identity: "sip-test".to_owned(),
    participant_name: Some("Test Caller".to_owned()),
    display_name: Some("My Custom Display Name".to_owned()),
    ..Default::default()
};

```

## Making a call with extension codes (DTMF)

To make outbound calls with fixed extension codes (DTMF tones), set `dtmf` field in `CreateSIPParticipant` request:

**LiveKit CLI**:

```json
{
  "sip_trunk_id": "<your-trunk-id>",
  "sip_call_to": "<phone-number-to-dial>",
  "dtmf": "*123#ww456",
  "room_name": "my-sip-room",
  "participant_identity": "sip-test",
  "participant_name": "Test Caller"
}

```

---

**Node.js**:

```typescript
const sipParticipantOptions = {
  participantIdentity: 'sip-test',
  participantName: 'Test Caller',
  dtmf: '*123#ww456'
};

```

---

**Python**:

```python
  request = CreateSIPParticipantRequest(
    sip_trunk_id = "<trunk_id>",
    sip_call_to = "<phone_number>",
    room_name = "my-sip-room",
    participant_identity = "sip-test",
    participant_name = "Test Caller",
    dtmf = "*123#ww456"
  )

```

---

**Ruby**:

```ruby
resp = sip_service.create_sip_participant(
    trunk_id,
    number,
    room_name,
    participant_identity: participant_identity,
    participant_name: participant_name,
    dtmf: "*123#ww456"
)

```

---

**Go**:

```go
  request := &livekit.CreateSIPParticipantRequest{
    SipTrunkId: trunkId,
    SipCallTo: phoneNumber,
    RoomName: roomName,
    ParticipantIdentity: participantIdentity,
    ParticipantName: participantName,
    Dtmf: "*123#ww456",
  }

```

---

**Kotlin**:

```kotlin
val options = CreateSipParticipantOptions(
    participantIdentity = "sip-test",
    participantName = "Test Caller",
    dtmf = "*123#ww456"
)

api.sip.createSipParticipant(trunkId, phoneNumber, roomName, options).execute()

```

---

**Rust**:

```rust
let options = CreateSIPParticipantOptions {
    participant_identity: "sip-test".to_owned(),
    participant_name: Some("Test Caller".to_owned()),
    dtmf: Some("*123#ww456".to_owned()),
    ..Default::default()
};

api.sip()
    .create_sip_participant(trunk_id, phone_number, room_name, options, None)
    .await?;

```

> 💡 **Tip**
> 
> Character `w` can be used to delay DTMF by 0.5 sec.

This example dials a specified number and sends the following DTMF tones:

- `*123#`
- Wait 1 sec
- `456`

## Playing dial tone while the call is dialing

SIP participants emit no audio by default while the call connects. This can be changed by setting `play_dialtone` field in `CreateSIPParticipant` request:

**LiveKit CLI**:

```json
{
  "sip_trunk_id": "<your-trunk-id>",
  "sip_call_to": "<phone-number-to-dial>",
  "room_name": "my-sip-room",
  "participant_identity": "sip-test",
  "participant_name": "Test Caller",
  "play_dialtone": true
}

```

---

**Node.js**:

```typescript
const sipParticipantOptions = {
  participantIdentity: 'sip-test',
  participantName: 'Test Caller',
  playDialtone: true
};

```

---

**Python**:

```python
  request = CreateSIPParticipantRequest(
    sip_trunk_id = "<trunk_id>",
    sip_call_to = "<phone_number>",
    room_name = "my-sip-room",
    participant_identity = "sip-test",
    participant_name = "Test Caller",
    play_dialtone = True
  )

```

---

**Ruby**:

```ruby
resp = sip_service.create_sip_participant(
    trunk_id,
    number,
    room_name,
    participant_identity: participant_identity,
    participant_name: participant_name,
    play_dialtone: true
)

```

---

**Go**:

```go
  request := &livekit.CreateSIPParticipantRequest{
    SipTrunkId: trunkId,
    SipCallTo: phoneNumber,
    RoomName: roomName,
    ParticipantIdentity: participantIdentity,
    ParticipantName: participantName,
    PlayDialtone: true,
  }

```

---

**Kotlin**:

```kotlin
val options = CreateSipParticipantOptions(
    participantIdentity = "sip-test",
    participantName = "Test Caller",
    playDialtone = true
)

```

---

**Rust**:

```rust
let options = CreateSIPParticipantOptions {
    participant_identity: "sip-test".to_owned(),
    participant_name: Some("Test Caller".to_owned()),
    play_dialtone: Some(true),
    ..Default::default()
};

```

If `play_dialtone` is enabled, the SIP Participant plays a dial tone to the room until the phone is picked up.

## Hang up

To let your agent end the call for all participants, add the prebuilt [EndCallTool](https://docs.livekit.io/agents/prebuilt/tools/end-call-tool.md) to your agent's tools. The tool shuts down the session and can delete the room to disconnect everyone. If the agent session ends but the room is not deleted, the user continues to hear silence until they hang up.

For a custom implementation, use the `delete_room` API. The following example implements a basic `hangup_call` function you can use as a starting point:

**Python**:

```python
# Add this import at the top of your file
from livekit.agents import get_job_context

# Add this function definition anywhere
async def hangup_call():
    ctx = get_job_context()
    if ctx is None:
        # Not running in a job context
        return

    # deletes the current room; room name and API lifecycle are managed for you
    await ctx.delete_room()

class MyAgent(Agent):
    ...

    # to hang up the call as part of a function call
    @function_tool
    async def end_call(self, ctx: RunContext):
        """Called when the user wants to end the call"""
        await ctx.wait_for_playout() # let the agent finish speaking

        await hangup_call()

```

---

**Node.js**:

```typescript
import { LiveKitAPI } from 'livekit-server-sdk';
import { getJobContext } from '@livekit/agents';

const hangUpCall = async () => {
  const jobContext = getJobContext();
  if (!jobContext) {
    return;
  }

  // Reads LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET from the environment.
  const api = new LiveKitAPI();

  if (jobContext.room.name) {
    await api.room.deleteRoom(
      jobContext.room.name,
    );
  }
}

class MyAgent extends voice.Agent {
  constructor() {
    super({
        instructions: 'You are a helpful voice AI assistant.',
        // ... existing code ...
        tools: {
          hangUpCall: llm.tool({
            description: 'Call this tool if the user wants to hang up the call.',
            execute: async (_, { ctx }: llm.ToolOptions<UserData>) => {
              await hangUpCall();
              return "Hung up the call";
            },
          }),
        },
    });
 }
}

```

---

This document was rendered at 2026-08-24T21:31:22.526Z.
For the latest version of this document, see [https://docs.livekit.io/telephony/making-calls/outbound-calls.md](https://docs.livekit.io/telephony/making-calls/outbound-calls.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).
