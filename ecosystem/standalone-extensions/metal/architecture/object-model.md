# Object model

One PHP object per native object, boxed as the binding's declared type, retained while PHP holds it.

## Overview

Every handle uses `metal_object { id ptr; zend_object std; }`. `ptr` is retained. `free_obj` releases it inside an autorelease pool and removes its identity-table entry.[^header]

Metal's concrete classes are private (`AGXG13GDevice` and the like), so boxing does not walk the Objective-C class chain. `metal_box` and `metal_box_owned` take the PHP class the binding declared. `metal_box` retains. `metal_box_owned` takes a +1 object (`new…`, `alloc`/`init`, `MTLCreateSystemDefaultDevice`) without a second retain, and releases that +1 when a box already exists.[^runtime]

The identity table is module global `boxes`: native address → `zend_object*`, not refcounted. The same native object in one thread is the same PHP object. The table is created in GINIT and destroyed in GSHUTDOWN, so each ZTS thread has its own table and does not share PHP objects with another thread.

`fromPointer(0)` throws `MetalException`. Otherwise the called class's `metal_map_native` entry is checked with `conformsToProtocol:` for a protocol type and `isKindOfClass:` for a real class. A mismatch throws. Any other address is trusted to hold an object.

A sub-object getter (`colorAttachments()`, `objectAtIndexedSubscript()`) uses `metal_box`, which retains. The PHP object stays valid after the parent is freed.

Value classes (`MTLOrigin`, `MTLSize`, `MTLRegion`, `MTLClearColor`, `MTLViewport`, `MTLScissorRect`, `CGSize`) are plain PHP objects with public properties. They are not handles.

Wrappers are not constructible, not cloneable (`clone_obj = NULL`), and not serializable.

[^runtime]: Boxing and fromPointer
[^header]: metal_object and module globals
