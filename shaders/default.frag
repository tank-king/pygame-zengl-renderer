#version 300 es
precision mediump float;

in vec3 color;
in vec2 tex_coord;
out vec4 out_color;

uniform sampler2D u_texture;

void main(){
    vec4 t_color = texture(u_texture, tex_coord);
    vec3 mult = mix(color.rgb * 0.9, t_color.rgb, step(0.99, t_color.a));
    out_color = vec4(mult, 1.0);
    // if a == 0 then color else white           k := step(0.1, a) => if a >= 0.1 then 1 else 0
    // mix (white, color, k) => if k == 0 then white else color
    // GLSL
}