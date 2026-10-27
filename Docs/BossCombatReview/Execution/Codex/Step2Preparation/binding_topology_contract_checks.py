"""Offline proposed diagnostic topology contract; no Unreal import or live driver edits."""
import copy
import re
import unittest

GUID = re.compile(r'[0-9a-fA-F]{32}')
GEN = re.compile(r'[1-9][0-9]{0,9}')

def validate_topology(records):
    """Four unique actor paths, one world, two Boss/Player pairs; diagnostic structure only."""
    if not isinstance(records, list) or len(records) != 4:
        return False, 'requires exactly four participant records'
    actors, keys, worlds, encounters = set(), set(), set(), {}
    for record in records:
        if not isinstance(record, dict):
            return False, 'record is not an object'
        actor, key = record.get('actor'), record.get('key')
        if not isinstance(actor, str) or not actor or actor in actors:
            return False, 'actor path missing or reused'
        if not isinstance(key, str):
            return False, 'key missing'
        parts = key.split('/')
        if len(parts) != 4:
            return False, 'key requires world/encounter/slot/generation'
        world, encounter, slot, generation = parts
        if not all(GUID.fullmatch(g) and g != '0'*32 for g in (world, encounter)):
            return False, 'invalid world or encounter identity'
        world, encounter = world.lower(), encounter.lower()
        if slot not in ('Boss', 'Player'):
            return False, 'unexpected participant slot'
        if not GEN.fullmatch(generation) or int(generation) > 0xffffffff:
            return False, 'generation not positive uint32'
        normalized = (world, encounter, slot, int(generation))
        if normalized in keys:
            return False, 'duplicate participant key'
        actors.add(actor); keys.add(normalized); worlds.add(world)
        group = encounters.setdefault(encounter, {})
        if slot in group:
            return False, 'reused slot within encounter'
        group[slot] = int(generation)
    if len(worlds) != 1 or len(encounters) != 2:
        return False, 'requires one world and two encounters'
    if any(set(group) != {'Boss', 'Player'} or group['Boss'] != group['Player']
           for group in encounters.values()):
        return False, 'each encounter requires same-generation Boss/Player pair'
    return True, 'diagnostic topology only; actor association and hydration not proven'

def fixture():
    return [{'actor':f'/Fixture/Actor{i}', 'key':f'{"a"*32}/{enc}/{slot}/{generation}'}
            for i, (enc, slot, generation) in enumerate([
                ('b'*32, 'Boss', 1), ('b'*32, 'Player', 1),
                ('c'*32, 'Boss', 2), ('c'*32, 'Player', 2)])]

class ContractTests(unittest.TestCase):
    def test_positive_independent_generations(self):
        self.assertTrue(validate_topology(fixture())[0])

    def test_uint32_upper_half_pair_valid(self):
        rows = fixture()
        for r in rows[:2]: r['key'] = r['key'].rsplit('/',1)[0] + '/4294967295'
        self.assertTrue(validate_topology(rows)[0])

    def test_original_unique_count_false_pass(self):
        # Four unique keys but one encounter and wrong slots passed original count/uniqueness checks.
        rows = fixture()
        for i, r in enumerate(rows): r['key'] = f'{"a"*32}/{"b"*32}/Slot{i}/1'
        self.assertEqual(len({r['key'] for r in rows}), 4)
        self.assertFalse(validate_topology(rows)[0])

    def test_adversarial_inputs(self):
        mutations = {
            'empty': lambda r: r.clear(),
            'extra': lambda r: r.append(copy.deepcopy(r[0])),
            'duplicate actor': lambda r: r[1].update(actor=r[0]['actor']),
            'duplicate key': lambda r: r[1].update(key=r[0]['key']),
            'foreign world': lambda r: r[1].update(key=r[1]['key'].replace('a'*32,'d'*32)),
            'generation mismatch': lambda r: r[1].update(key=r[1]['key'].rsplit('/',1)[0]+'/2'),
            'zero generation': lambda r: r[0].update(key=r[0]['key'].rsplit('/',1)[0]+'/0'),
            'overflow': lambda r: r[0].update(key=r[0]['key'].rsplit('/',1)[0]+'/4294967296'),
            'noncanonical': lambda r: r[0].update(key=r[0]['key'].rsplit('/',1)[0]+'/01'),
            'zero world': lambda r: r[0].update(key=r[0]['key'].replace('a'*32,'0'*32)),
            'malformed': lambda r: r[0].update(key='not/a/valid/key/extra'),
            'missing actor': lambda r: r[0].pop('actor'),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                rows=fixture(); mutate(rows)
                self.assertFalse(validate_topology(rows)[0])

if __name__ == '__main__':
    unittest.main(verbosity=2)
