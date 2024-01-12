#version 300 es
precision mediump float;

in vec4 color;
in vec2 tex_coord;
out vec4 out_color;

uniform sampler2D u_texture;

void main(){
    vec4 t_color = texture(u_texture, tex_coord);
    vec4 mult = t_color * color;
    out_color = mult;
//    if (out_color.r != 123.1112){
//        out_color = vec4(1, 1, 1, 0);
//    }
//    out_color = mix(t_color, color, 1.0);
}