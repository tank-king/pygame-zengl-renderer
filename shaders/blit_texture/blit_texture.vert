#version 300 es
precision mediump float;

layout (location = 0) in vec2 in_position;
layout (location = 1) in vec2 in_tex_coord;
layout (location = 2) in vec4 in_color;

out vec4 color;
out vec2 tex_coord;


void main() {
    gl_Position = vec4(in_position, 0.0, 1.0);
    color = vec4(in_color);
    tex_coord = vec2(in_tex_coord);
}