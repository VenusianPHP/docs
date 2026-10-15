# Bindings

The gl, CGL, and EGL surface, grouped the way the extension was built.

## Overview

The stubs are the declaration. This is the grouping. Every `gl*` function requires a current context. CGL is compiled on macOS, EGL on Linux.[^stub]

## State

`glGetError`, `glGetString`, `glGetIntegerv`, `glFlush`, `glFinish`.

`glGetIntegerv` fills 4 ints for `GL_VIEWPORT` and `GL_SCISSOR_BOX`, 2 for `GL_MAX_VIEWPORT_DIMS`, and 1 for every other pname.

Constants: `GL_NO_ERROR`, `GL_VERSION`, `GL_RENDERER`, `GL_VENDOR`, `GL_SHADING_LANGUAGE_VERSION`, `GL_MAX_SAMPLES`, `GL_VIEWPORT`, `GL_SCISSOR_BOX`, `GL_MAX_VIEWPORT_DIMS`, `GL_MAX_TEXTURE_SIZE`.

## Programs

`glCreateShader`, `glShaderSource`, `glCompileShader`, `glGetShaderiv`, `glGetShaderInfoLog`, `glDeleteShader`, `glCreateProgram`, `glAttachShader`, `glBindAttribLocation`, `glLinkProgram`, `glGetProgramiv`, `glGetProgramInfoLog`, `glUseProgram`, `glDeleteProgram`, `glGetUniformLocation`, `glGetAttribLocation`, `glUniform1i`, `glUniform1f`, `glUniform2f`, `glUniform4f`, `glUniformMatrix4fv`.

Constants: `GL_VERTEX_SHADER`, `GL_FRAGMENT_SHADER`, `GL_COMPILE_STATUS`, `GL_LINK_STATUS`, `GL_INFO_LOG_LENGTH`, `GL_TRUE`, `GL_FALSE`.

## Buffers

`glGenVertexArrays`, `glBindVertexArray`, `glDeleteVertexArrays`, `glGenBuffers`, `glBindBuffer`, `glBufferData`, `glBufferSubData`, `glDeleteBuffers`, `glEnableVertexAttribArray`, `glDisableVertexAttribArray`, `glVertexAttribPointer`, `glMapBufferRange`, `glUnmapBuffer`, `glFenceSync`, `glClientWaitSync`, `glDeleteSync`.

Handle: `GLsync`. `glGen*` with `n < 0` is a `ValueError`.

Constants: `GL_ARRAY_BUFFER`, `GL_ELEMENT_ARRAY_BUFFER`, `GL_PIXEL_PACK_BUFFER`, `GL_PIXEL_UNPACK_BUFFER`, `GL_STATIC_DRAW`, `GL_DYNAMIC_DRAW`, `GL_STREAM_DRAW`, `GL_STREAM_READ`, `GL_FLOAT`, `GL_UNSIGNED_BYTE`, `GL_UNSIGNED_SHORT`, `GL_UNSIGNED_INT`, `GL_MAP_READ_BIT`, `GL_MAP_WRITE_BIT`, `GL_MAP_INVALIDATE_RANGE_BIT`, `GL_MAP_INVALIDATE_BUFFER_BIT`, `GL_SYNC_GPU_COMMANDS_COMPLETE`, `GL_SYNC_FLUSH_COMMANDS_BIT`, `GL_ALREADY_SIGNALED`, `GL_CONDITION_SATISFIED`, `GL_TIMEOUT_EXPIRED`, `GL_WAIT_FAILED`, `GL_BUFFER_SIZE`.

## Textures and framebuffers

`glGenTextures`, `glBindTexture`, `glTexImage2D`, `glTexSubImage2D`, `glTexParameteri`, `glActiveTexture`, `glDeleteTextures`, `glPixelStorei`, `glGenFramebuffers`, `glBindFramebuffer`, `glFramebufferTexture2D`, `glCheckFramebufferStatus`, `glDeleteFramebuffers`, `glGenRenderbuffers`, `glBindRenderbuffer`, `glRenderbufferStorage`, `glRenderbufferStorageMultisample`, `glFramebufferRenderbuffer`, `glDeleteRenderbuffers`, `glBlitFramebuffer`, `glDrawBuffers`, `glReadBuffer`, `glReadPixels`.

Constants: `GL_TEXTURE_2D`, `GL_TEXTURE0`, `GL_RGBA`, `GL_RGBA8`, `GL_RGB`, `GL_RED`, `GL_R8`, `GL_DEPTH24_STENCIL8`, `GL_TEXTURE_MIN_FILTER`, `GL_TEXTURE_MAG_FILTER`, `GL_TEXTURE_WRAP_S`, `GL_TEXTURE_WRAP_T`, `GL_NEAREST`, `GL_LINEAR`, `GL_CLAMP_TO_EDGE`, `GL_UNPACK_ALIGNMENT`, `GL_UNPACK_ROW_LENGTH`, `GL_PACK_ALIGNMENT`, `GL_PACK_ROW_LENGTH`, `GL_UNPACK_SKIP_ROWS`, `GL_UNPACK_SKIP_PIXELS`, `GL_PACK_SKIP_ROWS`, `GL_PACK_SKIP_PIXELS`, `GL_FRAMEBUFFER`, `GL_READ_FRAMEBUFFER`, `GL_DRAW_FRAMEBUFFER`, `GL_RENDERBUFFER`, `GL_COLOR_ATTACHMENT0`, `GL_DEPTH_STENCIL_ATTACHMENT`, `GL_FRAMEBUFFER_COMPLETE`, `GL_COLOR_BUFFER_BIT`, `GL_DEPTH_BUFFER_BIT`, `GL_STENCIL_BUFFER_BIT`, `GL_PIXEL_PACK_BUFFER_BINDING`, `GL_DRAW_FRAMEBUFFER_BINDING`, `GL_READ_FRAMEBUFFER_BINDING`.

