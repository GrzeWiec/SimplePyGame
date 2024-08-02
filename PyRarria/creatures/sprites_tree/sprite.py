from creatures.sprites_tree.abstract_sprite import AbstractSprite
from creatures.hp_bar import HpBar
from creatures.physical_engine import *
from creatures.vector import PVector

ANIMATION = None
OBJECT = None


class Sprite(AbstractSprite):
    def __init__(self, x, y):
        super(Sprite, self).__init__(x, y)
        # self.create(x, y, **OBJECT)

    def create(self, x, y, manoeuvrability, maxspeed, maxforce, maxhp, mass, items, damage, defense):

        # variables
        self.radius = min(self.width, self.height)
        self.angle = 0.0
        self.mass = mass

        # limits
        self.maxspeed = maxspeed
        self.maxforce = maxforce
        self.maxhp = maxhp
        self.manoeuvrability = manoeuvrability

        # flags
        self.is_enemy = True
        self.is_hpbar = False
        self.is_hitbox = False
        self.is_fixpos = True

        # counters
        self.anim_count = 0
        self.bite_count = 0
        self.shot_count = 0
        self.freeze_count = 0

        # vectors
        self.position = PVector(x, y)
        self.velocity = PVector(0, 0.001)
        self.acceleration = PVector(0, 0)
        self.acceleration_no_limit = PVector(0, 0)

        # body
        w, h = self.width, self.height
        self.rect = pg.rect.Rect(0, 0, w, h)
        self.rect.center = self.position.repr()
        self.body = pg.rect.Rect(self.rect)
        self.hpbar = HpBar(self.body.midtop)

        # sprite specific
        self.hp = maxhp
        self.items = items
        self.damage = damage
        self.defense = defense

    def draw(self, win):
        pass

    def bite(self, player):
        if self.is_enemy and self.rect.colliderect(player):
            if self.bite_count > 0:
                self.bite_count -= 1
            else:
                direction = -1
                if self.position.x < player.position.x:
                    direction = 1
                player.hit(self.damage, direction)
                self.bite_count = 20

    def hit(self, player, damage_points):
        self.hp -= damage_points
        push_away(self, player, damage_points / self.maxhp)
        print(damage_points / self.maxhp)
        self.is_hpbar = True

    def update(self, player, blocks, map_position, items_factory):
        # dead
        if self.hp <= 0:
            self.die(items_factory)
            return

        # alive
        self.update_forces(player, blocks)
        self.move(map_position)
        self.fix_move(blocks, map_position)

    def move(self, map_position):
        # velocity
        self.velocity += self.acceleration
        self.velocity.xlimit(self.maxspeed)
        self.velocity += self.acceleration_no_limit
        self.position += self.velocity
        self.acceleration.zero()
        self.acceleration_no_limit.zero()

        # update body
        self.body.topleft = (self.position + map_position).repr()
        self.rect.topleft = (self.position + map_position).repr()
        self.hpbar.center(self.body.midtop)

        # update animation counter
        self.anim_count -= 1
        self.anim_count %= self.animation_ticks

    def fix_move(self, blocks, map_position):
        dx, dy = 0.0, 0.0

        hits = pg.sprite.spritecollide(self, blocks, False)
        if hits:
            hit = hits[0].rect
            rect = self.rect

            # vertical up
            if rect.top < hit.top and abs(rect.bottom - hit.bottom) > abs(rect.bottom - hit.top):
                dy = hit.top - rect.bottom
                self.velocity.y = 0.0

            # vertical down
            elif rect.bottom > hit.bottom and rect.left > hit.left and rect.right < hit.right:
                dy = hit.bottom - rect.top
                self.velocity.y = 0.0

            self.position.y += dy
            self.body.topleft = (self.position + map_position).repr()
            self.rect.topleft = (self.position + map_position).repr()
            self.hpbar.center(self.body.midtop)

        hits = pg.sprite.spritecollide(self, blocks, False)
        if hits:
            dx = 0.0
            hit = hits[0].rect
            rect = self.rect

            # vertical
            if rect.left < hit.left:
                dx = hit.left - rect.right
                self.velocity.x = 0.0
                reaction(self)
            elif rect.right > hit.right:
                dx = hit.right - rect.left
                self.velocity.x = 0.0
                reaction(self)

            self.position.x += dx
            self.body.topleft = (self.position + map_position).repr()
            self.rect.topleft = (self.position + map_position).repr()
            self.hpbar.center(self.body.midtop)

    def apply_force(self, force):
        force.limit(self.maxforce)
        self.acceleration += force

    def apply_force_no_limit(self, force):
        self.acceleration_no_limit += force

    def die(self, items_factory):
        # creature has got its own items
        if self.items:
            for item_name in self.items:
                items_factory.add_item(item_name, *self.position.repr())

        # creature hasn't got its own items
        else:
            items_factory.add_random_item(*self.position.repr())

        self.kill()

    def quiet_die(self):
        self.kill()

    def update_forces(self, player, blocks):
        pass
