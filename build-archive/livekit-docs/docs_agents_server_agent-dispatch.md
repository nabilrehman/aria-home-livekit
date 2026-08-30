warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /agents/server/agent-dispatch

LiveKit docs › Build Agents › Agent Server › Agent dispatch

---

# Agent dispatch

> Specifying how and when your agents are assigned to rooms.

## Dispatching agents

Dispatch is the process of assigning an agent to a room. LiveKit server manages this process as part of the [Server lifecycle](https://docs.livekit.io/agents/server/lifecycle.md). LiveKit optimizes dispatch for high concurrency and low latency, typically supporting hundreds of thousands of new connections per second with a max dispatch time under 150 ms.

Explicit dispatch is the recommended approach for most applications. It gives you full control over when and how agents join rooms and lets you pass job-specific metadata to each agent session.

## Dispatch name

The dispatch name is a unique identifier for an agent. Explicit dispatch uses it to route jobs to the right agent. It's the value of `agent_name` (Python) or `agentName` (Node.js) on `@server.rtc_session()` or `ServerOptions`.

The dispatch name is distinct from the agent's **display name** (`Participant.name`), which is set by the `name` parameter in `req.accept()` and shown to other participants in the room. The dispatch name targets the agent. The display name labels it. See [Request handler](https://docs.livekit.io/agents/server/options.md#request-handler) for setting the display name.

When you scaffold an agent with [`lk agent init`](https://docs.livekit.io/reference/developer-tools/livekit-cli/agent.md#init), the AGENT-NAME you provide becomes the dispatch name in the generated source. To change it later, edit the source code and redeploy.

To set the dispatch name in your server configuration:

**Python**:

In Python, set the agent name in the `@server.rtc_session` decorator:

```python
@server.rtc_session(agent_name="test-agent")
async def my_agent(ctx: JobContext):
    # Agent entrypoint code...

```

---

**Node.js**:

```ts
const opts = new ServerOptions({
  //...
  agentName: "test-agent",
});

```

With `agent_name` set, the agent is only assigned to rooms when explicitly dispatched using one of the following methods.

## Deployments

By default, dispatching an agent targets the `production` deployment. If an agent has [non-production deployments](https://docs.livekit.io/deploy/agents/deployments.md) (for example, `staging`), use the `deployment` parameter to route the dispatch to a specific deployment. On the worker side, registration is automatic: LiveKit Cloud sets `LIVEKIT_AGENT_DEPLOYMENT` on each deployment's containers, and the SDK registers under (`agent_name`, `deployment`). To learn more, see [Deployment environment variable](https://docs.livekit.io/agents/server/options.md#deployment-env-var).

To route a session to a specific deployment, use `deployment` with `agent_name` when you dispatch an agent:

- **Dispatch via API**: `CreateAgentDispatchRequest` accepts a `deployment` field alongside `agent_name`.
- **Dispatch via token**: `RoomAgentDispatch` (inside `RoomConfiguration.agents`) accepts a `deployment` field alongside `agent_name`.
- **SIP**: room agent dispatch on a SIP rule passes `deployment` through the same `RoomAgentDispatch` field.

For example, dispatch to the `staging` deployment from a token using the CLI:

```shell
lk token create --join --open meet --agent test-agent --deployment staging

```

If your app uses the [sandbox token server](https://docs.livekit.io/frontends/build/authentication/sandbox-token-server.md) or the `useSession` hook in a client SDK, pass `deployment` as an optional argument.

## Dispatch via API

You can explicitly dispatch an agent to a room using the `AgentDispatchService` [API](https://docs.livekit.io/reference/agents/agent-dispatch-service-api.md).

**LiveKit CLI**:

```shell
lk dispatch create \
  --agent-name test-agent \
  --room my-room \
  --metadata '{"user_id": "12345"}'

```

---

**Node.js**:

```ts
import { LiveKitAPI } from 'livekit-server-sdk';

const roomName = 'my-room';
const agentName = 'test-agent';

async function createExplicitDispatch() {
  const api = new LiveKitAPI();

  // create a dispatch request for an agent named "test-agent" to join "my-room"
  const dispatch = await api.agentDispatch.createDispatch(roomName, agentName, {
    metadata: '{"user_id": "12345"}',
    // deployment: 'staging', // Optional; empty = production
  });
  console.log('created dispatch', dispatch);

  const dispatches = await api.agentDispatch.listDispatch(roomName);
  console.log(`there are ${dispatches.length} dispatches in ${roomName}`);
}

```

---

**Python**:

```python
import asyncio
from livekit import api

room_name = "my-room"
agent_name = "test-agent"

async def create_explicit_dispatch():
    async with api.LiveKitAPI() as lkapi:
        dispatch = await lkapi.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                agent_name=agent_name,
                room=room_name,
                metadata='{"user_id": "12345"}',
                # deployment="staging",  # Optional; empty = production
            )
        )
        print("created dispatch", dispatch)

        dispatches = await lkapi.agent_dispatch.list_dispatch(room_name)
        print(f"there are {len(dispatches)} dispatches in {room_name}")

asyncio.run(create_explicit_dispatch())

```

---

**Ruby**:

```ruby
require "livekit"

room_name = "my-room"
agent_name = "test-agent"

lkapi = LiveKit::LiveKitAPI.new

dispatch = lkapi.agent_dispatch.create_dispatch(
  room_name,
  agent_name,
  metadata: '{"user_id": "12345"}',
  # deployment: "staging", # Optional; empty = production
)

puts "successfully dispatched agent #{dispatch.agent_name} to #{dispatch.room}"

```

---

**Go**:

```go
func createAgentDispatch() {
	api, err := lksdk.NewLiveKitAPI()
	if err != nil {
		panic(err)
	}

	req := &livekit.CreateAgentDispatchRequest{
		Room:      "my-room",
		AgentName: "test-agent",
		Metadata:  "{\"user_id\": \"12345\"}",
		// Deployment: "staging", // Optional; empty = production
	}
	dispatch, err := api.AgentDispatch().CreateDispatch(context.Background(), req)
	if err != nil {
		panic(err)
	}
	fmt.Printf("Dispatch created: %v\n", dispatch)
}

```

---

**Kotlin**:

```kotlin
import io.livekit.server.LiveKitAPI

val roomName = "my-room"
val agentName = "test-agent"

fun createExplicitDispatch() {
    val api = LiveKitAPI.createClient()
    val response = api.agentDispatch.createDispatch(
        room = roomName,
        agentName = agentName,
        metadata = """{"user_id": "12345"}""",
    ).execute().body()
    if (response != null) {
        println("successfully dispatched agent ${response.agentName} to ${response.room}")
    } else {
        println("failed to create dispatch")
    }
}

```

---

**Rust**:

```rust
use livekit_api::services::LiveKitApi;
use livekit_protocol::CreateAgentDispatchRequest;

let api = LiveKitApi::new("https://my-livekit-host")?;
let dispatch = api
    .agent_dispatch()
    .create_dispatch(CreateAgentDispatchRequest {
        room: "my-room".to_string(),
        agent_name: "test-agent".to_string(),
        metadata: "{\"user_id\": \"12345\"}".to_string(),
        ..Default::default()
    })
    .await?;
println!("created dispatch {:?}", dispatch);

let dispatches = api.agent_dispatch().list_dispatch("my-room").await?;
println!("there are {} dispatches in my-room", dispatches.len());

```

The room, `my-room`, is automatically created during dispatch if it doesn't already exist, and the agent server assigns `test-agent` to it.

### Job metadata

Explicit dispatch allows you to pass metadata to the agent, available in the `JobContext`. This is useful for including details such as the user's ID, name, or phone number.

The metadata field is a string, limited to 512 KiB. LiveKit recommends using JSON to pass structured data.

The [examples](#via-api) in the previous section demonstrate how to pass job metadata during dispatch.

For information on consuming job metadata in an agent, see the following guide:

- **[Job metadata](https://docs.livekit.io/agents/server/job.md#metadata)**: Learn how to consume job metadata in an agent.

## Dispatch from inbound SIP calls

Agents can be explicitly dispatched for inbound SIP calls. [SIP dispatch rules](https://docs.livekit.io/telephony/accepting-calls/dispatch-rule.md) can define one or more agents using the `room_config.agents` field.

LiveKit recommends explicit agent dispatch for SIP inbound calls rather than automatic agent dispatch as it allows multiple agents within a single project.

## Dispatch via access token

You can include one or more agent dispatch entries in a participant's access token. When the first participant connects and creates the room, LiveKit dispatches the specified agents.

> ℹ️ **Applied on room creation only**
> 
> Agent dispatch from the token only occurs when the room is first created. If the room already exists, the token's dispatch configuration is ignored. Use a unique room name per session or [dispatch via API](#via-api) for more control.

The following example creates a token that dispatches the `test-agent` agent to the `my-room` room:

**LiveKit CLI**:

The following example assumes the environment variables `LIVEKIT_API_KEY` and `LIVEKIT_API_SECRET` are set:

```shell
lk token create \
  --identity "my-participant" \
  --room "my-room" \
  --agent "test-agent" \
  --join

```

---

**Node.js**:

```ts
import { RoomAgentDispatch, RoomConfiguration } from '@livekit/protocol';
import { AccessToken } from 'livekit-server-sdk';

const roomName = 'my-room';
const agentName = 'test-agent';

async function createTokenWithAgentDispatch(): Promise<string> {
  const at = new AccessToken();
  at.identity = 'my-participant';
  at.addGrant({ roomJoin: true, room: roomName });
  at.roomConfig = new RoomConfiguration({
    agents: [
      new RoomAgentDispatch({
        agentName: agentName,
        metadata: '{"user_id": "12345"}',
        // deployment: 'staging', // Optional; empty = production
      }),
    ],
  });
  return await at.toJwt();
}

```

---

**Python**:

```python
from livekit.api import (
  AccessToken,
  RoomAgentDispatch,
  RoomConfiguration,
  VideoGrants,
)

room_name = "my-room"
agent_name = "test-agent"

def create_token_with_agent_dispatch() -> str:
    token = (
        AccessToken()
        .with_identity("my_participant")
        .with_grants(VideoGrants(room_join=True, room=room_name))
        .with_room_config(
            RoomConfiguration(
                agents=[
                    RoomAgentDispatch(
                        agent_name="test-agent",
                        metadata='{"user_id": "12345"}',
                        # deployment="staging",  # Optional; empty = production
                    )
                ],
            ),
        )
        .to_jwt()
    )
    return token

```

---

**Ruby**:

```ruby
require "livekit"

roomName = "my-room"
agentName = "test-agent"

def create_token_with_agent_dispatch(roomName:, agentName:)
  token = LiveKit::AccessToken.new(
    api_key: ENV["LIVEKIT_API_KEY"],
    api_secret: ENV["LIVEKIT_API_SECRET"],
    identity: "my-participant",
  )
  token.video_grant = LiveKit::VideoGrant.new(roomJoin: true, room: roomName)
  token.room_config = LiveKit::Proto::RoomConfiguration.new(
    agents: [
      LiveKit::Proto::RoomAgentDispatch.new(
        agent_name: agentName,
        metadata: '{"user_id": "12345"}',
        # deployment: "staging", # Optional; empty = production
      ),
    ],
  )
  token.to_jwt
end

```

---

**Go**:

```go
func createTokenWithAgentDispatch() (string, error) {
	at := auth.NewAccessToken(
		os.Getenv("LIVEKIT_API_KEY"),
		os.Getenv("LIVEKIT_API_SECRET"),
	).
		SetIdentity("my-participant").
		SetName("Participant Name").
		SetVideoGrant(&auth.VideoGrant{
			Room:     "my-room",
			RoomJoin: true,
		}).
		SetRoomConfig(&livekit.RoomConfiguration{
			Agents: []*livekit.RoomAgentDispatch{
				{
					AgentName: "test-agent",
					Metadata:  "{\"user_id\": \"12345\"}",
					// Deployment: "staging", // Optional; empty = production
				},
			},
		})

	return at.ToJWT()
}

```

---

**Kotlin**:

```kotlin
import io.livekit.server.AccessToken
import io.livekit.server.RoomJoin
import io.livekit.server.RoomName
import livekit.LivekitAgentDispatch
import livekit.LivekitRoom.RoomConfiguration

val roomName = "my-room"
val agentName = "test-agent"

fun createTokenWithAgentDispatch(): String {
    val token = AccessToken(
        System.getenv("LIVEKIT_API_KEY")!!,
        System.getenv("LIVEKIT_API_SECRET")!!,
    )
    token.identity = "my-participant"
    token.addGrants(RoomJoin(true), RoomName(roomName))
    token.roomConfiguration = RoomConfiguration.newBuilder()
        .addAgents(
            LivekitAgentDispatch.RoomAgentDispatch.newBuilder()
                .setAgentName(agentName)
                .setMetadata("""{"user_id": "12345"}""")
                // .setDeployment("staging") // Optional; empty = production
                .build(),
        )
        .build()
    return token.toJwt()
}

```

---

**Rust**:

```rust
use livekit_api::access_token::{AccessToken, VideoGrants};
use livekit_protocol::{RoomAgentDispatch, RoomConfiguration};

fn create_token_with_agent_dispatch() -> Result<String, Box<dyn std::error::Error>> {
    let token = AccessToken::with_api_key(
        &std::env::var("LIVEKIT_API_KEY")?,
        &std::env::var("LIVEKIT_API_SECRET")?,
    )
    .with_identity("my-participant")
    .with_grants(VideoGrants { room_join: true, room: "my-room".to_string(), ..Default::default() })
    .with_room_config(RoomConfiguration {
        agents: vec![RoomAgentDispatch {
            agent_name: "test-agent".to_string(),
            metadata: "{\"user_id\": \"12345\"}".to_string(),
            ..Default::default()
        }],
        ..Default::default()
    })
    .to_jwt()?;
    Ok(token)
}

```

## Automatic agent dispatch

> 🔥 **Caution**
> 
> Automatic dispatch is not recommended for most applications. It dispatches an agent to every new room, regardless of whether one is needed, and doesn't support passing metadata to the agent session. Use one of the explicit dispatch methods described in this topic instead.

When `agent_name` is not set, an agent is automatically dispatched to each new room. This can be useful for simple prototypes where every room requires the same agent.

---

This document was rendered at 2026-08-24T21:31:39.205Z.
For the latest version of this document, see [https://docs.livekit.io/agents/server/agent-dispatch.md](https://docs.livekit.io/agents/server/agent-dispatch.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).
