warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /telephony/making-calls/outbound-trunk

LiveKit docs › Telephony › Making calls › Outbound trunk

---

# SIP outbound trunk

> How to create and configure an outbound trunk to make outgoing calls.

## Overview

After you purchase a phone number and [configure your SIP trunking provider](https://docs.livekit.io/telephony/start/sip-trunk-setup.md), you can create a stored outbound trunk to make outgoing calls. The outbound trunk includes the authentication credentials and the provider's endpoint to use to verify authorization to make calls using the SIP trunking provider's phone number.

> ℹ️ **Inline trunk configuration**
> 
> A stored outbound trunk isn't required. You can pass trunk configuration [inline](https://docs.livekit.io/telephony/making-calls/outbound-calls.md#inline-trunk) with each `CreateSIPParticipant` request instead. Inline configuration is useful for quick setup or when trunk settings vary per call.

> ❗ **Reuse trunks across calls**
> 
> Trunks are long-lived configuration objects that LiveKit caches and reuses. Create one outbound trunk and reuse it for every call. Creating a new trunk for each call bypasses this caching and can degrade reliability at scale. To vary the caller ID per call, set `sip_number` on the [`CreateSIPParticipant`](https://docs.livekit.io/reference/telephony/sip-api.md#createsipparticipant) request instead of creating a separate trunk. See [Calls from any phone number](#calls-from-any-phone-number).

To provision an outbound trunk with the SIP Service, use the [`CreateSIPOutboundTrunk`](https://docs.livekit.io/reference/telephony/sip-api.md#createsipoutboundtrunk) API. It returns an `SIPOutboundTrunkInfo` object that describes the created SIP trunk. You can query these parameters any time using the `ListSIPOutboundTrunk` API.

## Restricting calls to a region

To originate calls from the same region as the destination phone number, set the `destination_country` parameter for an outbound trunk. To learn more about outbound region pinning, including supported country codes and an example, see [Outbound calls](https://docs.livekit.io/telephony/features/region-pinning.md#outbound-calls).

## Create an outbound trunk

The following creates a SIP outbound trunk with username and password authentication. It makes outbound calls from number `+15105550100`.

> ℹ️ **Authentication credentials**
> 
> All the examples in this section assume the SIP_AUTH_USERNAME and SIP_AUTH_PASSWORD environment variables are set. Use the `--auth-user` and `--auth-pass` flags to pass your SIP trunk credentials instead of including them in the JSON file.

**LiveKit CLI**:

1. Create a file named `outbound-trunk.json` using your phone number and trunk domain name:

**Twilio**:

```json
{
  "trunk": {
    "name": "My outbound trunk",
    "address": "<my-trunk>.pstn.twilio.com",
    "numbers": ["+15105550100"]
  }
}

```

---

**Telnyx**:

```json
{
  "trunk": {
    "name": "My outbound trunk",
    "address": "sip.telnyx.com",
    "numbers": ["+15105550100"]
  }
}

```

> ℹ️ **Use regional SIP proxy addresses**
> 
> Use a regional SIP Signaling Address from [Telnyx SIP Signaling Addresses](https://sip.telnyx.com/#signaling-addresses) for the `address` field. This example config uses the US SIP proxy, `sip.telnyx.com`.

---

**Plivo**:

```json
{
  "trunk": {
    "name": "My outbound trunk",
    "address": "<trunk-id>.zt.plivo.com",
    "numbers": ["+15105550100"]
  }
}

```

> ℹ️ **Plivo outbound trunk authentication**
> 
> Plivo recommends using username and password authentication for outbound trunks. To create credentials, see [Create and configure a Plivo SIP trunk](https://docs.livekit.io/telephony/start/providers/plivo.md).
2. Create the outbound trunk using the CLI. Pass your SIP trunk credentials using the `--auth-user` and `--auth-pass` flags:

```shell
lk sip outbound create outbound-trunk.json \
  --auth-user "$SIP_AUTH_USERNAME" \
  --auth-pass "$SIP_AUTH_PASSWORD"

```

The output of the command returns the trunk ID. Copy it for the next step:

```text
SIPTrunkID: <your-trunk-id>

```

---

**Node.js**:

```typescript
import { LiveKitAPI } from 'livekit-server-sdk';
import { SIPTransport } from '@livekit/protocol';

const api = new LiveKitAPI();

// SIP address is the hostname or IP the SIP INVITE is sent to.
// Address format for Twilio: <trunk-name>.pstn.twilio.com
// Address format for Telnyx: sip.telnyx.com
// Address format for Plivo: <trunk-id>.zt.plivo.com
const address = 'sip.telnyx.com';

// An array of one or more provider phone numbers associated with the trunk.
const numbers = ['+12135550100'];

// Trunk options
const trunkOptions = {
  transport: SIPTransport.SIP_TRANSPORT_AUTO,
  authUsername: process.env.SIP_AUTH_USERNAME,
  authPassword: process.env.SIP_AUTH_PASSWORD,
};

const trunk = await api.sip.createSipOutboundTrunk('My trunk', address, numbers, trunkOptions);

console.log(trunk);

```

---

**Python**:

```python
import asyncio
import os

from livekit import api
from livekit.protocol.sip import CreateSIPOutboundTrunkRequest, SIPOutboundTrunkInfo

async def main():
  lkapi = api.LiveKitAPI()

  trunk = SIPOutboundTrunkInfo(
    name = "My trunk",
    address = "sip.telnyx.com",
    numbers = ['+12135550100'],
    auth_username = os.getenv("SIP_AUTH_USERNAME"),
    auth_password = os.getenv("SIP_AUTH_PASSWORD"),
  )

  request = CreateSIPOutboundTrunkRequest(
    trunk = trunk
  )

  trunk = await lkapi.sip.create_sip_outbound_trunk(request)

  print(f"Successfully created {trunk}")

  await lkapi.aclose()

asyncio.run(main())

```

---

**Ruby**:

```ruby
require 'livekit'

name = "My trunk"
address = "sip.telnyx.com"
numbers = ["+12135550100"]
auth_username = ENV['SIP_AUTH_USERNAME']
auth_password = ENV['SIP_AUTH_PASSWORD']

lkapi = LiveKit::LiveKitAPI.new

trunk = lkapi.sip.create_sip_outbound_trunk(
    name,
    address,
    numbers,
    auth_username: auth_username,
    auth_password: auth_password
)

puts trunk

```

---

**Go**:

```go
package main

import (
  "context"
  "fmt"

  lksdk "github.com/livekit/server-sdk-go/v2"
  "github.com/livekit/protocol/livekit"
)

func main() {
  trunkName := "My trunk"
  address := "sip.telnyx.com"
  numbers := []string{"+16265550100"}

  trunkInfo := &livekit.SIPOutboundTrunkInfo{
    Name: trunkName,
    Address: address,
    Numbers: numbers,
  }

  // Create a request
  request := &livekit.CreateSIPOutboundTrunkRequest{
    Trunk: trunkInfo,
  }

  api, err := lksdk.NewLiveKitAPI()
  if err != nil {
    fmt.Println(err)
    return
  }

  // Create trunk
  trunk, err := api.SIP().CreateSIPOutboundTrunk(context.Background(), request)

  if err != nil {
    fmt.Println(err)
  } else {
    fmt.Println(trunk)
  }
}

```

---

**Kotlin**:

```kotlin
import io.livekit.server.LiveKitAPI
import io.livekit.server.CreateSipOutboundTrunkOptions

val api = LiveKitAPI.createClient()

val response = api.sip.createSipOutboundTrunk(
    name = "My outbound trunk",
    address = "sip.telnyx.com",
    numbers = listOf("+16265550100"),
    options = CreateSipOutboundTrunkOptions(
        authUsername = System.getenv("SIP_AUTH_USERNAME") ?: "",
        authPassword = System.getenv("SIP_AUTH_PASSWORD") ?: "",
    )
).execute()

if (!response.isSuccessful) {
    println(response.errorBody())
} else {
    val trunk = response.body()

    if (trunk != null) {
        println("Created outbound trunk: ${trunk.sipTrunkId}")
    }
}

```

---

**Rust**:

```rust
use livekit_api::services::sip::CreateSIPOutboundTrunkOptions;
use livekit_api::services::LiveKitApi;

#[tokio::main]
async fn main() {
    let api = LiveKitApi::new("https://my-project.livekit.cloud").unwrap();

    let options = CreateSIPOutboundTrunkOptions {
        auth_username: std::env::var("SIP_AUTH_USERNAME").unwrap_or_default(),
        auth_password: std::env::var("SIP_AUTH_PASSWORD").unwrap_or_default(),
        ..Default::default()
    };

    let trunk = api
        .sip()
        .create_sip_outbound_trunk(
            "My trunk".to_string(),
            "sip.telnyx.com".to_string(),
            vec!["+12135550100".to_string()],
            options,
        )
        .await
        .unwrap();

    println!("Created outbound trunk: {:?}", trunk);
}

```

---

**LiveKit Cloud**:

1. Sign in to the **LiveKit Cloud** [dashboard](https://cloud.livekit.io/).
2. Select **Telephony** → [**SIP trunks**](https://cloud.livekit.io/projects/p_/telephony/trunks).
3. Select **Create new trunk**.
4. Select the **JSON editor** tab.

> ℹ️ **Note**
> 
> You can also use the **Trunk details** tab to create a trunk. However, the JSON editor allows you to configure all available [parameters](https://docs.livekit.io/reference/telephony/sip-api.md#createsipoutboundtrunk).
5. Select **Outbound** for **Trunk direction**.
6. Copy and paste the following text into the editor:

```json
{
  "name": "My outbound trunk",
  "address": "sip.telnyx.com",
  "numbers": [
    "+12135550100"
  ],
  "authUsername": "<username>",
  "authPassword": "<password>"
}

```
7. Select **Create**.

### Calls from any phone number

You can configure an outbound trunk to allow calls from any phone number by setting the `numbers` parameter to an empty string or wildcard character, for example, `*`. This is useful if you want to use the same outbound trunk for all calls or if you want to use a different phone number for each call.

Instead of setting the number on the trunk, you can set the phone number to call from using the `sip_number` parameter for the [CreateSIPParticipant](https://docs.livekit.io/reference/telephony/sip-api.md#createsipparticipant) API.

The following example creates an outbound trunk that allows calling from any number, then initiates a call using the outbound trunk.

1. Create an outbound trunk using the CLI.

Create a file named `outbound-trunk.json` and copy and paste the following content:

```json
  {
    "trunk": {
      "name": "My outbound trunk",
      "address": "<my-trunk>.pstn.twilio.com",
      "numbers": ["*"]
    }
  }

```

Create the outbound trunk using the CLI:

```shell
lk sip outbound create outbound-trunk.json \
  --auth-user "$SIP_AUTH_USERNAME" \
  --auth-pass "$SIP_AUTH_PASSWORD"

```
2. Initiate a call from the number `+15105550100` using the CLI. This number is the phone number configured with your SIP trunk provider. Use the <trunk-id> from the output of the previous step.

Create a file named `participant.json` and copy and paste the following content:

```json
{
  "sip_number": "+15105550100",
  "sip_trunk_id": "<trunk-id>",
  "sip_call_to": "+12135550100",
  "room_name": "open-room",
  "participant_identity": "sip-test",
  "participant_name": "Test call participant",
  "wait_until_answered": true
}

```

> ❗ **Important**
> 
> If you're using Telnyx, the leading `+` in the phone number assumes the `Destination Number Format` is set to `+E.164` for your number.

Initiate the call using the CLI:

```shell
lk sip participant create participant.json

```

After you run the command, a call from the number `+15105550100` to `+12135550100` is initiated. Output from the command returns when the call is answered.

## List outbound trunks

Use the [`ListSIPOutboundTrunk`](https://docs.livekit.io/reference/telephony/sip-api.md#listsipoutboundtrunk) API to list all outbound trunks and trunk parameters.

**LiveKit CLI**:

```shell
lk sip outbound list

```

---

**Node.js**:

```typescript
import { LiveKitAPI } from 'livekit-server-sdk';

const api = new LiveKitAPI();

const trunks = await api.sip.listSipOutboundTrunk();

console.log(trunks);

```

---

**Python**:

```python
import asyncio

from livekit import api
from livekit.protocol.sip import ListSIPOutboundTrunkRequest

async def main():
  lkapi = api.LiveKitAPI()

  trunks = await lkapi.sip.list_sip_outbound_trunk(
    ListSIPOutboundTrunkRequest()
  )
  print(f"{trunks}")

  await lkapi.aclose()

asyncio.run(main())

```

---

**Ruby**:

```ruby
require 'livekit'

lkapi = LiveKit::LiveKitAPI.new

trunks = lkapi.sip.list_sip_outbound_trunk()

puts trunks

```

---

**Go**:

```go
package main

import (
  "context"
  "fmt"

  lksdk "github.com/livekit/server-sdk-go/v2"
  "github.com/livekit/protocol/livekit"
)

func main() {
  api, err := lksdk.NewLiveKitAPI()
  if err != nil {
    fmt.Println(err)
    return
  }

  // List outbound trunks
  trunks, err := api.SIP().ListSIPOutboundTrunk(
    context.Background(), &livekit.ListSIPOutboundTrunkRequest{})

  if err != nil {
    fmt.Println(err)
  } else {
    fmt.Println(trunks)
  }
}

```

---

**Kotlin**:

```kotlin
import io.livekit.server.LiveKitAPI

val api = LiveKitAPI.createClient()

val response = api.sip.listSipOutboundTrunk().execute()

if (!response.isSuccessful) {
  println(response.errorBody())
} else {
  val trunks = response.body()

  if (trunks != null) {
    println("Outbound trunks: ${trunks}")
  }
}

```

---

**Rust**:

```rust
use livekit_api::services::sip::ListSIPOutboundTrunkFilter;
use livekit_api::services::LiveKitApi;

#[tokio::main]
async fn main() {
    let api = LiveKitApi::new("https://my-project.livekit.cloud").unwrap();

    let trunks = api
        .sip()
        .list_sip_outbound_trunk(ListSIPOutboundTrunkFilter::All)
        .await
        .unwrap();

    println!("Outbound trunks: {:?}", trunks);
}

```

---

**LiveKit Cloud**:

1. Sign in to the **LiveKit Cloud** [dashboard](https://cloud.livekit.io/).
2. Select **Telephony** → [**SIP trunks**](https://cloud.livekit.io/projects/p_/telephony/trunks).
3. The **Outbound** section lists all outbound trunks.

## Update an outbound trunk

The [`UpdateSIPOutboundTrunk`](https://docs.livekit.io/reference/telephony/sip-api.md#updatesipoutboundtrunk) API allows you to update specific fields of an outbound trunk or [replace](#replace-sip-outbound-trunk) an outbound trunk with a new one.

### Update specific fields of an outbound trunk

The `UpdateSIPOutboundTrunkFields` API allows you to update specific fields of an outbound trunk without affecting other fields.

**LiveKit CLI**:

1. Create a file named `outbound-trunk.json` with the fields you want to update. The following example updates the name and phone numbers for the trunk:

**Twilio**:

```json
{
   "name": "My updated outbound trunk",
   "address": "<my-trunk>.pstn.twilio.com",
   "numbers": ["+15105550100"]
}

```

---

**Telnyx**:

```json
{
   "name": "My updated outbound trunk",
   "address": "sip.telnyx.com",
   "numbers": ["+15105550100"]
}

```

> ℹ️ **Note**
> 
> Use a regional SIP Signaling Address from [Telnyx SIP Signaling Addresses](https://sip.telnyx.com/#signaling-addresses) for the `address` field. This example config uses the US SIP proxy, `sip.telnyx.com`.

---

**Plivo**:

```json
{
   "name": "My updated outbound trunk",
   "address": "<trunk-id>.zt.plivo.com",
   "numbers": ["+15105550100"]
}

```
2. Update the outbound trunk using the CLI:

```shell
lk sip outbound update --id <sip-trunk-id> outbound-trunk.json

```

The output of the command returns the trunk ID:

```text
SIPTrunkID: <your-trunk-id>

```

---

**Node.js**:

```typescript
import { ListUpdate } from '@livekit/protocol';
import { LiveKitAPI } from 'livekit-server-sdk';

const api = new LiveKitAPI();

/**
 * Update fields of an outbound trunk.
 * @param {string} trunkId The ID of the trunk to update.
 * @returns {Object} The result of the update operation.
 */
async function updateTrunk(trunkId) {
  const updatedTrunkFields = {
    name: 'My updated trunk',
    address: 'my-trunk.pstn.twilio.com',
    numbers: new ListUpdate({
      add: ['+15220501011'], // Add specific numbers to the trunk
      remove: ['+15105550100'], // Remove specific numbers from the trunk
    }),
  };

  const trunk = await api.sip.updateSipOutboundTrunkFields(trunkId, updatedTrunkFields);

  return trunk;
}

updateTrunk('<outbound-trunk-id>');

```

---

**Python**:

```python
import asyncio

from livekit import api
from livekit.protocol.models import ListUpdate


async def main():
  lkapi = api.LiveKitAPI()

  trunk = await lkapi.sip.update_sip_outbound_trunk_fields(
    trunk_id = "<sip-trunk-id>",
    name = "My updated outbound trunk",
    address = "sip.telnyx.com",
    numbers = ListUpdate(
      add=['+15225550101'],
      remove=['+15105550100'],
    ) # Add and remove specific numbers from the trunk
  )

  print(f"Successfully updated {trunk}")

  await lkapi.aclose()

asyncio.run(main())

```

---

**Ruby**:

```ruby
require 'livekit'

lkapi = LiveKit::LiveKitAPI.new

update = LiveKit::Proto::SIPOutboundTrunkUpdate.new(
  name: "My updated outbound trunk",
  numbers: LiveKit::Proto::ListUpdate.new(
    add: ["+15220501011"],    # Add specific numbers to the trunk
    remove: ["+15105550100"], # Remove specific numbers from the trunk
  )
)

trunk = lkapi.sip.update_sip_outbound_trunk_fields("<sip-trunk-id>", update)

puts trunk

```

---

**Go**:

```go
package main

import (
  "context"
  "fmt"

  lksdk "github.com/livekit/server-sdk-go/v2"
  "github.com/livekit/protocol/livekit"
)

func main() {
  trunkName := "My updated outbound trunk"
  numbers := &livekit.ListUpdate{Set: []string{"+16265550100"}}
  transport := livekit.SIPTransport_SIP_TRANSPORT_UDP

  trunkId := "<sip-trunk-id>"

  trunkInfo := &livekit.SIPOutboundTrunkUpdate{
    Name: &trunkName,
    Numbers: numbers,
    Transport: &transport,
  }

  // Create a request
  request := &livekit.UpdateSIPOutboundTrunkRequest{
    SipTrunkId: trunkId,
    Action: &livekit.UpdateSIPOutboundTrunkRequest_Update{
      Update: trunkInfo,
    },
  }

  api, err := lksdk.NewLiveKitAPI()
  if err != nil {
    fmt.Println(err)
    return
  }

  // Update trunk
  trunk, err := api.SIP().UpdateSIPOutboundTrunk(context.Background(), request)

  if err != nil {
    fmt.Println(err)
  } else {
    fmt.Println(trunk)
  }
}

```

---

**Kotlin**:

```kotlin
import io.livekit.server.LiveKitAPI
import io.livekit.server.UpdateSipOutboundTrunkOptions

val api = LiveKitAPI.createClient()

val response = api.sip.updateSipOutboundTrunk(
    sipTrunkId = trunkId,
    options = UpdateSipOutboundTrunkOptions(
        name = "My updated outbound trunk",
        numbers = listOf("+16265550100"),
        metadata = "{'key1': 'value1', 'key2': 'value2'}",
        authUsername = System.getenv("SIP_AUTH_USERNAME") ?: "",
        authPassword = System.getenv("SIP_AUTH_PASSWORD") ?: "",
    )
).execute()

if (!response.isSuccessful) {
    println(response.errorBody())
} else {
    val trunk = response.body()

    if (trunk != null) {
        println("Updated outbound trunk: ${trunk}")
    }
}

```

---

**Rust**:

```rust
use livekit_api::services::LiveKitApi;
use livekit_protocol as proto;

#[tokio::main]
async fn main() {
    let api = LiveKitApi::new("https://my-project.livekit.cloud").unwrap();

    let update = proto::SipOutboundTrunkUpdate {
        name: Some("My updated outbound trunk".to_owned()),
        numbers: Some(proto::ListUpdate { set: vec!["+16265550100".to_owned()], ..Default::default() }),
        ..Default::default()
    };

    let trunk = api
        .sip()
        .update_sip_outbound_trunk("<sip-trunk-id>".to_owned(), update)
        .await
        .unwrap();

    println!("Updated outbound trunk: {:?}", trunk);
}

```

---

**LiveKit Cloud**:

Update and replace functions are the same in the LiveKit Cloud dashboard. For an example, see the [replace an outbound trunk](#replace-trunk) section.

### Replace an outbound trunk

The `UpdateSIPOutboundTrunk` API allows you to replace an existing outbound trunk with a new one using the same trunk ID.

**LiveKit CLI**:

The CLI doesn't support replacing outbound trunks.

---

**Node.js**:

```typescript
import { LiveKitAPI, SIPOutboundTrunkInfo } from 'livekit-server-sdk';

const api = new LiveKitAPI();

async function replaceTrunk(trunkId) {
  // Replace an outbound trunk entirely.
  const trunk = new SIPOutboundTrunkInfo({
    name: 'My replaced trunk',
    address: 'sip.telnyx.com',
    numbers: ['+17025550100'],
    metadata: '{"is_internal": true}',
    authUsername: process.env.SIP_AUTH_USERNAME,
    authPassword: process.env.SIP_AUTH_PASSWORD,
  });

  const updatedTrunk = await api.sip.updateSipOutboundTrunk(trunkId, trunk);

  return updatedTrunk;
}

replaceTrunk('<outbound-trunk-id>');

```

---

**Python**:

To replace a trunk, edit the previous example by adding the following import, `trunk`, and call the `update_outbound_trunk` function:

```python
import os
from livekit.protocol.sip import SIPOutboundTrunkInfo, SIPTransport

trunk = SIPOutboundTrunkInfo(
    address = "sip.telnyx.com",
    numbers = ['+15105550100'],
    name = "My replaced outbound trunk",
    transport = SIPTransport.SIP_TRANSPORT_AUTO,
    auth_username = os.getenv("SIP_AUTH_USERNAME"),
    auth_password = os.getenv("SIP_AUTH_PASSWORD"),
)

trunk = await lkapi.sip.update_outbound_trunk(
    "<sip-trunk-id>",
    trunk
)

```

---

**Ruby**:

```ruby
require 'livekit'

lkapi = LiveKit::LiveKitAPI.new

# Replace an outbound trunk entirely.
trunk = LiveKit::Proto::SIPOutboundTrunkInfo.new(
  name: "My replaced outbound trunk",
  address: "sip.telnyx.com",
  numbers: ["+15105550100"],
  transport: LiveKit::Proto::SIPTransport::SIP_TRANSPORT_AUTO,
  auth_username: ENV['SIP_AUTH_USERNAME'],
  auth_password: ENV['SIP_AUTH_PASSWORD'],
)

updated_trunk = lkapi.sip.update_sip_outbound_trunk("<sip-trunk-id>", trunk)

puts updated_trunk

```

---

**Go**:

To replace a trunk, use the previous example with the following `trunkInfo` and `request` values:

```go
  // Create a SIPOutboundTrunkInfo object
  trunkInfo := &livekit.SIPOutboundTrunkInfo{
    Name: "My replaced outbound trunk",
    Address: "sip.telnyx.com",
    Numbers: []string{"+16265550100"},
    Transport: livekit.SIPTransport_SIP_TRANSPORT_AUTO,
    AuthUsername: os.Getenv("SIP_AUTH_USERNAME"),
    AuthPassword: os.Getenv("SIP_AUTH_PASSWORD"),
  }

  // Create a request
  request := &livekit.UpdateSIPOutboundTrunkRequest{
    SipTrunkId: trunkId,
    Action: &livekit.UpdateSIPOutboundTrunkRequest_Replace{
      Replace: trunkInfo,
    },  
  }

```

---

**Kotlin**:

```kotlin
import io.livekit.server.LiveKitAPI
import livekit.LivekitSip

val api = LiveKitAPI.createClient()

// Replace an outbound trunk entirely.
val trunk = LivekitSip.SIPOutboundTrunkInfo.newBuilder()
    .setName("My replaced outbound trunk")
    .setAddress("sip.telnyx.com")
    .addAllNumbers(listOf("+16265550100"))
    .setTransport(LivekitSip.SIPTransport.SIP_TRANSPORT_AUTO)
    .setAuthUsername(System.getenv("SIP_AUTH_USERNAME") ?: "")
    .setAuthPassword(System.getenv("SIP_AUTH_PASSWORD") ?: "")
    .build()

val response = api.sip.updateSipOutboundTrunk(trunkId, trunk).execute()

if (!response.isSuccessful) {
    println(response.errorBody())
} else {
    val updatedTrunk = response.body()

    if (updatedTrunk != null) {
        println("Replaced outbound trunk: ${updatedTrunk}")
    }
}

```

---

**Rust**:

```rust
use livekit_api::services::LiveKitApi;
use livekit_protocol as proto;

#[tokio::main]
async fn main() {
    let api = LiveKitApi::new("https://my-project.livekit.cloud").unwrap();

    // Replace an outbound trunk entirely.
    let trunk = proto::SipOutboundTrunkInfo {
        name: "My replaced outbound trunk".to_owned(),
        address: "sip.telnyx.com".to_owned(),
        numbers: vec!["+16265550100".to_owned()],
        transport: proto::SipTransport::Auto as i32,
        auth_username: std::env::var("SIP_AUTH_USERNAME").unwrap_or_default(),
        auth_password: std::env::var("SIP_AUTH_PASSWORD").unwrap_or_default(),
        ..Default::default()
    };

    let trunk = api
        .sip()
        .update_sip_outbound_trunk_replace("<sip-trunk-id>".to_owned(), trunk)
        .await
        .unwrap();

    println!("Replaced outbound trunk: {:?}", trunk);
}

```

---

**LiveKit Cloud**:

1. Sign in to the **Telephony** → [**SIP trunks**](https://cloud.livekit.io/projects/p_/telephony/trunks) page.
2. Navigate to the **Outbound** section.
3. Find the outbound trunk you want to replace → select the more (**⋮**) menu → select **Configure trunk**.
4. Copy and paste the following text into the editor:

```json
{
  "name": "My replaced trunk",
  "address": "sip.telnyx.com",
  "numbers": [
    "+17025550100"
  ],
  "metadata": "{\"is_internal\": true}",
  "authUsername": "<updated-username>",
  "authPassword": "<updated-password>"
}

```
5. Select **Update**.

## IP address range for LiveKit Cloud SIP

LiveKit Cloud provides static IP ranges for the Canada, EU, India, Japan, and US regions, and these ranges apply to SIP signaling and media. For the ranges, the services they cover, and how regional endpoints work, see [Static IPs](https://docs.livekit.io/deploy/admin/regions/endpoints.md#static-ips).

For all other regions, LiveKit Cloud doesn't provide a static IP range. In that case, prefer username and password authentication on your SIP trunk provider.

If your provider requires an IP range in addition to (or instead of) credentials, and you can't use the static ranges above, set ranges that include all IPs, such as `0.0.0.0/0` or `0.0.0.0/1` and `128.0.0.0/1`.

---

This document was rendered at 2026-08-24T21:31:21.730Z.
For the latest version of this document, see [https://docs.livekit.io/telephony/making-calls/outbound-trunk.md](https://docs.livekit.io/telephony/making-calls/outbound-trunk.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).
