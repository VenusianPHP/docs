# SMBus helpers ≠ I2C_SMBUS ioctl

i2c_smbus_* helpers emulate register access via posix read/write; they do not issue I2C_SMBUS, so PEC/block-length semantics are not automatic.

## Symptom

`i2c_set_pec($bus, true)` appears to succeed, but `i2c_smbus_read_byte_data` / word / block helpers still fail on PEC-required devices, or block transfers lack the SMBus length byte / banked-address behavior expected from the kernel `I2C_SMBUS` path.

## Cause

The SMBus convenience helpers are **emulated** on top of `posix_read` / `posix_write` against the already-bound slave address. They do **not** issue the `I2C_SMBUS` ioctl (`I2COpCode::I2C_SMBUS`).[^readme][^bus]

Consequently:

- Kernel PEC computation for the SMBus ioctl path is **not** applied to these helpers — append the PEC byte manually if the device requires it.[^readme]
- SMBus block-length byte and banked addressing are **not** performed automatically.[^readme]
- `i2c_set_pec` only affects the kernel’s `I2C_SMBUS` ioctl path, which this package’s helpers do not use.[^readme]

`I2COpCode::I2C_SMBUS` and `SMBusSize` document the kernel vocabulary; they are not wired into the shipped `i2c_smbus_*` helpers.[^opcode]

## Mitigation

- Treat `i2c_smbus_*` as convenient register-access patterns for common sensor datasheets, not as a full SMBus protocol engine.[^readme]
- For PEC-required devices on the emulated path, append / verify the PEC byte in application code.
- Prefer `i2c_rdwr` when a device needs a repeated-START combined transaction rather than sequential write-then-read with STOPs.
- Do not assume enabling `i2c_set_pec` changes `i2c_smbus_*` behavior.

## Related

* [Helpers → Bus → posix/posi](/docs/{{version}}/ecosystem/gpio-modules/i2c/architecture/helpers-bus-posix)
* [Enums for kernel constants](/docs/{{version}}/ecosystem/gpio-modules/i2c/conventions/enums-for-kernel-constants)

[^readme]: README SMBus convenience and PEC notes
[^bus]: i2cSmbus* methods use posix_read / posix_write
[^opcode]: I2C_SMBUS opcode exists but helpers do not call it
