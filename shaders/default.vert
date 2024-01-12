#version 300 es
precision mediump float;

layout (location = 0) in vec2 in_position;
layout (location = 1) in vec2 in_tex_coord;
layout (location = 2) in vec3 in_color;

out vec3 color;
out vec2 tex_coord;

uniform float scale;
uniform float angle;

vec2 rotate(vec2 v, float angle) {
    float c = cos(angle);
    float s = sin(angle);
    return vec2(v.x * c - v.y * s, v.x * s + v.y * c);
}

void main() {
    gl_Position = vec4(rotate(in_position * scale, radians(angle)), 0.0, 1.0);
    color = vec3(in_color);
    tex_coord = vec2(in_tex_coord);
}