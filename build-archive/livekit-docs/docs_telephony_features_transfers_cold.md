warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /telephony/features/transfers/cold

LiveKit docs › Telephony › Features › Transfers › Call forwarding

---

# Call forwarding

> Transfer calls to another number or SIP endpoint using SIP REFER.

A _cold transfer_ refers to forwarding a caller to another phone number or SIP endpoint. Performing a cold transfer closes the caller's LiveKit session.

For transfers that include an AI agent to provide context, see the [Agent-assisted transfer](https://docs.livekit.io/telephony/features/transfers/warm.md) guide.

## How it works

To transfer a caller out of a LiveKit room to another phone number, use the following steps:

1. Call the `TransferSIPParticipant` API.
2. LiveKit sends a SIP REFER through your trunk, instructing the provider to connect the caller to the new number or SIP endpoint.
3. The caller leaves the LiveKit room, ending the session.

## Transferring a SIP participant using SIP REFER

REFER is a SIP method that allows you to move an active session to another endpoint (that is, transfer a call). For LiveKit telephony apps, you can use the [`TransferSIPParticipant`](https://docs.livekit.io/reference/telephony/sip-api.md#transfersipparticipant) server API to transfer a caller to another phone number or SIP endpoint.

In order to successfully transfer calls, you must configure your provider trunks to allow call transfers.

### Enable call transfers for your Twilio SIP trunk

Enable call transfer and PSTN transfers for your Twilio SIP trunk. To learn more, see Twilio's [Call Transfer via SIP REFER](https://www.twilio.com/docs/sip-trunking/call-transfer) documentation.

When you transfer a call, you have the option to set the caller ID to display the phone number of the transferee (the caller) or the transferrer (the phone number associated with your LiveKit trunk). Caller ID is configured on the trunk and can't be set per-transfer through the `TransferSIPParticipant` API.

**CLI**:

The following command enables call transfers and sets the caller ID to display the number of the transferee:

> ℹ️ **Note**
> 
> - To list trunks, execute `twilio api trunking v1 trunks list`.
> - To set the caller ID to the transferor, set `transfer-caller-id` to `from-transferor`.

```shell
twilio api trunking v1 trunks update --sid <twilio-trunk-sid> \
--transfer-mode enable-all \
--transfer-caller-id from-transferee

```

---

**Console**:

1. Sign in to the [Twilio console](https://console.twilio.com).
2. Navigate to **Elastic SIP Trunking** » **Manage** » **Trunks**, and select a trunk.
3. In the **Features** » **Call Transfer (SIP REFER)** section, select **Enabled**.
4. In the **Caller ID for Transfer Target** field, select an option.
5. Select **Enable PSTN Transfer**.
6. Save your changes.

### Enable call transfers for your Plivo SIP trunk

Plivo SIP trunks support SIP REFER by default for both inbound and outbound calls. No additional configuration is required. To learn more, see Plivo's [SIP REFER](https://www.plivo.com/docs/sip-trunking/concepts/sip-refer) documentation.

The `transfer_to` field in the `TransferSIPParticipant` request becomes the `Refer-To` URI in the outgoing SIP REFER request.

For transfers through a Plivo trunk, set `transfer_to` to a SIP URI with the following format:

- User set to the transfer destination (that is, a valid E.164 phone number).
- Host set to your Plivo SIP trunk domain ending in `.zt.plivo.com`.

For example, if the transfer destination is `+14155551234`, the `transfer_to` value should be set to the following:

```
sip:+14155551234@<trunk-id>.zt.plivo.com

```

> ❗ **Transfer restrictions**
> 
> Transfers to external SIP domains and private IP addresses are blocked.

When you transfer a call, the caller ID displayed to the transfer target is set automatically. For inbound calls, the transfer target sees the phone number of the transferee (the caller). For outbound calls, the transfer target sees the Plivo number used as the caller ID on the original call. Caller ID can't be set per-transfer through the `TransferSIPParticipant` API.

### Control transfer timeout

When LiveKit starts a transfer with a SIP REFER, the REFER doesn't complete until the destination answers. Because SIP doesn't impose a timeout if the destination keeps ringing, LiveKit uses `ringing_timeout` to cap how long it waits. This field defaults to 30 seconds. If the destination doesn't answer before the timeout, the request returns an error and the caller stays in the room, letting you decide how to handle the failed transfer.

You can control this timeout by setting the `ringing_timeout` field on the [TransferSIPParticipant](https://docs.livekit.io/reference/telephony/sip-api.md#transfersipparticipant) request.

### Usage

Set up the following environment variables:

```shell
export LIVEKIT_URL=%{wsURL}%
export LIVEKIT_API_KEY=<YOUR_API_KEY>
export LIVEKIT_API_SECRET=<YOUR_API_SECRET>

```

**Node.js**:

This example reads the LiveKit URL, API key, and secret from environment variables.

```typescript
import { LiveKitAPI, ServerError, SipCallError } from 'livekit-server-sdk';

// ...

async function transferParticipant(participant) {
  console.log('transfer participant initiated');

  const api = new LiveKitAPI();
  const transferTo = 'tel:+15105550100';

  try {
    await api.sip.transferSipParticipant('open-room', participant.identity, transferTo, {
      playDialtone: false,
    });
    console.log('SIP participant transferred successfully');
  } catch (error) {
    if (error instanceof SipCallError) {
      console.error('SIP error code: ', error.sipStatusCode);
      console.error('SIP error message: ', error.sipStatus);
    } else if (error instanceof ServerError) {
      console.error('Error transferring SIP participant: ', error.code, error.message);
    } else {
      console.error('Error transferring SIP participant: ', error);
    }
  }
}

```

---

**Python**:

```python
import logging

from livekit import api

logger = logging.getLogger("transfer-logger")
logger.setLevel(logging.INFO)

async def transfer_call(participant_identity: str, room_name: str) -> None:
  async with api.LiveKitAPI() as livekit_api:
    transfer_to = 'tel:+14155550100'

    try:
      await livekit_api.sip.transfer_sip_participant(
          api.TransferSIPParticipantRequest(
              participant_identity=participant_identity,
              room_name=room_name,
              transfer_to=transfer_to,
              play_dialtone=False,
          )
      )
      print("SIP participant transferred successfully")
    except api.SipCallError as error:
      print(f"SIP error code: {error.sip_status_code}")
      print(f"SIP error message: {error.sip_status}")
    except api.ServerError as error:
      print(f"Error transferring SIP participant: {error.code} - {error.message}")

```

For a full example using a voice agent, DTMF, and SIP REFER, see the [phone assistant example](https://github.com/ShayneP/phone-assistant).

---

**Ruby**:

```ruby
require 'livekit'

room_name = 'open-room'
participant_identity = 'participant_identity'

def transferParticipant(room_name, participant_identity)
  lkapi = LiveKit::LiveKitAPI.new

  transfer_to = 'tel:+14155550100'

  begin
    lkapi.sip.transfer_sip_participant(
      room_name,
      participant_identity,
      transfer_to,
      play_dialtone: false
    )
    puts "SIP participant transferred successfully"
  rescue LiveKit::SipCallError => e
    puts "SIP error code: #{e.sip_status_code}"
    puts "SIP error message: #{e.sip_status}"
  rescue LiveKit::ServerError => e
    puts "Error transferring SIP participant: #{e.code}"
  end
end

```

---

**Go**:

```go
import (
	"context"
	"errors"
	"fmt"

	"github.com/livekit/protocol/livekit"
	lksdk "github.com/livekit/server-sdk-go/v2"
)

func transferParticipant(ctx context.Context, participantIdentity string) {
	roomName := "open-room"
	transferTo := "tel:+14155550100"

	// Reads LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET from the environment.
	api, err := lksdk.NewLiveKitAPI()
	if err != nil {
		fmt.Println("Error:", err)
		return
	}

	transferRequest := &livekit.TransferSIPParticipantRequest{
		RoomName:            roomName,
		ParticipantIdentity: participantIdentity,
		TransferTo:          transferTo,
		PlayDialtone:        false,
	}

	_, err = api.SIP().TransferSIPParticipant(ctx, transferRequest)
	if err != nil {
		if s := lksdk.SIPStatusFrom(err); s != nil {
			fmt.Printf("SIP error: %d %s\n", s.Code, s.Status)
		} else {
			var se lksdk.ServerError
			if errors.As(err, &se) {
				fmt.Printf("Error transferring SIP participant: %s %s\n", se.Code(), se.Msg())
			} else {
				fmt.Println("Error:", err)
			}
		}
		return
	}

	fmt.Println("SIP participant transferred successfully")
}

```

---

**Kotlin**:

```kotlin
import io.livekit.server.LiveKitAPI
import io.livekit.server.SipCallError
import io.livekit.server.ServerError

fun transferParticipant(roomName: String, participantIdentity: String) {
    // Reads LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET from the environment.
    val api = LiveKitAPI.createClient()

    val transferTo = "tel:+14155550100"

    val response = api.sip.transferSipParticipant(
        roomName,
        participantIdentity,
        transferTo,
        io.livekit.server.TransferSipParticipantOptions(playDialtone = false),
    ).execute()

    if (response.isSuccessful) {
        println("SIP participant transferred successfully")
    } else {
        val sipError = SipCallError.from(response)
        if (sipError != null) {
            println("SIP error code: ${sipError.sipStatusCode}")
            println("SIP error message: ${sipError.sipStatus}")
        } else {
            val error = ServerError.from(response)
            println("Error transferring SIP participant: ${error?.code}")
        }
    }
}

```

---

**Rust**:

```rust
use livekit_api::services::sip::TransferSIPParticipantOptions;
use livekit_api::services::LiveKitApi;

#[tokio::main]
async fn main() {
    let api = LiveKitApi::new("https://my-project.livekit.cloud").unwrap();

    let room_name = "open-room".to_owned();
    let participant_identity = "<participant-identity>".to_owned();
    let transfer_to = "tel:+14155550100".to_owned();

    api.sip()
        .transfer_sip_participant(
            room_name,
            participant_identity,
            transfer_to,
            TransferSIPParticipantOptions { play_dialtone: Some(false), ..Default::default() },
        )
        .await
        .unwrap();

    println!("SIP participant transferred successfully");
}

```

---

**CLI**:

```shell
lk sip participant transfer --room <CURRENT_ROOM> \
   --identity <PARTICIPANT_ID> \
  --to "<SIP_ENDPOINT>"

```

Where `<SIP_ENDPOINT>` is a valid SIP endpoint or telephone number. The following examples are valid formats:

- `tel:+15105550100`
- `sip:+15105550100@sip.telnyx.com`
- `sip:+15105550100@my-livekit-demo.pstn.twilio.com`
- `sip:+15105550100@<trunk-id>.zt.plivo.com`

## Forward calls with an agent tool

Your agent can use the `TransferSIPParticipant` API to transfer calls without staying on the line. The current session ends after the transfer is complete. The following example shows how to define a tool in your agent class that calls `TransferSIPParticipant`.

`TransferSIPParticipant` requires the `participant_identity` of the SIP caller in the room, which is assigned at dispatch time and might differ from the caller's phone number. To reliably find the active SIP caller, look up the participant in the `remote_participants` list and filter on `ParticipantKind.SIP`. To learn more, see [Identifying SIP callers](https://docs.livekit.io/telephony/accepting-calls/workflow-setup.md#identifying-sip-callers).

The following examples assume a single SIP caller per room, which is the typical inbound-agent setup. If your room can contain multiple SIP participants (for example, during a warm transfer or conference), track the target caller's identity explicitly instead of picking the first SIP participant.

**Python**:

```python
from livekit import api, rtc
from livekit.agents import Agent, RunContext, function_tool, get_job_context

class Assistant(Agent):
    ## ... existing init code ...

    @function_tool()
    async def transfer_call(self, ctx: RunContext):
        """Transfer the call to a human agent, called after confirming with the user"""

        transfer_to = "+15105550123"

        job_ctx = get_job_context()

        # Find the active SIP caller in the room. The identity is set at
        # dispatch time and might not match the caller's phone number.
        # Assumes a single SIP caller per room.
        sip_participant = next(
            (
                p for p in job_ctx.room.remote_participants.values()
                if p.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
            ),
            None,
        )
        if sip_participant is None:
            return "no active SIP caller to transfer"

        # let the message play fully before transferring
        await ctx.session.generate_reply(
            instructions="Inform the user that you're transferring them to a different agent."
        )

        try:
            await job_ctx.api.sip.transfer_sip_participant(
                api.TransferSIPParticipantRequest(
                    room_name=job_ctx.room.name,
                    participant_identity=sip_participant.identity,
                    # to use a sip destination, use `sip:user@host` format
                    transfer_to=f"tel:{transfer_to}",
                )
            )
        except Exception as e:
            print(f"error transferring call: {e}")
            # give the LLM that context
            return "could not transfer call"

```

---

**Node.js**:

To use the Node.js example, install the `livekit-server-sdk` package:

```shell
pnpm add livekit-server-sdk

```

Define the transfer tool on your agent class using `llm.tool`. The following example shows a complete `Agent` with a `transferCall` tool. Replace the `src/agent.ts` file in the [`agent-starter-node`](https://github.com/livekit-examples/agent-starter-node) project with the following code:

```typescript
import { voice, llm, getJobContext } from '@livekit/agents';
import { LiveKitAPI } from 'livekit-server-sdk';
import { ParticipantKind } from '@livekit/rtc-node';
import { z } from 'zod';

export class Agent extends voice.Agent {
  constructor() {
    super({
      instructions: 'You are a helpful assistant.',
      tools: {
        transferCall: llm.tool({
          description:
            'Transfer the call to a human agent, called after confirming with the user.',
          parameters: z.object({}),
          execute: async (_, { ctx }) => {
            const transferTo = 'tel:+15105550123';
            const jobCtx = getJobContext();
            const room = jobCtx.room;

            // Find the active SIP caller in the room. The identity is set at
            // dispatch time and might not match the caller's phone number.
            // Assumes a single SIP caller per room.
            const sipParticipant = Array.from(room.remoteParticipants.values()).find(
              (p) => p.kind === ParticipantKind.SIP,
            );
            if (!sipParticipant) {
              return 'no active SIP caller to transfer';
            }

            // Let the message play fully before transferring
            ctx.session.generateReply({
              instructions: "Inform the user that you're transferring them to a different agent.",
            });
            await ctx.waitForPlayout();

            const api = new LiveKitAPI();

            try {
              await api.sip.transferSipParticipant(
                room.name!,
                sipParticipant.identity,
                transferTo,
                { playDialtone: false },
              );
            } catch (e) {
              console.log(`error transferring call: ${e}`);
              return 'could not transfer call';
            }
          },
        }),
      },
    });
  }
}

```

## Additional resources

The following guides provide more information on building voice agents for telephony.

- **[Agent-assisted warm transfer](https://docs.livekit.io/telephony/features/transfers/warm.md)**: Transfer calls with agent assistance and context.

- **[Tool definition & use](https://docs.livekit.io/agents/build/tools.md)**: Extend your agent's capabilities with tools.

- **[Workflows](https://docs.livekit.io/agents/logic/workflows.md)**: Orchestrate detailed workflows such as collecting credit card information over the phone.

- **[Agent speech](https://docs.livekit.io/agents/build/audio.md)**: Customize and perfect your agent's verbal interactions.

---

This document was rendered at 2026-08-24T21:31:37.123Z.
For the latest version of this document, see [https://docs.livekit.io/telephony/features/transfers/cold.md](https://docs.livekit.io/telephony/features/transfers/cold.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).
