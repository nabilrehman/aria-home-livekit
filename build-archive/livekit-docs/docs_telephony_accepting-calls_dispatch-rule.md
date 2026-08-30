warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /telephony/accepting-calls/dispatch-rule

LiveKit docs › Telephony › Accepting calls › Dispatch rule

---

# Dispatch rule

> How to create and configure a dispatch rule.

## Overview

A _dispatch rule_ determines which room each inbound SIP caller joins. You can send each caller to a dedicated room, put all callers in one room, or route them to a specific room by name or other criteria. When an inbound call reaches your SIP trunk and is handed off to LiveKit, the SIP service finds a matching dispatch rule and uses it to add the caller as a SIP participant to the appropriate room (creating the room if needed).

Create a dispatch rule using the `CreateSIPDispatchRule` API. By default, a dispatch rule matches all your trunks and makes a caller's phone number visible to others in the room. You can modify these defaults with dispatch rule options. For a full list of available options, see the [`CreateSIPDispatchRule`](https://docs.livekit.io/reference/telephony/sip-api.md#createsipdispatchrule) API reference.

> ❗ **Reuse dispatch rules across calls**
> 
> Dispatch rules are long-lived configuration objects meant to be reused. Create your dispatch rules once and reuse them for every call. Creating a new rule for each call adds unnecessary load and can degrade reliability at scale. To give each caller a unique room, rely on room naming within a single rule: an [individual dispatch rule](#individual-dispatch-rule) adds a random suffix per caller, and a [callee dispatch rule](#callee-dispatch-rule) names the room after the number that was dialed. To send each call to a specific, predetermined room, see [Route each call to a specific room with a unique ID](#route-to-specific-room).

## Dispatch to an agent

Use an individual dispatch rule to place each caller in their own room, and include the `roomConfig` option so your agent joins those rooms. See [Agent dispatch](#agent-dispatch) for `roomConfig` parameters.

### Individual dispatch rule

An `SIPDispatchRuleIndividual` rule creates a new room for each caller. The name of the created room is the phone number of the caller plus a random suffix. You can optionally add a specific prefix to the room name by using the `roomPrefix` option.

> 🔥 **Room names include the caller's phone number**
> 
> An individual dispatch rule names each room after the caller's phone number, which is personally identifiable information. Room names are recorded in logs and traces throughout LiveKit and aren't removed by [PII redaction](https://docs.livekit.io/deploy/observability/pii-redaction.md). To keep the phone number out of the room name, route each call to a predetermined room instead. See [Route each call to a specific room with a unique ID](#route-to-specific-room).

The following examples dispatch callers into individual rooms prefixed with `call-`, and [dispatches an agent](https://docs.livekit.io/agents/server/agent-dispatch.md) named `inbound-agent` to newly created rooms:

**LiveKit CLI**:

```json
{
  "dispatch_rule":
    {   
      "rule": {
        "dispatchRuleIndividual": {
          "roomPrefix": "call-"
        }   
      },  
      "name": "My dispatch rule",
      "roomConfig": {
        "agents": [{
          "agentName": "inbound-agent",
          "metadata": "job dispatch metadata"
        }]  
      }   
    }   
}

```

---

**Node.js**:

```typescript
import {
  LiveKitAPI,
  SipDispatchRuleIndividual,
  CreateSipDispatchRuleOptions,
} from 'livekit-server-sdk';
import { RoomConfiguration, RoomAgentDispatch } from '@livekit/protocol';

const api = new LiveKitAPI();

const rule: SipDispatchRuleIndividual = {
  roomPrefix: 'call-',
  type: 'individual',
};
const options: CreateSipDispatchRuleOptions = {
  name: 'My dispatch rule',
  roomConfig: new RoomConfiguration({
    agents: [
      new RoomAgentDispatch({
        agentName: 'inbound-agent',
        metadata: 'job dispatch metadata',
      }),
    ],
  }),
};

const dispatchRule = await api.sip.createSipDispatchRule(rule, options);
console.log('created dispatch rule', dispatchRule);

```

---

**Python**:

```python
from livekit import api

lkapi = api.LiveKitAPI()

# Create a dispatch rule to place each caller in a separate room
rule = api.SIPDispatchRule(
  dispatch_rule_individual = api.SIPDispatchRuleIndividual(
    room_prefix = 'call-',
  )
)

request = api.CreateSIPDispatchRuleRequest(
  dispatch_rule = api.SIPDispatchRuleInfo(
    rule = rule,
    name = 'My dispatch rule',
    trunk_ids = [],
    room_config=api.RoomConfiguration(
        agents=[api.RoomAgentDispatch(
            agent_name="inbound-agent",
            metadata="job dispatch metadata",
        )]
    )
  )
)

dispatch = await lkapi.sip.create_sip_dispatch_rule(request)
print("created dispatch", dispatch)
await lkapi.aclose()

```

---

**Ruby**:

```ruby
require 'livekit'

lkapi = LiveKit::LiveKitAPI.new

rule = LiveKit::Proto::SIPDispatchRule.new(
  dispatch_rule_individual: LiveKit::Proto::SIPDispatchRuleIndividual.new(
    room_prefix: "call-",
  )
)

resp = lkapi.sip.create_sip_dispatch_rule(
  rule,
  name: "My dispatch rule",
  room_config: LiveKit::Proto::RoomConfiguration.new(
    agents: [
      LiveKit::Proto::RoomAgentDispatch.new(
        agent_name: "inbound-agent",
        metadata: "job dispatch metadata",
      )
    ]
  )
)

puts resp

```

---

**Go**:

```go
package main

import (
  "context"
  "fmt"

  "github.com/livekit/protocol/livekit"
  lksdk "github.com/livekit/server-sdk-go/v2"
)

func main() {
  rule := &livekit.SIPDispatchRule{
    Rule: &livekit.SIPDispatchRule_DispatchRuleIndividual{
      DispatchRuleIndividual: &livekit.SIPDispatchRuleIndividual{
        RoomPrefix: "call-",
      },
    },
  }

  request := &livekit.CreateSIPDispatchRuleRequest{
    DispatchRule: &livekit.SIPDispatchRuleInfo{
      Name: "My dispatch rule",
      Rule: rule,
      RoomConfig: &livekit.RoomConfiguration{
        Agents: []*livekit.RoomAgentDispatch{
          {
            AgentName: "inbound-agent",
            Metadata:  "job dispatch metadata",
          },
        },
      },
    },
  }

  api, err := lksdk.NewLiveKitAPI()
  if err != nil {
    fmt.Println(err)
    return
  }

  // Execute the request
  dispatchRule, err := api.SIP().CreateSIPDispatchRule(context.Background(), request)
  if err != nil {
    fmt.Println(err)
  } else {
    fmt.Println(dispatchRule)
  }
}

```

---

**Kotlin**:

```kotlin
import io.livekit.server.LiveKitAPI
import io.livekit.server.SipDispatchRuleIndividual
import io.livekit.server.CreateSipDispatchRuleOptions
import livekit.LivekitRoom.RoomConfiguration
import livekit.LivekitAgentDispatch

val api = LiveKitAPI.createClient(
  host = System.getenv("LIVEKIT_URL"),
  apiKey = System.getenv("LIVEKIT_API_KEY"),
  secret = System.getenv("LIVEKIT_API_SECRET")
)

val rule = SipDispatchRuleIndividual(
    roomPrefix = "call-"
)

val roomConfig = RoomConfiguration.newBuilder()
    .addAgents(
        LivekitAgentDispatch.RoomAgentDispatch.newBuilder()
            .setAgentName("inbound-agent")
            .setMetadata("job dispatch metadata")
            .build()
    )
    .build()

val response = api.sip.createSipDispatchRule(
    rule = rule,
    options = CreateSipDispatchRuleOptions(
      name = "My dispatch rule",
      roomConfig = roomConfig
    )
).execute()

if (response.isSuccessful) {
    val dispatchRule = response.body()
    println("Dispatch rule created: ${dispatchRule}")
}

```

---

**Rust**:

```rust
use livekit_api::services::sip::CreateSIPDispatchRuleOptions;
use livekit_api::services::LiveKitApi;
use livekit_protocol as proto;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // host is required; API key and secret are read from
    // LIVEKIT_API_KEY and LIVEKIT_API_SECRET.
    let api = LiveKitApi::new("https://<your-subdomain>.livekit.cloud")?;

    let rule = proto::sip_dispatch_rule::Rule::DispatchRuleIndividual(
        proto::SipDispatchRuleIndividual {
            room_prefix: "call-".to_owned(),
            ..Default::default()
        },
    );

    let options = CreateSIPDispatchRuleOptions {
        name: "My dispatch rule".to_owned(),
        // Dispatch an agent into each room created by this rule.
        room_config: Some(proto::RoomConfiguration {
            agents: vec![proto::RoomAgentDispatch {
                agent_name: "inbound-agent".to_owned(),
                metadata: "job dispatch metadata".to_owned(),
                ..Default::default()
            }],
            ..Default::default()
        }),
        ..Default::default()
    };

    let dispatch_rule = api.sip().create_sip_dispatch_rule(rule, options).await?;
    println!("created dispatch rule {:?}", dispatch_rule);
    Ok(())
}

```

---

**LiveKit Cloud**:

1. Sign in to the **LiveKit Cloud** [dashboard](https://cloud.livekit.io/).
2. Select **Telephony** → [**Dispatch rules**](https://cloud.livekit.io/projects/p_/telephony/dispatch).
3. Select **Create new dispatch rule**.
4. Select the **JSON editor** tab.

> ℹ️ **Full parameter access**
> 
> You can also use the **Dispatch rule details** tab to create a dispatch rule. However, the JSON editor allows you to configure all available [parameters](https://docs.livekit.io/reference/telephony/sip-api.md#createsipdispatchrule).
5. Copy and paste the following JSON:

```json
 {
   "rule": {
     "dispatchRuleIndividual": {
       "roomPrefix": "call-"
     }
   },
   "name": "My dispatch rule",
   "roomConfig": {
     "agents": [{
       "agentName": "inbound-agent",
       "metadata": "job dispatch metadata"
     }]
   }
 }

```
6. Select **Create**.

> ℹ️ **Wildcard dispatch rule**
> 
> When you omit the `trunk_ids` field, the dispatch rule matches calls from all inbound trunks.

### Agent dispatch

Use the `roomConfig` parameter on a dispatch rule to specify which agents are dispatched to a room when it's created. The `agents` parameter for `roomConfig` is an array of agent dispatch entries. Each entry can include the following fields:

- `agentName`: Name of the agent to dispatch (required).
- `metadata`: Optional string metadata passed to the agent job.

Your agent receives the `metadata` string as job metadata. Access it in the entrypoint function using `ctx.job.metadata`. This is useful for routing or customizing agent behavior based on the dispatch rule. For example, you can route calls to different data stores or workflows:

**Python**:

```python
import json

@server.rtc_session(agent_name="inbound-agent")
async def my_agent(ctx: JobContext):
    metadata = json.loads(ctx.job.metadata)
    store_id = metadata.get("store_id")
    # Route to the correct store based on dispatch metadata

```

---

**Node.js**:

```typescript
export default {
  async entry(ctx: JobContext) {
    const metadata = JSON.parse(ctx.job.metadata);
    const storeId = metadata.storeId;
    // Route to the correct store based on dispatch metadata
  },
};

```

To learn more, see [Job metadata](https://docs.livekit.io/agents/server/job.md#metadata).

For the full set of room configuration options, see [`RoomConfiguration`](https://docs.livekit.io/reference/telephony/sip-api.md#roomconfiguration) in the SIP API reference. For agent dispatch behavior and configuration, see [Agent dispatch](https://docs.livekit.io/agents/server/agent-dispatch.md).

## Dispatch to rooms

The following rule types dispatch callers to shared rooms. Use them when you want all callers in the same room or when room assignment is based on the called number.

> ℹ️ **Shared rooms**
> 
> A direct dispatch rule with a static `roomName`, or a callee dispatch rule with `randomize` set to `false`, routes unrelated callers into the same room, where they can hear each other. For production telephony where each caller should be isolated, use an [individual dispatch rule](#individual-dispatch-rule) or a callee rule with the default `randomize=true` so each call gets a unique room.

### Direct dispatch rule

A direct dispatch rule places all callers into a specified room. You can optionally protect room access by adding a pin in the `pin` field:

In the following examples, all calls are immediately connected to room `open-room` on LiveKit.

**LiveKit CLI**:

1. Create a file named `dispatch-rule.json` and add the following:

```json
 {
   "dispatch_rule":
     {   
       "rule": {
         "dispatchRuleDirect": {
           "roomName": "open-room"
         }   
       },  
       "name": "My dispatch rule"
     }   
 }

```
2. Create the dispatch rule using `lk`:

```shell
lk sip dispatch create dispatch-rule.json

```

---

**Node.js**:

```typescript
import {
  LiveKitAPI,
  SipDispatchRuleDirect,
  CreateSipDispatchRuleOptions,
  ServerError,
} from 'livekit-server-sdk';

const api = new LiveKitAPI();

// Dispatch all callers to the same room
const rule: SipDispatchRuleDirect = {
  roomName: 'open-room',
  type: 'direct',
};

const options: CreateSipDispatchRuleOptions = {
  name: 'My dispatch rule',
};

try {
  const dispatchRule = await api.sip.createSipDispatchRule(rule, options);
  console.log(dispatchRule);
} catch (e) {
  if (e instanceof ServerError) {
    console.error(`${e.code} error: ${e.message}`);
  } else {
    throw e;
  }
}

```

---

**Python**:

```python
import asyncio

from livekit import api

async def main():
  livekit_api = api.LiveKitAPI()

  # Create a dispatch rule to place all callers in the same room
  rule = api.SIPDispatchRule(
    dispatch_rule_direct = api.SIPDispatchRuleDirect(
      room_name = 'open-room',
    )
  )

  request = api.CreateSIPDispatchRuleRequest(
    dispatch_rule = api.SIPDispatchRuleInfo(
      rule = rule,
      name = 'My dispatch rule',
    )
  )

  try:
    dispatchRule = await livekit_api.sip.create_sip_dispatch_rule(request)
    print(f"Successfully created {dispatchRule}")
  except api.ServerError as e:
    print(f"{e.code} error: {e.message}")

  await livekit_api.aclose()

asyncio.run(main())

```

---

**Ruby**:

```ruby
require 'livekit'

name = "My dispatch rule"
room_name = "open-room"

lkapi = LiveKit::LiveKitAPI.new

rule = LiveKit::Proto::SIPDispatchRule.new(
  dispatch_rule_direct: LiveKit::Proto::SIPDispatchRuleDirect.new(
    room_name: room_name,
  )
)

begin
  resp = lkapi.sip.create_sip_dispatch_rule(
    rule,
    name: name,
  )
  puts resp
rescue LiveKit::ServerError => e
  puts "#{e.code} error: #{e.message}"
end

```

---

**Go**:

```go
package main

import (
  "context"
  "errors"
  "fmt"

  "github.com/livekit/protocol/livekit"
  lksdk "github.com/livekit/server-sdk-go/v2"
)

func main() {

  // Specify rule type and options
  rule := &livekit.SIPDispatchRule{
    Rule: &livekit.SIPDispatchRule_DispatchRuleDirect{
      DispatchRuleDirect: &livekit.SIPDispatchRuleDirect{
        RoomName: "open-room",
      },
    },
  }

  // Create request
  request := &livekit.CreateSIPDispatchRuleRequest{
    DispatchRule: &livekit.SIPDispatchRuleInfo{
      Rule: rule,
      Name: "My dispatch rule",
    },
  }

  api, err := lksdk.NewLiveKitAPI()
  if err != nil {
    fmt.Println(err)
    return
  }

  // Execute the request
  dispatchRule, err := api.SIP().CreateSIPDispatchRule(context.Background(), request)

  if err != nil {
    var se lksdk.ServerError
    if errors.As(err, &se) {
      fmt.Printf("%s error: %s\n", se.Code(), se.Msg())
    } else {
      fmt.Println(err)
    }
  } else {
    fmt.Println(dispatchRule)
  }
}

```

---

**Kotlin**:

```kotlin
import io.livekit.server.LiveKitAPI
import io.livekit.server.SipDispatchRuleDirect
import io.livekit.server.CreateSipDispatchRuleOptions
import io.livekit.server.ServerError

val api = LiveKitAPI.createClient(
  host = System.getenv("LIVEKIT_URL"),
  apiKey = System.getenv("LIVEKIT_API_KEY"),
  secret = System.getenv("LIVEKIT_API_SECRET")
)

val rule = SipDispatchRuleDirect(
    roomName = "open-room"
)

val response = api.sip.createSipDispatchRule(
    rule = rule,
    options = CreateSipDispatchRuleOptions(
      name = "My dispatch rule"
    )
).execute()

if (response.isSuccessful) {
    val dispatchRule = response.body()
    println("Dispatch rule created: ${dispatchRule}")
} else {
    val error = ServerError.from(response)
    println("${error?.code} error: ${error?.message}")
}

```

---

**Rust**:

```rust
use livekit_api::services::sip::CreateSIPDispatchRuleOptions;
use livekit_api::services::LiveKitApi;
use livekit_protocol as proto;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // host is required; API key and secret are read from
    // LIVEKIT_API_KEY and LIVEKIT_API_SECRET.
    let api = LiveKitApi::new("https://<your-subdomain>.livekit.cloud")?;

    // Dispatch all callers to the same room
    let rule = proto::sip_dispatch_rule::Rule::DispatchRuleDirect(proto::SipDispatchRuleDirect {
        room_name: "open-room".to_owned(),
        ..Default::default()
    });

    let options = CreateSIPDispatchRuleOptions {
        name: "My dispatch rule".to_owned(),
        ..Default::default()
    };

    match api.sip().create_sip_dispatch_rule(rule, options).await {
        Ok(dispatch_rule) => println!("{:?}", dispatch_rule),
        Err(e) => eprintln!("failed to create dispatch rule: {e}"),
    }
    Ok(())
}

```

---

**LiveKit Cloud**:

1. Sign in to the **LiveKit Cloud** [dashboard](https://cloud.livekit.io/).
2. Select **Telephony** → [**Dispatch rules**](https://cloud.livekit.io/projects/p_/telephony/dispatch).
3. Select **Create new dispatch rule**.
4. Select the **JSON editor** tab.

> ℹ️ **Form editor**
> 
> You can also use the **Dispatch rule details** tab for this example by selecting **Direct** for **Rule type**.
5. Copy and paste the following JSON:

```json
 {
   "rule": {
     "dispatchRuleDirect": {
       "roomName": "open-room"
     }
   },
   "name": "My dispatch rule"
 }

```
6. Select **Create**.

#### Pin-protected room

Add a `pin` to a room to require callers to enter a pin to connect to a room in LiveKit. The following example requires callers to enter `12345#` on the phone to enter `safe-room`:

```json
{
  "dispatch_rule":
    {
      "trunk_ids": [],
      "rule": {
        "dispatchRuleDirect": {
          "roomName": "safe-room",
          "pin": "12345"
        }
      },
      "name": "My dispatch rule"
    }
}

```

### Callee dispatch rule

This creates a dispatch rule that puts callers into rooms based on the called number. The name of the room is the called phone number plus an optional prefix (if `roomPrefix` is set). You can optionally add a random suffix for each caller by setting `randomize` to true, making a separate room per caller.

**LiveKit CLI**:

```json
{
  "dispatch_rule":
    {
      "rule": {
        "dispatchRuleCallee": {
          "roomPrefix": "number-",
          "randomize": false
        }
      },
      "name": "My dispatch rule"
    }
}

```

---

**Node.js**:

For an executable example, replace the rule in the [Direct dispatch rule](#direct-dispatch-rule) example with the following rule:

```typescript
import { SipDispatchRuleCallee } from 'livekit-server-sdk';

// Create a dispatch rule to place callers to the same phone number in the same room
const rule: SipDispatchRuleCallee = {
  roomPrefix: 'number-',
  randomize: false,
  type: 'callee',
};

```

---

**Python**:

For an executable example, replace the rule in the [Direct dispatch rule](#direct-dispatch-rule) example with the following rule:

```python
from livekit import api

# Create a dispatch rule to place callers to the same phone number in the same room
rule = api.SIPDispatchRule(
  dispatch_rule_callee = api.SIPDispatchRuleCallee(
    room_prefix = 'number-',
    randomize = False,
  )
)

```

---

**Ruby**:

For an executable example, replace the rule in the [Direct dispatch rule](#direct-dispatch-rule) example with the following rule:

```ruby
rule = LiveKit::Proto::SIPDispatchRule.new(
  dispatch_rule_callee: LiveKit::Proto::SIPDispatchRuleCallee.new(
    room_prefix: 'number-',
    randomize: false,
  )
)

```

---

**Go**:

For an executable example, replace the rule in the [Direct dispatch rule](#direct-dispatch-rule) example with the following rule:

```go
  rule := &livekit.SIPDispatchRule{
    Rule: &livekit.SIPDispatchRule_DispatchRuleCallee{
      DispatchRuleCallee: &livekit.SIPDispatchRuleCallee{
        RoomPrefix: "number-",
        Randomize: false,
      },
    },
  }

```

---

**Kotlin**:

For an executable example, replace the rule in the [Direct dispatch rule](#direct-dispatch-rule) example with the following rule:

```kotlin
import io.livekit.server.SipDispatchRuleCallee

// Create a dispatch rule to place callers to the same phone number in the same room
val rule = SipDispatchRuleCallee(
    roomPrefix = "number-",
    randomize = false,
)

```

---

**Rust**:

For an executable example, replace the rule in the [Direct dispatch rule](#direct-dispatch-rule) example with the following rule:

```rust
let rule = proto::sip_dispatch_rule::Rule::DispatchRuleCallee(proto::SipDispatchRuleCallee {
    room_prefix: "number-".to_owned(),
    randomize: false,
    ..Default::default()
});

```

---

**LiveKit Cloud**:

1. Sign in to the **LiveKit Cloud** [dashboard](https://cloud.livekit.io/).
2. Select **Telephony** → [**Dispatch rules**](https://cloud.livekit.io/projects/p_/telephony/dispatch).
3. Select **Create new dispatch rule**.
4. Select the **JSON editor** tab.

> ℹ️ **Form editor**
> 
> You can also use the **Dispatch rule details** tab for this example by selecting **Callee** for **Rule type**.
5. Copy and paste the following JSON:

```json
 {
   "rule": {
     "dispatchRuleCallee": {
       "roomPrefix": "number-",
       "randomize": false
     }
   },
   "name": "My dispatch rule"
 }

```
6. Select **Create**.

### Route each call to a specific room with a unique ID

To route each inbound call to a specific room, use a single callee dispatch rule and control the SIP `To` header. This lets you route every call to a specific room without creating separate trunks or dispatch rules for individual destinations. It keeps the configuration simple and reusable.

A callee dispatch rule names the room after the _called_ destination, that is, the user part of the SIP `To` header. When `randomize` is `false` and `roomPrefix` is unset, the room name is set to that value, with no random suffix or prefix. The destination SIP username accepts alphanumeric characters and dashes, so you can use a UUID or other unique identifier as the destination and create a room with the same name.

> ❗ **Requires control of the SIP To header**
> 
> This pattern requires control of the destination SIP username in the `To` header, such as when using Twilio TwiML or your own SIP infrastructure. It doesn't apply to calls placed to a fixed LiveKit phone number, where the destination is the phone number itself.

#### Step 1. Create a wildcard inbound trunk

Create a single inbound trunk with no `numbers` set so it accepts calls to any destination. Secure the trunk with authentication, and note the trunk ID that the command returns.

1. Create an `inbound-trunk.json` file with the following contents:

```json
{
  "trunk": {
    "name": "Wildcard inbound trunk"
  }
}

```
2. Create the trunk with the CLI, passing the same username and password your caller uses to authenticate:

```shell
lk sip inbound create inbound-trunk.json \
  --auth-user <sip_trunk_username> \
  --auth-pass <sip_trunk_password>

```

Save the trunk ID in the output for use in the next step.

#### Step 2. Create a callee dispatch rule

Create a single callee dispatch rule bound to the trunk from the previous step. Set `randomize` to `false` and omit `roomPrefix` so the room name matches the destination exactly. Use `roomConfig` to dispatch your agent to each room the rule creates.

1. Create a `dispatch-rule.json` file with the following contents. Replace `<trunk-id>` with the ID from the previous step:

```json
{
  "dispatch_rule": {
    "rule": {
      "dispatchRuleCallee": {
        "randomize": false
      }
    },
    "name": "Route by ID",
    "trunk_ids": ["<trunk-id>"],
    "roomConfig": {
      "agents": [{
        "agentName": "inbound-agent"
      }]
    }
  }
}

```

This example dispatches the agent `inbound-agent` to the room after the SIP participant joins the room. To create the room and have the agent ready ahead of time, see [Pre-warm the room and agent](#pre-warm).
2. Create the dispatch rule with the CLI:

```shell
lk sip dispatch create dispatch-rule.json

```

#### Step 3. Set the destination to your unique ID

Generate a unique ID for the call and place it in the destination SIP username. The following [Twilio TwiML Bin](https://docs.livekit.io/telephony/accepting-calls/inbound-twilio.md) routes an inbound call to LiveKit with a UUID as the destination:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Dial>
    <Sip username="<sip_trunk_username>" password="<sip_trunk_password>">
      sip:123e4567-e89b-12d3-a456-426614174000@<your SIP endpoint>;transport=tcp
    </Sip>
  </Dial>
</Response>

```

Replace the UUID with an ID your app generates for each call, and `<your SIP endpoint>` with your project's [SIP endpoint](https://docs.livekit.io/telephony/start/sip-trunk-setup.md#sip-endpoint). Generate a fresh ID per call, typically from the webhook or app that returns the TwiML.

#### Step 4. Read the ID in your agent

The room name matches the ID you set. Your agent can read the ID and use it to load per-call context from a database or API that you control. The same value is also available as the `sip.trunkPhoneNumber` [participant attribute](https://docs.livekit.io/reference/telephony/sip-participant.md#sip-attributes).

**Python**:

```python
@server.rtc_session(agent_name="inbound-agent")
async def my_agent(ctx: JobContext):
    # The room name matches the unique ID set in the SIP `To` header
    call_id = ctx.room.name

    # Define a function named load_call_context that loads
    # per-call context that your application controls
    context = await load_call_context(call_id)

```

---

**Node.js**:

```typescript
export default {
  async entry(ctx: JobContext) {
    // The room name matches the unique ID set in the SIP `To` header
    const callId = ctx.room.name;

    // Define a function named loadCallContext that loads
    // per-call context that your application controls
    const context = await loadCallContext(callId);
  },
};

```

#### Pre-warm the room and agent

Because you choose the ID before the call connects, you can dispatch your agent to a room with that name ahead of time using the [`AgentDispatchService`](https://docs.livekit.io/agents/server/agent-dispatch.md#via-api) API. The agent dispatch creates the room if it doesn't already exist. When the call arrives, the SIP participant joins the existing room and the agent is ready immediately.

## Setting custom attributes on inbound SIP participants

LiveKit participants have an `attributes` field that stores key-value pairs. You can add custom attributes for SIP participants in the dispatch rule. These attributes are inherited by all SIP participants created by the dispatch rule.

To learn more, see [SIP participant attributes](https://docs.livekit.io/reference/telephony/sip-participant.md#sip-participant-attributes).

The following examples add two attributes to SIP participants created by this dispatch rule:

**LiveKit CLI**:

```json
{
  "dispatch_rule":
    {
      "attributes": {
        "<key_name1>": "<value1>",
        "<key_name2>": "<value2>"
      },
      "rule": {
        "dispatchRuleIndividual": {
          "roomPrefix": "call-"
        }
      },
      "name": "My dispatch rule"
    }
}

```

---

**Node.js**:

For an executable example, replace `options` in the [Direct dispatch rule](#direct-dispatch-rule) example with the following options:

```typescript
const options: CreateSipDispatchRuleOptions = {
  name: 'My dispatch rule',
  attributes: {
    "<key_name1>": "<value1>",
    "<key_name2>": "<value2>"
  },
};

```

---

**Python**:

For an executable example, replace `request` in the [Direct dispatch rule](#direct-dispatch-rule) example with the following options:

```python
request = api.CreateSIPDispatchRuleRequest(
  dispatch_rule = api.SIPDispatchRuleInfo(
    rule = rule,
    name = 'My dispatch rule',
    attributes = {
      "<key_name1>": "<value1>",
      "<key_name2>": "<value2>",
    }
  )
)

```

---

**Ruby**:

For an executable example, use the [Direct dispatch rule](#direct-dispatch-rule) example with the following options:

```ruby
resp = lkapi.sip.create_sip_dispatch_rule(
  rule,
  name: name,
  attributes: {
    "<key_name1>" => "<value1>",
    "<key_name2>" => "<value2>",
  },
)

```

---

**Go**:

For an executable example, replace `request` in the [Direct dispatch rule](#direct-dispatch-rule) example with the following code:

```go
  // Create a request
  request := &livekit.CreateSIPDispatchRuleRequest{
    DispatchRule: &livekit.SIPDispatchRuleInfo{
      Rule: rule,
      Name: "My dispatch rule",
      Attributes: map[string]string{
        "<key_name1>": "<value1>",
        "<key_name2>": "<value2>",
      },
    },
  }

```

---

**Kotlin**:

For an executable example, modify the parameters for `CreateSipDispatchRuleOptions` in the [Direct dispatch rule](#direct-dispatch-rule) example to include the `attributes` parameter:

```kotlin
val response = api.sip.createSipDispatchRule(
    rule = rule,
    options = CreateSipDispatchRuleOptions(
      name = "My dispatch rule",
      attributes = mapOf(
        "<key_name1>" to "<value1>",
        "<key_name2>" to "<value2>"
      )
    )
).execute()

```

---

**Rust**:

For an executable example, replace `options` in the [Direct dispatch rule](#direct-dispatch-rule) example with the following options:

```rust
use std::collections::HashMap;

let options = CreateSIPDispatchRuleOptions {
    name: "My dispatch rule".to_owned(),
    attributes: HashMap::from([
        ("<key_name1>".to_owned(), "<value1>".to_owned()),
        ("<key_name2>".to_owned(), "<value2>".to_owned()),
    ]),
    ..Default::default()
};

```

---

**LiveKit Cloud**:

1. Sign in to the **LiveKit Cloud** [dashboard](https://cloud.livekit.io/).
2. Select **Telephony** → [**Dispatch rules**](https://cloud.livekit.io/projects/p_/telephony/dispatch).
3. Select **Create new dispatch rule**.
4. Select the **JSON editor** tab.

> ℹ️ **Attributes parameter availability**
> 
> The `attributes` parameter is only available in the **JSON editor** tab.
5. Copy and paste the following text into the editor:

```json
{
  "name": "My dispatchrule",
  "attributes": {
    "<key_name1>": "<value1>",
    "<key_name2>": "<value2>"
  },
  "rule": {
    "dispatchRuleIndividual": {
      "roomPrefix": "call-"
    }
  }
}

```
6. Select **Create**.

## Setting custom metadata on inbound SIP participants

LiveKit participants have a `metadata` field that can store arbitrary data for your application (typically JSON). It can also be set on SIP participants created by a dispatch rule. Specifically, `metadata` set on a dispatch rule will be inherited by all SIP participants created by it.

The following examples add the metadata, `{"is_internal": true}`, to all SIP participants created from an inbound call by this dispatch rule:

**LiveKit CLI**:

```json
{
  "dispatch_rule": {
    "metadata": "{\"is_internal\": true}",
    "rule": {
      "dispatchRuleIndividual": {
        "roomPrefix": "call-"
      }
    },
    "name": "My dispatch rule"
  }
}

```

---

**Node.js**:

For an executable example, replace `options` in the [Direct dispatch rule](#direct-dispatch-rule) example with the following options:

```typescript
const options: CreateSipDispatchRuleOptions = {
  name: 'My dispatch rule',
  metadata: "{\"is_internal\": true}",
};

```

---

**Python**:

For an executable example, replace `request` in the [Direct dispatch rule](#direct-dispatch-rule) example with the following options:

```python
  request = api.CreateSIPDispatchRuleRequest(
    dispatch_rule = api.SIPDispatchRuleInfo(
      rule = rule,
      name = 'My dispatch rule',
      metadata = "{\"is_internal\": true}",
    )
  )

```

---

**Ruby**:

For an executable example, use the [Direct dispatch rule](#direct-dispatch-rule) example with the following options:

```ruby
resp = lkapi.sip.create_sip_dispatch_rule(
  rule,
  name: name,
  metadata: "{\"is_internal\": true}",
)

```

---

**Go**:

For an executable example, replace `request` in the [Direct dispatch rule](#direct-dispatch-rule) example with the following options:

```go
  // Create a request
  request := &livekit.CreateSIPDispatchRuleRequest{
    DispatchRule: &livekit.SIPDispatchRuleInfo{
      Rule: rule,
      Name: "My dispatch rule",
      Metadata: "{\"is_internal\": true}",
    },
  }

```

---

**Kotlin**:

For an executable example, modify the parameters for `CreateSipDispatchRuleOptions` in the [Direct dispatch rule](#direct-dispatch-rule) example to include the `metadata` parameter:

```kotlin
val response = api.sip.createSipDispatchRule(
    rule = rule,
    options = CreateSipDispatchRuleOptions(
      name = "My dispatch rule",
      metadata = "{\"is_internal\": true}"
    )
).execute()

```

---

**Rust**:

For an executable example, replace `options` in the [Direct dispatch rule](#direct-dispatch-rule) example with the following options:

```rust
let options = CreateSIPDispatchRuleOptions {
    name: "My dispatch rule".to_owned(),
    metadata: "{\"is_internal\": true}".to_owned(),
    ..Default::default()
};

```

---

**LiveKit Cloud**:

1. Sign in to the **LiveKit Cloud** [dashboard](https://cloud.livekit.io/).
2. Select **Telephony** → [**Dispatch rules**](https://cloud.livekit.io/projects/p_/telephony/dispatch).
3. Select **Create new dispatch rule**.
4. Select the **JSON editor** tab.

> ℹ️ **Metadata parameter availability**
> 
> The `metadata` parameter is only available in the **JSON editor** tab.
5. Copy and paste the following text into the editor:

```json
{
  "name": "My dispatch rule",
  "metadata": "{\"is_internal\": true}",
  "rule": {
    "dispatchRuleIndividual": {
      "roomPrefix": "call-"
    }
  }
}

```
6. Select **Create**.

## Update dispatch rule

Use the [`UpdateSIPDispatchRule`](https://docs.livekit.io/reference/telephony/sip-api.md#updatesipdispatchrule) API to update specific fields of a dispatch rule or [replace](#replace-dispatch-rule) a dispatch rule with a new one.

### Update specific fields of a dispatch rule

The `UpdateSIPDispatchRuleFields` API allows you to update specific fields of a dispatch rule without affecting other fields.

**LiveKit CLI**:

Create a file named `dispatch-rule.json` with the following content:

```json
{
  "name": "My updated dispatch rule",
  "rule": {
    "dispatchRuleCallee": {
      "roomPrefix": "number-",
      "randomize": false,
      "pin": "1234"
    }
  }
}

```

Update the dispatch rule using `lk`. You can update the `trunks` parameter to a comma-separated string of trunks IDs if the rule matches specific trunks.

```shell
lk sip dispatch update --id <dispatch-rule-id> \
  --trunks "[]" \
  dispatch-rule.json

```

---

**Node.js**:

```typescript
import { LiveKitAPI } from 'livekit-server-sdk';
import { ListUpdate } from '@livekit/protocol';

const api = new LiveKitAPI();

const ruleId = '<dispatch-rule-id>';

const updatedRuleFields = {
  name: 'My updated dispatch rule',
  trunkIds: new ListUpdate({ add: ["<trunk-id1>", "<trunk-id2>"] }), // Add trunk IDs to the dispatch rule
  metadata: "{\"is_internal\": false}",
};

const rule = await api.sip.updateSipDispatchRuleFields(
  ruleId,
  updatedRuleFields,
);

console.log(rule);

```

---

**Python**:

```python
import asyncio

from livekit import api
from livekit.protocol.models import ListUpdate


async def main():
  """Use the update_sip_dispatch_rule_fields method to update specific fields of a dispatch rule."""

  rule_id = '<dispatch-rule-id>'

  livekit_api = api.LiveKitAPI()
  dispatchRule = None

  try:
    dispatchRule = await livekit_api.sip.update_sip_dispatch_rule_fields(
        rule_id=rule_id,
        trunk_ids=ListUpdate(add=["<trunk-id1>", "<trunk-id2>"]), # Add trunk IDs to the dispatch rule
        metadata="{\"is_internal\": false}",
        attributes={
          "<updated_key1>": "<updated_value1>",
          "<updated_key2>": "<updated_value2>",
        }
    )
    print(f"Successfully updated {dispatchRule}")

  except api.ServerError as e:
    print(f"{e.code} error: {e.message}")

  await livekit_api.aclose()
  return dispatchRule

asyncio.run(main())

```

---

**Ruby**:

```ruby
require 'livekit'

lkapi = LiveKit::LiveKitAPI.new

rule_id = "<dispatch-rule-id>"

update = LiveKit::Proto::SIPDispatchRuleUpdate.new(
  name: "My updated dispatch rule",
  trunk_ids: LiveKit::Proto::ListUpdate.new(
    set: ["<trunk-id1>", "<trunk-id2>"]
  ),
  metadata: "{\"is_internal\": false}"
)

resp = lkapi.sip.update_sip_dispatch_rule_fields(rule_id, update)

puts resp

```

---

**Go**:

```go
package main

import (
  "context"
  "fmt"

  "github.com/livekit/protocol/livekit"
  lksdk "github.com/livekit/server-sdk-go/v2"
)

func main() {

  ruleId := "<dispatch-rule-id>"

  // Update dispatch rule
  name2 := "My updated dispatch rule"
  request := &livekit.UpdateSIPDispatchRuleRequest{
    SipDispatchRuleId: ruleId,
    Action: &livekit.UpdateSIPDispatchRuleRequest_Update{
      Update: &livekit.SIPDispatchRuleUpdate{
        Name: &name2,
        TrunkIds: &livekit.ListUpdate{
          Set: []string{"<trunk-id1>", "<trunk-id2>"},
        },
      },
    },
  }

  api, err := lksdk.NewLiveKitAPI()
  if err != nil {
    fmt.Println(err)
    return
  }

  updated, err := api.SIP().UpdateSIPDispatchRule(context.Background(), request)

  if err != nil {
    fmt.Println(err)
  } else {
    fmt.Println(updated)
  }
}

```

---

**Kotlin**:

The following updates the dispatch rule created in the [Direct dispatch rule](#direct-dispatch-rule) example. To update an individual dispatch rule, pass in a `SipDispatchRuleIndividual` object instead of a `SipDispatchRuleDirect` object.

```kotlin
import io.livekit.server.LiveKitAPI
import io.livekit.server.SipDispatchRuleDirect
import io.livekit.server.UpdateSipDispatchRuleOptions

val api = LiveKitAPI.createClient(
  host = System.getenv("LIVEKIT_URL"),
  apiKey = System.getenv("LIVEKIT_API_KEY"),
  secret = System.getenv("LIVEKIT_API_SECRET")
)

val response = api.sip.updateSipDispatchRule(
    sipDispatchRuleId = "<rule-id>",
    options = UpdateSipDispatchRuleOptions(
        name = "My updated dispatch rule",
        metadata = "{'key1': 'value1', 'key2': 'value2'}",
        rule = SipDispatchRuleDirect(
            roomName = "new-room"
        )
    )).execute()

if (response.isSuccessful) {
    val dispatchRule = response.body()
    println("Dispatch rule updated: ${dispatchRule}")
}

```

---

**Rust**:

```rust
use livekit_api::services::LiveKitApi;
use livekit_protocol as proto;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // host is required; API key and secret are read from
    // LIVEKIT_API_KEY and LIVEKIT_API_SECRET.
    let api = LiveKitApi::new("https://<your-subdomain>.livekit.cloud")?;

    let update = proto::SipDispatchRuleUpdate {
        name: Some("My updated dispatch rule".to_owned()),
        metadata: Some("{\"key1\": \"value1\", \"key2\": \"value2\"}".to_owned()),
        rule: Some(proto::SipDispatchRule {
            rule: Some(proto::sip_dispatch_rule::Rule::DispatchRuleDirect(
                proto::SipDispatchRuleDirect { room_name: "new-room".to_owned(), ..Default::default() },
            )),
        }),
        ..Default::default()
    };

    let dispatch_rule =
        api.sip().update_sip_dispatch_rule("<rule-id>".to_owned(), update).await?;

    println!("Dispatch rule updated: {:?}", dispatch_rule);
    Ok(())
}

```

---

**LiveKit Cloud**:

Update and replace functions are the same in the LiveKit Cloud dashboard. For an example, see the [replace dispatch rule](#replace-dispatch-rule) section.

### Replace dispatch rule

The `UpdateSIPDispatchRule` API allows you to replace an existing dispatch rule with a new one using the same dispatch rule ID.

**LiveKit CLI**:

The instructions for replacing a dispatch rule are the same as for [updating a dispatch rule](#update-specific-fields-of-a-dispatch-rule).

---

**Node.js**:

```typescript
import { LiveKitAPI } from 'livekit-server-sdk';
import {
  SIPDispatchRule,
  SIPDispatchRuleDirect,
  SIPDispatchRuleInfo,
} from '@livekit/protocol';

const api = new LiveKitAPI();

async function replaceDispatchRule(ruleId: string) {
  const ruleInfo = new SIPDispatchRuleInfo({
    name: 'My replaced dispatch rule',
    trunkIds: ['<trunk-id1>', '<trunk-id2>'],
    hidePhoneNumber: false,
    metadata: '{"is_internal": true}',
    rule: new SIPDispatchRule({
      rule: {
        case: 'dispatchRuleDirect',
        value: new SIPDispatchRuleDirect({ roomName: 'caller-room', pin: '1212' }),
      },
    }),
  });

  const updatedRule = await api.sip.updateSipDispatchRule(ruleId, ruleInfo);
  return updatedRule;
}

await replaceDispatchRule('<dispatch-rule-id>');

```

---

**Python**:

```python
import asyncio

from livekit import api


async def main():
  """Use the update_sip_dispatch_rule function to replace a dispatch rule."""

  livekit_api = api.LiveKitAPI()

  # Dispatch rule ID of rule to replace.
  rule_id = '<dispatch-rule-id>'

  # Dispatch rule type.
  rule = api.SIPDispatchRule(
    dispatch_rule_direct = api.SIPDispatchRuleDirect(
      room_name = "caller-room",
      pin = '1212'
    )
  )

  ruleInfo = api.SIPDispatchRuleInfo(
    rule = rule,
    name = 'My replaced dispatch rule',
    trunk_ids = ["<trunk-id1>", "<trunk-id2>"],
    hide_phone_number = True,
    metadata = "{\"is_internal\": false}",
    attributes = {
      "<replaced_key_name1>": "<replaced_value1>",
      "<replaced_key_name2>": "<replaced_value2>",
    },
  )

  dispatchRule = None
  try:
    dispatchRule = await livekit_api.sip.update_sip_dispatch_rule(
      rule_id,
      ruleInfo
    )
    print(f"Successfully replaced {dispatchRule}")

  except api.ServerError as e:
    print(f"{e.code} error: {e.message}")

  await livekit_api.aclose()
  return dispatchRule

asyncio.run(main())

```

---

**Ruby**:

```ruby
require 'livekit'

lkapi = LiveKit::LiveKitAPI.new

rule_id = "<dispatch-rule-id>"

rule = LiveKit::Proto::SIPDispatchRuleInfo.new(
  name: "My replaced dispatch rule",
  trunk_ids: ["<trunk-id1>", "<trunk-id2>"],
  hide_phone_number: false,
  metadata: "{\"is_internal\": true}",
  rule: LiveKit::Proto::SIPDispatchRule.new(
    dispatch_rule_direct: LiveKit::Proto::SIPDispatchRuleDirect.new(
      room_name: "caller-room",
      pin: "1212"
    )
  )
)

resp = lkapi.sip.update_sip_dispatch_rule(rule_id, rule)

puts resp

```

---

**Go**:

```go
package main

import (
  "context"
  "fmt"

  "github.com/livekit/protocol/livekit"
  lksdk "github.com/livekit/server-sdk-go/v2"
)

func main() {

  ruleId := "<dispatch-rule-id>"

  // Replace dispatch rule
  rule := &livekit.SIPDispatchRuleInfo{
    Name:     "My replaced dispatch rule",
    TrunkIds: []string{"<trunk-id1>", "<trunk-id2>"},
    Rule: &livekit.SIPDispatchRule{
      Rule: &livekit.SIPDispatchRule_DispatchRuleDirect{
        DispatchRuleDirect: &livekit.SIPDispatchRuleDirect{
          RoomName: "my-room",
        },
      },
    },
  }

  request := &livekit.UpdateSIPDispatchRuleRequest{
    SipDispatchRuleId: ruleId,
    Action: &livekit.UpdateSIPDispatchRuleRequest_Replace{
      Replace: rule,
    },
  }

  api, err := lksdk.NewLiveKitAPI()
  if err != nil {
    fmt.Println(err)
    return
  }

  updated, err := api.SIP().UpdateSIPDispatchRule(context.Background(), request)

  if err != nil {
    fmt.Println(err)
  } else {
    fmt.Println(updated)
  }
}

```

---

**Kotlin**:

Use `updateSipDispatchRule` with a new `rule` to replace an existing dispatch rule:

```kotlin
import io.livekit.server.LiveKitAPI
import io.livekit.server.SipDispatchRuleDirect
import io.livekit.server.UpdateSipDispatchRuleOptions

val api = LiveKitAPI.createClient(
  host = System.getenv("LIVEKIT_URL"),
  apiKey = System.getenv("LIVEKIT_API_KEY"),
  secret = System.getenv("LIVEKIT_API_SECRET")
)

val response = api.sip.updateSipDispatchRule(
    sipDispatchRuleId = "<dispatch-rule-id>",
    options = UpdateSipDispatchRuleOptions(
        name = "My replaced dispatch rule",
        trunkIds = listOf("<trunk-id1>", "<trunk-id2>"),
        metadata = "{\"is_internal\": true}",
        rule = SipDispatchRuleDirect(
            roomName = "caller-room"
        )
    )).execute()

if (response.isSuccessful) {
    val dispatchRule = response.body()
    println("Dispatch rule replaced: ${dispatchRule}")
}

```

---

**Rust**:

```rust
use livekit_api::services::LiveKitApi;
use livekit_protocol as proto;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // host is required; API key and secret are read from
    // LIVEKIT_API_KEY and LIVEKIT_API_SECRET.
    let api = LiveKitApi::new("https://<your-subdomain>.livekit.cloud")?;

    // Replace a dispatch rule entirely.
    let rule = proto::SipDispatchRuleInfo {
        name: "My replaced dispatch rule".to_owned(),
        trunk_ids: vec!["<trunk-id1>".to_owned(), "<trunk-id2>".to_owned()],
        hide_phone_number: false,
        metadata: "{\"is_internal\": true}".to_owned(),
        rule: Some(proto::SipDispatchRule {
            rule: Some(proto::sip_dispatch_rule::Rule::DispatchRuleDirect(
                proto::SipDispatchRuleDirect { room_name: "caller-room".to_owned(), ..Default::default() },
            )),
        }),
        ..Default::default()
    };

    let dispatch_rule = api
        .sip()
        .update_sip_dispatch_rule_replace("<dispatch-rule-id>".to_owned(), rule)
        .await?;

    println!("Dispatch rule replaced: {:?}", dispatch_rule);
    Ok(())
}

```

---

**LiveKit Cloud**:

1. Sign in to the **LiveKit Cloud** [dashboard](https://cloud.livekit.io/).
2. Select **Telephony** → [**Dispatch rules**](https://cloud.livekit.io/projects/p_/telephony/dispatch).
3. Navigate to the **Dispatch rules** section and find the dispatch rule you want to update.
4. Select the more (**⋮**) menu → select **Edit**.
5. Select the **JSON editor** tab and copy and paste the following text into the editor:

```json
 {
   "name": "My replaced dispatch rule",
   "rule": {
     "dispatchRuleIndividual": {
       "roomPrefix": "caller-room"
     }
   },
   "trunkIds": ["<trunk-id1>", "<trunk-id2>"],
   "hidePhoneNumber": false,
   "metadata": "{\"is_internal\": true}",
   "attributes": {
     "<replaced_key_name1>": "<replaced_value1>",
     "<replaced_key_name2>": "<replaced_value2>",
   }
 }

```
6. Select **Update**.

## List dispatch rules

Use the [`ListSIPDispatchRule`](https://docs.livekit.io/reference/telephony/sip-api.md#listsipdispatchrule) API to list all dispatch rules.

**LiveKit CLI**:

```shell
lk sip dispatch list

```

---

**Node.js**:

```typescript
import { LiveKitAPI } from 'livekit-server-sdk';

const api = new LiveKitAPI();

const rules = await api.sip.listSipDispatchRule();

console.log(rules);

```

---

**Python**:

```python
import asyncio

from livekit import api

async def main():
  livekit_api = api.LiveKitAPI()

  rules = await livekit_api.sip.list_sip_dispatch_rule(
    api.ListSIPDispatchRuleRequest()
  )
  print(f"{rules}")

  await livekit_api.aclose()

asyncio.run(main())

```

---

**Ruby**:

```ruby
require 'livekit'

lkapi = LiveKit::LiveKitAPI.new

resp = lkapi.sip.list_sip_dispatch_rule()

puts resp.items

```

---

**Go**:

```go
package main

import (
  "context"
  "fmt"

  "github.com/livekit/protocol/livekit"
  lksdk "github.com/livekit/server-sdk-go/v2"
)

func main() {

  api, err := lksdk.NewLiveKitAPI()
  if err != nil {
    fmt.Println(err)
    return
  }

  // List dispatch rules
  dispatchRules, err := api.SIP().ListSIPDispatchRule(
    context.Background(), &livekit.ListSIPDispatchRuleRequest{})

  if err != nil {
    fmt.Println(err)
  } else {
    fmt.Println(dispatchRules)
  }
}

```

---

**Kotlin**:

```kotlin
import io.livekit.server.LiveKitAPI

val api = LiveKitAPI.createClient(
  host = System.getenv("LIVEKIT_URL"),
  apiKey = System.getenv("LIVEKIT_API_KEY"),
  secret = System.getenv("LIVEKIT_API_SECRET")
)

val response = api.sip.listSipDispatchRule().execute()
if (response.isSuccessful) {
    val dispatchRules = response.body()
    println("Number of dispatch rules: ${dispatchRules?.size}")
}

```

---

**Rust**:

```rust
use livekit_api::services::sip::ListSIPDispatchRuleFilter;
use livekit_api::services::LiveKitApi;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // host is required; API key and secret are read from
    // LIVEKIT_API_KEY and LIVEKIT_API_SECRET.
    let api = LiveKitApi::new("https://<your-subdomain>.livekit.cloud")?;

    let rules = api.sip().list_sip_dispatch_rule(ListSIPDispatchRuleFilter::All).await?;
    println!("{:?}", rules);
    Ok(())
}

```

---

**LiveKit Cloud**:

1. Sign in to the **LiveKit Cloud** [dashboard](https://cloud.livekit.io/).
2. Select **Telephony** → [**Dispatch rules**](https://cloud.livekit.io/projects/p_/telephony/dispatch).
3. The **Dispatch rules** section lists all dispatch rules.

## Additional resources

The following resources provide additional details about the topics covered in this guide.

- **[Telephony overview](https://docs.livekit.io/telephony.md)**: Overview of LiveKit telephony features for inbound and outbound calling.

- **[Voice AI quickstart](https://docs.livekit.io/agents/start/voice-ai.md)**: Create an agent to test inbound calling end to end.

---

This document was rendered at 2026-08-24T21:31:19.049Z.
For the latest version of this document, see [https://docs.livekit.io/telephony/accepting-calls/dispatch-rule.md](https://docs.livekit.io/telephony/accepting-calls/dispatch-rule.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).
