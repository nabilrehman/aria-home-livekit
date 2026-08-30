warning: the LiveKit docs server is version 1.5.0 but this CLI was built for 1.4.x — consider updating lk to the latest version
## /deploy/admin/regions/agent-deployment

LiveKit docs › Manage & Deploy › Administration › Regions › Agent deployment

---

# Agent deployment

> Configure and manage agent deployments across multiple regions.

## Overview

When you deploy agents on LiveKit Cloud, each agent is assigned to a specific region. This region assignment determines where the agent's compute resources run and cannot be changed after creation. By default, users connect to the agent deployment in the region closest to them, minimizing network latency and ensuring responsive interactions.

For global apps, you can deploy the same agent to multiple regions. This provides redundancy and ensures users worldwide experience low latency by connecting to their nearest deployment. You can also control region assignment explicitly using agent dispatch to route users to specific regional deployments based on your app's requirements.

## Deployment regions

Each agent deployment is isolated to a single region, which you must select during the first deployment. For the current list of available regions, see [Agent deployment regions](https://docs.livekit.io/deploy/admin/regions/endpoints.md#agent-deployments).

Region assignment is immutable, and cannot be changed after agent creation.

## Multi-region deployments

To deploy an agent in multiple regions, use `lk agent create` once per region. To keep track of the deployments, add the region to the configuration filename. For instance, these commands deploy a new agent to both `us-east` and `eu-central` regions:

```shell
lk agent create --region us-east --config livekit.us-east.toml
lk agent create --region eu-central --config livekit.eu-central.toml

```

Now you can deploy the agent to each region as needed by specifying the appropriate configuration file:

```shell
lk agent deploy --config livekit.us-east.toml
lk agent deploy --config livekit.eu-central.toml

```

By default, users connect to the agent in the region closest to them. In some cases, if agents are at capacity, users may connect to an agent in a different region. For fine-grained control over which regions users connect to, set a separate agent name for each region and use [explicit dispatch](https://docs.livekit.io/agents/server/agent-dispatch.md) to directly assign users to the appropriate agent.

## Moving an agent to a new region

To move an existing agent to a new region, you should follow the preceding steps for [multi-region deployments](#multi-region-deployments) to add a deployment in the new region. Then, you can delete the agent in the old region using `lk agent delete`, specifying the old agent's ID or configuration file.

---

This document was rendered at 2026-08-24T21:33:05.578Z.
For the latest version of this document, see [https://docs.livekit.io/deploy/admin/regions/agent-deployment.md](https://docs.livekit.io/deploy/admin/regions/agent-deployment.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).
