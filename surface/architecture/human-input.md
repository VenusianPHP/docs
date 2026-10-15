# HumanInput

Keyboards, mice, game pads and game controllers from every source in one vocabulary, read as state once per frame.

## Overview

Split `venusian-surface/human-input`, container `human-input` = `HumanInputManager`, facade `Surface\HumanInput\MagicAliases\HumanInput`. Contracts live in `Surface\Contracts\HumanInput`: `Key`, `MouseButton`, `GamepadButton`, `GamepadAxis`, `ButtonState`, `Modifiers`, the device interfaces (`Keyboard`, `Mouse`, `GamePad`, `GameController`) and the source interfaces (`InputSource`, `InputEngineDriver`, `PadSource`, `Circuits\ButtonPad`, `Circuits\GameController`). Surface names no toolkit and no pad package.[^manager]

## Sources

| Source | Gives | Starts | Registered by |
|---|---|---|---|
| Input engine (`InputEngineDriver`) | keyboard, mouse | when that toolkit's bridge session connects; stops when it leaves | the toolkit package: `app('human-input')->extend('<toolkit>', fn (InputFrame $frame): InputEngineDriver => …)` |
| Pad source (`PadSource`) | every pad, window or not | first poll; the one `human-input.pads.<os>` names | the pad package: `extendPads('<name>', …)` |
| Circuit (`ButtonPad`) | one pad from a board | `HumanInput::attach($ic, 'p1')` (returns `ICInput`) | the sketch; `detach($name)` |

One pad source per process lists every pad once; engines list none. A circuit replaces a device of the same name. Several toolkit sessions (Linux): one merged keyboard, one merged mouse; position, window and buttons follow the engine that reported last, motion and wheel sum.

## Reads

* `keyboard()`: `isDown`, `isPressed`, `wasReleased`, `isHolding(key, ms)`, `downKeys`, `pressedKeys`, `releasedKeys`, `text()`, `modifiers()`.
* `mouse()`: `x`, `y`, `window()`, `motion()`, `wheel()`, `button`/`isDown`/`isPressed`/`wasReleased` by `MouseButton`.
* `gamePads()` (no sticks) / `gameControllers()` (sticks): arrays by id. `GamePad`: `id`, `name`, `supports`, `button`, `isDown`, `isPressed`, `wasReleased`, `isHolding`, `downButtons`, `pressedButtons`, `hardwareId()` (same physical pad across a reconnect, null without identity), `setPlayerIndex(?int)`. `GameController` adds `axes`, `axis`, `leftStick`, `rightStick`, `leftTrigger`, `rightTrigger`.

Errors land on the reads that need them: a connected session without a registered engine → keyboard and mouse reads throw `HumanInputException`; pad source unregistered or its connect failed → pad reads throw, and the next poll retries the connect. A faulted circuit is released, mailed disconnected and never polled again; `detach()` + `attach()` recovers.

## Frames

`InputFrame` length = `1 / sketches.refresh_rate`. Edges (`isPressed`, `wasReleased`, text, motion, wheel) stay until a frame reads input, so a tap between two frames reads both edges in the next; input unread for two frame lengths drops its edges. A frame's first read applies what the toolkit dispatched since the last poll.

`HumanInputPoller` (resource `input`, `Background`) joins the loop when `event-loop` is first resolved: one `poll()` per turn, never keeps the loop alive; the loop's stop hook calls `destroy()` before the sketch's own shutdown. Without a loop call `HumanInput::poll()` once per frame.

## Mail

`GamepadConnected` → `input.gamepad.connected.<id>`, `GamepadDisconnected` → `input.gamepad.disconnected.<id>`, once per change, posted to the loop when it is resolved.

## Examples

```php
use Surface\Contracts\HumanInput\Key;
use Surface\HumanInput\MagicAliases\HumanInput;

public function loop(array $mail = []): SketchLoopResult
{
    if (HumanInput::keyboard()->isPressed(Key::SPACE)) {
        $this->jump();
    }

    foreach (HumanInput::gameControllers() as $pad) {
        $this->x += 2.0 * $pad->leftStick()['x'];
    }

    return SketchLoopResult::CONTINUE;
}
```

Config: [config](/docs/{{version}}/surface/api/config). Pad sources and engines: the jovian driver bundles.

[^manager]: HumanInputManager, HumanInputServiceProvider, HumanInputPoller, README
