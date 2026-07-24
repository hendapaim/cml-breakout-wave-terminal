# CML2 consoles in Wave Terminal (Linux)

This directory uses Cisco CML2 `breakout` as a local console proxy and Wave
Terminal's `wsh run` command to create one terminal block per serial console.
It replaces the former SecureCRT-session generator; `config.ini` is retained
only for legacy use.

## First use

In a Wave terminal block, from this directory:

```bash
export BREAKOUT_USERNAME=admin
export BREAKOUT_PASSWORD='your-cml2-password'
./breakout -config config.yaml -labs labs.yaml init 'INIT'
python3 main.py INIT
```

The `init` command writes the CML2 lab and its console-port allocation to
`labs.yaml`. Confirm that the wanted lab and nodes are enabled there.

## Open the lab

Use the single launcher from a Wave terminal block:

```bash
python3 main.py INIT --run
```

Or run the generated `./wave-cml2` directly. It asks for the CML2 password
without echoing it when needed, refreshes `labs.yaml` from CML2 on every launch
and rebuilds itself with the active devices and their current console ports. It
then starts `breakout` in its own Wave block when it is not already running,
waits for the local console proxy,
then creates one Wave command block per enabled serial interface. Consoles use
`telnet` or `nc`.

The launcher is portable: it finds `breakout`, `config.yaml`, and `labs.yaml`
beside itself, so the complete directory can be moved or renamed. To use a
different proxy listener for one execution, set `CONSOLE_HOST`, for example
`CONSOLE_HOST=127.0.0.1 ./wave-cml2`.

The default listener is loopback-only (`[::1]`), so consoles are not exposed to
the network. Install `telnet` or `netcat-openbsd` if neither `telnet`, `nc`, nor
`ncat` is already available.
# cml-breakout-wave-terminal
