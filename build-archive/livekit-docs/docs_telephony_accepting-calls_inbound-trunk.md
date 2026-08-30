warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /telephony/accepting-calls/inbound-trunk

LiveKit docs › Telephony › Accepting calls › Inbound trunk

---

# Inbound trunk

> How to create and configure an inbound trunk to accept incoming calls using a SIP provider.

## Overview

After you purchase a phone number and [configure your SIP trunking provider](https://docs.livekit.io/telephony/start/sip-trunk-setup.md), you must create an inbound trunk and [dispatch rule](https://docs.livekit.io/telephony/accepting-calls/dispatch-rule.md) to accept incoming calls. The inbound trunk allows you to limit incoming calls to those coming from your SIP trunking provider.

You can also configure additional properties for all incoming calls that match the trunk including SIP headers, participant metadata and attributes, and session properties. For a full list of available parameters, see [`CreateSIPInboundTrunk`](https://docs.livekit.io/reference/telephony/sip-api.md#createsipinboundtrunk).

If you're using [LiveKit Phone Numbers](https://docs.livekit.io/telephony/start/phone-numbers.md), you **do not** need to create an inbound trunk.

> ❗ **Reuse trunks across calls**
> 
> Trunks are long-lived configuration objects that LiveKit caches and reuses. Create an inbound trunk once and reuse it for every call, typically one trunk per phone number. Creating a new trunk for each call bypasses this caching and can degrade reliability at scale. To place each caller in a separate room, use a [dispatch rule](https://docs.livekit.io/telephony/accepting-calls/dispatch-rule.md#individual-dispatch-rule).

> ℹ️ **Username and password support varies**
> 
> LiveKit supports username and password authentication for inbound trunks, but your SIP trunking provider must also support it. Support varies by provider. For example, Twilio Elastic SIP Trunking doesn’t support it, though you can use username and password authentication with [TwiML](https://docs.livekit.io/telephony/accepting-calls/inbound-twilio.md). Check with your provider to confirm.

To learn more about LiveKit SIP, see [SIP overview](https://docs.livekit.io/telephony.md). To learn more about SIP API endpoints and types, see [SIP API](https://docs.livekit.io/reference/telephony/sip-api.md).

## Restricting calls to a region

When you configure your SIP trunking provider for inbound calls, you need to specify the LiveKit SIP endpoint to use. By default, this is a global endpoint and incoming calls are routed to the region closest to the call's origination point — typically the region where your telephony provider initiated the call. You can limit calls to a specific region using [region pinning](https://docs.livekit.io/telephony/features/region-pinning.md).

## Inbound trunk example

The following examples create an inbound trunk that accepts calls made to the number `+1-510-555-0100`. This phone number is the number purchased from your SIP trunking provider.

**LiveKit CLI**:

1. Create a file named `inbound-trunk.json` with the following content:

```json
{
  "trunk": {
    "name": "My trunk",
    "numbers": [
      "+15105550100"
    ]
  }
}

```

> ❗ **Important**
> 
> If you're using Telnyx, the leading `+` in the phone number assumes the `Destination Number Format` is set to `+E.164` for your number.
2. Create the inbound trunk using `lk`:

```shell
lk sip inbound create inbound-trunk.json

```

---

**Node.js**:

```typescript
import { LiveKitAPI } from 'livekit-server-sdk';

const api = new LiveKitAPI();

// An array of one or more provider phone numbers associated with the trunk.
const numbers = ['+15105550100'];

const name = 'My trunk';

const trunk = await api.sip.createSipInboundTrunk(name, numbers);

console.log(trunk);

```

---

**Python**:

```python
import asyncio

from livekit import api

async def main():
  lkapi = api.LiveKitAPI()

  trunk = api.SIPInboundTrunkInfo(
    name = "My trunk",
    numbers = ["+15105550100"],
  )

  request = api.CreateSIPInboundTrunkRequest(
    trunk = trunk
  )

  trunk = await lkapi.sip.create_sip_inbound_trunk(request)

  print(trunk)

  await lkapi.aclose()

asyncio.run(main())

```

---

**Ruby**:

```ruby
require 'livekit'

name = "My trunk"
numbers = ["+15105550100"]

lkapi = LiveKit::LiveKitAPI.new

trunk = lkapi.sip.create_sip_inbound_trunk(
    name,
    numbers
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
  trunkName := "My inbound trunk"
  numbers := []string{"+15105550100"}

  trunkInfo := &livekit.SIPInboundTrunkInfo{
    Name: trunkName,
    Numbers: numbers,
  }

  // Create a request
  request := &livekit.CreateSIPInboundTrunkRequest{
    Trunk: trunkInfo,
  }

  api, err := lksdk.NewLiveKitAPI()
  if err != nil {
    fmt.Println(err)
    return
  }

  // Create trunk
  trunk, err := api.SIP().CreateSIPInboundTrunk(context.Background(), request)

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

val api = LiveKitAPI.createClient()

val response = api.sip.createSipInboundTrunk(
    name = "My inbound trunk",
    numbers = listOf("+15105550100"),
).execute()

if (!response.isSuccessful) {
    println(response.errorBody())
} else {
    val trunk = response.body()

    if (trunk != null) {
        println("Created inbound trunk: ${trunk.sipTrunkId}")
    }
}

```

---

**Rust**:

```rust
use livekit_api::services::LiveKitApi;

#[tokio::main]
async fn main() {
    let api = LiveKitApi::new("https://my-project.livekit.cloud").unwrap();

    let trunk = api
        .sip()
        .create_sip_inbound_trunk(
            "My trunk".to_string(),
            vec!["+15105550100".to_string()],
            Default::default(),
        )
        .await
        .unwrap();

    println!("Created inbound trunk: {:?}", trunk);
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
> You can also use the **Trunk details** tab to create a basic trunk. However, the JSON editor allows you to configure all available [parameters](https://docs.livekit.io/reference/telephony/sip-api.md#createsipinboundtrunk). For example, the `krispEnabled` parameter is only available in the JSON editor.
5. Select **Inbound** for **Trunk direction**.
6. Copy and paste the following text into the editor:

```json
{
  "name": "My trunk",
  "numbers": [
    "+15105550100"
  ],
  "krispEnabled": true
}

```
7. Select **Create**.

## Accepting calls to any phone number

You can configure an inbound trunk to accept incoming calls to any phone number by setting the `numbers` parameter to an empty array. This is useful if you want to use the same inbound trunk for incoming calls to all your phone numbers.

> ❗ **Requires additional fields**
> 
> When you use an empty `numbers` parameter, you must set either a username and password for authentication or the `allowed_addresses` parameter. See [CreateSIPInboundTrunk](https://docs.livekit.io/reference/telephony/sip-api.md#createsipinboundtrunk) for parameter details.

> ℹ️ **allowed_addresses requires enablement**
> 
> The `allowed_addresses` field must be enabled for your project before you can use it. Contact LiveKit support to request access.

## Accepting calls from specific phone numbers

You can configure an inbound trunk to accept phone calls only from specific numbers. The following example configuration accepts inbound calls to the number `+1-510-555-0100` from caller numbers `+1-310-555-1100` and `+1-714-555-0100`.

> ❗ **Replace phone numbers**
> 
> Remember to replace the numbers in the example with actual phone numbers when creating your trunks.

> 💡 **Tip**
> 
> You can also filter allowed caller numbers with a [Dispatch Rule](https://docs.livekit.io/telephony/accepting-calls/dispatch-rule.md).

**LiveKit CLI**:

1. Create a file named `inbound-trunk.json` with the following content:

```json
{
   "trunk": {
     "name": "My trunk",
     "numbers": [
       "+15105550100"
     ],
     "allowedNumbers": [
       "+13105550100",
       "+17145550100"
     ]
   }
}

```

> ❗ **Important**
> 
> If you're using Telnyx, the leading `+` in the phone number assumes the `Destination Number Format` is set to `+E.164` for your number.
2. Create the inbound trunk using `lk`:

```shell
lk sip inbound create inbound-trunk.json

```

---

**Node.js**:

For an executable example, replace the `trunk` in the [Inbound trunk example](#inbound-trunk-example) to include the following `trunkOptions`:

```typescript
// Trunk options
const trunkOptions = {
  allowedNumbers: ['+13105550100', '+17145550100'],
};

const trunk = await api.sip.createSipInboundTrunk(name, numbers, trunkOptions);

```

---

**Python**:

For an executable example, replace the `trunk` in the [Inbound trunk example](#inbound-trunk-example) with the following:

```python
  trunk = api.SIPInboundTrunkInfo(
    name = "My trunk",
    numbers = ["+15105550100"],
    allowed_numbers = ["+13105550100", "+17145550100"]
  )

```

---

**Ruby**:

For an executable example, replace `trunk` in the [Inbound trunk example](#inbound-trunk-example) with the following:

```ruby
trunk = lkapi.sip.create_sip_inbound_trunk(
    name,
    numbers,
    allowed_numbers: ["+13105550100", "+17145550100"]
)

```

---

**Go**:

For an executable example, replace `trunkInfo` in the [Inbound trunk example](#inbound-trunk-example) with the following:

```go
allowedNumbers := []string{"+13105550100", "+17145550100"}

trunkInfo := &livekit.SIPInboundTrunkInfo{
  Name: trunkName,
  Numbers: numbers,
  AllowedNumbers: allowedNumbers,
}

```

---

**Kotlin**:

```kotlin
import io.livekit.server.LiveKitAPI
import io.livekit.server.CreateSipInboundTrunkOptions

val api = LiveKitAPI.createClient()

val response = api.sip.createSipInboundTrunk(
  name = "My inbound trunk",
  numbers = listOf("+15105550100"),
  options = CreateSipInboundTrunkOptions(
    allowedNumbers = listOf("+13105550100", "+17145550100")
  )
).execute()

if (!response.isSuccessful) {
  println(response.errorBody())
} else {
  val trunk = response.body()

  if (trunk != null) {
    println("Created inbound trunk: ${trunk.sipTrunkId}")
  }
}

```

---

**Rust**:

For an executable example, replace the `options` in the [Inbound trunk example](#inbound-trunk-example) with the following:

```rust
let options = CreateSIPInboundTrunkOptions {
    allowed_numbers: Some(vec![
        "+13105550100".to_string(),
        "+17145550100".to_string(),
    ]),
    ..Default::default()
};

```

---

**LiveKit Cloud**:

1. Sign in to the **LiveKit Cloud** [dashboard](https://cloud.livekit.io/).
2. Select **Telephony** → [**SIP trunks**](https://cloud.livekit.io/projects/p_/telephony/trunks).
3. Select **Create new trunk**.
4. Select the **JSON editor** tab.

> ℹ️ **Note**
> 
> The `krispEnabled` and `allowedNumbers` parameters are only available in the **JSON editor** tab.
5. Select **Inbound** for **Trunk direction**.
6. Copy and paste the following text into the editor:

```json
{
  "name": "My trunk",
  "numbers": [
    "+15105550100"
  ],
  "krispEnabled": true,
  "allowedNumbers": [
    "+13105550100",
    "+17145550100"
  ]
}

```
7. Select **Create**.

## List inbound trunks

Use the [`ListSIPInboundTrunk`](https://docs.livekit.io/reference/telephony/sip-api.md#listsipinboundtrunk) API to list all inbound trunks and trunk parameters.

**LiveKit CLI**:

```shell
lk sip inbound list

```

---

**Node.js**:

```typescript
import { LiveKitAPI } from 'livekit-server-sdk';

const api = new LiveKitAPI();

const trunks = await api.sip.listSipInboundTrunk();

console.log(trunks);

```

---

**Python**:

```python
import asyncio

from livekit import api

async def main():
  lkapi = api.LiveKitAPI()

  trunks = await lkapi.sip.list_sip_inbound_trunk(
    api.ListSIPInboundTrunkRequest()
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

trunks = lkapi.sip.list_sip_inbound_trunk()

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

  // List inbound trunks
  trunks, err := api.SIP().ListSIPInboundTrunk(
    context.Background(), &livekit.ListSIPInboundTrunkRequest{})

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

val response = api.sip.listSipInboundTrunk().execute()

if (!response.isSuccessful) {
  println(response.errorBody())
} else {
  val trunks = response.body()

  if (trunks != null) {
    println("Inbound trunks: ${trunks}")
  }
}

```

---

**Rust**:

```rust
use livekit_api::services::sip::ListSIPInboundTrunkFilter;
use livekit_api::services::LiveKitApi;

#[tokio::main]
async fn main() {
    let api = LiveKitApi::new("https://my-project.livekit.cloud").unwrap();

    let trunks = api
        .sip()
        .list_sip_inbound_trunk(ListSIPInboundTrunkFilter::All)
        .await
        .unwrap();

    println!("Inbound trunks: {:?}", trunks);
}

```

---

**LiveKit Cloud**:

1. Sign in to the **LiveKit Cloud** [dashboard](https://cloud.livekit.io/).
2. Select **Telephony** → [**SIP trunks**](https://cloud.livekit.io/projects/p_/telephony/trunks).
3. The **Inbound** section lists all inbound trunks.

## Update inbound trunk

Use the [`UpdateSIPInboundTrunk`](https://docs.livekit.io/reference/telephony/sip-api.md#updatesipinboundtrunk) API to update specific fields of an inbound trunk or [replace](#replace-inbound-trunk) an inbound trunk with a new one.

### Update specific fields of an inbound trunk

The `UpdateSIPInboundTrunkFields` API allows you to update specific fields of an inbound trunk without affecting other fields.

**LiveKit CLI**:

1. Create a file named `inbound-trunk.json` with the following content:

```json
{
  "name": "My trunk",
  "numbers": [
    "+15105550100"
  ]
}

```

> ❗ **Important**
> 
> If you're using Telnyx, the leading `+` in the phone number assumes the `Destination Number Format` is set to `+E.164` for your number.

Update the inbound trunk using `lk`:

```shell
lk sip inbound update --id <trunk-id> inbound-trunk.json

```

---

**Node.js**:

```typescript
import { ListUpdate } from '@livekit/protocol';
import { LiveKitAPI } from 'livekit-server-sdk';

const api = new LiveKitAPI();

async function main() {
  const updatedTrunkFields = {
    numbers: new ListUpdate({ set: ['+15105550100'] }), // Replace existing list
    allowedNumbers: new ListUpdate({ add: ['+14155550100'] }), // Add to existing list
    name: 'My updated trunk',
  };

  const trunk = await api.sip.updateSipInboundTrunkFields('<inbound-trunk-id>', updatedTrunkFields);

  console.log('updated trunk ', trunk);
}

await main();

```

---

**Python**:

```python
import asyncio

from livekit import api
from livekit.protocol.models import ListUpdate


async def main():
  livekit_api = api.LiveKitAPI()
  
  # To update specific trunk fields, use the update_inbound_trunk_fields method.
  trunk = await livekit_api.sip.update_inbound_trunk_fields(
    trunk_id = "<sip-trunk-id>",
    numbers = ListUpdate(add=['+15105550100']),         # Add to existing list
    allowed_numbers = ["+13105550100", "+17145550100"], # Replace existing list
    name = "My updated trunk",
  )
  
  print(f"Successfully updated trunk {trunk}")

  await livekit_api.aclose()

asyncio.run(main())

```

---

**Ruby**:

```ruby
require 'livekit'

lkapi = LiveKit::LiveKitAPI.new

update = LiveKit::Proto::SIPInboundTrunkUpdate.new(
  name: "My updated trunk",
  numbers: LiveKit::Proto::ListUpdate.new(set: ["+15105550100"]),        # Replace existing list
  allowed_numbers: LiveKit::Proto::ListUpdate.new(add: ["+14155550100"]) # Add to existing list
)

trunk = lkapi.sip.update_sip_inbound_trunk_fields("<sip-trunk-id>", update)

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
  trunkName := "My updated inbound trunk"
  numbers := &livekit.ListUpdate{Set: []string{"+16265550100"}}                        // Replace existing list
  allowedNumbers := &livekit.ListUpdate{Add: []string{"+13105550100", "+17145550100"}} // Add to existing list

  trunkId := "<sip-trunk-id>"

  trunkInfo := &livekit.SIPInboundTrunkUpdate{
    Name: &trunkName,
    Numbers: numbers,
    AllowedNumbers: allowedNumbers,
  }

  // Create a request
  request := &livekit.UpdateSIPInboundTrunkRequest{
    SipTrunkId: trunkId,
    Action: &livekit.UpdateSIPInboundTrunkRequest_Update{
      Update: trunkInfo,
    },
  }

  api, err := lksdk.NewLiveKitAPI()
  if err != nil {
    fmt.Println(err)
    return
  }

  // Update trunk
  trunk, err := api.SIP().UpdateSIPInboundTrunk(context.Background(), request)

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
import io.livekit.server.UpdateSipInboundTrunkOptions

val api = LiveKitAPI.createClient()

val response = api.sip.updateSipInboundTrunk(
    sipTrunkId = trunkId,
    options = UpdateSipInboundTrunkOptions(
        name = "My updated trunk",
        numbers = listOf("+15105550123")
    )
).execute()

if (!response.isSuccessful) {
    println(response.errorBody())
} else {
    val trunk = response.body()

    if (trunk != null) {
        println("Updated inbound trunk: ${trunk}")
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

    let update = proto::SipInboundTrunkUpdate {
        name: Some("My updated inbound trunk".to_owned()),
        numbers: Some(proto::ListUpdate { set: vec!["+16265550100".to_owned()], ..Default::default() }),
        allowed_numbers: Some(proto::ListUpdate {
            add: vec!["+13105550100".to_owned(), "+17145550100".to_owned()],
            ..Default::default()
        }),
        ..Default::default()
    };

    let trunk = api
        .sip()
        .update_sip_inbound_trunk("<sip-trunk-id>".to_owned(), update)
        .await
        .unwrap();

    println!("Updated inbound trunk: {:?}", trunk);
}

```

---

**LiveKit Cloud**:

Update and replace functions are the same in the LiveKit Cloud dashboard. For an example, see the [replace inbound trunk](#replace-inbound-trunk) section.

### Replace inbound trunk

The `UpdateSIPInboundTrunk` API allows you to replace an existing inbound trunk with a new one using the same trunk ID.

**LiveKit CLI**:

The CLI doesn't support replacing inbound trunks.

---

**Node.js**:

```typescript
import { LiveKitAPI, SIPInboundTrunkInfo } from 'livekit-server-sdk';

const api = new LiveKitAPI();

async function main() {
  // Replace an inbound trunk entirely.
  const trunk = new SIPInboundTrunkInfo({
    name: 'My replaced trunk',
    numbers: ['+17025550100'],
    metadata: 'Replaced metadata',
    allowedAddresses: ['192.168.254.10'],
    allowedNumbers: ['+14155550100', '+17145550100'],
  });

  const updatedTrunk = await api.sip.updateSipInboundTrunk(trunkId, trunk);

  console.log('replaced trunk ', updatedTrunk);
}

await main();

```

---

**Python**:

To replace an existing trunk, edit the previous example by adding the import line,`trunk` and calling the `update_inbound_trunk` function:

```python
async def main():
  livekit_api = api.LiveKitAPI()

  trunk = api.SIPInboundTrunkInfo(
      numbers = ['+15105550100'],
      allowed_numbers = ["+13105550100", "+17145550100"],
      name = "My replaced inbound trunk",
  )

  # This takes positional parameters
  trunk = await livekit_api.sip.update_inbound_trunk("<sip-trunk-id>", trunk)

```

---

**Ruby**:

```ruby
require 'livekit'

lkapi = LiveKit::LiveKitAPI.new

# Replace an inbound trunk entirely.
trunk = LiveKit::Proto::SIPInboundTrunkInfo.new(
  name: "My replaced inbound trunk",
  numbers: ["+15105550100"],
  allowed_numbers: ["+13105550100", "+17145550100"],
)

updated_trunk = lkapi.sip.update_sip_inbound_trunk("<sip-trunk-id>", trunk)

puts updated_trunk

```

---

**Go**:

To replace the trunk, update the previous example with the following `trunkInfo` and `request` objects:

```go
  // To replace the trunk, use the SIPInboundTrunkInfo object.
  trunkInfo := &livekit.SIPInboundTrunkInfo{
      Numbers: numbers,
      AllowedNumbers: allowedNumbers,
      Name: trunkName,
  }

  // Create a request.
  request := &livekit.UpdateSIPInboundTrunkRequest{
    SipTrunkId: trunkId,
    // To replace the trunk, use the Replace action instead of Update.
    Action: &livekit.UpdateSIPInboundTrunkRequest_Replace{
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

// Replace an inbound trunk entirely.
val trunk = LivekitSip.SIPInboundTrunkInfo.newBuilder()
    .setName("My replaced inbound trunk")
    .addAllNumbers(listOf("+15105550100"))
    .addAllAllowedNumbers(listOf("+13105550100", "+17145550100"))
    .build()

val response = api.sip.updateSipInboundTrunk(trunkId, trunk).execute()

if (!response.isSuccessful) {
    println(response.errorBody())
} else {
    val updatedTrunk = response.body()

    if (updatedTrunk != null) {
        println("Replaced inbound trunk: ${updatedTrunk}")
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

    // Replace an inbound trunk entirely.
    let trunk = proto::SipInboundTrunkInfo {
        name: "My replaced inbound trunk".to_owned(),
        numbers: vec!["+15105550100".to_owned()],
        allowed_numbers: vec!["+13105550100".to_owned(), "+17145550100".to_owned()],
        ..Default::default()
    };

    let trunk = api
        .sip()
        .update_sip_inbound_trunk_replace("<sip-trunk-id>".to_owned(), trunk)
        .await
        .unwrap();

    println!("Replaced inbound trunk: {:?}", trunk);
}

```

---

**LiveKit Cloud**:

1. Sign in to the **Telephony** → [**SIP trunks**](https://cloud.livekit.io/projects/p_/telephony/trunks) page.
2. Navigate to the **Inbound** section.
3. Find the inbound trunk you want to replace → select the more (**⋮**) menu → select **Configure trunk**.
4. Copy and paste the following text into the editor:

```json
{
  "name": "My replaced trunk",
  "numbers": [
    "+17025550100"
  ],
  "metadata": "Replaced metadata",
  "allowedAddresses": ["192.168.254.10"],
  "allowedNumbers": [
    "+14155550100",
    "+17145550100"
  ]
}

```
5. Select **Update**.

---

This document was rendered at 2026-08-24T21:31:18.332Z.
For the latest version of this document, see [https://docs.livekit.io/telephony/accepting-calls/inbound-trunk.md](https://docs.livekit.io/telephony/accepting-calls/inbound-trunk.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).
