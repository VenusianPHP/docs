# Bindings

Every function, class and constant ext-libsoundio binds, by libsoundio group; each function one libsoundio call.

## Overview

Stubs = declaration; `SUPPORT.md` counts 72 / 72 of the header's `SOUNDIO_EXPORT` functions.[^stubs] Names = C names. Translations: handle struct → handle class with live field properties; value struct → copied object; out-param → by-ref; counted list → PHP list plus its count parameter; buffer/area/`userdata`/off-thread callback → `int` address. Failure = C error code. Refusals: only the sites in `bindings.json`, each with a probe in `tests/Probes`.

| Group | Functions |
|---|---|
| Version | soundio_version_string, soundio_version_major, soundio_version_minor, soundio_version_patch |
| Context, backends, events | soundio_create, soundio_destroy, soundio_connect, soundio_connect_backend, soundio_disconnect, soundio_strerror, soundio_backend_name, soundio_backend_count, soundio_get_backend, soundio_have_backend, soundio_flush_events, soundio_wait_events, soundio_wakeup, soundio_force_device_scan |
| Channel layouts | soundio_channel_layout_equal, soundio_get_channel_name, soundio_parse_channel_id, soundio_channel_layout_builtin_count, soundio_channel_layout_get_builtin (index refused outside the table), soundio_channel_layout_get_default, soundio_channel_layout_find_channel, soundio_channel_layout_detect_builtin (layout by-ref), soundio_best_matching_channel_layout (two lists with their counts), soundio_sort_channel_layouts (list sorted in place, by-ref) |
| Formats | soundio_get_bytes_per_sample, soundio_format_string |
| Devices | soundio_input_device_count, soundio_output_device_count, soundio_get_input_device, soundio_get_output_device, soundio_default_input_device_index, soundio_default_output_device_index, soundio_device_ref, soundio_device_unref (releases on the last reference), soundio_device_equal, soundio_device_sort_channel_layouts, soundio_device_supports_format, soundio_device_supports_layout, soundio_device_supports_sample_rate, soundio_device_nearest_sample_rate |
| Output streams | soundio_outstream_create, soundio_outstream_destroy, soundio_outstream_open, soundio_outstream_start (refused with write_callback 0), soundio_outstream_begin_write (areas list and frame_count by-ref), soundio_outstream_end_write, soundio_outstream_clear_buffer, soundio_outstream_pause, soundio_outstream_get_latency (by-ref), soundio_outstream_set_volume (refused off CoreAudio/WASAPI) |
| Input streams | soundio_instream_create, soundio_instream_destroy, soundio_instream_open, soundio_instream_start (refused with read_callback 0), soundio_instream_begin_read, soundio_instream_end_read, soundio_instream_pause, soundio_instream_get_latency |
| Ring buffer | soundio_ring_buffer_create, soundio_ring_buffer_destroy, soundio_ring_buffer_capacity, soundio_ring_buffer_write_ptr (address), soundio_ring_buffer_advance_write_ptr, soundio_ring_buffer_read_ptr (address), soundio_ring_buffer_advance_read_ptr, soundio_ring_buffer_fill_count, soundio_ring_buffer_free_count, soundio_ring_buffer_clear |

Classes: handles `SoundIo`, `SoundIoDevice`, `SoundIoOutStream`, `SoundIoInStream`, `SoundIoRingBuffer`; values `SoundIoChannelLayout` (name, channel_count, channels list), `SoundIoSampleRateRange` (min, max), `SoundIoChannelArea` (ptr address, step).

Constants: every `SoundIoError*`, `SoundIoChannelId*`, `SoundIoChannelLayoutId*`, `SoundIoBackend*`, `SoundIoDeviceAim*` and `SoundIoFormat*` enumerator, the native-endian `SoundIoFormat*NE`/`*FE` aliases, and `SOUNDIO_MAX_CHANNELS`, with their header value.

[^stubs]: libsoundio, soundio, soundio_stream, soundio_types and soundio_constants stubs
