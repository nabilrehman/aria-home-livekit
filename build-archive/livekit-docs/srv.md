LiveKit docs › Build Agents › Agent Server › Overview

---

# Agent server overview

> An overview of agent server components for LiveKit Agents.

## Overview

LiveKit Agents supports an agent server architecture for managing multiple concurrent agent sessions and programmatic participants. Use dispatch, job execution, and configuration options to scale your agents horizontally and manage their lifecycles.

### Programmatic participants

The Agents framework isn't limited to AI agents. You can use it to deploy any code that needs to process realtime media and data streams as a programmatic participant. A programmatic participant is any code that joins a LiveKit room as a participant — this includes AI agents, media processors, or custom logic that processes realtime streams.

Some examples of what these participants can do include:

- **Process audio streams**: Analyze audio for patterns, quality metrics, or content detection.
- **Handle video processing**: Apply computer vision, video effects, or content moderation.
- **Manage data flows**: Aggregate, transform, or route realtime data between participants.
- **Provide services**: Act as bridges to external APIs, databases, or other systems.

The framework provides the same production-ready infrastructure for all types of programmatic participants, including automatic scaling and load balancing. You can use the [entrypoint function](https://docs.livekit.io/agents/server/job.md#entrypoint) without creating an `AgentSession` to build programmatic participants that are automatically dispatched to rooms.

- **[Processing raw media tracks](https://docs.livekit.io/transport/media/raw-tracks.md)**: Learn how to process raw audio and video tracks in your programmatic participants.

## Agent server components

Use core components to manage agent servers, including agent dispatch, job execution, and configuration.

| Component | Description | Use cases |
| **Agent dispatch** | Assign agents to rooms automatically or explicitly, with load balancing and high concurrency support. | Automatic agent assignment, explicit dispatch control, and custom dispatch logic. |
| **Job lifecycle** | Manage the entrypoint function, job execution, and session cleanup for each agent instance. | Entrypoint configuration, session management, and graceful shutdown. |
| **Server options** | Configure permissions, dispatch rules, prewarm functions, and server behavior. | Permission management, load balancing configuration, and server initialization. |

## In this section

Read more about each component.

- **[Server lifecycle](https://docs.livekit.io/agents/server/lifecycle.md)**: How agent servers register, receive requests, and manage jobs.

- **[Agent dispatch](https://docs.livekit.io/agents/server/agent-dispatch.md)**: Specify how and when agents are assigned to rooms.

- **[Job lifecycle](https://docs.livekit.io/agents/server/job.md)**: Learn about the entrypoint function and session management.

- **[Server options](https://docs.livekit.io/agents/server/options.md)**: Configure permissions, dispatch rules, and server behavior.

---

This document was rendered at 2026-08-23T06:19:28.009Z.
For the latest version of this document, see [https://docs.livekit.io/agents/server.md](https://docs.livekit.io/agents/server.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).