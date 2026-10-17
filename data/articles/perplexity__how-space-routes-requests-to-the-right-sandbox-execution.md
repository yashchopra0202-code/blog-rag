---
url: https://www.perplexity.ai/hub/blog/how-space-routes-requests-to-the-right-sandbox-execution
title: How SPACE routes requests to the right sandbox execution
site: perplexity
date: 2026-10-14
scraped_at: 2026-10-17T08:10:46+00:00
---

Perplexity's SPACE binds AI agent requests to the right sandbox execution with identity checks and signed routes.

Contents

When someone asks an AI agent to analyze a spreadsheet or test software, they’re trusting it to work safely with their files and data. Agents need isolated environments where they can carry out that work without exposing other users’ data or interfering with their workloads.

As agents take on more complex tasks with greater autonomy, these environments help contain mistakes and limit the damage that unsafe or malicious code can cause. Sandboxes provide that isolation while sharing control-plane services, worker nodes, and routing infrastructure.

That shared infrastructure must deliver each operation to the execution authorized to handle it. A stale route can send a valid request to another sandbox, or to an older execution of the right sandbox.

, Perplexity’s secure sandbox platform, binds each operation to a selected execution and checks the destination before forwarding.

For months, SPACE has handled millions of executions per day, each protected by a unique cryptographic identity, with an error rate below 0.0002% and zero dropped connections.

Sandbox security also depends on getting each request to the right destination. Even a simple file read passes through shared infrastructure that must keep track of where the sandbox is running as it pauses, resumes, or moves between machines.

A file read travels through several components. SPACE’s control plane resolves the sandbox to an execution and worker. The request enters through

, passes to the sandbox manager,

, and crosses a Unix socket to the host bridge,

. The bridge forwards it over VSOCK, the host-to-guest socket transport, to

inside the Firecracker microVM.

Each decision relies on state that can lag behind infrastructure changes. A database may retain an old placement, a cached address may point elsewhere, or a socket path may acquire a different listener. A successful connection can still reach the wrong destination. A read could expose another user’s data; a write could modify the wrong filesystem.

Snapshots add another issue. Resuming a sandbox on another worker preserves its logical identity but starts a new execution. A delayed request or surviving connection may reach its predecessor and return old state under the right sandbox name.

SPACE separates the user’s environment from the runtime serving it:

An execution generation distinguishes runtime incarnations. On Kubernetes, the route also includes the pod UID. Addresses locate endpoints; execution identity determines whether those endpoints may serve the operation.

Suppose sandbox S runs as execution 7 on worker A, then resumes as execution 8 on worker B. A request selected for execution 8 must fail if it reaches execution 7. Checking only the sandbox ID would miss the disagreement.

Each request carries signed proof of which sandbox execution may handle it and what access is allowed. The receiving component checks that proof against its own runtime identity before letting the request proceed.

After caller authorization, SPACE issues a short-lived, signed capability identifying the sandbox, execution, placement, and permitted access. Public service-port capabilities also specify the allowed port and protocol.

The receiving sandbox manager verifies the signature and compares the complete identity with its locally persisted runtime record. The signature establishes who authorized the selection. The comparison establishes whether that selection matches the receiver.

ServicePort traffic receives a second check at the per-sandbox network gateway,

, before a guest connection opens. The gateway compares the identity against trusted activation state and checks the port and protocol. Control operations proceed to bridge endpoint verification.

SPACE uses Ed25519 signatures. Control-plane signing keys issue capabilities; public verification keys on workers and gateways cannot issue them.

Capabilities last 120 seconds, with up to 15 seconds of expiration clock-skew allowance. A valid signature and unexpired token are still insufficient when the selected and installed identities disagree.

The receiving worker can catch a routing mistake even when the request itself is authorized. It checks whether it is running the execution selected for that request and rejects the request if they differ.

If a request selected for execution 8 reaches worker A, which still serves execution 7, worker A rejects it before forwarding. Once a receiver installs execution 8’s identity, it also rejects capabilities for execution 7, even before they expire.

There’s an important boundary to this guarantee. A capability for execution 7 can still match a worker serving execution 7 until that worker learns of retirement or the capability expires. Local enforcement and bounded capability lifetime work together while updates propagate.

A matching runtime record establishes the intended execution. The control bridge must also reach the processes and transport belonging to that activation, rather than a replacement that inherited the same address.

The sandbox and node managers verify the host bridge’s peer credentials and both bridge and Firecracker process identities, including start times, detecting reused IDs or changed executables

Transport checks tie the VSOCK listener to the expected Firecracker process using socket ownership, guest identity, and kernel socket evidence. The bridge forwards operations only after verification and refuses transparent reconnects. Every new connection must pass the checks again.

This verification covers the Firecracker control bridge on Kubernetes and directly managed hosts. ServicePort traffic uses execution and port checks at its gateway; it does not attest the identity of an arbitrary application inside the guest.

Some connections stay open while a sandbox’s execution changes, so identity checks must extend beyond the initial request. SPACE retires connections tied to the old execution and lets eligible operations reconnect to the current one under the same security checks.

Terminals and file watches can outlive their opening requests. SPACE ties backend streams to an identity epoch so a stream cannot remain attached to its predecessor after the receiver installs a replacement execution.

SPACE rechecks durable identity before opening a stream. Replacing its route or execution cancels the stream’s lease, stopping input and output.

Ownership changes are distinct from execution replacement. A lifecycle-operation handoff on an unchanged Kubernetes resident preserves its route identity, unexpired capabilities, and streams. The gateway also preserves established streams for activation-attempt-only changes within the same route and execution generation. New opens require the updated identity.

Recovery keeps these checks intact. The identity comparator can return

for an incarnation mismatch within the same sandbox, or

for a different sandbox. Only a recognized refresh signal triggers route repair after identity rejection. Transport failures follow separate, operation-specific recovery rules. Invalid signatures, purposes, or port profiles remain denied.

An eligible operation can resolve the current execution and make one rebuilt attempt. Cache replacement is conditional on the rejected route, preventing a delayed rejection from evicting a newer entry. Native-session refresh preserves the original cache expiry, separating route repair from renewal of caller authorization.

Replay rules remain operation-specific. A replacement backend must pass admission again, even when the client-facing WebSocket stays open.

Execution identity becomes security-critical state. Control-plane updates and verification-key bundles must reach serving components, and retirement takes effect when each receiver installs the update. Short capability lifetimes bound reuse during propagation.

The design assumes identity enforcement is enabled and trusts the control-plane signer, worker kernel, and node-local management services. Worker-root or privileged cluster-administrator compromise is outside the threat model. Bridge verification is local process and transport verification, not hardware-backed remote attestation.

Signature verification, runtime comparisons, and bridge validation add work to the request path. They use local state rather than a remote authorization lookup at every private hop.

The relevant comparison is how platforms handle an authorized request reaching the wrong execution of the right sandbox. These findings concern the inspected implementations, not overall platform security. SPACE, OpenShell, and E2B were checked on October 8, 2026:

Safe delegation depends on keeping each agent’s work within the boundaries intended for it. A microVM provides isolation, while the surrounding platform must ensure that every request and ongoing connection reaches the execution authorized to handle it.

SPACE makes execution identity part of that protection. By checking destinations, verifying bridge endpoints, and tying connections to the execution that authorized them, it preserves those boundaries as sandboxes pause, resume, and move.

We’re continuing the work as the infrastructure evolves. For SPACE and other sandbox platforms, security requires testing these paths against both routine routing mistakes and hostile workloads, then strengthening the boundaries wherever those tests reveal gaps.
