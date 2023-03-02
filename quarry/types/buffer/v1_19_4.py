from quarry.types.buffer.v1_14 import smelt_types
from quarry.types.buffer.v1_19_3 import Buffer1_19_3

simple_recipe_types = ('minecraft:crafting_decorated_pot', 'minecraft:crafting_special_armordye',
                       'minecraft:crafting_special_bookcloning', 'minecraft:crafting_special_mapcloning',
                       'minecraft:crafting_special_mapextending',  'minecraft:crafting_special_firework_rocket',
                       'minecraft:crafting_special_firework_star', 'minecraft:crafting_special_firework_star_fade',
                       'minecraft:crafting_special_tippedarrow', 'minecraft:crafting_special_bannerduplicate',
                       'minecraft:crafting_special_shielddecoration', 'minecraft:crafting_special_shulkerboxcoloring',
                       'minecraft:crafting_special_suspiciousstew', 'minecraft:crafting_special_repairitem')


class Buffer1_19_4(Buffer1_19_3):

    @classmethod
    def pack_entity_metadata(cls, metadata):
        """
        Packs entity metadata.
        """

        pack_position = lambda pos: cls.pack_position(*pos)
        pack_global_position = lambda pos: cls.pack_global_position(*pos)

        out = b""
        for ty_key, val in metadata.items():
            ty, key = ty_key
            out += cls.pack('B', key)
            out += cls.pack_varint(ty)

            if   ty == 0:  out += cls.pack('b', val)
            elif ty == 1:  out += cls.pack_varint(val)
            elif ty == 2:  out += cls.pack('q', val)
            elif ty == 3:  out += cls.pack('f', val)
            elif ty == 4:  out += cls.pack_string(val)
            elif ty == 5:  out += cls.pack_chat(val)
            elif ty == 6:  out += cls.pack_optional(cls.pack_chat, val)
            elif ty == 7:  out += cls.pack_slot(**val)
            elif ty == 8:  out += cls.pack('?', val)
            elif ty == 9:  out += cls.pack_rotation(*val)
            elif ty == 10: out += cls.pack_position(*val)
            elif ty == 11: out += cls.pack_optional(pack_position, val)
            elif ty == 12: out += cls.pack_direction(val)
            elif ty == 13: out += cls.pack_optional(cls.pack_uuid, val)
            elif ty == 14: out += cls.pack_block(val)
            elif ty == 15: out += cls.pack_block(val)
            elif ty == 16: out += cls.pack_nbt(val)
            elif ty == 17: out += cls.pack_particle(*val)
            elif ty == 18: out += cls.pack_villager(*val)
            elif ty == 19: out += cls.pack_optional_varint(val)
            elif ty == 20: out += cls.pack_pose(val)
            elif ty == 21: out += cls.pack_varint(val)
            elif ty == 22: out += cls.pack_varint(val)
            elif ty == 23: out += cls.pack_optional(pack_global_position, val)
            elif ty == 24: out += cls.pack_varint(val) # Painting variant type
            elif ty == 25: out += cls.pack_varint(val) # Sniffer state
            elif ty == 26: out += None #FIXME: Vector
            elif ty == 27: out += None #FIXME: Quaternion
            else: raise ValueError("Unknown entity metadata type: %d" % ty)
        out += cls.pack('B', 255)
        return out

    def unpack_entity_metadata(self):
        """
        Unpacks entity metadata.
        """

        metadata = {}
        while True:
            key = self.unpack('B')
            if key == 255:
                return metadata
            ty = self.unpack('B')
            if   ty == 0:  val = self.unpack('b')
            elif ty == 1:  val = self.unpack_varint()
            elif ty == 2:  val = self.unpack('q')
            elif ty == 3:  val = self.unpack('f')
            elif ty == 4:  val = self.unpack_string()
            elif ty == 5:  val = self.unpack_chat()
            elif ty == 6:  val = self.unpack_optional(self.unpack_chat)
            elif ty == 7:  val = self.unpack_slot()
            elif ty == 8:  val = self.unpack('?')
            elif ty == 9:  val = self.unpack_rotation()
            elif ty == 10: val = self.unpack_position()
            elif ty == 11: val = self.unpack_optional(self.unpack_position)
            elif ty == 12: val = self.unpack_direction()
            elif ty == 13: val = self.unpack_optional(self.unpack_uuid)
            elif ty == 14: val = self.unpack_block()
            elif ty == 15: val = self.unpack_block()
            elif ty == 16: val = self.unpack_nbt()
            elif ty == 17: val = self.unpack_particle()
            elif ty == 18: val = self.unpack_villager()
            elif ty == 19: val = self.unpack_optional_varint()
            elif ty == 20: val = self.unpack_pose()
            elif ty == 21: val = self.unpack_varint(val)
            elif ty == 22: val = self.unpack_varint(val)
            elif ty == 23: val = self.unpack_optional(self.unpack_global_position)
            elif ty == 24: val = self.unpack_varint(val)
            elif ty == 25: val = self.unpack_varint(val) # Sniffer state
            elif ty == 26: val = None #FIXME: Vector
            elif ty == 27: val = None #FIXME: Quaternion
            else: raise ValueError("Unknown entity metadata type: %d" % ty)
            metadata[ty, key] = val

    def unpack_recipe(self):
        """
        Unpacks a crafting recipe.
        """
        recipe = {}
        recipe['type'] = self.unpack_string()
        recipe['name'] = self.unpack_string()

        if recipe['type'] == 'minecraft:crafting_shapeless':
            recipe['group'] = self.unpack_string()
            recipe['category'] = self.unpack_varint()
            recipe['ingredients'] = [
                self.unpack_ingredient() for _ in range(self.unpack_varint())]
            recipe['result'] = self.unpack_slot()

        elif type in simple_recipe_types:
            recipe['category'] = self.unpack_varint()
        else:
            self.restore()
            return super().pack_recipe()

        return recipe

    @classmethod
    def pack_recipe(cls, name, type, **recipe):
        """
        Packs a crafting recipe.
        """
        data = cls.pack_string(type) + cls.pack_string(name)

        if type == 'minecraft:crafting_shapeless':
            data += cls.pack_string(recipe['group'])
            data += cls.pack_varint(recipe['category'])
            data += cls.pack_varint(len(recipe['ingredients']))
            for ingredient in recipe['ingredients']:
                data += cls.pack_ingredient(ingredient)
            data += cls.pack_slot(**recipe['result'])
            data += cls.pack('?', recipe['show_notification']) # Show notification

        elif type in simple_recipe_types:
            data += cls.pack_varint(recipe['category'])
        else:
            return super().pack_recipe(name, type, recipe)

        return data