## Draws

`glViewport`, `glScissor`, `glEnable`, `glDisable`, `glBlendFunc`, `glBlendFuncSeparate`, `glBlendEquation`, `glColorMask`, `glClearColor`, `glClearStencil`, `glClear`, `glStencilFunc`, `glStencilOp`, `glStencilOpSeparate`, `glStencilMask`, `glCullFace`, `glFrontFace`, `glDrawArrays`, `glDrawElements`.

Constants: `GL_BLEND`, `GL_SCISSOR_TEST`, `GL_STENCIL_TEST`, `GL_DEPTH_TEST`, `GL_CULL_FACE`, `GL_SRC_ALPHA`, `GL_ONE_MINUS_SRC_ALPHA`, `GL_ONE`, `GL_ZERO`, `GL_FUNC_ADD`, `GL_ALWAYS`, `GL_NEVER`, `GL_EQUAL`, `GL_NOTEQUAL`, `GL_KEEP`, `GL_REPLACE`, `GL_INVERT`, `GL_INCR_WRAP`, `GL_DECR_WRAP`, `GL_FRONT`, `GL_BACK`, `GL_FRONT_AND_BACK`, `GL_CW`, `GL_CCW`, `GL_TRIANGLES`, `GL_TRIANGLE_STRIP`, `GL_TRIANGLE_FAN`, `GL_LINES`, `GL_POINTS`.

## CGL (macOS)

Handles: `CGLPixelFormatObj`, `CGLContextObj`.

`CGLChoosePixelFormat`, `CGLDestroyPixelFormat`, `CGLCreateContext`, `CGLReleaseContext`, `CGLSetCurrentContext`, `CGLGetCurrentContext`, `CGLErrorString`, `CGLFlushDrawable`, `CGLSetParameter`.

Constants: `kCGLPFAOpenGLProfile`, `kCGLOGLPVersion_3_2_Core`, `kCGLOGLPVersion_GL4_Core`, `kCGLPFAColorSize`, `kCGLPFAAlphaSize`, `kCGLPFADepthSize`, `kCGLPFAStencilSize`, `kCGLPFAAccelerated`, `kCGLPFAAllowOfflineRenderers`, `kCGLCPSwapInterval`, `kCGLNoError`.

## EGL (Linux)

Handles: `EGLDisplay`, `EGLConfig`, `EGLContext`, `EGLSurface`.

`eglGetDisplay`, `eglGetPlatformDisplay`, `eglInitialize`, `eglTerminate`, `eglBindAPI`, `eglChooseConfig`, `eglCreateContext`, `eglDestroyContext`, `eglCreatePbufferSurface`, `eglDestroySurface`, `eglMakeCurrent`, `eglGetCurrentContext`, `eglGetCurrentDisplay`, `eglGetCurrentSurface`, `eglSwapBuffers`, `eglGetError`, `eglQueryString`; `eglSwapInterval`, `eglQuerySurface` (by reference), `eglSwapBuffersWithDamageKHR` (rects flat, four ints each, bottom-left origin; false with nothing swapped when the display's extension string does not list `EGL_KHR_swap_buffers_with_damage`). Constants `EGL_SWAP_BEHAVIOR`, `EGL_BUFFER_PRESERVED`, `EGL_BUFFER_DESTROYED`, `EGL_RENDER_BUFFER`, `EGL_BACK_BUFFER`, `EGL_SINGLE_BUFFER`.

Constants: `EGL_PLATFORM_SURFACELESS_MESA`, `EGL_DEFAULT_DISPLAY` (literal 0), `EGL_NONE`, `EGL_SUCCESS`, `EGL_OPENGL_ES_API`, `EGL_RENDERABLE_TYPE`, `EGL_OPENGL_ES3_BIT`, `EGL_SURFACE_TYPE`, `EGL_PBUFFER_BIT`, `EGL_RED_SIZE`, `EGL_GREEN_SIZE`, `EGL_BLUE_SIZE`, `EGL_ALPHA_SIZE`, `EGL_DEPTH_SIZE`, `EGL_STENCIL_SIZE`, `EGL_WIDTH`, `EGL_HEIGHT`, `EGL_DRAW`, `EGL_READ`, `EGL_CONTEXT_MAJOR_VERSION`, `EGL_CONTEXT_MINOR_VERSION`, `EGL_VENDOR`, `EGL_VERSION`, `EGL_EXTENSIONS`, `EGL_CLIENT_APIS`.

[^stub]: stubs/gl.stub.php
