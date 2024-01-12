import logging
from typing import Sequence

import numpy
import pygame.display
import zengl

from utils import *


# TODO fix rendering logic

class Frame:
    def __init__(self, ctx):
        self.ctx = ctx

    def __enter__(self):
        self.ctx.new_frame()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ctx.end_frame()


class Renderer:
    _init = False

    def __init__(self, size=(1000, 800), shader_path=None):
        if Renderer._init:
            raise Exception("Renderer already set up")
        self.width = size[0]
        self.height = size[1]
        self.shader_path = shader_path if shader_path else Path(__file__).parent / 'shaders'
        self._size = self.size
        self._preserve_aspect = True
        self.ctx = zengl.context()
        self.image = self.ctx.image(self.size, 'rgba8unorm')
        self.output = self.ctx.image(self.size, 'rgba8unorm')
        # self.pipelines: dict[str, zengl.Pipeline] = {}
        # self.pipelines = {
        #     i: self.__getattribute__(f'pipeline_for_{i}')() for i in ['blit_texture']
        # }
        self._curr_pipeline = 'blit_texture'

    # def __del__(self):
    #     for i in self.pipelines.values():
    #         self.ctx.release(i)

    def _shader_from_dir(self, directory):
        return load_shaders((self.shader_path / directory / directory).__str__())

    @property
    def pipeline(self):
        return self.pipelines[self._curr_pipeline]

    @property
    def size(self):
        return self.width, self.height

    @staticmethod
    def buffer(args, dtype='f4'):
        return numpy.array(args, dtype=dtype)

    def clear(self, color=None):
        if color:
            self.image.clear_value = [*pygame.Color(color).normalize()]
        self.image.clear()

    @staticmethod
    def empty_buffer(n, dtype='f4'):
        return numpy.zeros(n).astype(dtype)

    def set_float_uniform(self, uniform, value):
        self.pipeline.uniforms[uniform][:] = float_bytes(value)

    def new_frame(self):
        return Frame(self.ctx)

    def resize(self, width, height):
        self.width = width
        self.height = height
        if not self._preserve_aspect:
            self._size = self.size
            self.ctx.release(self.image)
            self.image = self.ctx.image(self.size, 'rgba8unorm')
        self.output = self.ctx.image(self.size, 'rgba8unorm')

    def draw_texture(self,
                     texture: 'Texture',
                     src_rect=None,
                     dst_rect=None,
                     target: 'Texture' = None,
                     angle=0.0,
                     scale=1.0,
                     ):
        if not target:
            target_tex = self.image
        else:
            target_tex = target.texture
        src_rect = pygame.Rect(*src_rect) if src_rect else pygame.Rect(texture.rect)
        dst_rect = pygame.Rect(*dst_rect) if dst_rect else pygame.Rect(0, 0, *target_tex.size)

        src_points = rect_to_normalized_vertices(src_rect, texture.size)
        dst_points = rotate_and_scale_rect_points(dst_rect, scale, angle)
        dst_points = [point_to_coordinates(i, target_tex.size, cartesian=True) for i in dst_points]

        a1, b1, c1, d1 = dst_points
        a2, b2, c2, d2 = src_points

        vertex_buffer = self.ctx.buffer(numpy.array([
            # format -> x, y, tx, ty, r, g, b
            *a1, *a2, 1.0, 1.0, 1.0, 1.0,  # A
            *b1, *b2, 1.0, 1.0, 1.0, 1.0,  # B
            *c1, *c2, 1.0, 1.0, 1.0, 1.0,  # C
            *d1, *d2, 1.0, 1.0, 1.0, 1.0,  # D
        ], dtype='f4'))

        index_buffer = self.ctx.buffer(numpy.array([
            0, 1, 2,
            2, 3, 0
        ], dtype='i4'), index=True)

        pipeline = self.ctx.pipeline(
            **self._shader_from_dir('blit_texture'),
            framebuffer=[target_tex],
            vertex_buffers=[
                *zengl.bind(vertex_buffer, '2f 2f 4f', 0, 1, 2)
            ],
            index_buffer=index_buffer,
            vertex_count=6,
            layout=[
                {
                    'name': 'u_texture',
                    'binding': 0
                }
            ],
            resources=[
                {
                    'type': 'sampler',
                    'binding': 0,
                    'image': texture.texture
                }
            ]
        )
        pipeline.render()
        self.ctx.release(pipeline)

    def present(self):
        if self._preserve_aspect:
            target_viewport = pygame.Rect(0, 0, *scale_rect(self.size, self._size))
        else:
            target_viewport = pygame.Rect(0, 0, *self.size)
        target_viewport.center = pygame.Vector2(*self.size) / 2
        r = target_viewport
        # self.ctx.new_frame()
        self.image.blit(self.output, target_viewport=(r.x, r.y, r.w, r.h), filter=True)
        self.output.blit()
        # self.ctx.end_frame()


class Texture:
    """
    May not be thread-safe due to __del__ method
    """

    def __init__(self, renderer: Renderer, size: Sequence[int], buffer=None):
        self.renderer = renderer
        self.size = size
        self.texture = renderer.ctx.image((size[0], size[1]), 'rgba8unorm', buffer, texture=True)
        self.rect = pygame.Rect(0, 0, *self.size)

    @staticmethod
    def from_surface(renderer: Renderer, surf: pygame.Surface):
        return Texture(renderer, surf.get_size(), pygame.image.tobytes(surf, 'RGBA', False))

    # def __del__(self):
    #     # logging.debug(f'Deleting texture {self}')
    #     self.renderer.ctx.release(self.texture)


if __name__ == '__main__':
    def main():
        shader_path = Path(__file__).parent / 'shaders'
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)s : %(message)s')
        pygame.init()
        pygame.display.set_mode([1000, 800], pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
        zengl.init()
        r = Renderer(pygame.display.get_surface().get_size())
        t = Texture(r, [400, 400])  # should be auto-cleaned on program exit
        t = Texture.from_surface(r, pygame.image.load('assets/crab.png'))
        clock = pygame.Clock()
        running = True
        while running:
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    running = False
                if e.type == pygame.QUIT:
                    running = False
                if e.type == pygame.WINDOWRESIZED:
                    r.resize(e.x, e.y)
            keys = pygame.key.get_pressed()
            with r.new_frame():
                if keys[pygame.K_p]:
                    r.clear('blue')
                else:
                    r.clear('red')
                r.draw_texture(t, src_rect=[0, 0, 800, 400], dst_rect=[0, 0, 800, 400])
                r.present()
            pygame.display.flip()
            clock.tick(0)
            pygame.display.set_caption(clock.get_fps().__int__().__str__())

        pygame.display.quit()


    main()
